# Lesson 8: Comparing and Validating Clusters

## Learning outcomes

By the end of this lesson, you should be able to Compare clustering solutions with silhouette and Davies–Bouldin scores; test stability across random seeds; profile results; and explain why no single metric proves a natural cluster structure.

![Cluster outputs require diagnostics and human validation](/course-assets/ws09/clustering-concepts.svg)

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

## Deeper explanation: validate from several angles

Clustering has no single universally correct score because ground-truth labels may not exist. Internal measures use only the data and assignments. Silhouette rewards cohesion and separation. Davies–Bouldin compares within-cluster scatter with separation between clusters; lower is generally better. Calinski–Harabasz compares between-cluster dispersion with within-cluster dispersion; higher is generally better. These measures favour particular geometries and are not interchangeable truth.

External measures compare assignments with known labels when available. Such labels can be useful diagnostics, but they were not used to fit the unsupervised model. High agreement does not prove that the algorithm discovered the only meaningful structure.

Stability checks rerun the method with different seeds, bootstrap samples or time periods. Cluster IDs can swap, so compare partitions with a label-invariant measure such as adjusted Rand index rather than comparing raw numeric labels. Adjusted Rand index is 1 for identical partitions up to label permutation, around 0 for chance-level agreement and can be negative.

Domain review is essential. Inspect representative records, cluster sizes, original-unit profiles and whether the distinction supports a useful action. A mathematically separated group may be irrelevant or unfair to use.

**Practice:** Create a validation table containing method, parameters, internal scores, stability, cluster sizes and a domain interpretation. Identify which evidence is strong, weak or missing.

### Worked example: build a validation evidence table

Use one row per experiment and columns for method, distance, preprocessing, parameters, internal scores, cluster sizes, seed stability and profile notes. This makes it possible to compare experiments without relying on memory or choosing the most attractive plot after the fact.

A high silhouette score with unstable assignments is a warning. Stable assignments with no meaningful profile may also be unhelpful. A domain expert's approval is valuable but should not replace quantitative checks; experts can also see patterns that are not supported by the data.

Validation is a collection of evidence. State which checks were performed, which were not possible because labels were unavailable, and what uncertainty remains. Never imply that a single internal score certifies the clusters.
