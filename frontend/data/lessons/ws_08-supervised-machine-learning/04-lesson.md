# Lesson 4: Simple Linear Regression

## Learning outcomes
Explain the supervised-learning concept, implement the method in Python, interpret its output and identify assumptions and common failure modes.

## 1. Core explanation
Simple linear regression models a numeric target y using one feature x: predicted y = intercept + slope × x. The slope estimates the expected change in the target for a one-unit increase in x under the fitted linear relationship. The intercept is the predicted target when x is zero; it may have no practical meaning if zero is outside the observed range.

Ordinary least squares chooses the line that minimises the sum of squared residuals. A residual is actual minus predicted. Inspect a scatter plot and residual plot: a curve suggests non-linearity; a funnel shape suggests changing error variance; a few extreme points may dominate the fit. Regression estimates association, not causation.

Do not extrapolate far beyond the observed feature range without strong justification. A line that fits between 1 and 10 study hours may produce nonsensical predictions at 100 hours. Report units and the range of the data.

## 2. Worked example
Use VS Code and a project virtual environment. Install the packages used in this lesson with `python -m pip install numpy pandas matplotlib scikit-learn`.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

hours = np.array([1, 2, 3, 4, 5, 6]).reshape(-1, 1)
scores = np.array([45, 49, 55, 59, 64, 68])
model = LinearRegression().fit(hours, scores)
pred = model.predict(hours)
print("Slope:", model.coef_[0], "Intercept:", model.intercept_)
plt.scatter(hours, scores, label="Observed")
plt.plot(hours, pred, label="Fitted line")
plt.xlabel("Study hours"); plt.ylabel("Assessment score")
plt.legend(); plt.show()
```

## 3. Interpretation and diagnostics
Explain what each feature and target represent, the units of the output and how the model was evaluated. Inspect errors and check that all preprocessing was learned from training data only. Never infer causation from predictive coefficients without a suitable causal design.

## 4. Guided practice
Interpret the slope in score points per additional study hour. Inspect residuals by subtracting predictions from observed values. State why the fitted slope does not prove that increasing study hours alone will cause a score increase.

## 5. Independent practice
Apply the method to a dataset of your choice. Define the prediction moment, target and feature availability. Compare with a simple baseline and report at least one metric plus an error analysis.

## 6. Knowledge check
1. What does the model estimate?
2. What assumptions or limitations matter most?
3. How could leakage or an inappropriate split inflate performance?
4. What additional analysis is needed before use?

## Lesson summary
Supervised models must be framed around a precise target and evaluated on unseen data. Model complexity and scores matter less than reliable performance for the intended decision.