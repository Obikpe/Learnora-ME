# Lesson 2: Preparing Data Without a Target

## Learning outcomes

By the end of this lesson, you should be able to Prepare a feature matrix without a target; inspect missingness, types and scales; choose defensible transformations; and explain how feature representation affects distance-based methods.

## 1. Core explanation
Without a target, feature selection depends on the question and the concept you want the algorithm to represent. For customer segmentation, transaction frequency, average basket size and recency may be meaningful. Customer ID is not a behavioural measure. For document clustering, word or embedding features represent text content. Irrelevant features can dominate distances and obscure useful structure.

Inspect missingness, duplicates, extreme values and feature distributions. Impute or remove missing records only with a defensible reason. Convert categories thoughtfully. Standardise numeric fields when distance-based algorithms are used; otherwise a large-unit feature can dominate. For skewed positive variables, a log transform may reduce extreme scale differences.

Do not include target-like outcomes or variables created after the observation time. Even without labels, leakage can make clusters reflect information unavailable for the intended use. Preserve a record of transformations so cluster profiles can be interpreted in the original units.

## 2. Worked Python example
Run in VS Code. Install relevant packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`. Some scikit-learn dataset loaders may require internet access on first use.

```python
import pandas as pd
from sklearn.preprocessing import StandardScaler

customers = pd.DataFrame({
    "recency_days": [5, 12, 60, 90, 8],
    "orders_90d": [12, 8, 1, 0, 10],
    "avg_basket": [35, 42, 18, 12, 39]
})
scaled = StandardScaler().fit_transform(customers)
print(pd.DataFrame(scaled, columns=customers.columns).round(2))
```

## 3. Interpretation
Describe the feature representation, distance or objective, model settings and what the output means. Cluster IDs are arbitrary. An anomaly flag is a prompt for investigation, not proof of misconduct. Validate any discovered pattern in original units and with domain knowledge.

## 4. Guided practice
Add a customer identifier column and observe what happens if you include it in clustering. Explain why arbitrary IDs should normally be excluded and why scaling is needed for these variables.

## 5. Independent practice
Choose a dataset and state the purpose of the unsupervised analysis. Compare at least two parameter settings. Profile the resulting groups or flagged cases and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the algorithm attempting to discover?
2. Which assumptions are introduced by the distance or representation?
3. How can you tell whether the result is useful rather than merely computable?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Human interpretation, stability checks and practical validation determine whether those patterns deserve to be used.