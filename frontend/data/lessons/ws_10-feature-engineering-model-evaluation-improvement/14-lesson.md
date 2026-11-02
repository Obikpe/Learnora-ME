# Lesson 14: Classification Evaluation Metrics

## Learning outcomes
Explain the technique, implement it in Python and justify the validation choices.

## 1. Core explanation
Accuracy is the proportion of correct labels. Precision is the proportion of predicted positives that are truly positive; recall is the proportion of actual positives found. Specificity measures the proportion of negatives correctly rejected. F1 is the harmonic mean of precision and recall. Balanced accuracy averages recall across classes.

Use the confusion matrix to connect metrics to errors. In fraud screening, false negatives are missed fraud and false positives are legitimate transactions flagged for review. In medical screening, the cost of missed cases may be high. No metric is universally best; choose based on the decision and report the threshold.

For multiclass problems, inspect per-class scores and macro/weighted averages. Accuracy can hide poor performance on rare classes. Include class support so readers understand how many observations underlie each score.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, balanced_accuracy_score

actual = [0, 0, 0, 0, 1, 1, 1, 1]
pred =   [0, 0, 1, 0, 1, 0, 1, 1]
print(confusion_matrix(actual, pred))
print("Precision", precision_score(actual, pred))
print("Recall", recall_score(actual, pred))
print("F1", f1_score(actual, pred))
print("Balanced accuracy", balanced_accuracy_score(actual, pred))
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune a threshold, select features or choose hyperparameters.

## 4. Guided practice
Explain which errors the model made. Recommend a metric for a low-cost fraud review queue and another for an automated action with serious consequences.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.