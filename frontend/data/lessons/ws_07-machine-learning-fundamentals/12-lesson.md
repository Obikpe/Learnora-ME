# Lesson 12: Loss Functions and Learning

## Learning outcomes
Explain loss and objective functions; calculate MAE, MSE and log loss; distinguish loss from evaluation metrics; understand residuals and probability penalties; and explain why the chosen loss shapes model behaviour.

![Loss function comparison](/course-assets/ws07/12-loss-functions.svg)

## 1. What is a loss function?
A model produces predictions. A loss function measures how undesirable those predictions are compared with known outcomes. Training algorithms adjust model parameters to reduce a chosen objective.

The loss function is the mathematical definition of what the training process is trying to improve. It is not automatically the same as the business goal. A delivery company may care more about late deliveries than early ones, while ordinary squared error treats positive and negative errors symmetrically.

## 2. Regression residuals
A residual is actual value minus predicted value:
\[
e_i=y_i-\hat y_i
\]
A positive residual means the model underpredicted; a negative residual means it overpredicted. Residual analysis helps identify systematic patterns, such as errors that grow with the target value.

## 3. Mean absolute error
\[
MAE=\frac{1}{n}\sum_{i=1}^{n}|y_i-\hat y_i|
\]
MAE averages absolute errors. It is expressed in the same unit as the target and is relatively less sensitive to a very large error than squared error.

## 4. Mean squared error and root mean squared error
\[
MSE=\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat y_i)^2
\]
MSE squares each error, so large errors receive much greater penalty. RMSE is the square root of MSE and returns to the target's unit. RMSE can be useful when large errors are especially costly, but it can be strongly affected by outliers.

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

actual = np.array([10, 12, 15, 20])
predicted = np.array([11, 10, 17, 28])
mae = mean_absolute_error(actual, predicted)
mse = mean_squared_error(actual, predicted)
rmse = np.sqrt(mse)
print("MAE:", mae)
print("MSE:", mse)
print("RMSE:", rmse)
```

For these predictions, residual magnitudes are 1, 2, 2 and 8. MAE is 3.25. MSE is 18.25 and RMSE is approximately 4.27. The largest miss has a strong influence on MSE.

## 5. Log loss for classification
Many classifiers produce probability estimates. Log loss penalises the probability assigned to the true class. A confident correct prediction receives a small penalty; a confident incorrect prediction receives a large penalty.

For binary classification:
\[
L=-[y\log(p)+(1-y)\log(1-p)]
\]
where y is 0 or 1 and p is the predicted probability of class 1. The expression is averaged across observations for mean log loss. Implementations clip probabilities to avoid taking the logarithm of zero.

```python
from sklearn.metrics import log_loss

y_true = [0, 1, 1]
probabilities = [0.10, 0.80, 0.40]
print("Log loss:", log_loss(y_true, probabilities))
```

The third example is an actual positive case assigned probability 0.40, so it receives a penalty. If the model assigned 0.99 to that positive case, its penalty would be much smaller.

## 6. Loss versus metric
A training loss is what an optimisation process minimises. An evaluation metric is how we assess model performance for a task. They may be the same, but they do not have to be. A classifier may be trained using log loss and evaluated using recall, precision, F1 or another measure.

Accuracy measures the proportion of correct class predictions after applying a decision rule. It does not evaluate the quality of probability estimates. Log loss evaluates predicted probabilities and therefore responds to confidence.

## 7. Choosing a loss responsibly
Ask:
- Which errors are costly?
- Are large errors disproportionately harmful?
- Is overprediction worse than underprediction?
- Do we need accurate probabilities or only a ranking?
- Is the target noisy or affected by extreme observations?
- Does the training objective align with the intended decision?

No loss function can compensate for a poorly defined target or unrepresentative data.

## 8. Common mistakes
- Assuming MAE and MSE mean the same thing.
- Forgetting RMSE is in the target's original unit.
- Treating accuracy as a probability-quality measure.
- Comparing losses on different target scales or datasets.
- Assuming lower training loss guarantees lower test error.

## Guided practice
Change the final predicted value from 28 to 40. Recalculate MAE, MSE and RMSE. Explain which measure reacts most strongly to the extreme miss.

## Independent practice
Choose a regression and a classification dataset. Calculate at least two suitable metrics for each. Explain what a model could optimise and what a stakeholder should see in the final evaluation.

## Knowledge check
1. What is a residual?
2. Why does MSE penalise large errors more?
3. What does log loss measure?
4. How does a loss differ from an evaluation metric?
5. Why might the business objective not match the default training loss?

## Lesson summary
A loss function defines what the learning algorithm tries to minimise. Choosing it thoughtfully helps align model training with the task, but evaluation must still examine real-world consequences.