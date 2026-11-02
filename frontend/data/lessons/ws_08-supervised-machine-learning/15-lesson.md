# Lesson 15: Gradient Boosting Concepts

## Learning outcomes
Explain the technique, implement the worked example, interpret the output and justify when the method is suitable.

## 1. Core explanation
Boosting builds a sequence of weak learners, each focusing on errors made by the current ensemble. Gradient boosting adds trees that follow the negative gradient of a chosen loss. Learning rate controls the contribution of each new tree; the number and depth of trees control model complexity.

Boosting can achieve strong predictive performance on tabular data but requires careful tuning. A low learning rate often needs more trees. Deep trees and too many estimators can overfit. Early stopping uses validation performance to stop adding learners when improvement stalls. Do not use the final test set for early stopping.

Gradient boosting implementations differ in handling missing values, categorical features and regularisation. Start with a simple baseline and inspect validation metrics. A small score gain may not justify longer training, less transparency or increased operational complexity.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may need internet access on first use.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42, stratify=data.target)
model = HistGradientBoostingClassifier(max_iter=150, learning_rate=.08,
                                       max_leaf_nodes=15, random_state=42)
model.fit(Xtr, ytr)
print("Test ROC AUC:", roc_auc_score(yte, model.predict_proba(Xte)[:, 1]))
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report the limitations of the dataset.

## 4. Guided practice
Compare two learning rates while holding other parameters fixed. Record validation performance and training time. Explain why changing several parameters at once makes it hard to identify what caused an improvement.

## 5. Independent practice
Extend the example with a second model or a different evaluation view. Keep a record of every change and compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder.

## 6. Knowledge check
1. What does this method optimise or estimate?
2. Which assumptions or settings affect its behaviour?
3. How would you detect overfitting or leakage?
4. What evidence is needed before the model is used?

## Lesson summary
Supervised learning is a complete evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.