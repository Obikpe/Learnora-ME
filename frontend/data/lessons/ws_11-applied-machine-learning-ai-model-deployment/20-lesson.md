# Lesson 20: Responsible AI, Privacy and Security

## Learning outcomes
Explain the production concept, implement the example and evaluate the system against its intended use.

## 1. Core explanation
Responsible AI is a lifecycle discipline. Identify who is affected, what decisions the system influences and what harm can occur from errors, bias, misuse or over-reliance. Use data minimisation, purpose limitation, access control, retention limits and appropriate consent or lawful basis. Avoid collecting sensitive information merely because it may improve a metric.

Security risks include exposed model endpoints, leaked credentials, malicious files, prompt injection, data poisoning and model extraction. For generative systems, retrieved documents and user input are untrusted content. Keep instructions separate from data, restrict tool permissions and validate outputs before actions.

Governance includes documentation, approval, audit logs, incident response, human review and a way to challenge decisions. Explain model limitations in plain language. A human in the loop is not sufficient if reviewers cannot understand or override the output.

## 2. Worked example
Run the Python example in VS Code. Use the course virtual environment and install relevant packages with `python -m pip install pandas scikit-learn fastapi pydantic joblib`.

```python
security_review = {
    "data_minimisation": "Only fields needed for the defined purpose",
    "access": "Authenticated roles with least privilege",
    "secrets": "Environment variables or secret manager; never source control",
    "input_validation": "Schema, range and file checks",
    "monitoring": "Errors, drift, subgroup performance and access events",
    "oversight": "Named owner, appeal path and rollback procedure"
}
for control, description in security_review.items():
    print(f"{control}: {description}")
```

## 3. Operational interpretation
Distinguish model quality, software correctness and organisational readiness. Document assumptions, data handling, security controls and failure behaviour. A local demonstration is not automatically a production deployment.

## 4. Guided practice
Complete a risk review for a learner dropout-risk model. Include privacy, bias, access control, explanation, human review, appeal and a prohibition on using predictions as automatic punishment.

## 5. Independent practice
Apply the lesson to your project. Produce evidence such as tests, a model card, a runbook, a security checklist or a release decision. Explain what remains uncertain.

## 6. Knowledge check
1. What evidence is required before release?
2. Which risks are not captured by model accuracy?
3. Who owns incidents and rollback?
4. Under what conditions should release be delayed?

## Lesson summary
Applied ML must be validated as both a predictive system and a software service, with clear accountability, security, monitoring and rollback.