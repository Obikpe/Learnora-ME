# Lesson 6: Hierarchical Clustering and Dendrograms

## Learning outcomes

By the end of this lesson, you should be able to explain agglomerative hierarchical clustering; describe how clusters merge; interpret a dendrogram and its merge heights; distinguish common linkage methods; fit a hierarchical model with SciPy and scikit-learn; and identify when hierarchical clustering is useful or unsuitable.

![A hierarchical tree showing how observations merge](/course-assets/ws09/dendrogram.svg)

## 1. What makes hierarchical clustering different?

K-means asks you to choose K before fitting and then represents each group with a centroid. Hierarchical clustering builds a nested structure of groups. Instead of immediately producing one flat partition, it records how observations or existing groups are joined together at different levels of similarity.

The result is often displayed as a **dendrogram**, a tree diagram. The leaves at the bottom represent individual observations. Branches show which observations or groups are joined. The height at which branches meet represents the distance or dissimilarity at which the merge occurs.

Hierarchical clustering is useful when you want to explore relationships at multiple levels. For example, a collection of products may first form several close families, which later combine into broader product categories.

## 2. Agglomerative clustering: build from small to large

Agglomerative clustering is a bottom-up hierarchical method. It begins with every observation as its own cluster.

The general process is:

1. Start with n observations and n one-row clusters.
2. Calculate distances between clusters.
3. Merge the two clusters considered closest under the selected linkage rule.
4. Recalculate the distances between the new cluster and the remaining clusters.
5. Repeat until all observations are joined into one tree.

At the beginning, the closest pair of observations is merged. Later, the algorithm compares groups containing multiple observations. The way it defines the distance between groups is called **linkage**.

## 3. Linkage methods: how is cluster-to-cluster distance defined?

Different linkage methods can produce different trees from the same observations.

### Single linkage

Single linkage defines the distance between two clusters as the smallest distance between any observation in one cluster and any observation in the other. It can connect long, curved or chain-like structures, but it may create a chaining effect: a sequence of nearby points joins groups that are not compact overall.

### Complete linkage

Complete linkage uses the largest pairwise distance between observations across the two clusters. It tends to favour compact groups because a merge is judged by the most distant pair. It can be sensitive to outliers.

### Average linkage

Average linkage calculates the average distance across all pairs of observations, one from each cluster. It is a compromise between single and complete linkage.

### Ward linkage

Ward linkage merges the pair of clusters that produces the smallest increase in total within-cluster variance. It often produces compact groups and is commonly used with Euclidean distance. Ward linkage is not interchangeable with arbitrary distance metrics; use it with the assumptions required by the implementation.

## 4. Read a dendrogram carefully

A dendrogram is not a decorative tree. Its structure carries information.

- Each leaf corresponds to an original observation.
- A branch point indicates a merge.
- The vertical position of a merge represents the distance or linkage cost at which the merge happened.
- A horizontal cut across the tree creates a flat clustering. The number of branches the cut crosses determines the number of groups.

If two observations merge at a low height, they were close under the chosen distance and linkage. If two large branches join only at a much higher height, the groups were more dissimilar at the time they merged.

The horizontal ordering of leaves is often rearranged for readability. Do not interpret left-to-right position as a ranking or a meaningful numeric scale.

## 5. Build and inspect a dendrogram with SciPy

Install the required packages:

```bash
python -m pip install numpy scipy matplotlib 'scikit-learn>=1.2'
```

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster

X = np.array([
    [1, 2], [1.5, 1.8], [2, 2.2],
    [8, 8], [8.5, 9], [9, 8.2]
])

# Ward linkage builds the hierarchy.
Z = linkage(X, method="ward")

plt.figure(figsize=(9, 5))
dendrogram(Z, labels=["A", "B", "C", "D", "E", "F"])
plt.ylabel("Ward linkage distance")
plt.title("Agglomerative hierarchical clustering")
plt.tight_layout()
plt.show()

