# Lesson 14: Regression Evaluation Metrics

## Learning outcomes
Explain MAE, MSE, RMSE and R-squared; calculate and interpret regression metrics; recognise the effect of outliers and target scale; and select metrics based on the business cost of errors.

## 1. What is a regression error?
Regression predicts a numeric value, such as house price, delivery time or monthly sales. For each observation, the error or residual is the actual value minus the prediction. A metric summarises errors across observations.

No single metric describes every aspect of model quality. Choose metrics that reflect the decision and explain their units. A model that predicts delivery time within ten minutes may be useful for one operation but unacceptable for another.

## 2. Mean Absolute Error (MAE)
MAE is the average absolute difference between actual and predicted values:

`MAE = mean(|actual - predicted|)`

If MAE is 8 minutes, the average absolute prediction error is 8 minutes. MAE is easy to explain and less sensitive to large errors than squared-error metrics.

## 3. Mean Squared Error and RMSE
MSE averages squared errors. Squaring gives larger errors much more influence. Its units are squared, so it is less intuitive to communicate.

RMSE is the square root of MSE and returns to the target's units. It penalises large errors more strongly than MAE. When large mistakes are especially costly, RMSE may be informative.

## 4. R-squared
R² compares the model's squared error with a baseline that predicts the mean target. A value of 1 indicates perfect predictions; 0 indicates performance equivalent to the mean baseline under the standard definition; negative values indicate worse performance than that baseline on the evaluation data. R² is not the percentage of predictions that are correct and does not establish causation.

![Regression metric comparison](/course-assets/ws10/regression-metrics.svg)

## 5. Worked example
```python
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score
)
import numpy as np

actual = np.array([100, 120, 130, 150, 200])
predicted = np.array([110, 118, 125, 160, 170])

mae = mean_absolute_error(actual, predicted)
mse = mean_squared_error(actual, predicted)
rmse = np.sqrt(mse)
r2 = r2_score(actual, predicted)

print("MAE:", round(mae, 2))
print("MSE:", round(mse, 2))
print("RMSE:", round(rmse, 2))
print("R-squared:", round(r2, 3))
```

Interpret the metrics together. MAE describes average absolute error. RMSE increases the influence of the large miss on the final observation. R² compares the residual variation with a mean-prediction baseline. None tells you whether errors are systematically too high or too low, so inspect residuals.

## 6. Percentage metrics and caveats
Mean Absolute Percentage Error (MAPE) divides absolute error by the actual value. It becomes undefined at zero and can become enormous when actual values are close to zero. It can also behave asymmetrically. Use it only when percentage error is meaningful and the target values support it.

For targets with different scales across groups, consider whether absolute or relative errors are more useful. For intermittent demand with many zeros, MAE, RMSE or specialised metrics may be more appropriate than MAPE.

## 7. Common mistakes
- Comparing RMSE values across different target units without adjustment.
- Treating R² as accuracy.
- Using MAPE when actual values can be zero.
- Reporting only one metric.
- Ignoring systematic residual patterns.
- Choosing a metric after seeing which one makes the model look best.

## Guided practice
A delivery model has MAE of 12 minutes and RMSE of 28 minutes. Explain what the gap might suggest about occasional large errors. Describe one operational question that MAE alone cannot answer.

## Independent practice
Train a regression model and report MAE, RMSE and R² on the same held-out set. Plot residuals against predictions and inspect errors by a meaningful subgroup.

## Knowledge check
1. What does MAE measure?
2. Why does RMSE penalise large errors more?
3. What does a negative R² mean?
4. Why can MAPE fail when actual values are zero?
5. Why should residuals be inspected?

## Lesson summary
Regression metrics describe different aspects of prediction error. Select them according to the consequences of mistakes, explain their units and inspect residual patterns rather than relying on a single headline number.

## 8. Deeper reasoning: inspect the shape of regression errors

A single average metric can hide systematic errors. Residuals are actual minus predicted values. If residuals are mostly positive for expensive houses, the model is underpredicting that segment. If errors grow as predicted values increase, the model may have scale-dependent error. If residuals show a curve against predictions, a linear model may be missing a non-linear relationship. If residuals cluster by region, the model may lack location information or the data may be collected differently across regions.

MAE and RMSE respond differently to extreme misses. Imagine nine predictions are wrong by 2 units and one is wrong by 30 units. MAE treats each absolute miss linearly; RMSE gives the 30-unit error much more influence because the error is squared before averaging. This is not a flaw in RMSE. It reflects a different preference about the consequences of large errors. If a single very late delivery is operationally much worse than several small timing errors, RMSE may reveal a risk that MAE softens.

R-squared can be negative on test data because the model may perform worse than predicting the training-derived mean baseline. It can also be high when the model has systematic bias in a way that is not obvious from the score. Do not use R² alone to decide whether a model is operationally acceptable.

Always report the target unit. An MAE of 5 means little without knowing whether the target is minutes, kilograms, naira or thousands of naira. If the target was transformed during modelling, calculate evaluation metrics in the original business unit where possible.