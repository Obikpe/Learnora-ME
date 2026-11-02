# Lesson 9: Testing ML Applications

## Learning outcomes
Explain the applied ML engineering concept, implement the example and identify operational risks.

## 1. Core explanation
Testing an ML application includes ordinary software tests and model-specific checks. Unit tests cover feature transformations and validation functions. Integration tests exercise the API and model artefact together. Contract tests check request and response schemas. Regression tests compare outputs on known examples within an acceptable tolerance.

Do not require exact prediction equality across all environments if numerical libraries can introduce small floating-point differences. Test invariants and acceptable ranges. Include edge cases: empty input, missing fields, unseen categories, extreme values and corrupted model files.

Model tests should also monitor performance metrics and data quality, but a unit test cannot prove future generalisation. Keep test data separate and avoid hard-coding sensitive production records. Automate a small set of essential tests to control CI cost.

## 2. Worked Python example
Use VS Code and a project virtual environment. Install the relevant packages with `python -m pip install pandas scikit-learn fastapi uvicorn joblib httpx` as required.

```python
from fastapi.testclient import TestClient
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()
class Item(BaseModel):
    value: float = Field(ge=0, le=100)

@app.post("/score")
def score(item: Item):
    return {"score": item.value / 100}

client = TestClient(app)
assert client.post("/score", json={"value": 50}).status_code == 200
assert client.post("/score", json={"value": -2}).status_code == 422
```

## 3. Engineering checks
Check schema compatibility, dependency versions, error handling, privacy and reproducibility. Distinguish a local demonstration from a production service. Never claim deployment readiness from a notebook score alone.

## 4. Guided practice
Add tests for missing fields, wrong types and boundary values. Explain what these tests prove and what they do not prove about the model's real-world accuracy.

## 5. Independent practice
Extend the example into a small, testable module. Document its input/output contract, setup instructions, expected failure behaviour and limitations. Add at least two tests.

## 6. Knowledge check
1. What responsibility belongs to the model and what belongs to the service?
2. What should happen when input is invalid?
3. Which information should be logged, and what should not?
4. What operational test would you run before release?

## Lesson summary
An applied ML product includes data transformations, model artefacts, validation, service contracts, tests, security and monitoring. The estimator is only one component.