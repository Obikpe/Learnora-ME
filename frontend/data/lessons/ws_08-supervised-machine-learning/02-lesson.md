# Lesson 2: Regression and Classification Targets

## Learning outcomes

By the end of this lesson, you should be able to Distinguish regression targets from binary and multiclass classification targets; identify target data types; and explain how the target definition determines the modelling task and evaluation metrics.

## 1. Core explanation
A regression target is a numeric quantity where distances between values matter, such as price or delivery duration. A classification target is a category, such as approved/declined or fraud/not fraud. Binary classification has two classes; multiclass classification has more than two. Multi-label classification allows more than one label per observation.

The target's meaning determines the task. A numeric code for categories does not make a regression problem. If product type is encoded 0, 1 and 2, predicting 1.4 is meaningless. Conversely, a numeric measurement such as temperature should not usually be converted into arbitrary categories because doing so loses information.

Target construction needs care. Check class definitions, inconsistent labels, rare classes and delayed outcomes. For regression, inspect range, skew and impossible values. For classification, inspect class proportions and whether classes are mutually exclusive. Document how ambiguous cases are handled.

## 2. Worked example
Use VS Code and a project virtual environment. Install the packages used in this lesson with `python -m pip install numpy pandas matplotlib scikit-learn`.

```python
import pandas as pd

df = pd.DataFrame({
    "house_price": [120000, 185000, 210000],
    "loan_status": ["paid", "late", "paid"],
    "product_type": ["phone", "laptop", "phone"]
})
print(df.dtypes)
print(df["loan_status"].value_counts())
print(df["product_type"].value_counts())
```

## 3. Interpretation and diagnostics
Explain what each feature and target represent, the units of the output and how the model was evaluated. Inspect errors and check that all preprocessing was learned from training data only. Never infer causation from predictive coefficients without a suitable causal design.

## 4. Guided practice
For a dataset containing age, income, customer segment and churn status, identify which column is the target for a churn classifier. Explain why customer segment encoded as 1, 2 and 3 is not a valid numeric regression target.

## 5. Independent practice
Apply the method to a dataset of your choice. Define the prediction moment, target and feature availability. Compare with a simple baseline and report at least one metric plus an error analysis.

## 6. Knowledge check
1. What does the model estimate?
2. What assumptions or limitations matter most?
3. How could leakage or an inappropriate split inflate performance?
4. What additional analysis is needed before use?

## Lesson summary
Supervised models must be framed around a precise target and evaluated on unseen data. Model complexity and scores matter less than reliable performance for the intended decision.