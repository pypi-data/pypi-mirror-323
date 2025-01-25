# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: binding=False
# cython: initializedcheck=False
# cython: cdivision=True
# distutils: extra_compile_args=-fopenmp
# distutils: extra_link_args=-fopenmp

import numpy as np
from scipy.sparse import csr_matrix
from numpy.math cimport INFINITY

import cython
from cython.cimports.libc.math import log
from cython.parallel import prange

DTYPE = np.float64

@cython.cclass
class Metric:

    @cython.cfunc
    @cython.nogil
    @cython.exceptval(check=False)
    def compute(self, term: cython.Py_ssize_t, tf: cython.double, p_c: cython.double, p_b: cython.double) -> cython.double:
        pass


@cython.final
@cython.cclass
class Kld(Metric):

    mu_smoothing: cython.double
    l_smoothing: cython.double
    
    def __init__(self, mu_smoothing: cython.double = 0.1, l_smoothing: cython.double = 0.1):
        self.mu_smoothing = mu_smoothing
        self.l_smoothing = l_smoothing

    @cython.final
    @cython.ccall
    @cython.nogil
    @cython.exceptval(check=False)
    def compute(self, term: cython.Py_ssize_t, tf: cython.double, p_c: cython.double, p_b: cython.double) -> cython.double:
        return skld(tf, p_c, p_b, self.l_smoothing, self.mu_smoothing)


@cython.final
@cython.cclass
class Qkld(Metric):

    query_biased_term_weights: cython.double[::1]
    mu_smoothing: cython.double
    l_smoothing: cython.double
    b_smoothing: cython.double

    def __init__(self, query_biased_term_weights: cython.double[::1], mu_smoothing: cython.double = 0.1, l_smoothing: cython.double = 0.1, b_smoothing: cython.double = 1 / 16):
        self.query_biased_term_weights = query_biased_term_weights
        self.mu_smoothing = mu_smoothing
        self.l_smoothing = l_smoothing
        self.b_smoothing = b_smoothing

    @cython.final
    @cython.ccall
    @cython.nogil
    @cython.exceptval(check=False)
    def compute(self, term: cython.Py_ssize_t, tf: cython.double, p_c: cython.double, p_b: cython.double) -> cython.double:
        return skld(tf, p_c, p_b, self.l_smoothing, self.mu_smoothing) * (self.query_biased_term_weights[term] + self.b_smoothing)


@cython.nogil
@cython.cfunc
@cython.inline
@cython.exceptval(check=False)
def skld(tf: cython.double, p_c: cython.double, p_b: cython.double,
         l_smoothing: cython.double, mu_smoothing: cython.double) -> cython.double:
    if p_c == 0:
        return 0

    l_p_b: cython.double = l_smoothing * p_b

    p_d: cython.double = (1 - mu_smoothing) * tf + mu_smoothing * p_b

    return p_c * log(p_d / l_p_b) + p_d * log(p_c / l_p_b)


@cython.exceptval(check=False)
def assign_documents_to_clusters(
    docs: csr_matrix, centroids: cython.double[:, ::1], background_model: cython.double[::1], metric: Metric
) -> tuple[np.ndarray, np.ndarray]:
    ndocs: cython.Py_ssize_t = docs.shape[0]
    nclusters: cython.Py_ssize_t = centroids.shape[0]

    assert docs.shape[1] == centroids.shape[1]
    assert docs.dtype == DTYPE, docs.dtype

    docs_indptr: cython.int[:] = docs.indptr
    docs_indices: cython.int[:] = docs.indices
    docs_data: cython.double[:] = docs.data

    doc: cython.Py_ssize_t
    cluster: cython.int
    indptr: cython.Py_ssize_t
    term: cython.Py_ssize_t

    sim: cython.double

    assignments_np = np.empty(ndocs, dtype=np.int32)
    similarities_np = np.full(ndocs, -np.inf, dtype=DTYPE)

    assignments: cython.int[::1] = assignments_np
    similarities: cython.double[::1] = similarities_np

    for doc in prange(ndocs, nogil=True):
        for cluster in range(nclusters):
            sim = 0

            for indptr in range(docs_indptr[doc], docs_indptr[doc + 1]):
                term = docs_indices[indptr]

                sim = sim + metric.compute(term, docs_data[indptr], centroids[cluster, term], background_model[term])

            if sim > similarities[doc]:
                assignments[doc] = cluster
                similarities[doc] = sim

    return assignments_np, similarities_np


@cython.exceptval(check=False)
def fill_empty_clusters(
    assignments_np: np.ndarray, similarities_np: np.ndarray, nclusters: cython.int
) -> tuple[np.ndarray, np.ndarray]:    
    assert assignments_np.shape[0] == similarities_np.shape[0]

    assignments: cython.int[::1] = assignments_np
    similarities: cython.double[::1] = similarities_np

    cluster_sizes: cython.int[::1] = compute_cluster_sizes(assignments, nclusters)

    ndocs: cython.Py_ssize_t = assignments_np.shape[0]
    least_similar_doc: cython.Py_ssize_t
    original_assignment: cython.Py_ssize_t

    # Assign least similar doc to empty cluster
    for cluster in range(nclusters):
        if cluster_sizes[cluster] == 0:
            least_similar_doc = 0
            for doc in range(1, ndocs):
                if ((cluster_sizes[assignments[least_similar_doc]] == 1 or similarities[doc] < similarities[least_similar_doc])
                        and cluster_sizes[assignments[doc]] > 1):
                    least_similar_doc = doc
    
            original_assignment = assignments[least_similar_doc]
            cluster_sizes[cluster] += 1
            cluster_sizes[original_assignment] -= 1
    
            assignments[least_similar_doc] = cluster
            similarities[least_similar_doc] = INFINITY

    return assignments_np, similarities_np


