# Lesson 11: Confusion Matrix and Classification Metrics

## Learning outcomes
Explain the technique, implement the worked example, interpret the output and justify when the method is suitable.

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