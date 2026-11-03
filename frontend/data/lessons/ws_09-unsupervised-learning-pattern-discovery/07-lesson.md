# Lesson 7: DBSCAN and Density-Based Clustering

## Learning outcomes

By the end of this lesson, you should be able to explain density-based clustering; define epsilon, min_samples, core points, border points and noise; describe how DBSCAN expands clusters; fit DBSCAN with scikit-learn; interpret noise labels; and explain why scaling and parameter selection are important.

![Density-based clustering separates dense regions and noise](/course-assets/ws09/clustering-concepts.svg)

## 1. Why do we need another clustering method?

K-means is useful for compact groups, but it has important limitations. It asks for K in advance, uses centroids and tends to favour roughly spherical clusters. Imagine GPS observations forming two curved shapes, or sensor readings forming dense regions surrounded by scattered points. A centroid-based method may divide these shapes poorly.

DBSCAN stands for **Density-Based Spatial Clustering of Applications with Noise**. It identifies clusters as connected regions of sufficiently high point density. It can find non-spherical shapes and explicitly mark observations that do not belong to a dense region as noise.

DBSCAN does not require the analyst to specify the number of clusters. However, it does require parameters that define what counts as a dense neighbourhood. It is not parameter-free.

## 2. The two main parameters

### Epsilon (eps)

Epsilon is the neighbourhood radius. For an observation, DBSCAN looks for other observations within this distance. A small epsilon creates small neighbourhoods; a larger epsilon includes more points.

The correct numerical value depends on the feature scale and distance metric. An epsilon of 0.5 means very different things when features are measured in metres versus standardised units. Always inspect the representation before choosing it.

### Minimum samples (min_samples)

`min_samples` is the minimum number of observations required in an epsilon-neighbourhood for a point to qualify as a **core point**. The count includes the point itself in scikit-learn's DBSCAN implementation.

A larger value requires denser neighbourhoods. A smaller value allows sparser regions to qualify, but may create more clusters from accidental local concentrations.

## 3. Core, border and noise points

DBSCAN distinguishes three kinds of points.

- **Core point:** has at least `min_samples` points in its epsilon-neighbourhood.
- **Border point:** is within the neighbourhood of a core point but does not itself have enough neighbours to be core.
- **Noise point:** is not assigned to a cluster through the density-reachability process.

A border point can belong to a cluster even though its own neighbourhood is not dense enough to start or expand one. A noise point receives label -1 in scikit-learn.

Noise does not mean that the row is wrong, fraudulent or unimportant. It means the point was not assigned to a dense cluster under the chosen parameters and representation.

## 4. How DBSCAN forms clusters

1. Select an unvisited observation.
2. Find all observations within its epsilon-neighbourhood.
3. If it has fewer than `min_samples` neighbours, mark it temporarily as noise.
4. If it is a core point, start a cluster.
5. Add its density-reachable neighbours. If one of those neighbours is also a core point, expand the cluster using that point's neighbourhood too.
6. Continue until the cluster can no longer expand.
7. Move to another unvisited observation and repeat.

A point previously marked as noise may later be included as a border point if it is found within the neighbourhood of a core point. This is why noise labels are model outcomes, not permanent properties of a record.

## 5. Fit DBSCAN in Python

Install the packages:

```bash
python -m pip install numpy pandas matplotlib scikit-learn
```

```python
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

data = pd.DataFrame({
    "measurement_a": [1.0, 1.1, 0.9, 1.2, 5.0, 5.1, 4.9, 5.2, 9.0],
    "measurement_b": [1.0, 1.2, 0.8, 1.1, 5.0, 5.2, 4.8, 5.1, 1.0]
})

X_scaled = StandardScaler().fit_transform(data)

model = DBSCAN(eps=0.6, min_samples=3)
labels = model.fit_predict(X_scaled)

print("Labels:", labels)
print("Cluster counts:")
print(pd.Series(labels).value_counts().sort_index())

plt.scatter(data["measurement_a"], data["measurement_b"], c=labels)
plt.xlabel("Measurement A")
plt.ylabel("Measurement B")
plt.title("DBSCAN results (-1 represents noise)")
plt.show()
```

