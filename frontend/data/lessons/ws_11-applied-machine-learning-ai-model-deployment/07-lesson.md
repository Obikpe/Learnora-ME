# Lesson 7: FastAPI Model Service Fundamentals

## Learning outcomes

By the end of this lesson, you should be able to Create a FastAPI service with health and prediction routes; define Pydantic input schemas; return structured JSON; and explain service startup and interactive API documentation.

## 1. Core explanation
FastAPI uses Python type hints and Pydantic models to validate request data and generate API documentation. A route function defines the HTTP method and path. The service can load a fitted model at application startup and reuse it for requests rather than loading the file on every call.

Keep model-loading logic separate from route handlers. Return a clear response schema with prediction, model version and optional confidence. Use appropriate status codes for invalid input or unavailable service. Do not return internal exception details to users.

For local development, Uvicorn runs the ASGI application. The interactive documentation is usually available at /docs. This local setup is for learning; a production service needs a proper process manager, secure deployment, authentication and monitoring.

## 2. Worked Python example
Use VS Code and a project virtual environment. Install the relevant packages with `python -m pip install pandas scikit-learn fastapi uvicorn joblib httpx` as required.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Demo ML service", version="1.0.0")

class Features(BaseModel):
    study_hours: float = Field(ge=0, le=24)
    attendance_rate: float = Field(ge=0, le=1)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(features: Features):
    probability = min(0.99, max(0.01,
        0.02 * features.study_hours + 0.8 * features.attendance_rate))
    return {"probability": probability, "model_version": "demo-1"}
```

## 3. Engineering checks
Check schema compatibility, dependency versions, error handling, privacy and reproducibility. Distinguish a local demonstration from a production service. Never claim deployment readiness from a notebook score alone.

## 4. Guided practice
Create /health and /predict endpoints. Explain the difference between a liveness check and a readiness check. Document how you would handle a missing or incompatible model artefact.

## 5. Independent practice
Extend the example into a small, testable module. Document its input/output contract, setup instructions, expected failure behaviour and limitations. Add at least two tests.

## 6. Knowledge check
1. What responsibility belongs to the model and what belongs to the service?
2. What should happen when input is invalid?
3. Which information should be logged, and what should not?
4. What operational test would you run before release?

## Lesson summary
An applied ML product includes data transformations, model artefacts, validation, service contracts, tests, security and monitoring. The estimator is only one component.