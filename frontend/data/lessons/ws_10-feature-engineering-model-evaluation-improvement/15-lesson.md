# Lesson 15: Precision-Recall and ROC Analysis

## Learning outcomes

By the end of this lesson, you should be able to Calculate precision, recall, F1, specificity and balanced accuracy; interpret a confusion matrix; and choose classification metrics based on class balance and error costs.

## 1. Core explanation
A ROC curve plots true-positive rate against false-positive rate across thresholds. ROC-AUC measures ranking ability across thresholds. A precision-recall curve plots precision against recall and is often more informative for rare positive classes. The baseline precision in a PR curve is related to positive-class prevalence.

ROC-AUC can look strong even when precision is poor in a highly imbalanced problem. Always inspect the confusion matrix and precision at the operating threshold. The threshold should be chosen using validation data and operational constraints.

Curves summarise ranking, not calibration or decision cost. If a model will trigger a limited number of investigations, consider precision among the top k alerts. If the goal is screening, examine recall at a tolerable false-positive rate.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import RocCurveDisplay, PrecisionRecallDisplay, roc_auc_score, average_precision_score
import matplotlib.pyplot as plt

X, y = make_classification(n_samples=2500, weights=[.96, .04],
                           random_state=8)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=8)
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
p = model.predict_proba(Xte)[:, 1]
print("ROC AUC", roc_auc_score(yte, p), "Average precision", average_precision_score(yte, p))
RocCurveDisplay.from_predictions(yte, p)
plt.show()
PrecisionRecallDisplay.from_predictions(yte, p)
plt.show()
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune a threshold, select features or choose hyperparameters.

## 4. Guided practice
Compare the two curves and explain why average precision should be interpreted relative to class prevalence. Identify a threshold for a specified recall requirement using validation data.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.