@cython.exceptval(check=False)
def recompute_centroids(
    docs: csr_matrix, assignments: cython.int[::1], nclusters: cython.int
) -> np.ndarray:
    ndocs: cython.Py_ssize_t = docs.shape[0]
    nterms: cython.Py_ssize_t = docs.shape[1]

    assert docs.shape[0] == assignments.shape[0]
    assert docs.dtype == DTYPE, docs.dtype

    docs_indptr: cython.int[:] = docs.indptr
    docs_indices: cython.int[:] = docs.indices
    docs_data: cython.double[:] = docs.data

    centroids_np = np.zeros((nclusters, nterms), dtype=DTYPE)
    centroids: cython.double[:, ::1] = centroids_np

    cluster_sizes: cython.int[::1] = np.zeros(nclusters, dtype=np.int32)

    doc: cython.Py_ssize_t
    cluster: cython.Py_ssize_t
    indptr: cython.Py_ssize_t
    term: cython.Py_ssize_t

    for doc in range(ndocs):
        cluster = assignments[doc]
        cluster_sizes[cluster] += 1
        for indptr in range(docs_indptr[doc], docs_indptr[doc + 1]):
            centroids[cluster, docs_indices[indptr]] += docs_data[indptr]

    for cluster in prange(nclusters, nogil=True):
        for term in range(nterms):
            centroids[cluster, term] /= cluster_sizes[cluster]

    return centroids_np


@cython.exceptval(check=False)
def normalize_documents(docs: csr_matrix) -> csr_matrix:
    ndocs: cython.Py_ssize_t = docs.shape[0]

    doc: cython.Py_ssize_t
    indptr: cython.Py_ssize_t

    size: cython.double

    docs_indptr: cython.int[:] = docs.indptr
    docs_data: cython.long[:] = docs.data

    new_data_np = np.empty_like(docs.data, dtype=DTYPE)
    new_data: cython.double[::1] = new_data_np

    for doc in prange(ndocs, nogil=True):
        size = 0

        for indptr in range(docs_indptr[doc], docs_indptr[doc + 1]):
            size = size + docs_data[indptr]

        for indptr in range(docs_indptr[doc], docs_indptr[doc + 1]):
            new_data[indptr] = docs_data[indptr] / size

    return csr_matrix((new_data_np, docs.indices, docs.indptr), shape=docs.shape)


@cython.exceptval(check=False)
def compute_cluster_sizes(assignment: cython.int[::1], nclusters: cython.int) -> np.ndarray:
    ndocs: cython.Py_ssize_t = assignment.shape[0]

    cluster_sizes_np = np.zeros(nclusters, dtype=np.int32)
    cluster_sizes: cython.int[::1] = cluster_sizes_np

    doc: cython.Py_ssize_t

    for doc in range(ndocs):
        cluster_sizes[assignment[doc]] += 1

    return cluster_sizes_np


@cython.exceptval(check=False)
def merge_shards(assignment: cython.int[::1], nshards: cython.int, avg_shard_size: cython.double) -> tuple[np.ndarray, int]:
    ndocs: cython.Py_ssize_t = assignment.shape[0]

    shard_sizes: cython.int[::1] = compute_cluster_sizes(assignment, nshards)
    ordered_shards: cython.Py_ssize_t[:] = np.argsort(shard_sizes)[::-1]

    shard_mapping: cython.int[::1] = np.full_like(shard_sizes, -1, dtype=np.int32)

    new_shard_num: cython.int = 0

    i: cython.Py_ssize_t
    j: cython.Py_ssize_t
    sink: cython.Py_ssize_t
    source: cython.Py_ssize_t

    for i in range(nshards):
        sink = ordered_shards[i]

        if shard_mapping[sink] >= 0:
            continue

        shard_mapping[sink] = new_shard_num

        if shard_sizes[sink] > 1.1 * avg_shard_size:
            new_shard_num += 1
            continue

        for j in range(i + 1, nshards):
            source = ordered_shards[j]

            if shard_mapping[source] >= 0:
                continue
            elif shard_sizes[source] >= 0.9 * avg_shard_size:
                continue
            elif shard_sizes[sink] + shard_sizes[source] > 1.1 * avg_shard_size:
                continue

            shard_mapping[source] = new_shard_num
            break

        new_shard_num += 1

    doc: cython.Py_ssize_t

    new_assignment_np = np.empty_like(assignment, dtype=np.int32)
    new_assignment: cython.int[::1] = new_assignment_np

    for doc in prange(ndocs, nogil=True):
        new_assignment[doc] = shard_mapping[assignment[doc]]

    return new_assignment_np, new_shard_num
