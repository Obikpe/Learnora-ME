# Lesson 3: Distance and Similarity Measures

## Learning outcomes

By the end of this lesson, you should be able to Calculate and compare Euclidean distance and cosine similarity; explain when magnitude versus direction matters; and identify why scaling and feature choice change similarity.

![Feature points are compared using a chosen similarity definition](/course-assets/ws09/clustering-concepts.svg)

## 1. Core explanation
Distance quantifies how far two observations are in feature space. Euclidean distance is the straight-line distance and is common for continuous numeric data. Manhattan distance sums absolute coordinate differences. Cosine similarity compares vector direction and is useful for sparse text representations where magnitude may be less important. Jaccard similarity compares overlap between sets or binary attributes.

A distance measure encodes assumptions about what “similar” means. Euclidean distance is sensitive to feature scale and outliers. Cosine similarity ignores overall magnitude. Jaccard is appropriate for sets or binary presence/absence, not arbitrary continuous values. Choose a measure based on data meaning.

High-dimensional spaces create difficulties: distances can become less discriminative, and irrelevant features add noise. Standardisation can help numeric features with different units, but it does not make every variable equally meaningful. Weight features only when there is a defensible reason.

## 2. Worked Python example
Run in VS Code. Install relevant packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`. Some scikit-learn dataset loaders may require internet access on first use.

```python
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances, cosine_similarity

A = np.array([[1, 2], [2, 4], [8, 1]])
print("Euclidean distances:")
print(euclidean_distances(A).round(2))
print("Cosine similarity:")
print(cosine_similarity(A).round(2))
```

## 3. Interpretation
Describe the feature representation, distance or objective, model settings and what the output means. Cluster IDs are arbitrary. An anomaly flag is a prompt for investigation, not proof of misconduct. Validate any discovered pattern in original units and with domain knowledge.

## 4. Guided practice
Compare vectors [1,2] and [2,4]. Their directions match but their magnitudes differ. Explain why cosine similarity is high while Euclidean distance is not zero. Give an example where that is useful.

## 5. Independent practice
Choose a dataset and state the purpose of the unsupervised analysis. Compare at least two parameter settings. Profile the resulting groups or flagged cases and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the algorithm attempting to discover?
2. Which assumptions are introduced by the distance or representation?
3. How can you tell whether the result is useful rather than merely computable?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Human interpretation, stability checks and practical validation determine whether those patterns deserve to be used.

## Deeper explanation: calculate distance before trusting it

For points A=(1,2) and B=(4,6), Euclidean distance is the straight-line distance: square the coordinate differences, add them, and take the square root. The result is 5. Manhattan distance adds the absolute coordinate differences, giving 7. They differ because they define closeness differently.

Cosine similarity compares the angle between vectors rather than their lengths. Vectors (1,2) and (2,4) point in the same direction, so their cosine similarity is 1 even though their Euclidean distance is not zero. This is useful for comparing text vectors where document length may matter less than word proportions. It is unsuitable when magnitude itself is meaningful, such as total energy consumption.

Euclidean distance is common for continuous numeric measurements but is sensitive to scale and outliers. Manhattan distance can suit additive coordinate differences. Cosine similarity is common for sparse text vectors. Jaccard similarity compares overlap between sets or binary attributes; it is not a general replacement for distance on continuous measurements.

High-dimensional data creates another problem: as dimensions increase, distances can become less discriminative. Irrelevant features add noise. Standardisation helps with units but does not solve poor feature selection. A full pairwise distance matrix for n rows contains n-squared distances and can become expensive.

**Practice:** Compare vectors (1,2), (2,4), and (8,1) using Euclidean distance and cosine similarity. Explain why the first two are directionally alike but differ in magnitude. Then describe a real situation where that distinction matters.

### Worked example: interpret the distance matrix

A pairwise distance matrix is symmetric: distance from A to B equals distance from B to A. The diagonal is zero because every observation has zero distance from itself. The smallest off-diagonal value identifies the closest pair under the chosen measure, not necessarily the pair that a subject expert would consider most alike.

Do not interpret a numerical distance without its representation. A distance of 2 after standardisation is not two naira, two customers or two units of physical separation. It is a distance in the transformed feature space. If a feature is duplicated, it can effectively receive extra weight because its contribution is counted more than once.

Before using nearest neighbours, inspect whether the data contains duplicate rows, highly correlated features or sparse columns. These can make some observations appear unusually close for reasons unrelated to the intended concept.
