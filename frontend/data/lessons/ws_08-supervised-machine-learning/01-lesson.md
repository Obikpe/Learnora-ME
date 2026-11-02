# Lesson 1: Supervised Learning: Problem Framing

## Learning outcomes
Explain the supervised-learning concept, implement the method in Python, interpret its output and identify assumptions and common failure modes.

## 1. Core explanation
Supervised learning uses examples with known outcomes to learn a mapping from features X to target y. The first task is not choosing an algorithm; it is defining the decision. Specify who will use the prediction, what action follows, when the prediction is made and what errors cost. A target such as “customer churn” must have an operational definition: for example, no qualifying purchase within the next 60 days.

Define one row precisely. A row might represent a customer at a monthly snapshot, not simply a customer. Set the prediction timestamp and use only fields available at that moment. Decide the prediction horizon and how delayed outcomes are labelled. Ambiguous targets produce models that optimise the wrong problem.

Regression predicts numeric values; classification predicts classes or class probabilities. Some business questions can be framed either way, but the output and decision differ. A risk score is not itself a decision threshold. Stakeholders must decide what level of risk triggers action, considering capacity and error costs.

## 2. Worked example
Use VS Code and a project virtual environment. Install the packages used in this lesson with `python -m pip install numpy pandas matplotlib scikit-learn`.

```python
import pandas as pd

cases = pd.DataFrame({
    "customer": [1, 2, 3, 4],
    "snapshot_date": pd.to_datetime(["2026-01-01"] * 4),
    "days_since_purchase": [5, 70, 20, 90],
    "purchase_next_60_days": [1, 0, 1, 0]
})
X = cases[["days_since_purchase"]]
y = cases["purchase_next_60_days"]
print(X.head())
print(y.value_counts(normalize=True))
```

## 3. Interpretation and diagnostics
Explain what each feature and target represent, the units of the output and how the model was evaluated. Inspect errors and check that all preprocessing was learned from training data only. Never infer causation from predictive coefficients without a suitable causal design.

## 4. Guided practice
Write a precise problem statement for predicting late loan repayment. Define the row, prediction date, target horizon, allowed features, intended action and the cost of false alarms versus missed late payments.

## 5. Independent practice
Apply the method to a dataset of your choice. Define the prediction moment, target and feature availability. Compare with a simple baseline and report at least one metric plus an error analysis.

## 6. Knowledge check
1. What does the model estimate?
2. What assumptions or limitations matter most?
3. How could leakage or an inappropriate split inflate performance?
4. What additional analysis is needed before use?

## Lesson summary
Supervised models must be framed around a precise target and evaluated on unseen data. Model complexity and scores matter less than reliable performance for the intended decision.