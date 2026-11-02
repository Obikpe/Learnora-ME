# Lesson 6: Serving Predictions Through an API

## Learning outcomes
Explain the applied ML engineering concept, implement the example and identify operational risks.

## 1. Core explanation
An API exposes model inference to other software through a defined request and response contract. A client sends structured input, the service validates it, loads a model, performs inference and returns a structured response. Keep the contract stable and version it when fields or meanings change.

An API is not the model itself. It is an operational boundary that handles authentication, validation, errors, rate limits, logging and availability. Do not expose raw stack traces or internal paths to clients. Avoid logging sensitive request bodies. Set timeouts and consider concurrency and model loading behaviour.

Start with a local service in development. Test valid, invalid, missing and out-of-range inputs. Document the endpoint, schema and response. Production deployment requires secure transport, access controls, monitoring and an operational owner.

## 2. Worked Python example
Use VS Code and a project virtual environment. Install the relevant packages with `python -m pip install pandas scikit-learn fastapi uvicorn joblib httpx` as required.

```python
# Minimal API sketch; save as app.py after installing fastapi and uvicorn.
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Study Outcome Prediction API")

class PredictionInput(BaseModel):
    study_hours: float = Field(ge=0, le=24)
    attendance: float = Field(ge=0, le=1)

@app.post("/predict")
def predict(payload: PredictionInput):
    # Replace with a loaded, versioned model pipeline.
    score = 0.15 * payload.study_hours + 0.85 * payload.attendance
    return {"demo_score": round(score, 3), "model_version": "demo-0"}
# Run: uvicorn app:app --reload
```

## 3. Engineering checks
Check schema compatibility, dependency versions, error handling, privacy and reproducibility. Distinguish a local demonstration from a production service. Never claim deployment readiness from a notebook score alone.

## 4. Guided practice
Call the local endpoint with valid values, then send negative study hours and attendance above 1. Explain why input validation belongs at the API boundary as well as in downstream data checks.

## 5. Independent practice
Extend the example into a small, testable module. Document its input/output contract, setup instructions, expected failure behaviour and limitations. Add at least two tests.

## 6. Knowledge check
1. What responsibility belongs to the model and what belongs to the service?
2. What should happen when input is invalid?
3. Which information should be logged, and what should not?
4. What operational test would you run before release?

## Lesson summary
An applied ML product includes data transformations, model artefacts, validation, service contracts, tests, security and monitoring. The estimator is only one component.