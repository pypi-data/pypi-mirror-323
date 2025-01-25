# Document Clustering for Selective Search

This repository contains an open source implementation of the SB² K-means clustering algorithm for document collections. It supports a standard KLD-based distance metric, but also query-biased distance metric QKLD and query-biased centroid initialization QInit. Tokenization and vectorization is performed using scikit-learn, and we implemented the clustering algorithm efficiently (and parallelized wherever possible) using custom Cython code.

## Installation

Simply install the dependencies and `doc_clustering` module using Poetry:

    poetry install

We plan to also publish this as a PyPI package soon, stay tuned!

## Usage

The clustering API closely follows the scikit-learn API:

```python
from doc_clustering import Clustering

num_clusters = 5
clustering = Clustering(num_clusters).fit(['document A', 'document B'])

mapping = clustering.transform(['document C'])
```

To use the QKLD distance metric (instead of the default KLD), supply the `metric` parameter and supply queries in the call to `fit`.

```python
clustering = Clustering(num_clusters, metric='qkld')
clustering.fit(['document A', 'document B'], ['query 1', 'query 2'])

mapping = clustering.transform(['document C'])
```

To use the QInit centroid initialization, supply the `centroid_init` and `glove_vectors` parameters, and again supply queries in the `fit` call:

```python
clustering = Clustering(num_clusters, centroid_init='qinit', glove_vectors='/path/to/glove.6B.100d.txt')
clustering.fit(['document A', 'document B'], ['query 1', 'query 2'])

mapping = clustering.transform(['document C'])
```

Finally, to perform size-bounded clustering, you can use the `split_large_shards` and `merge_small_shards` parameters.

```python
clustering = Clustering(num_clusters, split_large_shards=True, merge_small_shards=True)
clustering.fit(['document A', 'document B'])

mapping = clustering.transform(['document C'])
```

For a full example, check out [the script we used to cluster the TREC CAsT corpus](cluster_cast.py).

## References

1. Kulkarni, A. 2013. Efficient and Effective Large-scale Search. Carnegie Mellon University.
2. Dai, Z. et al. 2016. Query-Biased Partitioning for Selective Search. CIKM 2016.
