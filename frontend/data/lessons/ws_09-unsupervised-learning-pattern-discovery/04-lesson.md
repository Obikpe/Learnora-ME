# Lesson 4: K-Means Clustering

## Learning outcomes
Explain the unsupervised-learning concept, implement the worked example, interpret the output and assess whether the discovered structure is meaningful.

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