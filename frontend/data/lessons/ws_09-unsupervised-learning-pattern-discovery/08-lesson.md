# Lesson 8: Comparing and Validating Clusters

## Learning outcomes
Explain the unsupervised-learning concept, implement the worked example, interpret the output and assess whether the discovered structure is meaningful.

## 1. Core explanation
There is no ground-truth label in unsupervised clustering, so validation is more difficult than supervised evaluation. Internal metrics such as silhouette score assess geometric cohesion and separation. Davies-Bouldin and Calinski-Harabasz scores provide other views, each with assumptions and biases.

External validation is possible when independent labels or outcomes exist, but those labels should not be used to create the clusters if the goal is unsupervised discovery. Compare clusters with known groups only after clustering and treat agreement as one piece of evidence. Stability testing repeats clustering across samples, seeds or small feature changes to see whether the structure persists.

Practical validation asks whether segments are interpretable, actionable, stable and useful for the original purpose. A mathematically separated cluster may not lead to a meaningful action. Conversely, a useful operational segmentation may have overlapping boundaries.

## 2. Worked Python example
Run in VS Code. Install relevant packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`. Some scikit-learn dataset loaders may require internet access on first use.

```python
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score

X = StandardScaler().fit_transform(load_iris().data)
for seed in [1, 7, 42]:
    labels = KMeans(n_clusters=3, n_init=20, random_state=seed).fit_predict(X)
    print(seed, "silhouette", silhouette_score(X, labels),
          "Davies-Bouldin", davies_bouldin_score(X, labels))
```

## 3. Interpretation
Describe the feature representation, distance or objective, model settings and what the output means. Cluster IDs are arbitrary. An anomaly flag is a prompt for investigation, not proof of misconduct. Validate any discovered pattern in original units and with domain knowledge.

## 4. Guided practice
Repeat clustering across several seeds and compare metric values and cluster profiles. State whether the segmentation is stable enough for its proposed use and what additional evidence would be useful.

## 5. Independent practice
Choose a dataset and state the purpose of the unsupervised analysis. Compare at least two parameter settings. Profile the resulting groups or flagged cases and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the algorithm attempting to discover?
2. Which assumptions are introduced by the distance or representation?
3. How can you tell whether the result is useful rather than merely computable?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Human interpretation, stability checks and practical validation determine whether those patterns deserve to be used.