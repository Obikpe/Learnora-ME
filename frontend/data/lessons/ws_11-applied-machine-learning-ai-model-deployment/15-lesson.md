# Lesson 15: Data Drift and Concept Drift

## Learning outcomes
Explain the production concept, implement the worked example where applicable, and identify reliability, security and governance requirements.

## 1. Core explanation
Data drift occurs when the input feature distribution changes. Concept drift occurs when the relationship between features and target changes. A change in customer demographics may create data drift; a new fraud strategy may change how transaction features relate to fraud. Drift can occur independently or together.

Statistical tests and distribution measures can detect changes, but large datasets can make tiny differences statistically significant. Set practical thresholds and inspect feature-level changes. Drift is a signal to investigate, not automatic proof that the model is failing. Delayed labels are needed to measure actual predictive performance.

Possible responses include checking data pipelines, recalibrating thresholds, retraining or reverting to a previous model. Do not retrain automatically on every detected change. Confirm data quality, label correctness and governance before changing the model.

## 2. Worked example
Run the Python example in VS Code. Install relevant packages with `python -m pip install numpy pandas scipy scikit-learn`. Cloud services and hosted models are not required for the local examples.

```python
import numpy as np
from scipy.stats import ks_2samp

reference = np.random.default_rng(1).normal(50, 10, 1000)
current = np.random.default_rng(2).normal(55, 12, 1000)
stat, p_value = ks_2samp(reference, current)
print("KS statistic:", stat, "p-value:", p_value)
```

## 3. Operational interpretation
State what the example demonstrates and what it does not demonstrate. Distinguish a local prototype from a production deployment. Document dependencies, input/output contracts, data handling, failure modes and model version.

## 4. Guided practice
Explain the difference between input drift and concept drift. Propose a monitoring plan for a delivery-time model where seasonal demand changes and delivery routes are updated.

## 5. Independent practice
Add the lesson's control or component to your own small ML application. Write a short runbook explaining how to test it, monitor it and respond when it fails.

## 6. Knowledge check
1. What can fail outside the model itself?
2. What should be logged and what should remain private?
3. How would you detect a change in behaviour?
4. What is the rollback or fallback plan?

## Lesson summary
Production ML is an engineered service with explicit contracts, versioning, monitoring, security and human accountability. A model score alone is not evidence of production readiness.