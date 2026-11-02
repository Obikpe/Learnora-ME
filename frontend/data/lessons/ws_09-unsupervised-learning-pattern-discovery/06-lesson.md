# Lesson 6: Hierarchical Clustering and Dendrograms

## Learning outcomes

By the end of this lesson, you should be able to Build a hierarchical clustering tree; explain linkage and Ward's method; interpret a dendrogram and cut level; and compare the resulting groups with K-means.

## 1. Core explanation
Hierarchical clustering builds a tree of nested groups. Agglomerative clustering begins with each observation as its own cluster and repeatedly merges the closest clusters. Linkage defines cluster-to-cluster distance: single uses the nearest pair, complete uses the farthest pair, average uses mean pairwise distance, and Ward minimises the increase in within-cluster variance.

A dendrogram visualises merge distances. Cutting the tree at a chosen height produces a set of clusters. The choice of distance metric and linkage changes the result. Ward linkage is typically used with Euclidean distance and numeric features. Hierarchical methods can be expensive for large datasets because pairwise distances and merges grow rapidly.

The dendrogram is not a natural taxonomy by itself. Use domain context, cluster profiles and stability to decide whether a cut is useful. For larger datasets, consider sampling or other scalable methods.

## 2. Worked Python example
Run in VS Code. Install relevant packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`. Some scikit-learn dataset loaders may require internet access on first use.

```python
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster

X = StandardScaler().fit_transform(load_iris().data)
tree = linkage(X, method="ward")
dendrogram(tree, truncate_mode="lastp", p=25)
plt.title("Hierarchical clustering dendrogram")
plt.xlabel("Merged observations or clusters")
plt.ylabel("Merge distance")
plt.show()
labels = fcluster(tree, t=3, criterion="maxclust")
print("Cluster count:", len(set(labels)))
```

## 3. Interpretation
Describe the feature representation, distance or objective, model settings and what the output means. Cluster IDs are arbitrary. An anomaly flag is a prompt for investigation, not proof of misconduct. Validate any discovered pattern in original units and with domain knowledge.

## 4. Guided practice
Compare Ward and average linkage. Explain what the dendrogram height represents and how cutting at different heights changes the number of clusters.

## 5. Independent practice
Choose a dataset and state the purpose of the unsupervised analysis. Compare at least two parameter settings. Profile the resulting groups or flagged cases and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the algorithm attempting to discover?
2. Which assumptions are introduced by the distance or representation?
3. How can you tell whether the result is useful rather than merely computable?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Human interpretation, stability checks and practical validation determine whether those patterns deserve to be used.