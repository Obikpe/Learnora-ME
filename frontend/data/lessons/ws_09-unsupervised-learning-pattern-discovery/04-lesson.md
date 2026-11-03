# Lesson 4: K-Means Clustering

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain the purpose of K-means and the meaning of a centroid.
- Describe the assignment and update steps that make up the K-means algorithm.
- Calculate a simple cluster centroid by hand.
- Fit K-means with scikit-learn and explain its important parameters.
- Interpret cluster assignments and profiles in original feature units.
- Recognise K-means assumptions, strengths, weaknesses and common failure cases.

![The iterative K-means clustering process](/course-assets/ws09/kmeans-steps.svg)

## 1. What problem does K-means solve?

K-means is a clustering algorithm that divides observations into a chosen number of groups. It attempts to place observations into groups so that each observation is relatively close to the centre of its assigned group.

The letter K represents the number of clusters requested. If you set K to 3, the algorithm will attempt to form three groups. It does not discover the correct number automatically. Choosing K is a separate analytical decision that we will examine in the next lesson.

K-means is popular because it is relatively simple, efficient on many numeric datasets and easy to demonstrate. However, it is not suitable for every shape of data. It works best when groups are reasonably compact and separated under the distance measure being used.

## 2. What is a centroid?

A centroid is the arithmetic mean position of a group. Imagine a cluster containing three points in two dimensions:

- A = (2, 4)
- B = (4, 6)
- C = (6, 8)

The centroid's first coordinate is the average of 2, 4 and 6:

```
(2 + 4 + 6) / 3 = 4
```

The second coordinate is the average of 4, 6 and 8:

```
(4 + 6 + 8) / 3 = 6
```

The centroid is therefore (4, 6). It is the centre calculated by averaging each feature separately. The centroid does not have to be an actual observation in the dataset.

For a dataset with five features, the centroid has five coordinates. Each coordinate is the mean of that feature among observations assigned to the cluster.

## 3. The K-means algorithm step by step

K-means repeatedly performs two main operations: assignment and update.

### Step 1: Choose K initial centroids

The algorithm begins with K starting centres. Different initial positions can lead to different final groupings, particularly when the data has several local solutions.

A common initialisation method is K-means++. It chooses initial centres in a way intended to spread them out and improve the starting point. It does not guarantee the globally best clustering.

### Step 2: Assign each observation to its nearest centroid

For every row, calculate its distance to each centroid. Assign it to the cluster whose centroid is nearest. With ordinary K-means, the distance is Euclidean distance in the feature space supplied to the algorithm.

### Step 3: Recalculate each centroid

For each cluster, calculate the mean of all observations currently assigned to it. This produces a new centroid.

### Step 4: Repeat assignment and update

Using the new centroids, assign observations again. Recalculate the centroids. Continue until the assignments or centroids stop changing significantly, or the algorithm reaches its iteration limit.

The process can be summarised as:

1. Initialise centres.
2. Assign observations.
3. Recalculate means.
4. Repeat until convergence.

## 4. What is K-means trying to minimise?

K-means aims to minimise the **within-cluster sum of squares**, often abbreviated WCSS or inertia. For every observation, calculate the squared distance to its assigned centroid, then add these squared distances across all observations.

```
WCSS = sum of squared distances from each point to its assigned centroid
```

A lower WCSS means observations are, on average in the squared-distance sense, closer to their assigned centres. But WCSS always tends to decrease as K increases. If every observation had its own cluster, WCSS would be zero. That would not be a useful segmentation. This is why a low inertia value alone cannot tell you the best K.

## 5. A small numerical example

Suppose a one-dimensional dataset contains values 2, 3, 4, 10, 11 and 12, and we request K=2. Imagine the initial centroids are 3 and 11.

The first three observations are closer to 3; the final three are closer to 11. The first cluster's new mean is:

```
(2 + 3 + 4) / 3 = 3
```

The second cluster's new mean is:

```
(10 + 11 + 12) / 3 = 11
```

The centroids remain at 3 and 11, so another assignment step would not change the result. The algorithm has converged.

This example is deliberately simple. Real datasets have multiple features, many observations and starting positions that may require several iterations.

## 6. Implement K-means with scikit-learn

Install the required libraries:

```bash
python -m pip install pandas numpy matplotlib scikit-learn
```

