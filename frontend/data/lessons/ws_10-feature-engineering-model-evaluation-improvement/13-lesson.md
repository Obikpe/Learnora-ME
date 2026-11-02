# Lesson 13: Cross-Validation Design

## Learning outcomes

By the end of this lesson, you should be able to Compare K-fold, StratifiedKFold, GroupKFold and TimeSeriesSplit; select a splitter that matches the data structure; and explain what each validation score estimates.

## 1. Core explanation
Cross-validation estimates how a workflow performs across several training/validation partitions. K-fold splits data into k folds; stratified k-fold preserves class proportions; group k-fold keeps groups intact; time-series split trains on earlier observations and validates on later ones. The choice must match the dependence and time structure of the data.

Use Pipelines so every fold fits preprocessing only on that fold's training subset. When many hyperparameters and features are selected, nested cross-validation can provide a less biased estimate: inner folds select settings, outer folds estimate the full selection procedure. Nested CV is computationally expensive but important in small datasets with extensive tuning.

Fold scores vary. Report mean and spread, and inspect whether one fold is unusually difficult. Cross-validation does not correct biased sampling or poor target definitions.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

data = load_breast_cancer(as_frame=True)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
scores = cross_val_score(pipe, data.data, data.target, cv=cv, scoring="roc_auc")
print(scores, "mean", scores.mean(), "std", scores.std())
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune a threshold, select features or choose hyperparameters.

## 4. Guided practice
Choose a splitter for three scenarios: independent customer records, repeated patient records and future monthly demand. Explain why ordinary shuffled folds are not suitable for every case.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.