from pathlib import Path
import logging
from typing import Iterable, Literal

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import AgglomerativeClustering
from tqdm import tqdm, trange

from document_clustering.qkld_sim import (
    Metric,
    Kld,
    Qkld,
    assign_documents_to_clusters,
    fill_empty_clusters,
    recompute_centroids,
    normalize_documents,
    compute_cluster_sizes,
    merge_shards,
)

np.seterr(all="raise")

logging.basicConfig(level=logging.INFO)


class Qinit:
    def __init__(
        self,
        vocabulary: dict[str, int],
        glove_vectors_path: str | Path,
        query_biased_term_weights: np.ndarray,
    ):
        self.vocabulary = vocabulary
        self.glove_vectors_path = glove_vectors_path
        self.query_biased_term_weights = query_biased_term_weights

        assert len(vocabulary) == query_biased_term_weights.shape[0]

        self.clustering = AgglomerativeClustering(
            metric="cosine", linkage="average", compute_full_tree=True, memory=".cache"
        )

        self.term_embeddings: np.ndarray | None = None
        self.query_terms: list[str] | None = None

    def fit(self) -> "Qinit":
        glove_vectors = self.load_glove_vectors(self.glove_vectors_path)

        self.query_terms = sorted(glove_vectors.keys())
        self.term_embeddings = np.stack(
            [glove_vectors[term] for term in self.query_terms]
        )

        # We fit the full tree here, so extracting centroids for different numbers of clusters is faster later on
        self.clustering.fit(self.term_embeddings)

        return self

    def create_centroids(self, num_clusters: int) -> np.ndarray:
        self.clustering.set_params(n_clusters=num_clusters)
        self.clustering.fit(self.term_embeddings)

        centroids = np.zeros(
            (num_clusters, self.query_biased_term_weights.shape[0]),
            dtype=self.query_biased_term_weights.dtype,
        )

        for term, cluster in zip(self.query_terms, self.clustering.labels_):
            term_id = self.vocabulary[term]
            term_weight = self.query_biased_term_weights[term_id]

            centroids[cluster, term_id] = term_weight

        return centroids

    def load_glove_vectors(
        self, glove_vectors_path: str | Path
    ) -> dict[str, np.ndarray]:
        vocab = set(self.vocabulary)

        vectors = {}
        with open(glove_vectors_path) as file:
            for line in tqdm(file, desc="Loading GloVe embeddings", total=400000):
                parts = line.strip().split()

                if parts[0] in vocab:
                    vectors[parts[0]] = np.array(
                        list(map(float, parts[1:])), dtype="float16"
                    )

        # Ensure all vectors have the same length
        assert len({len(vec) for vec in vectors.values()}) == 1

        return vectors


