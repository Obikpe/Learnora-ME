# Lesson 3: Building Reproducible Training Pipelines

## Learning outcomes
Explain the applied ML engineering concept, implement the example and identify operational risks.

## 1. Core explanation
A training pipeline makes preprocessing and fitting repeatable. Use ColumnTransformer for numeric and categorical fields, then chain the transformer with the estimator. The pipeline should be trained from a defined data version and produce the same feature mapping when used for inference.

Keep training code separate from serving code. Store configuration in a controlled file, log model parameters and metrics, and make random seeds explicit where applicable. Validate the input schema before fitting. Save the fitted pipeline and a manifest of feature names, target definition, data snapshot and package versions.

A pipeline does not automatically guarantee reproducibility if upstream data changes or dependencies drift. Pin versions, record data provenance and include tests that check expected outputs and schema.

## 2. Worked Python example
Use VS Code and a project virtual environment. Install the relevant packages with `python -m pip install pandas scikit-learn fastapi uvicorn joblib httpx` as required.

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

X = pd.DataFrame({"age": [20, 35, None, 44, 28, 50],
                  "region": ["N", "S", "N", "W", "E", "S"]})
y = [0, 1, 0, 1, 0, 1]
prep = ColumnTransformer([
    ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                      ("scale", StandardScaler())]), ["age"]),
    ("cat", OneHotEncoder(handle_unknown="ignore"), ["region"])
])
pipe = Pipeline([("prep", prep), ("model", RandomForestClassifier(random_state=4))])
pipe.fit(X, y)
print(pipe.predict(pd.DataFrame({"age": [31], "region": ["Central"]})))
```

## 3. Engineering checks
Check schema compatibility, dependency versions, error handling, privacy and reproducibility. Distinguish a local demonstration from a production service. Never claim deployment readiness from a notebook score alone.

## 4. Guided practice
Extend the example with a train/test split and evaluation. Save the pipeline and a manifest that lists feature names, data version, package versions and training date.

## 5. Independent practice
Extend the example into a small, testable module. Document its input/output contract, setup instructions, expected failure behaviour and limitations. Add at least two tests.

## 6. Knowledge check
1. What responsibility belongs to the model and what belongs to the service?
2. What should happen when input is invalid?
3. Which information should be logged, and what should not?
4. What operational test would you run before release?

## Lesson summary
An applied ML product includes data transformations, model artefacts, validation, service contracts, tests, security and monitoring. The estimator is only one component.