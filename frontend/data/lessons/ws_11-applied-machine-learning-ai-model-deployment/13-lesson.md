# Lesson 13: Cloud Deployment Concepts

## Learning outcomes

By the end of this lesson, you should be able to Compare VM, container and serverless hosting; plan environment configuration, network access, logging, spending limits and rollback; and identify data residency and retention constraints.

## 1. Core explanation
Cloud deployment runs an application on infrastructure managed by a cloud provider. Common options include virtual machines, containers, managed application platforms and serverless functions. The choice affects scaling, cost, cold starts, networking, data residency, logging and operational responsibility.

A deployment plan needs configuration, secrets, storage, identity, networking, health checks, monitoring and a rollback route. Keep development, staging and production environments separate. Do not assume a free tier is permanent or that an endpoint is private by default. Review current pricing, limits and data-handling terms before selecting a provider.

For a learning project, first deploy locally and test the container. Cloud deployment should be an explicit next step with a budget and security review. A public endpoint needs authentication or rate limiting where appropriate and should never expose sensitive training data.

## 2. Worked example
Run the Python example in VS Code. Install relevant packages with `python -m pip install numpy pandas scipy scikit-learn`. Cloud services and hosted models are not required for the local examples.

```python
# Deployment checklist (provider-neutral)
# [ ] Choose runtime: VM, container platform or serverless
# [ ] Set environment-specific configuration
# [ ] Store secrets outside source control
# [ ] Restrict inbound network access
# [ ] Configure health checks and logs
# [ ] Set resource and spending limits
# [ ] Test rollback to the previous model version
# [ ] Confirm data region and retention requirements
```

## 3. Operational interpretation
State what the example demonstrates and what it does not demonstrate. Distinguish a local prototype from a production deployment. Document dependencies, input/output contracts, data handling, failure modes and model version.

## 4. Guided practice
Prepare a cloud deployment plan without actually publishing a service. Compare two hosting options on cost, scaling, data residency, secrets and operational complexity. State what must be checked before any real deployment.

## 5. Independent practice
Add the lesson's control or component to your own small ML application. Write a short runbook explaining how to test it, monitor it and respond when it fails.

## 6. Knowledge check
1. What can fail outside the model itself?
2. What should be logged and what should remain private?
3. How would you detect a change in behaviour?
4. What is the rollback or fallback plan?

## Lesson summary
Production ML is an engineered service with explicit contracts, versioning, monitoring, security and human accountability. A model score alone is not evidence of production readiness.