# Lesson 13: Building a Defensible Predictive Model

## Learning outcomes

By the end of this lesson, you should be able to Build a defensible predictive model with a clear target and prediction time; compare against a baseline; use leakage-safe preprocessing; and communicate evaluation limits.

## 1. Core explanation
A defensible model project begins with a decision and target that can be measured. Establish a baseline, define prediction time, audit features for leakage, choose a split that represents deployment and select metrics based on error costs. Keep preprocessing and model selection within training data.

Compare a transparent baseline with more flexible models. Inspect performance overall and across relevant groups. Review false positives, false negatives or residuals. If the model is intended to support people, explain how users should interpret its output and when to override it.

Document intended use, prohibited uses, limitations and monitoring requirements. A model should not be presented as a universal truth. It is an estimate based on a particular dataset, time period and modelling procedure.

## 2. Worked example or template
Use the example in VS Code or adapt the structure to your project.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42, stratify=data.target)
for model in [DummyClassifier(strategy="most_frequent"),
              make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))]:
    model.fit(Xtr, ytr)
    print(type(model).__name__, f1_score(yte, model.predict(Xte)))
```

## 3. Professional application
Keep the artefact reproducible and honest. State the data source, time period, methods, your contribution and limitations. Do not publish confidential data or make unsupported performance claims.

## 4. Guided practice
Write a model card containing intended use, data, evaluation, subgroup checks, limitations, human oversight and monitoring. Explain why a high F1 score is not enough to justify automated decisions.

## 5. Independent practice
Create or improve the corresponding project artefact. Ask another person to review it and record any unclear assumptions or missing instructions.

## 6. Knowledge check
1. What decision or audience does this artefact serve?
2. What evidence supports the claim?
3. Which limitations must be disclosed?
4. How can another person verify the work?

## Lesson summary
A professional portfolio demonstrates judgement, evidence, reproducibility and communication—not just familiarity with tools.