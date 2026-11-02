# Applied Machine Learning, AI & Model Deployment
Course: ws_11
Level: Intermediate to advanced
Duration: 18h • 22 lessons
Prerequisite: WS01–WS10; Python, scikit-learn, evaluation, feature engineering and model validation

## Course purpose
Move from notebooks and experiments to useful, maintainable Python model applications. Learners package preprocessing and models, expose predictions through a small API, understand deployment options, monitor model behaviour and explore responsible AI/LLM integration without treating generative AI as a substitute for validated machine learning.

## Learning outcomes
Prepare a model for handoff; persist and load pipelines safely; create prediction functions and APIs; validate inputs; understand deployment patterns; monitor data and model drift; manage versions; consider security and privacy; understand AI/LLM concepts; and document model limitations.

## Lesson sequence
01. From Experiment to Application — notebook vs service, user needs, model contract and operational readiness.
02. Reproducible Python Environments — virtual environments, dependencies, requirements files and version compatibility.
03. Packaging a Complete Pipeline — preprocessing plus estimator, fit boundaries and consistent inference.
04. Saving and Loading Models — joblib/pickle risks, trusted artifacts, versioning and reproducibility.
05. Building a Prediction Interface — input schema, validation, output contract, batch vs single prediction.
06. Designing a Python API — HTTP basics, request/response, FastAPI concepts and endpoint design.
07. Implementing a Prediction API — FastAPI app, Pydantic validation, model loading and prediction route.
08. Testing Model Applications — unit, integration and input-validation tests; deterministic test cases.
09. Batch Inference and Data Pipelines — reading data, batch scoring, output persistence and failure handling.
10. Deployment Architecture — local, server, container and managed platform options; cost and constraints.
11. Containers and Reproducible Runtime — Docker concepts, image, container, ports, dependencies and secrets.
12. Deployment Readiness and Release — configuration, health checks, logging, rollback and model artifact handling.
13. Model Monitoring — service health, latency, error rates, data quality and prediction distributions.
14. Data Drift and Concept Drift — definitions, detection signals, delayed labels and retraining decisions.
15. Model Versioning and Lifecycle — experiment records, artifact registry concepts, champion/challenger and rollback.
16. Security, Privacy and Governance — input validation, access control, secrets, sensitive data and auditability.
17. Responsible AI in Practice — bias, explainability, human oversight, intended use and limitations.
18. AI and Generative AI Foundations — language models, tokens, embeddings, retrieval, prompts and hallucinations.
19. Combining Predictive ML with LLM Workflows — deterministic model outputs, retrieval grounding, tool boundaries and evaluation.
20. Evaluating AI Features — task-specific metrics, human review, safety tests, latency and cost.
21. End-to-End Applied ML Deployment Project — packaged pipeline, API or batch service, tests, monitoring plan and documentation.
22. Operational Handoff and Course Review — model card, runbook, versioning, incident response and portfolio-ready presentation.

## Tools
Python, scikit-learn, joblib, FastAPI, Pydantic, pytest, Docker concepts and optional local/cloud deployment platforms. Keep core exercises runnable locally; clearly label optional infrastructure.

## Assessment
Model packaging task, validated prediction interface, API tests, monitoring design and an end-to-end applied project. Deployment must not require paid cloud services to complete the learning outcomes.

## Completion standard
Learners can turn a validated Python model into a documented and testable application, explain its operational risks and plan monitoring and maintenance.
