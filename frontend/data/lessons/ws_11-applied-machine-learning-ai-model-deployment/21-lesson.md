# Lesson 21: Deployment Project: Build and Serve a Model

## Learning outcomes
Explain the production concept, implement the example and evaluate the system against its intended use.

## 1. Core explanation
This project combines model development with a small local prediction service. Select a public educational dataset, define the target and intended use, create a reproducible preprocessing-and-model Pipeline, evaluate it on a held-out set and save the complete artefact. Build an API that validates inputs and returns a prediction with a model version.

The API must not silently accept invalid fields. Include a health endpoint, tests for valid and invalid requests, and clear setup instructions. Do not deploy publicly as part of this exercise. A local service is sufficient to demonstrate the engineering workflow.

The report must distinguish model evaluation from API correctness. A service can return valid JSON while the model is inaccurate. Conversely, a good model can be exposed through an insecure or unreliable service. Evaluate both layers.

## 2. Worked example
Run the Python example in VS Code. Use the course virtual environment and install relevant packages with `python -m pip install pandas scikit-learn fastapi pydantic joblib`.

```python
# Project structure
# ml-service/
#   app.py
#   train.py
#   model_pipeline.joblib
#   requirements.txt
#   tests/test_api.py
#   README.md
#
# Minimum API contract:
# POST /predict -> {"prediction": ..., "model_version": "..."}
# GET /health -> {"status": "ok"}
# Validate all input fields with Pydantic.
# Keep model preprocessing inside the saved sklearn Pipeline.
```

## 3. Operational interpretation
Distinguish model quality, software correctness and organisational readiness. Document assumptions, data handling, security controls and failure behaviour. A local demonstration is not automatically a production deployment.

## 4. Guided practice
Deliver a local API, trained pipeline, test suite, README and model card. Demonstrate one valid request and two invalid requests. Explain model performance, operational limitations, privacy controls and why the service is not yet production-ready.

## 5. Independent practice
Apply the lesson to your project. Produce evidence such as tests, a model card, a runbook, a security checklist or a release decision. Explain what remains uncertain.

## 6. Knowledge check
1. What evidence is required before release?
2. Which risks are not captured by model accuracy?
3. Who owns incidents and rollback?
4. Under what conditions should release be delayed?

## Lesson summary
Applied ML must be validated as both a predictive system and a software service, with clear accountability, security, monitoring and rollback.