`fit_predict` fits DBSCAN and returns one label for each row. Cluster labels are non-negative integers; -1 means noise. The plot uses the original coordinates for readability, while DBSCAN was fitted on standardised coordinates. Therefore, the visual distances in the plot are not the exact distances the model used.

The values of `eps` and `min_samples` in this example are illustrative. They should not be copied into another dataset without examining scale, density and the resulting clusters.

## 6. Choosing parameters responsibly

Parameter selection is one of the hardest parts of DBSCAN.

- If epsilon is too small, most points may be labelled noise and only tiny clusters may form.
- If epsilon is too large, separate dense regions may merge into one cluster.
- If min_samples is too low, small accidental concentrations may become clusters.
- If min_samples is too high, meaningful but less dense regions may disappear.

A k-distance plot can help. For each point, calculate the distance to its kth nearest neighbour, sort those distances and plot them. A bend in the sorted curve may suggest a useful epsilon range. It is a heuristic, not a guaranteed answer.

```python
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

X_scaled = StandardScaler().fit_transform(data)

neighbors = NearestNeighbors(n_neighbors=4)
neighbors.fit(X_scaled)
distances, indices = neighbors.kneighbors(X_scaled)

k_distances = sorted(distances[:, -1])
plt.plot(k_distances)
plt.xlabel("Observations sorted by neighbour distance")
plt.ylabel("Distance to the 4th nearest neighbour")
plt.title("K-distance plot")
plt.show()
```

The selected neighbour count should be related to the intended `min_samples` setting. Inspect the data and test a reasonable range of values rather than choosing a bend mechanically.

## 7. Strengths and limitations

DBSCAN can identify irregularly shaped dense clusters, does not require K, and can leave isolated points unassigned. These properties make it useful for spatial patterns and some sensor or behavioural datasets.

However, standard DBSCAN struggles when clusters have very different densities. One epsilon value may be too small for a sparse cluster and too large for a dense one. High-dimensional distance can also become less informative. Scaling and feature selection remain important.

For datasets with varying density, consider methods such as HDBSCAN where available and appropriate. This course focuses on understanding DBSCAN's principles before moving to more advanced density-based approaches.

## 8. Compare DBSCAN with K-means

K-means assigns every observation to one of K clusters and is based on distances to centroids. DBSCAN groups dense connected regions and can label some observations as noise. K-means may be preferable for compact groups and large numeric datasets; DBSCAN may be preferable when irregular shapes and noise are central to the problem.

Do not compare their raw cluster numbers. Compare whether their outputs represent the intended structure, how stable they are and how well the results can be explained.

## 9. Common mistakes

- Choosing epsilon before understanding feature scaling.
- Treating every -1 label as a data error.
- Assuming DBSCAN will identify every cluster shape.
- Using one parameter setting without sensitivity analysis.
- Forgetting that `min_samples` includes the point itself in scikit-learn.
- Interpreting cluster labels as rankings.
- Using a two-dimensional plot to claim that all high-dimensional structure is visible.

## 10. Guided practice

Draw a group of points on paper. Mark a circle around one point to represent epsilon. Count the points inside the circle, including the centre point. Repeat with different min_samples values and identify which points would be core, border and noise.

## 11. Independent practice

Apply DBSCAN to a numeric dataset. Scale the features, test at least three epsilon values and two min_samples values, then record cluster count, noise count and cluster sizes. Plot the result if the data has two interpretable dimensions. Explain how parameter changes alter the structure and why the selected result is defensible.

## 12. Knowledge check

1. What does DBSCAN stand for?
2. What does epsilon control?
3. What does min_samples control?
4. How is a core point different from a border point?
5. What does the label -1 mean in scikit-learn DBSCAN?
6. Why can one epsilon fail when clusters have different densities?
7. Why should the features usually be scaled before distance-based DBSCAN?

## Lesson summary

DBSCAN defines clusters as connected dense regions. Epsilon sets the neighbourhood radius, while min_samples sets the density requirement. It can discover irregular shapes and identify noise without specifying K, but its results are sensitive to scale and parameters, especially when densities vary. Treat noise as a prompt for interpretation, not a verdict about an observation.