class Clustering:
    def __init__(
        self,
        num_clusters: int,
        # min_df: int = 1,
        pretokenized: bool = False,
        vocabulary: dict[str, int] | None = None,
        tol: float = 1e-5,
        max_iter: int = 300,
        centroid_init: Literal["random", "qinit"] = "qinit",
        metric: Literal["kld", "qkld"] = "qkld",
        split_large_shards: bool = True,
        merge_small_shards: bool = True,
        num_split_iterations: int = 5,
        num_merge_iterations: int = 5,
        glove_vectors: str | Path | None = None,
        verbose: bool = False,
        metric_kwargs: dict | None = None,
        tokenizer_kwargs: dict | None = None,
        # **metric_kwargs,
    ):
        self.num_clusters = num_clusters
        self.pretokenized = pretokenized
        self.vocabulary = vocabulary
        # self.min_df = min_df
        self.tol = tol
        self.max_iter = max_iter
        self.split_large_shards = split_large_shards
        self.merge_small_shards = merge_small_shards
        self.num_split_iterations = num_split_iterations
        self.num_merge_iterations = num_merge_iterations
        self.glove_vectors = glove_vectors
        self.verbose = verbose

        self.centroid_init = centroid_init
        self.metric_name = metric
        self.metric_kwargs = metric_kwargs or {}

        self.tokenizer_kwargs = dict(stop_words="english", strip_accents="ascii")
        if tokenizer_kwargs is not None:
            self.tokenizer_kwargs.update(tokenizer_kwargs)

        self.vectorizer: CountVectorizer | None = None
        self.background_model: np.ndarray | None = None
        self.query_biased_term_weights: np.ndarray | None = None
        self.centroids: np.ndarray | None = None
        self.qinit: Qinit | None = None
        self.metric: Metric | None = None
        self.num_clusters_: int | None = None

        if self.centroid_init == "qinit" and self.glove_vectors is None:
            raise ValueError(
                "QInit centroid initialization requires GloVe vectors to be passed."
            )

        if self.pretokenized and self.vocabulary is None and self.centroid_init == "qinit":
            raise ValueError(
                "QInit centroid initialization needs a specific vocabulary when "
                "using pretokenized documents."
            )

    def fit(self, documents: Iterable[str] | csr_matrix, queries: Iterable[str] | csr_matrix | None = None):
        self.fit_transform(documents, queries)
        return self

    def fit_transform(
        self, documents: Iterable[str] | csr_matrix, queries: Iterable[str] | csr_matrix | None = None
    ):
        if queries is None and (
            self.metric_name == "qkld" or self.centroid_init == "qinit"
        ):
            raise ValueError(
                "QKLD metric and QInit centroid initialization require queries to be passed."
            )

        self._check_inputs(documents, queries)

        if not self.pretokenized:
            self.vectorizer = CountVectorizer(**self.tokenizer_kwargs)
            documents: csr_matrix = self.vectorizer.fit_transform(
                tqdm(documents, desc="Tokenizing documents", disable=not self.verbose)
            )
            self.vocabulary = self.vectorizer.vocabulary_

        logging.info("Computing document frequencies")
        document_frequencies = (documents > 0).sum(axis=0).A1

        logging.info("Normalizing documents")
        documents = normalize_documents(documents)

        logging.info("Computing background model")
        self.background_model = documents.mean(axis=0).A1

        num_docs = documents.shape[0]

        if self.metric_name == "qkld" or self.centroid_init == "qinit":
            self._init_query_biased_term_weights(
                queries, num_docs, document_frequencies
            )

        if self.metric_name == "kld":
            self.metric = Kld(**self.metric_kwargs)
        elif self.metric_name == "qkld":
            self.metric = Qkld(self.query_biased_term_weights, **self.metric_kwargs)

        if self.centroid_init == "qinit":
            self.qinit = Qinit(
                self.vocabulary,
                self.glove_vectors,
                self.query_biased_term_weights,
            ).fit()

        logging.info("Clustering documents")
        centroids, assignment = self._cluster_documents(documents)

        if self.split_large_shards:
            centroids, assignment = self._split_large_shards(
                documents, centroids, assignment
            )

        self.num_clusters_ = centroids.shape[0]
        self.centroids = centroids


        if self.merge_small_shards:
            assignment = self._merge_small_shards(assignment)

        return assignment

    def transform(self, documents: Iterable[str] | csr_matrix) -> np.ndarray:
        assignment = self._transform_documents(documents)

        if self.merge_small_shards:
            assignment = self._merge_small_shards(assignment)

        return assignment

    def transform_batches(self, batches: Iterable[Iterable[str] | csr_matrix]) -> np.ndarray:
        assignments = []

        for batch in tqdm(
            batches, desc="Transforming batches", disable=not self.verbose
        ):
            assignments.append(self._transform_documents(batch))

        assignment = np.concatenate(assignments)

        if self.merge_small_shards:
            assignment = self._merge_small_shards(assignment)

        return assignment

    def _transform_documents(self, documents: Iterable[str] | csr_matrix) -> np.ndarray:
        if self.centroids is None:
            raise ValueError("Clustering module has not been fit.")

        self._check_inputs(documents)

        if not self.pretokenized:
            documents: csr_matrix = self.vectorizer.transform(
                tqdm(documents, desc="Tokenizing documents", disable=not self.verbose)
            )

        docs = normalize_documents(documents)

        assignment, _ = assign_documents_to_clusters(
            docs, self.centroids, self.background_model, self.metric
        )

        return assignment

    def _cluster_documents(
        self, documents: csr_matrix, num_clusters: int | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        is_main_clustering = num_clusters is None
        if is_main_clustering:
            num_clusters = self.num_clusters

        centroids = self._create_centroids(documents, num_clusters)
        assignment = np.zeros(documents.shape[0], dtype=np.int32)

        with trange(
            self.max_iter,
            desc="Clustering",
            disable=not self.verbose,
            leave=is_main_clustering,
        ) as pbar:
            for i in pbar:
                assignment_new, similarities = assign_documents_to_clusters(
                    documents, centroids, self.background_model, self.metric
                )
                assignment_new, similarities = fill_empty_clusters(
                    assignment_new, similarities, num_clusters
                )

                assignment, assignment_new = assignment_new, assignment

                centroids_new = recompute_centroids(documents, assignment, num_clusters)
                centroids, centroids_new = centroids_new, centroids

                center_shift_tot = ((centroids - centroids_new) ** 2).sum()

                pbar.set_postfix(
                    {
                        "diff": (assignment != assignment_new).sum(),
                        "center_shift": center_shift_tot,
                    }
                )

                if np.array_equal(assignment, assignment_new):
                    if is_main_clustering:
                        pbar.write(f"Converged at iteration {i}: strict convergence.")
                    break
                elif center_shift_tot < self.tol:
                    if is_main_clustering:
                        pbar.write(
                            f"Converged at iteration {i}: center shift "
                            f"{center_shift_tot} within tolerance {self.tol}."
                        )
                    break

        return centroids, assignment

    def _split_shards(
        self,
        documents: csr_matrix,
        centroids: np.ndarray,
        assignment: np.ndarray,
        avg_shard_size: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        cluster_sizes = compute_cluster_sizes(assignment, centroids.shape[0])
        large_shards = cluster_sizes > 1.1 * avg_shard_size

        if not large_shards.any():
            if self.verbose:
                print("No longer splitting")
            return centroids, assignment

        # TODO: can we optimize this using Cython?

        normal_shards = np.argwhere(~large_shards).flatten()

        num_splits = np.where(
            large_shards, np.ceil(cluster_sizes / avg_shard_size).astype(np.int32), 1
        )

        new_num_clusters = num_splits.sum()

        new_centroids = np.zeros(
            (new_num_clusters, centroids.shape[1]), dtype=np.float64
        )
        new_assignment = np.empty_like(assignment)

        new_centroids[: len(normal_shards)] = centroids[normal_shards]
        normal_offset = 0
        large_offset = len(normal_shards)

        for shard, nsplits in enumerate(num_splits):
            if nsplits == 1:
                new_assignment[assignment == shard] = normal_offset
                normal_offset += 1
            else:
                subset = documents[assignment == shard]
                sub_centroids, sub_assignment = self._cluster_documents(subset, nsplits)

                new_centroids[large_offset : large_offset + nsplits] = sub_centroids
                new_assignment[assignment == shard] = sub_assignment + large_offset

                large_offset += nsplits

        assert (
            compute_cluster_sizes(new_assignment, new_num_clusters).sum()
            == cluster_sizes.sum()
        )

        return new_centroids, new_assignment

    def _split_large_shards(
        self, documents: csr_matrix, centroids: np.ndarray, assignment: np.ndarray
    ) -> np.ndarray:
        average_shard_size = assignment.shape[0] / centroids.shape[0]

        for _ in trange(
            self.num_split_iterations,
            desc="Splitting large shards",
            disable=not self.verbose,
        ):
            centroids, assignment = self._split_shards(
                documents, centroids, assignment, average_shard_size
            )

        return centroids, assignment

    def _merge_small_shards(self, assignments: np.array) -> np.array:
        average_shard_size = assignments.shape[0] / self.num_clusters

        num_shards = self.num_clusters_

        for _ in trange(
            self.num_merge_iterations,
            desc="Merging small shards",
            disable=not self.verbose,
        ):
            assignments, num_shards = merge_shards(
                assignments, num_shards, average_shard_size
            )

        return assignments

    def _create_centroids(self, documents: csr_matrix, num_clusters: int) -> np.ndarray:
        if self.centroid_init == "random":
            selected_docs = np.random.choice(
                documents.shape[0], num_clusters, replace=False
            )
            return documents[selected_docs].toarray()
        if self.centroid_init == "qinit":
            return self.qinit.create_centroids(num_clusters)
        raise ValueError(
            f"Invalid centroid initialization method {self.centroid_init}."
        )

    def _init_query_biased_term_weights(
        self, queries: Iterable[str] | csr_matrix, num_docs: int, document_frequencies: np.ndarray
    ):
        if not self.pretokenized:
            queries: csr_matrix = self.vectorizer.transform(
                tqdm(queries, desc="Tokenizing queries", disable=not self.verbose)
            )

        query_term_counts = queries.sum(axis=0).A1

        self.query_biased_term_weights = np.log1p(query_term_counts) * np.log1p(
            num_docs / document_frequencies
        )

    def _check_inputs(self, documents: Iterable[str] | csr_matrix, queries: Iterable[str] | csr_matrix | None = None):
        if self.pretokenized:
            assert isinstance(documents, csr_matrix), "Documents must be passed as csr_matrix when pre_tokenized=True."

            if queries is not None:
                assert isinstance(queries, csr_matrix), "Queries must be passed as csr_matrix when pre_tokenized=True."
        else:
            assert not isinstance(documents, csr_matrix), "Documents passed as csr_matrix, but pre_tokenized=False."
            assert not isinstance(queries, csr_matrix), "Queries passed as csr_matrix, but pre_tokenized=False."
