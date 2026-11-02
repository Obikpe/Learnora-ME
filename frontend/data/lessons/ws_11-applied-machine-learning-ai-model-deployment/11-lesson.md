# Lesson 11: Deployment Options and Trade-Offs

## Learning outcomes
Explain the production concept, implement the worked example where applicable, and identify reliability, security and governance requirements.

## 1. Core explanation
Deployment means making a model available to the process that needs its output. Options include batch jobs, scheduled pipelines, a web API, an embedded model in an application or an edge device. Batch prediction is often simpler and cheaper when real-time responses are unnecessary. An API suits interactive requests but introduces availability and latency requirements.

Choose based on prediction frequency, freshness, volume, latency, privacy, network access, cost and operational capability. A cloud service may simplify scaling but creates dependency and data-transfer concerns. Local deployment can improve control and offline operation but requires device resources and update mechanisms.

Plan failure behaviour. What happens if the model service is down, input data is delayed or the prediction is outside expected ranges? A fallback process may be safer than returning a default prediction. Define ownership, rollback and support before release.

## 2. Worked example
Run the Python example in VS Code. Install relevant packages with `python -m pip install numpy pandas scipy scikit-learn`. Cloud services and hosted models are not required for the local examples.

```python
deployment_options = [
    {"mode": "Batch", "latency": "Minutes/hours", "best_for": "Scheduled scoring"},
    {"mode": "API", "latency": "Low", "best_for": "Interactive applications"},
    {"mode": "Edge", "latency": "Local", "best_for": "Offline or device use"}
]
for option in deployment_options:
    print(option)
```

## 3. Operational interpretation
State what the example demonstrates and what it does not demonstrate. Distinguish a local prototype from a production deployment. Document dependencies, input/output contracts, data handling, failure modes and model version.

## 4. Guided practice
Choose a deployment pattern for (a) weekly customer segmentation, (b) a live fraud checkout check and (c) an offline quality inspection device. Defend the choice and state one operational risk for each.

## 5. Independent practice
Add the lesson's control or component to your own small ML application. Write a short runbook explaining how to test it, monitor it and respond when it fails.

## 6. Knowledge check
1. What can fail outside the model itself?
2. What should be logged and what should remain private?
3. How would you detect a change in behaviour?
4. What is the rollback or fallback plan?

## Lesson summary
Production ML is an engineered service with explicit contracts, versioning, monitoring, security and human accountability. A model score alone is not evidence of production readiness.