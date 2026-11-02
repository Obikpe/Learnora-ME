# Lesson 14: Monitoring Model and Data Quality

## Learning outcomes
Explain the production concept, implement the worked example where applicable, and identify reliability, security and governance requirements.

## 1. Core explanation
Monitoring checks whether the service and model continue to behave as expected. System metrics include availability, latency, error rate and resource use. Data quality metrics include missingness, schema changes, value ranges and category frequencies. Model metrics include prediction distribution, confidence, delayed ground-truth performance and subgroup error rates.

Model quality may not be measurable immediately because labels arrive later. Use leading indicators such as input drift and prediction distribution, but do not treat them as proof of performance degradation. Define alert thresholds, owners and actions. A dashboard without an incident response process does not provide operational safety.

Monitor data at the point of ingestion and inference. Track model version and input schema with each prediction. Protect privacy by minimising logged content and restricting access. Monitoring itself can create sensitive records.

## 2. Worked example
Run the Python example in VS Code. Install relevant packages with `python -m pip install numpy pandas scipy scikit-learn`. Cloud services and hosted models are not required for the local examples.

```python
import pandas as pd

reference = pd.Series([18, 22, 25, 30, 35, 40, 45])
current = pd.Series([18, 20, 24, 29, 70, 75, 80])
summary = pd.DataFrame({
    "reference_mean": [reference.mean()],
    "current_mean": [current.mean()],
    "reference_missing": [reference.isna().mean()],
    "current_missing": [current.isna().mean()]
})
print(summary)
```

## 3. Operational interpretation
State what the example demonstrates and what it does not demonstrate. Distinguish a local prototype from a production deployment. Document dependencies, input/output contracts, data handling, failure modes and model version.

## 4. Guided practice
Design a monitoring dashboard for an ML API. Include service metrics, input quality, prediction distribution, delayed outcome metrics and subgroup checks. For each metric define an alert threshold and an owner response.

## 5. Independent practice
Add the lesson's control or component to your own small ML application. Write a short runbook explaining how to test it, monitor it and respond when it fails.

## 6. Knowledge check
1. What can fail outside the model itself?
2. What should be logged and what should remain private?
3. How would you detect a change in behaviour?
4. What is the rollback or fallback plan?

## Lesson summary
Production ML is an engineered service with explicit contracts, versioning, monitoring, security and human accountability. A model score alone is not evidence of production readiness.