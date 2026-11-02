# Lesson 8: Regression Metrics and Residual Analysis

## Learning outcomes

By the end of this lesson, you should be able to Calculate MAE, MSE, RMSE and R-squared; interpret residuals and their units; compare the effect of large errors; and identify when each metric can mislead.

## 1. Core explanation
Regression metrics summarise different aspects of error. MAE is the average absolute residual and is easy to interpret in target units. MSE averages squared residuals and penalises large errors more strongly. RMSE is the square root of MSE and returns to target units. R-squared compares model error with a mean-prediction reference, but can be negative on test data.

No single metric tells the whole story. A small MAE may hide a few very large errors. Inspect residuals against predictions and relevant features. Patterns can reveal non-linearity, heteroscedasticity, subgroup errors or time drift. Check whether errors are systematically positive or negative for important groups.

Metrics must be calculated on the same rows and target scale for fair comparison. If you transform the target, explain whether metrics are reported on transformed or original units. For high-stakes applications, consider asymmetric costs: overestimating a delivery time may have a different cost from underestimating it.

## 2. Worked example
Use VS Code and a project virtual environment. Install the packages used in this lesson with `python -m pip install numpy pandas matplotlib scikit-learn`.

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

actual = np.array([100, 120, 130, 150, 180])
predicted = np.array([105, 115, 140, 145, 220])
residuals = actual - predicted
print("MAE:", mean_absolute_error(actual, predicted))
print("MSE:", mean_squared_error(actual, predicted))
print("RMSE:", mean_squared_error(actual, predicted)**0.5)
print("R2:", r2_score(actual, predicted))
print("Residuals:", residuals)
```

## 3. Interpretation and diagnostics
Explain what each feature and target represent, the units of the output and how the model was evaluated. Inspect errors and check that all preprocessing was learned from training data only. Never infer causation from predictive coefficients without a suitable causal design.

## 4. Guided practice
Calculate all four metrics for two candidate prediction arrays. Identify whether one model has lower average error but a worse extreme error. Decide which metric best matches your application and defend your choice.

## 5. Independent practice
Apply the method to a dataset of your choice. Define the prediction moment, target and feature availability. Compare with a simple baseline and report at least one metric plus an error analysis.

## 6. Knowledge check
1. What does the model estimate?
2. What assumptions or limitations matter most?
3. How could leakage or an inappropriate split inflate performance?
4. What additional analysis is needed before use?

## Lesson summary
Supervised models must be framed around a precise target and evaluated on unseen data. Model complexity and scores matter less than reliable performance for the intended decision.