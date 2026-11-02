# Lesson 14: Regression Evaluation Metrics

## Learning outcomes

By the end of this lesson, you should be able to Compare K-fold, StratifiedKFold, GroupKFold and TimeSeriesSplit; select a splitter that matches the data structure; and explain what each validation score estimates.

## 1. Core explanation
MAE is the average absolute error and is easy to interpret in target units. MSE squares residuals and penalises large errors; RMSE returns to target units. R-squared compares model squared error with a mean-prediction reference and can be negative on test data. MAPE expresses percentage error but behaves badly when actual values are zero or near zero.

Metric choice reflects the decision. If large errors are especially harmful, RMSE may be more informative than MAE. If errors are interpreted in the original unit, MAE and RMSE are useful. If underprediction and overprediction have different costs, use an appropriate asymmetric loss or report both directions.

Always compare on the same rows and scale. Inspect residual plots and error by segment. A single average can hide systematic errors for high-value customers or long delivery routes.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

actual = np.array([100, 120, 130, 150, 180])
pred = np.array([105, 115, 140, 145, 220])
print("MAE", mean_absolute_error(actual, pred))
print("RMSE", mean_squared_error(actual, pred)**.5)
print("R2", r2_score(actual, pred))
print("Residuals", actual - pred)
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune a threshold, select features or choose hyperparameters.

## 4. Guided practice
Compare two candidate prediction arrays. Select a primary metric for a delivery-time model and explain whether late predictions or early predictions are more costly.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.