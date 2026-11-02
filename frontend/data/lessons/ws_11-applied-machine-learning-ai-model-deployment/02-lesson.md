# Lesson 2: Choosing and Framing an Applied Problem

## Learning outcomes
Explain the applied ML engineering concept, implement the example and identify operational risks.

## 1. Core explanation
An applied ML project starts with a real decision, not an algorithm. Identify the stakeholder, current process, decision timing, action triggered by a prediction and the cost of errors. Decide whether a predictive model adds value compared with a rule, report or process change.

Define the target operationally and establish a baseline. Clarify who is affected and what happens when the model is unavailable or uncertain. Determine whether the task is suitable for automation or should support human review. A model should not be used simply because data exists.

Write a short problem brief with scope, success measures, constraints, data sources and out-of-scope uses. Make sure success is measurable and does not reward harmful shortcuts such as reducing false positives by ignoring an underserved group.

## 2. Worked Python example
Use VS Code and a project virtual environment. Install the relevant packages with `python -m pip install pandas scikit-learn fastapi uvicorn joblib httpx` as required.

```python
problem_brief = {
    "decision": "Which deliveries need proactive review?",
    "prediction_time": "At dispatch",
    "target": "Arrival later than promised window",
    "action": "Prioritise a human review queue",
    "success_metric": "Recall at a fixed daily review capacity",
    "guardrail": "Report errors by delivery region"
}
for key, value in problem_brief.items():
    print(f"{key}: {value}")
```

## 3. Engineering checks
Check schema compatibility, dependency versions, error handling, privacy and reproducibility. Distinguish a local demonstration from a production service. Never claim deployment readiness from a notebook score alone.

## 4. Guided practice
Write a one-page problem brief for a model that predicts learner dropout risk. Define the prediction moment, target window, intervention, error costs and safeguards against labelling learners unfairly.

## 5. Independent practice
Extend the example into a small, testable module. Document its input/output contract, setup instructions, expected failure behaviour and limitations. Add at least two tests.

## 6. Knowledge check
1. What responsibility belongs to the model and what belongs to the service?
2. What should happen when input is invalid?
3. Which information should be logged, and what should not?
4. What operational test would you run before release?

## Lesson summary
An applied ML product includes data transformations, model artefacts, validation, service contracts, tests, security and monitoring. The estimator is only one component.