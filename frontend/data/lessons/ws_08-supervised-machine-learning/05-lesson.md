# Lesson 5: Multiple Linear Regression

## Learning outcomes
Explain the supervised-learning concept, implement the method in Python, interpret its output and identify assumptions and common failure modes.

## 1. Core explanation
Multiple linear regression uses several features: prediction = intercept + b1x1 + b2x2 + ... . Each coefficient describes the model's expected change in prediction for a one-unit increase in that feature while holding the other included features fixed. This “holding other features fixed” interpretation is conditional on the model and data; it is not automatically causal.

Correlated predictors can make coefficients unstable. This is multicollinearity: several features carry overlapping information. Coefficients may change greatly when data or features change even if predictions remain similar. Inspect correlations and domain relationships. Consider regularisation or reducing redundant variables where appropriate.

Categorical features need encoding. A coefficient for a one-hot indicator compares that category with the omitted reference category. State the reference group. Evaluate the model on unseen data and inspect residuals, not only R-squared. R-squared measures variation explained in the sample and does not guarantee predictive accuracy.

## 2. Worked example
Use VS Code and a project virtual environment. Install the packages used in this lesson with `python -m pip install numpy pandas matplotlib scikit-learn`.

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

df = pd.DataFrame({
    "area": [45, 55, 60, 72, 80, 90, 100, 110],
    "bedrooms": [1, 2, 2, 2, 3, 3, 3, 4],
    "price": [80, 105, 115, 130, 155, 170, 190, 215]
})
X = df[["area", "bedrooms"]]; y = df["price"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.25, random_state=2)
model = LinearRegression().fit(Xtr, ytr)
pred = model.predict(Xte)
print("Coefficients:", model.coef_)
print("MAE:", mean_absolute_error(yte, pred), "R2:", r2_score(yte, pred))
```

## 3. Interpretation and diagnostics
Explain what each feature and target represent, the units of the output and how the model was evaluated. Inspect errors and check that all preprocessing was learned from training data only. Never infer causation from predictive coefficients without a suitable causal design.

## 4. Guided practice
Explain the coefficient units. If area is square metres and price is thousands of currency units, state what one coefficient unit means. Add a strongly correlated feature and explain why coefficients may become less stable.

## 5. Independent practice
Apply the method to a dataset of your choice. Define the prediction moment, target and feature availability. Compare with a simple baseline and report at least one metric plus an error analysis.

## 6. Knowledge check
1. What does the model estimate?
2. What assumptions or limitations matter most?
3. How could leakage or an inappropriate split inflate performance?
4. What additional analysis is needed before use?

## Lesson summary
Supervised models must be framed around a precise target and evaluated on unseen data. Model complexity and scores matter less than reliable performance for the intended decision.