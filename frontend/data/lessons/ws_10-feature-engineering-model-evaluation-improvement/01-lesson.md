# Lesson 1: Feature Engineering as a Modelling Discipline

## Learning outcomes

By the end of this lesson, you should be able to Explain feature engineering as the construction of prediction-time inputs; aggregate raw records at the correct observation grain; create recency, frequency and monetary features; and document availability and meaning.

## 1. Core explanation
Feature engineering creates useful model inputs from raw fields. A feature is not simply any column available in a database; it must represent information available at prediction time and relate to the problem. Domain knowledge guides transformations such as ratios, recency, counts, rates, lags and interactions.

Begin by defining the observation unit and prediction timestamp. For each proposed feature, ask: what does it measure, how is it calculated, when is it known, could it reveal the target, and will the same calculation be available in production? A feature that uses future information is leakage even if it improves validation performance.

Good feature engineering is reproducible and tested. Keep transformations in code or a Pipeline rather than manually editing training and test files separately. Preserve the raw variables, document units and check for divide-by-zero, impossible values and missingness.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas scikit-learn`.

```python
import pandas as pd

orders = pd.DataFrame({
    "customer": [1, 1, 1, 2, 2],
    "order_date": pd.to_datetime(["2026-01-02", "2026-01-10", "2026-01-25",
                                  "2026-01-04", "2026-01-18"]),
    "amount": [30, 45, 25, 90, 60]
})
snapshot = pd.Timestamp("2026-02-01")
features = orders.groupby("customer").agg(
    order_count=("amount", "size"),
    total_spend=("amount", "sum"),
    average_order=("amount", "mean"),
    last_order=("order_date", "max")
)
features["recency_days"] = (snapshot - features["last_order"]).dt.days
print(features)
```

## 3. Interpretation and safeguards
State when each feature is available, how it was derived and whether it can be calculated consistently at prediction time. Fit all learned transformations on training data only. Compare performance using the same validation design and check that transformations do not remove meaningful information.

## 4. Guided practice
Create three features for predicting whether a customer will purchase next month. State the snapshot date and explain how each feature can be calculated without looking into the future.

## 5. Independent practice
Create a small feature-engineering workflow for a dataset. Include a data dictionary, transformation rationale, pipeline and validation plan. Identify one transformation you decided not to use and explain why.

## 6. Knowledge check
1. What information does this transformation add?
2. Could it leak information from after the prediction time?
3. Does it need to be fitted on training data?
4. How will you test its value and stability?

## Lesson summary
Feature engineering should create meaningful, available and reproducible inputs. Every transformation must be justified and validated within a leakage-safe workflow.