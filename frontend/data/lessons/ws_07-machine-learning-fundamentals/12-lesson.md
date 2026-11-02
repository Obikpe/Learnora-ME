# Lesson 12: Loss Functions and Learning

## Learning outcomes

By the end of this lesson, you should be able to Explain a loss function as a measure of prediction error; calculate MAE and MSE for regression; interpret log loss for probabilistic classification; and explain how the choice changes what errors are penalised.

## 1. Concepts and reasoning
A loss function turns prediction errors into a numerical quantity that a training algorithm can minimise. For regression, mean squared error (MSE) squares residuals, penalising large errors strongly. Mean absolute error (MAE) uses absolute residuals and is less sensitive to extremes. For classification, log loss penalises confident incorrect probabilities.

Training algorithms search for parameters that reduce loss. The chosen loss expresses what the algorithm is optimising, not necessarily what the business values. A model trained with MSE may be judged by a business that cares about absolute error or the cost of underprediction. Evaluation metrics should therefore be selected with the decision context in mind.

A lower training loss does not guarantee better performance on new data. Compare training and validation loss. A widening gap can indicate overfitting. Loss values are meaningful only in context: compare models using the same target, split and metric.

## 2. Worked example
Run in VS Code in your course virtual environment. Install packages as required: `python -m pip install numpy pandas scikit-learn matplotlib`.

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, log_loss

actual = np.array([10, 12, 15, 20])
predicted = np.array([11, 10, 17, 28])
print("MAE:", mean_absolute_error(actual, predicted))
print("MSE:", mean_squared_error(actual, predicted))

y_true = [0, 1, 1]
probabilities = [[0.8, 0.2], [0.3, 0.7], [0.6, 0.4]]
print("Log loss:", log_loss(y_true, probabilities))
```

## 3. Interpretation
State what was learned from training data and what was measured on unseen data. Check whether the metric answers the real decision question. A technically correct output can still be misleading if the target, split or population is wrong.

## 4. Guided practice
Change the final regression prediction from 28 to 40. Compare how MAE and MSE change. Explain which metric penalises the extreme error more and whether that is desirable for your chosen application.

## 5. Independent practice
Apply the lesson to a small dataset. Record the source, unit of observation, target and feature availability. Save your code and a short report that includes evidence, limitations and the next validation step.

## 6. Knowledge check
1. What assumption is most important in this method?
2. What is the difference between training performance and generalisation?
3. How could leakage or sampling bias affect the result?
4. What would you tell a stakeholder before they use the model?

## Lesson summary
A trustworthy ML workflow is reproducible, uses a suitable baseline and evaluation design, and communicates errors and limitations as carefully as headline performance.