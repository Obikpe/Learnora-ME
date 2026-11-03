# Lesson 11: Confusion Matrix and Classification Metrics

## Learning outcomes

By the end of this lesson, you should be able to Read a confusion matrix; calculate accuracy, precision, recall, specificity and F1; explain false positives and false negatives; and select metrics based on error consequences.

## 1. Core explanation
A confusion matrix compares predicted classes with actual classes. For binary classification, true positives (TP) and true negatives (TN) are correct; false positives (FP) are incorrect positive predictions; false negatives (FN) are missed positives. Precision = TP/(TP+FP); recall or sensitivity = TP/(TP+FN); specificity = TN/(TN+FP); F1 is the harmonic mean of precision and recall.

Accuracy counts all correct predictions and can be misleading when classes are imbalanced. If only 1% of transactions are fraudulent, a model that predicts “not fraud” every time achieves 99% accuracy but detects no fraud. Always connect the metric to the consequences of each error.

The confusion matrix depends on the chosen threshold. Report the threshold and positive-class definition. For multiclass tasks, inspect per-class precision and recall, macro averages and weighted averages. A weighted average can hide poor performance on a rare class.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may need internet access on first use.

```python
from sklearn.metrics import confusion_matrix, classification_report
y_true = [0, 0, 0, 1, 1, 1, 1, 0]
y_pred = [0, 1, 0, 1, 0, 1, 1, 0]
print(confusion_matrix(y_true, y_pred))
print(classification_report(y_true, y_pred, zero_division=0))
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report the limitations of the dataset.

## 4. Guided practice
Create a confusion matrix for a fraud-screening scenario. Identify which cell represents a fraudulent transaction the model failed to flag. Explain why accuracy alone is insufficient when fraud is rare.

## 5. Independent practice
Extend the example with a second model or a different evaluation view. Keep a record of every change and compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder.

## 6. Knowledge check
1. What does this method optimise or estimate?
2. Which assumptions or settings affect its behaviour?
3. How would you detect overfitting or leakage?
4. What evidence is needed before the model is used?

## Lesson summary
Supervised learning is a complete evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.

## 7. Understand the model before using it

A machine-learning algorithm is a procedure for finding a useful pattern in examples. It does not understand the real-world meaning of a row. That meaning comes from the way the analyst defines the observation, target, features and prediction time. Begin by describing these in plain language. Then explain what the algorithm changes during training and what it produces for an unseen observation.

Interpret every output in context. A probability is not a guarantee; a coefficient is not automatically a causal effect; a feature-importance score is not proof that changing the feature will change the target. Evaluation metrics summarise selected aspects of performance and can hide important errors. Translate them into practical consequences.

## 8. A disciplined modelling workflow

Inspect the target and feature columns before fitting. Check data types, missing values, duplicated observations, unusual values and class balance. Decide how the data should be split based on how the model will be used. Random splitting is not always appropriate: future forecasting usually requires time-ordered evaluation, while repeated observations from the same person may require group-aware splitting.

Fit preprocessing steps on training data only. Keep transformations and estimators together in a pipeline so the same operations are applied consistently at prediction time. Establish a simple baseline, train a candidate, select settings using validation or cross-validation, and reserve the test set for final evaluation. Record package versions, random seeds, feature definitions and modelling choices.

## 9. Worked reasoning example

Suppose an analyst is predicting late repayment. One row represents an account at the end of a billing period, and the target indicates whether repayment becomes more than 30 days late in the next period. Current balance and previous repayment behaviour may be available; the actual next-period payment is not. Including that future payment would leak the answer. A model must be evaluated on accounts and time periods that reflect its intended use. Its errors should then be reviewed in terms of the operational cost of unnecessary alerts and missed late payments.

## 10. Self-study and independent practice

Explain the technique from memory, including its purpose, the information it requires, its central learning mechanism, an important setting, a likely failure mode and a suitable evaluation approach. Then apply it to a documented dataset. Include a clear problem statement, data-quality checks, a defensible split, baseline comparison, explained metrics, error inspection and limitations. Record why each preprocessing decision was made; do not delete difficult observations merely to improve the score.

## 11. Knowledge check

1. What does the technique learn, and what does it output?
2. Which assumptions or parameter choices matter most?
3. What would constitute leakage in this problem?
4. How would you know whether the model generalises?
5. What additional evidence is needed before using the result to support a real decision?

Explain your reasoning in complete sentences. If you cannot justify a modelling choice in ordinary language, revisit the lesson before moving on.
