# Lesson 1: Understanding Unsupervised Learning

## Learning outcomes
Explain the unsupervised-learning concept, implement the worked example, interpret the output and assess whether the discovered structure is meaningful.

## 1. Core explanation
Unsupervised learning looks for structure when the dataset has no supplied target label. The algorithm receives features but not a correct answer for each row. Common goals include grouping similar observations, reducing the number of dimensions, detecting unusual cases and discovering co-occurrence patterns.

An unsupervised output is not automatically a meaningful discovery. A clustering algorithm will assign groups even when the data has no natural clusters. The analyst must decide whether the structure is stable, useful and interpretable. Cluster labels such as 0, 1 and 2 are arbitrary identifiers, not rankings or real-world categories.

Start with the purpose: segmentation, compression, anomaly triage or exploration. Define the unit of observation and choose features that represent the concept. Exclude identifiers and post-outcome fields. Scale features where distance matters, and document missing-value handling. Validate with internal measures and domain knowledge rather than claiming a cluster is objectively true.

## 2. Worked Python example
Run in VS Code. Install relevant packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`. Some scikit-learn dataset loaders may require internet access on first use.

```python
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.cluster import KMeans

data = load_iris(as_frame=True)
X = data.data
model = KMeans(n_clusters=3, random_state=42, n_init=10)
labels = model.fit_predict(X)
print(pd.Series(labels).value_counts().sort_index())
print(pd.DataFrame(X).assign(cluster=labels).groupby("cluster").mean())
```

## 3. Interpretation
Describe the feature representation, distance or objective, model settings and what the output means. Cluster IDs are arbitrary. An anomaly flag is a prompt for investigation, not proof of misconduct. Validate any discovered pattern in original units and with domain knowledge.

## 4. Guided practice
Give an example of an unsupervised problem in retail. Define the observation unit, candidate features and what a useful segment would help a manager do. Explain why the cluster number is not a known customer type.

## 5. Independent practice
Choose a dataset and state the purpose of the unsupervised analysis. Compare at least two parameter settings. Profile the resulting groups or flagged cases and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the algorithm attempting to discover?
2. Which assumptions are introduced by the distance or representation?
3. How can you tell whether the result is useful rather than merely computable?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Human interpretation, stability checks and practical validation determine whether those patterns deserve to be used.