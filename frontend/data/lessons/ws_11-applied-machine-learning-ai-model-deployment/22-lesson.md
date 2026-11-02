# Lesson 22: Production Readiness Review

## Learning outcomes

By the end of this lesson, you should be able to Assess production readiness across model validity, feature parity, input validation, authentication, monitoring, rollback and ownership; identify blockers; and make a justified go/no-go recommendation.

## 1. Core explanation
A readiness review asks whether the system is safe and supportable in its intended environment. Check model evidence, data lineage, feature parity, latency, throughput, availability, security, privacy, monitoring, retraining, rollback, cost and ownership. Ensure that a person or team is responsible for responding to incidents.

Define release gates before launch. Examples include minimum performance on a representative test, no critical subgroup failure, validated API contract, passing security checks, monitoring dashboards and a tested rollback. High-risk applications require stronger independent review and governance.

Readiness is not a permanent status. Reassess after data changes, model updates, new use cases or incidents. If evidence is insufficient, delay release or restrict the model to a monitored pilot. “It works on my machine” is not a deployment criterion.

## 2. Worked example
Run the Python example in VS Code. Use the course virtual environment and install relevant packages with `python -m pip install pandas scikit-learn fastapi pydantic joblib`.

```python
readiness = {
    "model_validation": False,
    "feature_parity_tested": False,
    "input_schema_validated": True,
    "authentication_configured": False,
    "monitoring_and_alerts": False,
    "rollback_tested": False,
    "owner_assigned": True
}
for item, passed in readiness.items():
    print(("PASS" if passed else "NOT READY"), item)
```

## 3. Operational interpretation
Distinguish model quality, software correctness and organisational readiness. Document assumptions, data handling, security controls and failure behaviour. A local demonstration is not automatically a production deployment.

## 4. Guided practice
Perform a readiness review of your deployment project. Mark each control pass, fail or not applicable. List release blockers and define evidence required to close each one. Make a final recommendation: release, limited pilot or do not release.

## 5. Independent practice
Apply the lesson to your project. Produce evidence such as tests, a model card, a runbook, a security checklist or a release decision. Explain what remains uncertain.

## 6. Knowledge check
1. What evidence is required before release?
2. Which risks are not captured by model accuracy?
3. Who owns incidents and rollback?
4. Under what conditions should release be delayed?

## Lesson summary
Applied ML must be validated as both a predictive system and a software service, with clear accountability, security, monitoring and rollback.