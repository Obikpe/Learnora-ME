# Lesson 8: Comparing and Validating Clusters

## Learning outcomes

By the end of this lesson, you should be able to explain why clustering needs validation even without target labels; calculate and interpret silhouette scores; explain Davies–Bouldin and Calinski–Harabasz scores; examine cluster size and stability; compare methods fairly; and report uncertainty and limitations.

![A cluster validation workflow](/course-assets/ws09/clustering-concepts.svg)

## 1. Why is clustering validation different?

In supervised learning, a prediction can be compared with a known target. If a model predicts a class, the analyst can compare that prediction with the actual class label in a labelled test set.

In unsupervised learning, the dataset often has no correct group label. There may be no external answer key. This does not mean evaluation is impossible. It means evaluation must ask different questions.

A useful clustering solution should have some combination of:
- Cohesion: observations within a group are reasonably similar.
- Separation: groups are distinguishable from one another.
- Stability: similar structure appears under reasonable changes.
- Interpretability: the groups can be described in original features.
- Practical relevance: the structure helps answer the original question.
- Responsible use: the output does not invite harmful or unsupported decisions.

A metric measures only part of this picture. No single score can establish that the groups are objectively true.

## 2. Internal validation: evaluate the geometry

Internal metrics use the feature matrix and cluster assignments. They do not require known labels. Their interpretation depends on the distance measure, feature scaling and the geometry they favour.

### Silhouette coefficient

For an observation, let a be the average distance to points in its own cluster and b be the smallest average distance to points in another cluster. The silhouette coefficient is:

```
s = (b - a) / max(a, b)
```

Its range is -1 to 1:
- Near 1: the observation is much closer to its own cluster than to the nearest alternative.
- Around 0: the observation is near a boundary or clusters overlap.
- Below 0: the observation may be closer to another cluster than to its assigned cluster.

The average silhouette score summarises all observations. Also inspect per-cluster scores and the distribution of individual scores. A single average can hide one poorly separated group.

### Davies–Bouldin index

The Davies–Bouldin index compares within-cluster scatter with separation between cluster centres. Lower values generally indicate clusters that are compact relative to their separation. It is an internal comparison, not a universal quality score. It is influenced by the geometry of the data and should be compared across models using the same representation.

### Calinski–Harabasz index

The Calinski–Harabasz index compares between-cluster dispersion with within-cluster dispersion. Higher values generally indicate better separation relative to compactness. It can favour certain cluster structures and should not be interpreted as a probability or percentage of correctness.

## 3. Calculate several metrics with scikit-learn

```python
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score
)

customers = pd.DataFrame({
    "recency": [5, 8, 12, 65, 75, 90, 3, 10, 55, 70, 15, 82],
    "orders": [12, 10, 8, 2, 1, 0, 14, 9, 7, 2, 11, 1],
    "basket": [500, 420, 380, 90, 70, 30, 550, 400, 360, 80, 480, 60]
})

X = StandardScaler().fit_transform(customers)

for k in [2, 3, 4]:
    labels = KMeans(
        n_clusters=k,
        n_init=20,
        random_state=42
    ).fit_predict(X)

    print(
        f"K={k}",
        "silhouette=", round(silhouette_score(X, labels), 3),
        "Davies-Bouldin=", round(davies_bouldin_score(X, labels), 3),
        "Calinski-Harabasz=", round(calinski_harabasz_score(X, labels), 2)
    )
```

Each metric gives a different perspective. Silhouette is higher when observations are well matched to their own group and separated from the nearest alternative. Davies–Bouldin is generally lower for more compact, separated groups. Calinski–Harabasz is generally higher when between-group dispersion is large relative to within-group dispersion.

Do not compare scores from unrelated feature transformations as if they were directly interchangeable. If you change the scaling or features, you have changed the geometry being evaluated.

## 4. Inspect cluster sizes and profiles

A metric may look good while the result is impractical. Imagine a solution with 98% of customers in one cluster and 2% in another. That may be valid in some contexts, but it may not provide the useful segmentation expected.

Check:
- Count and percentage of observations in each cluster.
- Means and medians of the original features.
- Spread, such as standard deviation and interquartile range.
- Categorical proportions where relevant.
- Whether one cluster is dominated by unusual or poor-quality records.
- Whether the differences are meaningful for the stated purpose.

