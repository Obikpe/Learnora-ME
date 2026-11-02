# Lesson 1: From Notebook to Applied ML Product

## Learning outcomes

By the end of this lesson, you should be able to Explain the gap between a notebook experiment and an applied ML product; identify the data, preprocessing, model, interface and operational components; and define the handover requirements for a reproducible application.

## 1. Core explanation
A notebook is useful for exploration because it combines code, output and narrative. A product needs a repeatable process that accepts new input, applies the same transformations, produces an output and handles failure. Moving from notebook to product requires separating experimentation from production logic.

Identify the model's user, input schema, output contract, latency needs, failure behaviour and decision context. Refactor repeated notebook cells into functions and modules. Remove hard-coded local paths, hidden state and exploratory outputs. Add input validation, logging and tests. Keep secrets and personal data out of source control.

A model product includes more than a trained estimator: preprocessing, dependencies, configuration, documentation, monitoring and a rollback plan are part of the system. A model that performs well in a notebook but cannot be reproduced or safely called is not production-ready.

## 2. Worked Python example
Use VS Code and a project virtual environment. Install the relevant packages with `python -m pip install pandas scikit-learn fastapi uvicorn joblib httpx` as required.

```python
# src/predict.py
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

def train_model(X: pd.DataFrame, y):
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    return model.fit(X, y)

def predict_one(model, record: dict) -> int:
    frame = pd.DataFrame([record], columns=["study_hours", "attendance"])
    return int(model.predict(frame)[0])
```

## 3. Engineering checks
Check schema compatibility, dependency versions, error handling, privacy and reproducibility. Distinguish a local demonstration from a production service. Never claim deployment readiness from a notebook score alone.

## 4. Guided practice
Take a notebook-based model and list what must change before another application can call it reliably. Include input validation, versioning, tests, logging and security.

## 5. Independent practice
Extend the example into a small, testable module. Document its input/output contract, setup instructions, expected failure behaviour and limitations. Add at least two tests.

## 6. Knowledge check
1. What responsibility belongs to the model and what belongs to the service?
2. What should happen when input is invalid?
3. Which information should be logged, and what should not?
4. What operational test would you run before release?

## Lesson summary
An applied ML product includes data transformations, model artefacts, validation, service contracts, tests, security and monitoring. The estimator is only one component.