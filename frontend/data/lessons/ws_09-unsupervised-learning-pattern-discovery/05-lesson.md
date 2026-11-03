# Lesson 5: Choosing the Number of Clusters

## Learning outcomes

By the end of this lesson, you should be able to explain why K must be selected before fitting ordinary K-means; calculate and interpret inertia; use the elbow method and silhouette score; compare candidate solutions using cluster sizes and profiles; and justify a choice without pretending that one score proves the true number of groups.

![K-means clustering and cluster selection](/course-assets/ws09/kmeans-steps.svg)

## 1. Why does K need to be chosen?

In K-means, K is the number of clusters the algorithm is asked to create. If K=2, it creates two groups. If K=5, it creates five. The algorithm does not know how many customer types, product families or behavioural patterns truly exist. It simply optimises its objective for the K supplied.

Imagine six points arranged in two clearly separated clouds. K=2 may represent them well. If you ask for K=5, K-means still tries to divide the data into five groups. It may split a natural cloud into several smaller pieces. This is not necessarily a software error; it is the consequence of the instruction.

There is no universal rule that says every dataset has one correct K. Real data may contain overlapping patterns, gradual variation or no meaningful clusters at all. The goal is to find a useful and defensible representation, not to force the data into a story.

## 2. Inertia and the within-cluster sum of squares

Inertia is the sum of squared distances from each observation to the centroid of its assigned cluster. It measures how tightly points sit around their assigned centres under the K-means objective.

As K increases, inertia cannot increase in the ideal optimisation: adding more centres gives the algorithm more flexibility to reduce distances. At the extreme, if every observation receives its own cluster, inertia becomes zero. But one cluster per observation is rarely a useful segmentation.

This creates a trade-off: more clusters generally improve compactness, but they make the solution more complicated and can produce tiny, difficult-to-use groups.

## 3. The elbow method

The elbow method fits K-means for several candidate K values and plots K against inertia. At first, adding clusters may reduce inertia substantially. Later, the improvement may become smaller. The point where the curve begins to flatten is sometimes called the elbow.

The elbow is a visual heuristic, not a mathematical law. Some datasets have a clear bend; others produce a smooth curve with no obvious elbow. Two analysts may reasonably choose different K values, especially if the practical costs of additional segments differ.

A reproducible implementation:

```python
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

data = pd.DataFrame({
    "recency": [5, 8, 12, 65, 75, 90, 3, 10, 55, 70, 15, 82],
    "orders": [12, 10, 8, 2, 1, 0, 14, 9, 7, 2, 11, 1],
    "basket": [500, 420, 380, 90, 70, 30, 550, 400, 360, 80, 480, 60]
})

X = StandardScaler().fit_transform(data)
inertias = []

for k in range(1, 8):
    model = KMeans(n_clusters=k, n_init=20, random_state=42)
    model.fit(X)
    inertias.append(model.inertia_)

plt.plot(range(1, 8), inertias, marker="o")
plt.xlabel("Number of clusters (K)")
plt.ylabel("Inertia")
plt.title("Elbow method")
plt.xticks(range(1, 8))
plt.show()
```

The loop fits a new model for each candidate K. `inertia_` stores the within-cluster sum of squares for that fitted model. The plot allows you to inspect how much improvement each extra cluster provides.

## 4. Silhouette score: compare cohesion and separation

The silhouette score evaluates how well each observation fits its own cluster compared with the nearest alternative cluster.

For one observation:

- (a) is its average distance to other observations in its own cluster.
- (b) is the smallest average distance to observations in another cluster.
- The silhouette coefficient is ((b-a)/max(a,b)).

The score ranges from -1 to 1. A value close to 1 suggests the observation is much closer to its own cluster than to the nearest alternative. A value around 0 suggests overlapping or boundary placement. A negative value suggests it may be closer to another cluster.

The average silhouette score summarises the observations, but always inspect the distribution by cluster too. A good overall average can hide one weak cluster. The score also depends on the distance metric and geometry; it tends to favour compact, separated groups and should not be treated as a universal quality measure.

```python
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import pandas as pd

data = pd.DataFrame({
    "recency": [5, 8, 12, 65, 75, 90, 3, 10, 55, 70, 15, 82],
    "orders": [12, 10, 8, 2, 1, 0, 14, 9, 7, 2, 11, 1],
    "basket": [500, 420, 380, 90, 70, 30, 550, 400, 360, 80, 480, 60]
})
X = StandardScaler().fit_transform(data)

for k in range(2, 7):
    labels = KMeans(n_clusters=k, n_init=20, random_state=42).fit_predict(X)
    score = silhouette_score(X, labels)
    print(f"K={k}: silhouette={score:.3f}")
```

Silhouette score requires at least two clusters and fewer clusters than observations. It can be computationally expensive on very large datasets because pairwise distances are involved. For large datasets, scikit-learn provides a sampling option.

## 5. Compare several kinds of evidence

Do not choose K by taking the largest score and ignoring everything else. Compare:

1. **Elbow behaviour:** does adding another cluster provide a meaningful reduction in inertia?
2. **Silhouette:** are observations generally closer to their own group than to alternatives?
3. **Cluster sizes:** are there tiny groups that are difficult to interpret or act on?
4. **Profiles:** do groups differ on original features in a way that answers the question?
5. **Stability:** do similar groups appear with different random seeds or samples?
6. **Usefulness:** can the organisation do something responsible with the segments?
7. **Complexity:** does the benefit of another cluster justify the extra explanation and maintenance?

A lower K may be preferable when it creates broad, stable, understandable groups. A higher K may be useful when it separates genuinely different behaviours. The decision depends on the purpose.

## 6. Common mistakes

- Choosing K only because a chart has a visually pleasing elbow.
- Treating the highest silhouette score as proof of the correct K.
- Ignoring tiny clusters or a cluster with poor silhouette values.
- Comparing models fitted on differently scaled feature matrices.
- Changing K repeatedly until a preferred story appears.
- Forgetting that the data may not contain useful clusters at all.

## 7. Guided practice

Fit K-means for K values 2, 3 and 4 on a small numeric dataset. Record inertia, average silhouette score and each cluster's size. Write a short justification for the K you would investigate further. State one reason you might reject that choice.

## 8. Independent practice

Use a dataset with at least 100 observations. Compare K=2 through K=8. Produce an elbow plot, silhouette comparison and original-unit profile table. Test at least two random seeds. Recommend a candidate K or conclude that the evidence does not support a stable segmentation.

## 9. Knowledge check

1. Why does inertia usually decrease as K increases?
2. Why is K equal to the number of observations not a useful answer?
3. What does an elbow indicate, and why is it subjective?
4. What does a negative silhouette coefficient suggest?
5. Why should cluster sizes and profiles be inspected alongside scores?
6. What would you report if no candidate K produced stable, interpretable groups?

## Lesson summary

Selecting K is a judgement supported by diagnostics, not a button the algorithm can press for you. Inertia describes compactness; the elbow suggests diminishing returns; silhouette compares within-group cohesion with nearest-group separation. Combine these measures with stability, cluster sizes, profiles, domain knowledge and practical purpose.
