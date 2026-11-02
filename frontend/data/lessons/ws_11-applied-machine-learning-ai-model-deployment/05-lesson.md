# Lesson 5: Inference and Batch Prediction

## Learning outcomes
Explain the applied ML engineering concept, implement the example and identify operational risks.

## 1. Core explanation
Inference applies a fitted model to new observations. Single-record inference is useful for interactive applications; batch inference processes many records at once. Both must apply the same schema and transformations used in training. Validate required fields, types, missingness and plausible ranges before prediction.

Batch jobs should be idempotent: rerunning the same input should not create duplicate downstream actions. Include an input identifier for traceability, but do not feed arbitrary identifiers into the model unless justified. Handle partial failures and record which rows were rejected and why.

Predictions should include model version and timestamp. Store probabilities when useful, but do not confuse them with certainty. Apply a threshold policy separately from the model so it can be reviewed and changed under governance.

## 2. Worked Python example
Use VS Code and a project virtual environment. Install the relevant packages with `python -m pip install pandas scikit-learn fastapi uvicorn joblib httpx` as required.

```python
import pandas as pd
import joblib

# Assumes model_pipeline.joblib was created in the previous lesson.
model = joblib.load("model_pipeline.joblib")
batch = pd.DataFrame({"hours": [1.5, 3.5, 5.5]})
predictions = model.predict(batch)
result = batch.assign(prediction=predictions,
                      model_version="demo-1",
                      predicted_at=pd.Timestamp.utcnow())
print(result)
```

## 3. Engineering checks
Check schema compatibility, dependency versions, error handling, privacy and reproducibility. Distinguish a local demonstration from a production service. Never claim deployment readiness from a notebook score alone.

## 4. Guided practice
Extend batch inference to reject rows with missing required fields and preserve a reason for rejection. Explain how you would make a repeated batch run idempotent.

## 5. Independent practice
Extend the example into a small, testable module. Document its input/output contract, setup instructions, expected failure behaviour and limitations. Add at least two tests.

## 6. Knowledge check
1. What responsibility belongs to the model and what belongs to the service?
2. What should happen when input is invalid?
3. Which information should be logged, and what should not?
4. What operational test would you run before release?

## Lesson summary
An applied ML product includes data transformations, model artefacts, validation, service contracts, tests, security and monitoring. The estimator is only one component.