# Lesson 15: Gradient Boosting Concepts

## Learning outcomes

By the end of this lesson, you should be able to Explain boosting as sequential correction of model errors; fit a gradient-boosting classifier; evaluate probability ranking with ROC AUC; and identify complexity and tuning risks.


![classification concept diagram](/course-assets/ws08/classification.svg)

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
