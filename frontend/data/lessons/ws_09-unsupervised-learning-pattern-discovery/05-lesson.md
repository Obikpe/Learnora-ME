# Lesson 5: Choosing the Number of Clusters

## Learning outcomes

By the end of this lesson, you should be able to Use inertia and silhouette score to compare candidate cluster counts; interpret an elbow plot cautiously; and explain why internal metrics cannot establish that clusters are useful business segments.

![K-means repeatedly assigns points and updates centroids](/course-assets/ws09/kmeans-steps.svg)

## 1. Core explanation
The k value controls how many groups K-means produces. The elbow method plots within-cluster sum of squares against k. The curve always decreases as k increases, so look for a point where additional clusters give diminishing improvement rather than treating the elbow as a mathematical proof.

The silhouette coefficient compares within-cluster cohesion with separation from the nearest other cluster. It ranges from -1 to +1; larger values generally indicate better separation. It can favour simple, well-separated shapes and may not suit every clustering structure. Use several measures and inspect profiles.

Choose k based on the analytical purpose, stability, interpretability and actionability. If every value of k produces weak separation, the data may not contain clear clusters. It is acceptable to conclude that segmentation is not supported.

## 2. Worked Python example
Run in VS Code. Install relevant packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`. Some scikit-learn dataset loaders may require internet access on first use.

```python
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

X = StandardScaler().fit_transform(load_iris().data)
inertia, silhouettes = [], []
for k in range(2, 8):
    model = KMeans(n_clusters=k, n_init=20, random_state=42).fit(X)
    inertia.append(model.inertia_)
    silhouettes.append(silhouette_score(X, model.labels_))
print("k values:", list(range(2, 8)))
print("Inertia:", inertia)
print("Silhouette:", silhouettes)
plt.plot(range(2, 8), inertia, marker="o")
plt.xlabel("Number of clusters (k)"); plt.ylabel("Within-cluster sum of squares")
plt.show()
```

## 3. Interpretation
Describe the feature representation, distance or objective, model settings and what the output means. Cluster IDs are arbitrary. An anomaly flag is a prompt for investigation, not proof of misconduct. Validate any discovered pattern in original units and with domain knowledge.

## 4. Guided practice
Plot silhouette score against k as a second chart. Compare both views and choose a k, explaining why the choice is a judgement rather than a universal rule.

## 5. Independent practice
Choose a dataset and state the purpose of the unsupervised analysis. Compare at least two parameter settings. Profile the resulting groups or flagged cases and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the algorithm attempting to discover?
2. Which assumptions are introduced by the distance or representation?
3. How can you tell whether the result is useful rather than merely computable?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Human interpretation, stability checks and practical validation determine whether those patterns deserve to be used.

## Deeper explanation: choosing k is a judgement

Inertia is the total within-cluster squared distance. It cannot increase when more centroids are added. At k equal to the number of observations, every observation can become its own cluster and inertia becomes zero. Therefore, selecting the lowest inertia always produces an unhelpful answer.

The elbow method plots inertia against k and looks for a point after which adding clusters gives diminishing improvement. Some datasets have no obvious elbow. Do not force one. The silhouette coefficient compares a point's average distance to its own cluster with its distance to the nearest other cluster. Scores near 1 suggest separation; near 0 suggest overlap; negative values suggest the point may be closer to another cluster.

An average silhouette score can conceal a poorly represented small cluster. Inspect sample-level scores, cluster sizes and profiles. Keep the feature matrix and scaling procedure constant when comparing k values. Also test stability across random seeds or resampled observations.

Choose k only when metrics, stability, interpretability and intended use support the same decision. A slightly better score may not justify a tiny unstable segment with no practical distinction. It is acceptable to conclude that the data does not support a useful segmentation.

**Practice:** Write a selection memo listing candidate k values, inertia, silhouette, cluster sizes, stability and original-unit profiles. Explain the trade-offs or justify declining to select a value.
