# Lesson 8: Regression Metrics and Residual Analysis

## Learning outcomes

By the end of this lesson, you should be able to Calculate MAE, MSE, RMSE and R-squared; interpret residuals and their units; compare the effect of large errors; and identify when each metric can mislead.


![regression concept diagram](/course-assets/ws08/regression.svg)

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

## 7. Learn the idea, not just the API

Separate three questions when studying this method. First, what is it trying to learn from the examples? Identify its inputs, target and the quantity or structure adjusted during training. Second, what does its fitted output mean in the real problem? Translate predictions, coefficients, probabilities, splits and metrics into the original units. Third, what evidence would make the result trustworthy? Check whether the data represents future use, whether the prediction timeline is respected and whether evaluation observations were kept separate from fitting.

Training is practice with known answers. Validation is a rehearsal used to choose between approaches. Testing is the final examination. Repeatedly changing a model after inspecting test results turns the test set into another validation set and makes the final score optimistic.

## 8. Read the implementation carefully

Read the Python workflow from the data outward. Identify the input columns and target. Find the split operation and establish which rows are held back. Find fit: this is where the model learns. Find predict or predict_proba: these apply the fitted model to new rows. Finally, locate the metric and confirm that it compares predictions with the correct held-out target values.

A parameter is an instruction that changes behaviour, not a magic setting. Ask what happens when it increases, what trade-off it controls and how it should be selected. Use training/validation data or cross-validation to choose settings, never repeated optimisation of the final test score.

## 9. Worked reasoning example

Imagine a learning platform predicts whether a learner will complete a course. One row represents a learner at the end of week two; the target is completion by the end of week eight. Candidate inputs include attendance, assignments submitted and lesson activity recorded up to week two. Before fitting, check that no feature contains week-three-to-week-eight information. Compare the model with a simple baseline. If the model improves the headline score, inspect which learners it gets wrong and whether errors are concentrated in a particular group. Decide whether the improvement is reliable and useful enough to support the proposed intervention.

A good model is not simply one that scores well. It must answer the intended question at the intended time, use legitimate information and make errors that are acceptable for the decision.

## 10. Self-study and independent exercise

Without looking at the code, explain the method in your own words. Include its purpose, required data, central idea, one important parameter, one failure mode and one fair evaluation method. Then use a documented dataset to create a reproducible notebook containing a precise problem statement, target and feature definitions, data-quality checks, a defensible split, a baseline, the method from this lesson, an explained evaluation result and an error analysis.

Do not remove unusual observations merely because they worsen the score. Investigate whether they are data errors, rare but valid cases or evidence of weak model performance. Record the reason for every cleaning and modelling decision.

## 11. Knowledge check: explain your reasoning

1. Explain the method to someone new to machine learning.
2. What does it learn from training examples, and what does it return for a new observation?
3. Which setting most changes its behaviour? Explain the trade-off.
4. Give an example of leakage or unfair evaluation that could inflate performance.
5. What further evidence is needed before using the model in a real decision?

A strong answer explains why, not only what. Revisit the relevant section if you cannot justify a choice in ordinary language.
