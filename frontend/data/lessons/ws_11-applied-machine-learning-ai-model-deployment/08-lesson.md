# Lesson 8: Input Validation and Error Handling

## Learning outcomes
Explain the applied ML engineering concept, implement the example and identify operational risks.

## 1. Core explanation
Input validation protects the model from malformed or nonsensical data. Validate types, required fields, allowed categories, ranges, units and cross-field constraints. A numeric value can be syntactically valid but semantically impossible, such as a negative age or a percentage above 100.

Return clear client errors for invalid requests and server errors for unexpected failures. Avoid silently clipping or coercing values unless the behaviour is documented. Log enough information to diagnose problems without storing unnecessary personal or sensitive data. Use request IDs to trace events across services.

Validation should be consistent with training data and the model's contract. Schema changes require versioning and tests. Do not allow invalid input to flow through simply because a library can convert it to a number.

## 2. Worked Python example
Use VS Code and a project virtual environment. Install the relevant packages with `python -m pip install pandas scikit-learn fastapi uvicorn joblib httpx` as required.

```python
from pydantic import BaseModel, Field, model_validator

class LoanFeatures(BaseModel):
    annual_income: float = Field(gt=0)
    loan_amount: float = Field(gt=0)
    term_months: int = Field(ge=1, le=480)

    @model_validator(mode="after")
    def amount_reasonable(self):
        if self.loan_amount > self.annual_income * 10:
            raise ValueError("Loan amount exceeds configured plausibility limit")
        return self

print(LoanFeatures(annual_income=50000, loan_amount=10000, term_months=24))
```

## 3. Engineering checks
Check schema compatibility, dependency versions, error handling, privacy and reproducibility. Distinguish a local demonstration from a production service. Never claim deployment readiness from a notebook score alone.

## 4. Guided practice
Add validation for a date range or category field. Distinguish schema validation (correct type) from domain validation (plausible business value). Explain how an API should respond to each failure.

## 5. Independent practice
Extend the example into a small, testable module. Document its input/output contract, setup instructions, expected failure behaviour and limitations. Add at least two tests.

## 6. Knowledge check
1. What responsibility belongs to the model and what belongs to the service?
2. What should happen when input is invalid?
3. Which information should be logged, and what should not?
4. What operational test would you run before release?

## Lesson summary
An applied ML product includes data transformations, model artefacts, validation, service contracts, tests, security and monitoring. The estimator is only one component.