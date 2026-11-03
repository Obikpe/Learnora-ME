# Lesson 4: K-Means Clustering

## Learning outcomes

By the end of this lesson, you should be able to Explain the K-means objective; scale features where appropriate; fit and interpret centroids and cluster assignments; and identify sensitivity to initialisation, outliers and the chosen k.

![K-means assignment and centroid update](/course-assets/ws09/kmeans-steps.svg)

## 1. Core explanation
K-means partitions observations into k clusters by assigning each point to its nearest centroid and updating each centroid to the mean of its assigned points. It repeats assignment and update until assignments or centroid positions stabilise. The objective is within-cluster sum of squared distances.

K-means requires k in advance and works best when clusters are roughly compact and similarly scaled. It is sensitive to feature scaling, outliers and initial centroid placement. Use multiple initialisations and a fixed random seed for reproducibility. It is not suited to arbitrary-shaped clusters or mixed data without an appropriate representation.

A cluster ID is arbitrary. Profile clusters using original features, inspect representative observations and ask whether differences are meaningful. Do not label a cluster “high-value customers” solely because its average spending is higher; validate stability and business relevance.

## 2. Worked Python example
Run in VS Code. Install relevant packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`. Some scikit-learn dataset loaders may require internet access on first use.

```python
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

X = pd.DataFrame({
    "recency": [5, 8, 12, 60, 75, 90, 3, 10],
    "frequency": [12, 10, 8, 2, 1, 0, 14, 9],
    "spend": [500, 420, 380, 90, 70, 30, 550, 400]
})
Z = StandardScaler().fit_transform(X)
model = KMeans(n_clusters=2, n_init=20, random_state=42)
labels = model.fit_predict(Z)
print(X.assign(cluster=labels).groupby("cluster").mean())
```

## 3. Interpretation
Describe the feature representation, distance or objective, model settings and what the output means. Cluster IDs are arbitrary. An anomaly flag is a prompt for investigation, not proof of misconduct. Validate any discovered pattern in original units and with domain knowledge.

## 4. Guided practice
Run k=2, 3 and 4. Profile the resulting groups using original units. Explain why cluster numbering can change between runs and why labels should not be interpreted as an ordered scale.

## 5. Independent practice
Choose a dataset and state the purpose of the unsupervised analysis. Compare at least two parameter settings. Profile the resulting groups or flagged cases and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the algorithm attempting to discover?
2. Which assumptions are introduced by the distance or representation?
3. How can you tell whether the result is useful rather than merely computable?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Human interpretation, stability checks and practical validation determine whether those patterns deserve to be used.

## Deeper explanation: what K-means optimises

K-means minimises the total squared distance between each observation and the centroid of its assigned cluster. A centroid is the mean feature vector of the observations assigned to that group. The algorithm alternates between assigning each point to its nearest centroid and recomputing each centroid from its assigned points.

Each assignment/update cycle does not increase the objective, but the algorithm can settle at a local solution. Different starting centroids can lead to different results. The n_init setting runs several initialisations and retains the best objective found; a fixed random_state makes the experiment reproducible.

K-means requires the analyst to choose k. It works best when groups are roughly compact and similarly scaled under Euclidean geometry. It is sensitive to outliers because means can be pulled by extreme values. It also assigns every observation, even one far from all centroids. It is not designed for arbitrary-shaped groups or mixed data without an appropriate representation.

Centroids after standardisation are expressed in standard-deviation units. They help compare relative positions but are not suitable for explaining a business segment in original units. Use the assignments to profile the original data with means, medians and distributions.

**Practice:** Fit K-means with one initialisation and several random seeds, then repeat with multiple initialisations. Record inertia and cluster profiles. Explain why more initialisations improve the search but do not prove that groups are real or useful.
