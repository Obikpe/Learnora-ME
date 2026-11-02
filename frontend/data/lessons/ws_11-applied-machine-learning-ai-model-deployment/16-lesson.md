# Lesson 16: Retraining and Model Versioning

## Learning outcomes
Explain the production concept, implement the worked example where applicable, and identify reliability, security and governance requirements.

## 1. Core explanation
Retraining updates a model using newer data. It should be triggered by a planned schedule, a verified performance decline or a material change in the environment—not merely because new rows exist. Check label quality, representativeness and whether the new data reflects the intended population.

Version model code, training data snapshot, preprocessing, hyperparameters and evaluation results. A model registry or controlled manifest records which version is approved, deployed and retired. Keep the previous model available for rollback. Compare a candidate against the current production model on a common evaluation design.

Retraining can make a model worse if new labels are noisy, drift is temporary or the sample is biased. Use a release gate and human review appropriate to risk. Monitor after release and maintain an audit trail.

## 2. Worked example
Run the Python example in VS Code. Install relevant packages with `python -m pip install numpy pandas scipy scikit-learn`. Cloud services and hosted models are not required for the local examples.

```python
model_manifest = {
    "model_name": "delivery-delay-classifier",
    "version": "1.2.0",
    "training_data_snapshot": "orders_2026_09",
    "features_schema_version": "3",
    "validation_metric": "recall_at_capacity",
    "status": "candidate"
}
print(model_manifest)
```

## 3. Operational interpretation
State what the example demonstrates and what it does not demonstrate. Distinguish a local prototype from a production deployment. Document dependencies, input/output contracts, data handling, failure modes and model version.

## 4. Guided practice
Write a model-version manifest for a retrained classifier. Define promotion criteria, rollback criteria and who approves a release. Explain why retraining must not overwrite the previous approved artefact.

## 5. Independent practice
Add the lesson's control or component to your own small ML application. Write a short runbook explaining how to test it, monitor it and respond when it fails.

## 6. Knowledge check
1. What can fail outside the model itself?
2. What should be logged and what should remain private?
3. How would you detect a change in behaviour?
4. What is the rollback or fallback plan?

## Lesson summary
Production ML is an engineered service with explicit contracts, versioning, monitoring, security and human accountability. A model score alone is not evidence of production readiness.