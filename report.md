# t-Spanner Construction Project Report

## 1. Introduction

Graph spanners are sparse subgraphs that approximately preserve distances between nodes. Given a graph $ G = (V, E) $, a subgraph $ H = (V, E') $ is a *t*-spanner if for all $ u, v \in V $, the distance $ d_H(u, v) \leq t \cdot d_G(u, v) $, where $ t \geq 1 $ is the stretch factor.

This project focuses on the randomized algorithms for *t*-spanner construction, particularly the algorithm by **Baswana and Sen**, which efficiently constructs sparse *t*-spanners with provable guarantees on size and stretch. The primary goal is to analyze these algorithms, study engineering trade-offs, and experimentally evaluate performance.

## 2. Problem Statement

Given an undirected, connected, weighted or unweighted graph $ G $, the task is to construct a sparse *t*-spanner $ H \subseteq G $ such that:

- $ H $ contains significantly fewer edges than $ G $,
- $ H $ approximately preserves shortest path distances within a factor of $ t $,
- The construction algorithm is efficient in terms of runtime and memory usage.

We study:
- Trade-offs between sparsity and runtime,
- Heuristics like keeping all edges from low-degree nodes,
- Parallelism for scalable construction.

## 3. Background and Literature Review

The algorithm by **Baswana and Sen (2007)** constructs a $ (2k - 1) $-spanner in $ O(k \cdot m) $ expected time for any $ k \geq 1 $, where $ m = |E| $. It uses randomized clustering over $ k $ iterations:

- Randomly mark a subset of vertices as cluster centers,
- Add edges to connect each vertex to a nearby center,
- Propagate clusters over successive iterations,
- Maintain cluster hierarchy to ensure the spanner property.

For $ k = 2 $, we obtain a 3-spanner, which is the case discussed in class. The approach generalizes to any $ t = 2k - 1 $ by increasing $ k $.

Key readings: Sections 2, 3, 4.3, and 5.3 of [randstruc.pdf] (Baswana & Sen).

## 4. Algorithm Overview

### 4.1 Baswana-Sen Randomized Spanner Construction (for $ t = 2k - 1 $)

#### Pseudocode Outline:

1. **Initialization**: Each vertex is in its own cluster.
2. **Repeat for $ k - 1 $ iterations**:
   - Randomly sample clusters with probability $ n^(-1/k) $
   - For each vertex, connect to a marked neighbor (if any).
   - Merge vertices into clusters based on chosen centers.
3. **Edge Inclusion**: Add smallest vertex-cluster edges in phase 2 to preserve spanner guarantees.

## 5. Engineering Choices

- **Retention of edges from low-degree nodes**: Reduces distortion locally at the expense of extra edges.
- **Data structure**: Graphs represented using adjacency lists for efficient traversal.
- **Parallelism**: Can be explored in the clustering and neighbor-checking steps.

## 6. Implementation Details

- Language: C/C++
- Graph stored as adjacency lists using STL containers (e.g., `vector<vector<int>>`) for efficient traversal.
- Each edge can easily refer to the reverse edge for efficient lazy deletion and additon.
- **Avoidance of High-Level Data Structures**: High-level structures like `std::set` and `std::map` are avoided to reduce memory and runtime overhead. Instead, arrays (`std::vector`) and manual indexing are used for graph data and cluster management.
- **Global Variables for Consistency**: Global variables like `adj` (adjacency list) and `cluster` ensure that the order of node processing does not affect the algorithm's correctness. This simplifies logic and avoids unintended side effects from local variable scoping.
- Randomized clustering uses `std::random_device` and `std::mt19937_64` for efficient and reproducible random sampling.
- **Manual Edge Management**: Edges are explicitly marked with statuses (`0` for removed, `1` for possible, `2` for included in the spanner) to avoid dynamic data structure operations.
- Optional multithreading with OpenMP for edge marking and scanning.
- Input/Output through text files, edge lists, or adjacency lists.

## 7. Experiments

### 7.1 Experimental Setup

- Dataset: Synthetic graphs (random, grid, scale-free), real-world graph samples
- Metrics:
  - Number of edges in spanner vs. original
  - Runtime for construction
  - Average and maximum stretch

### 7.2 Results

(Include plots and tables here: edge count vs. t, runtime vs. input size, etc.)

### 7.3 Running Tests

Use the following command to view the test suite:
`python main.py -h`


## 8. Conclusion

The Baswana-Sen algorithm offers an efficient and scalable approach for t-spanner construction. Through appropriate implementation and optimization, it can be applied to large-scale graphs with strong empirical results in sparsity and runtime.

## 9. References

- Baswana, S., & Sen, S. (2007). *A simple and linear time randomized algorithm for computing sparse spanners in weighted graphs*. [randstruc.pdf]

## Appendix

### A. Sample Input Format

```
n m t
u_1 v_1 w_1
u_2 v_2 w_2
...
u_m v_m w_m
```

### Sample Output Format

```
n m
u_1 v_1 w_1
u_2 v_2 w_2
...
u_m v_m w_m
```
The format shown above represents the spanner (`m` is the number of edges in the spanner).