# Cut the tree to obtain three flat groups.
labels = fcluster(Z, t=3, criterion="maxclust")
print("Cluster assignments:", labels)
```

`linkage` constructs the hierarchy. Its output is a linkage matrix: each row records the two clusters merged, the merge distance and the number of original observations contained in the new cluster. `method="ward"` selects Ward's variance-minimising rule.

`dendrogram` draws the tree. Labels help you identify the leaves in this small example. `fcluster` converts the hierarchy into a flat set of groups. With `criterion="maxclust"`, `t=3` requests no more than three clusters.

For a large dataset, drawing every leaf becomes unreadable. You may need a sample, a truncated dendrogram or a different visual summary. Hierarchical methods can also require substantial memory and computation because they rely on pairwise relationships.

## 6. Use scikit-learn for cluster labels

```python
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
import pandas as pd

customers = pd.DataFrame({
    "recency": [5, 8, 12, 65, 75, 90],
    "orders": [12, 10, 8, 2, 1, 0],
    "basket": [500, 420, 380, 90, 70, 30]
})

X_scaled = StandardScaler().fit_transform(customers)

model = AgglomerativeClustering(
    n_clusters=2,
    metric="euclidean",
    linkage="ward"
)
labels = model.fit_predict(X_scaled)

print(customers.assign(cluster=labels))
```

The model is fitted using scaled measurements. `n_clusters=2` requests two flat groups. `metric="euclidean"` selects Euclidean distance, and `linkage="ward"` selects Ward's method. The labels are then attached to the original values for interpretation.

Hierarchical clustering is often described as not needing K, but this needs qualification. You can inspect the full hierarchy without deciding on a flat K first. If you want a final set of groups, you still need to choose a cut height or number of clusters.

## 7. Hierarchical clustering compared with K-means

| Property | K-means | Agglomerative hierarchical |
|---|---|---|
| Main output | Flat clusters and centroids | Nested merge tree |
| Must choose K before fitting? | Yes | Not to build the full tree |
| Group representation | Mean centroid | Nested membership |
| Typical strengths | Efficient for many numeric rows | Useful for exploring nested structure |
| Common limitations | Shape and scale assumptions | Pairwise computation and sensitivity to linkage |

Neither method is universally superior. K-means can be more practical for large datasets. Hierarchical clustering can be easier to explore when the dataset is small enough and the nested relationships matter.

## 8. Common mistakes

- Assuming a dendrogram's horizontal leaf order is a ranking.
- Treating merge height as a probability.
- Comparing trees built with different feature scaling without noting it.
- Using Ward linkage with an incompatible distance definition.
- Cutting the dendrogram at an arbitrary height without explaining why.
- Drawing thousands of leaves and expecting a readable chart.
- Assuming a hierarchical tree proves natural categories exist.

## 9. Guided practice

Use six points arranged in three visibly close pairs. Build a Ward dendrogram. Identify the first merges and the final merge. Draw an imaginary horizontal cut that produces three groups, then explain why a lower or higher cut would change the number of groups.

## 10. Independent practice

Choose a small numeric dataset. Scale it where appropriate and compare single, complete, average and Ward linkage. Plot the dendrograms and explain how the merge structure changes. Select one solution for further interpretation and justify the choice using both the tree and the original feature profiles.

## 11. Knowledge check

1. What is the difference between agglomerative and divisive hierarchical clustering?
2. What does a leaf represent in a dendrogram?
3. How does single linkage define the distance between clusters?
4. Why can complete linkage favour compact clusters?
5. What does a horizontal cut across a dendrogram do?
6. Why is Ward linkage commonly paired with Euclidean distance?
7. What practical limitation appears when the dataset contains many thousands of rows?

## Lesson summary

Agglomerative hierarchical clustering starts with individual observations and repeatedly merges groups. The dendrogram records this nested history. Linkage determines how group-to-group distance is measured, and a cut converts the tree into a flat clustering. Interpret merge heights in the context of the chosen features, scaling and linkage; do not treat the tree as proof of objectively correct categories.
