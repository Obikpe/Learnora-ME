# Lesson 4: Saving Models and Preprocessing Together

## Learning outcomes
Explain the applied ML engineering concept, implement the example and identify operational risks.

## 1. Core explanation
Save the complete fitted Pipeline rather than the estimator alone. If training used scaling, imputation or encoding, inference must use the same fitted transformations and feature order. Saving only the estimator can lead to inconsistent preprocessing and invalid predictions.

Joblib is commonly used for scikit-learn artefacts, but it is based on Python object serialisation. Loading an untrusted file can execute arbitrary code. Restrict access to model artefacts, verify provenance and use controlled storage. Record compatible library versions because serialized objects may not work across major version changes.

Test round-trip behaviour: predict using the in-memory model, save it, load it and predict again. Compare results on known examples. Store a model card or manifest describing intended use, limitations, metrics and training data.

## 2. Worked Python example
Use VS Code and a project virtual environment. Install the relevant packages with `python -m pip install pandas scikit-learn fastapi uvicorn joblib httpx` as required.

```python
import joblib
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X = pd.DataFrame({"hours": [1, 2, 3, 4, 5, 6]})
y = [0, 0, 0, 1, 1, 1]
model = make_pipeline(StandardScaler(), LogisticRegression()).fit(X, y)
before = model.predict(pd.DataFrame({"hours": [2, 5]}))
joblib.dump(model, "model_pipeline.joblib")
loaded = joblib.load("model_pipeline.joblib")
after = loaded.predict(pd.DataFrame({"hours": [2, 5]}))
print(before, after)
```

## 3. Engineering checks
Check schema compatibility, dependency versions, error handling, privacy and reproducibility. Distinguish a local demonstration from a production service. Never claim deployment readiness from a notebook score alone.

## 4. Guided practice
Create a model manifest with model version, feature schema, training data identifier, package versions, evaluation metrics, intended use and known limitations. Explain why the model file should be loaded only from a trusted source.

## 5. Independent practice
Extend the example into a small, testable module. Document its input/output contract, setup instructions, expected failure behaviour and limitations. Add at least two tests.

## 6. Knowledge check
1. What responsibility belongs to the model and what belongs to the service?
2. What should happen when input is invalid?
3. Which information should be logged, and what should not?
4. What operational test would you run before release?

## Lesson summary
An applied ML product includes data transformations, model artefacts, validation, service contracts, tests, security and monitoring. The estimator is only one component.