```python
result = customers.assign(cluster=labels)

print(result["cluster"].value_counts().sort_index())
print(result.groupby("cluster").agg(
    count=("recency", "size"),
    median_recency=("recency", "median"),
    median_orders=("orders", "median"),
    median_basket=("basket", "median")
))
```

The cluster labels are attached to the original unscaled data. This allows the analyst to explain the groups in days, order counts and currency rather than only in standardised units.

## 5. Stability: would the pattern survive a reasonable change?

Clustering algorithms can produce different results when:
- Random initial centroids change.
- A sample of observations changes.
- A few extreme observations are added or removed.
- The time period changes.
- A reasonable feature or scaling choice changes.

A stable result is not automatically correct, but an unstable result should be treated cautiously. Compare cluster assignments across random seeds or bootstrap samples. Because cluster IDs are arbitrary, do not compare label 0 in one run with label 0 in another directly. Use a label-invariant comparison such as adjusted Rand index when comparing two partitions of the same observations.

```python
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

model_a = KMeans(n_clusters=3, n_init=1, random_state=10)
model_b = KMeans(n_clusters=3, n_init=1, random_state=99)

labels_a = model_a.fit_predict(X)
labels_b = model_b.fit_predict(X)

agreement = adjusted_rand_score(labels_a, labels_b)
print("Adjusted Rand index:", round(agreement, 3))
```

The adjusted Rand index compares whether pairs of observations are grouped together or apart in two partitions, adjusting for chance agreement. A value near 1 indicates strong agreement; values near 0 indicate agreement similar to random partitioning under the adjustment. Negative values can occur when agreement is worse than expected by chance.

## 6. External validation: use labels only when they genuinely exist

Sometimes a dataset has a separate label that was not used to fit the clusters. For example, a retailer may have a later customer outcome or an independently created category. Such information can be used to examine whether the clusters relate to an external measure.

Be careful: if you use the external label to choose features, tune the algorithm repeatedly or name the clusters, it is no longer an independent validation. Also, a relationship between clusters and an outcome does not prove that the clusters caused that outcome.

## 7. Compare algorithms fairly

When comparing K-means, hierarchical clustering and DBSCAN:
- Use a defensible common feature representation where possible.
- State any metric-specific preprocessing.
- Do not force every algorithm to produce the same number of clusters if that conflicts with its design.
- Compare noise handling, cluster size, stability and interpretability.
- Use metrics appropriate to the method and number of clusters.
- Inspect the original data, not only summary scores.

Silhouette can be calculated for many clusterings, but it is not equally informative for every geometry. A density-based clustering with noise may require special care about whether noise points are included in the metric calculation.

## 8. When should you reject a clustering result?

Reject or qualify a solution when clusters change dramatically under small reasonable changes, when most groups overlap, when a cluster is mostly data errors, when the groups cannot be interpreted in original features, or when no responsible use can be identified. It is acceptable to conclude that the current data does not support useful clusters.

Do not keep trying parameter values until a preferred story appears. That creates confirmation bias. Decide what counts as a useful result before exploring too many alternatives, and document the settings you tried.

## 9. Guided practice

Fit K-means for K=2 and K=3. Calculate silhouette, Davies–Bouldin and Calinski–Harabasz scores. Compare group sizes and original-unit medians. Write a paragraph explaining why one solution is preferable for the stated purpose—or why neither is convincing.

## 10. Independent practice

Choose a dataset and compare at least two clustering methods or several meaningful parameter settings. Include internal metrics, cluster-size tables, original-feature profiles and a stability check. Write a short validation section that distinguishes what the metrics show from what domain evidence and practical usefulness still need to establish.

## 11. Knowledge check

1. Why is there no simple accuracy score for most unsupervised clustering?
2. What does a silhouette score near zero suggest?
3. Is a higher or lower Davies–Bouldin index generally preferred?
4. What does the Calinski–Harabasz index compare?
5. Why can cluster IDs not be compared directly across runs?
6. What does the adjusted Rand index help compare?
7. Why is it valid to report that no useful clusters were found?

## Lesson summary

Cluster validation is a collection of checks rather than one final number. Internal metrics describe geometric cohesion and separation; profiles describe the groups in real units; stability checks test sensitivity; external evidence and domain knowledge assess relevance. A responsible analyst reports uncertainty and is willing to reject a weak or unhelpful clustering.
