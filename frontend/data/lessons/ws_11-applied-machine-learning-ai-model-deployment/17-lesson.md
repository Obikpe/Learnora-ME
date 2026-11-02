# Lesson 17: Experiment Tracking and Model Registry Concepts

## Learning outcomes
Explain the production concept, implement the worked example where applicable, and identify reliability, security and governance requirements.

## 1. Core explanation
Experiment tracking records what was tried, on which data, with which code and settings, and what result followed. Without tracking, teams cannot reliably reproduce or compare experiments. Record parameters, metrics, artefact locations, dataset identifiers and source-code commits.

A model registry adds lifecycle state: candidate, validated, approved, deployed, archived. Approval should include evaluation, intended use, limitations, security and operational checks. Registry metadata is not a substitute for access controls or data governance.

For small projects, a structured CSV or JSON manifest can be sufficient. Larger projects may use MLflow or another experiment platform. Avoid introducing infrastructure that costs more to maintain than the project itself.

## 2. Worked example
Run the Python example in VS Code. Install relevant packages with `python -m pip install numpy pandas scipy scikit-learn`. Cloud services and hosted models are not required for the local examples.

```python
import json
experiment = {
    "run_id": "exp-004",
    "git_commit": "replace-with-commit",
    "data_version": "dataset-v2",
    "parameters": {"max_depth": 5, "min_samples_leaf": 4},
    "metrics": {"f1": 0.84, "recall": 0.88},
    "status": "candidate"
}
with open("experiment.json", "w", encoding="utf-8") as f:
    json.dump(experiment, f, indent=2)
```

## 3. Operational interpretation
State what the example demonstrates and what it does not demonstrate. Distinguish a local prototype from a production deployment. Document dependencies, input/output contracts, data handling, failure modes and model version.

## 4. Guided practice
Create a lightweight experiment log for three model runs. Explain which metadata is essential for reproducibility and which model-registry state changes require approval.

## 5. Independent practice
Add the lesson's control or component to your own small ML application. Write a short runbook explaining how to test it, monitor it and respond when it fails.

## 6. Knowledge check
1. What can fail outside the model itself?
2. What should be logged and what should remain private?
3. How would you detect a change in behaviour?
4. What is the rollback or fallback plan?

## Lesson summary
Production ML is an engineered service with explicit contracts, versioning, monitoring, security and human accountability. A model score alone is not evidence of production readiness.