```python
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

customers = pd.DataFrame({
    "recency_days": [5, 8, 12, 65, 75, 90, 3, 10, 55, 70],
    "orders_90d": [12, 10, 8, 2, 1, 0, 14, 9, 3, 2],
    "average_basket": [500, 420, 380, 90, 70, 30, 550, 400, 110, 80]
})

# Keep a copy in original units for interpretation.
X = customers[["recency_days", "orders_90d", "average_basket"]]

# Scale because the features use different units and ranges.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = KMeans(
    n_clusters=2,
    init="k-means++",
    n_init=20,
    max_iter=300,
    random_state=42
)

labels = model.fit_predict(X_scaled)

profile = customers.assign(cluster=labels)
print(profile.groupby("cluster").agg(
    customers=("recency_days", "size"),
    median_recency=("recency_days", "median"),
    mean_orders=("orders_90d", "mean"),
    mean_basket=("average_basket", "mean")
).round(1))

# A two-feature view for visual inspection.
plt.scatter(
    customers["recency_days"],
    customers["orders_90d"],
    c=labels
)
plt.xlabel("Days since last purchase")
plt.ylabel("Orders in last 90 days")
plt.title("K-means customer groups")
plt.show()
```

### Understand the important parameters

- `n_clusters=2`: requests two clusters. You must justify this choice using diagnostics and context.
- `init="k-means++"`: chooses starting centroids using the K-means++ strategy.
- `n_init=20`: runs the algorithm with 20 initialisations and retains the best result according to inertia. This reduces dependence on one unlucky starting arrangement.
- `max_iter=300`: limits the number of assignment/update iterations for each run.
- `random_state=42`: makes random initialisation reproducible.
- `fit_predict(X_scaled)`: fits the model and returns one cluster label per observation.

The `StandardScaler` is fitted on the feature matrix and transforms the columns. The scatter plot shows only two of the three features. It is therefore a partial view of a three-dimensional clustering. A point that looks close in this chart may differ in average basket value, which is not shown.

The `c=labels` argument colours points by their assigned cluster. The colour is a visual identifier, not a ranking or a measurement. In a larger report, include a legend or explain the cluster IDs.

## 7. Why inspect the original feature values?

The model operates on scaled values, but managers and subject experts need to understand the groups in meaningful units. A median recency of 70 days is understandable; a scaled value of 1.4 is less directly useful.

Attach cluster labels to the original data and profile the original columns. Compare group size, medians, means and distributions. Avoid naming a group “loyal customers” merely because it has a low recency value. It may have low recency but also very low order frequency or another important characteristic.

## 8. Important assumptions and limitations

K-means has several characteristics that should influence your choice:

- It requires K to be specified in advance.
- It uses means as centres, so extreme values can pull centroids.
- It is based on Euclidean geometry and is sensitive to feature scale.
- It tends to favour compact, roughly spherical groups.
- It can struggle with clusters of very different density or strongly non-spherical shapes.
- It assigns every observation to a cluster, even when an observation is far from every centre.
- Different initialisations can produce different results.

K-means is not automatically the right choice for categorical-only data. It is also not a direct anomaly detector: an unusual point is still assigned to its nearest cluster.

## 9. Common mistakes

1. Running K-means on unscaled features with very different units without considering the consequences.
2. Treating K as the number of naturally existing groups.
3. Using only one initialisation.
4. Interpreting cluster IDs as ordered categories.
5. Naming clusters without inspecting their original feature distributions.
6. Assuming a two-dimensional scatter plot displays every dimension used by the model.
7. Treating a low inertia value as proof of a good model.

## 10. Guided practice

Use the one-dimensional values [1, 2, 3, 9, 10, 11] and initial centroids 2 and 10. Assign each value to its nearest centroid, calculate the two new means and decide whether another iteration would change the result.

## 11. Independent practice

Use a customer or product dataset with at least three numeric features. Fit K-means for K=2 and K=3 using scaling and at least 10 initialisations. Compare group sizes and original-unit profiles. Explain which solution is more interpretable and why you cannot choose K using inertia alone.

## 12. Knowledge check

1. What is a centroid?
2. What are the assignment and update steps?
3. What does K represent?
4. Why does K-means use multiple initialisations?
5. What does inertia measure?
6. Name two kinds of cluster shape that K-means may struggle to represent.
7. Why should the final clusters be profiled using the original feature values?

## Lesson summary

K-means partitions observations around K centroids by repeatedly assigning each point to its nearest centre and recalculating the centres as means. It is efficient and useful for compact numeric groups, but its result depends on K, scaling, initialisation and the geometry of the data. Always inspect profiles and validate whether the groups are stable and useful.
