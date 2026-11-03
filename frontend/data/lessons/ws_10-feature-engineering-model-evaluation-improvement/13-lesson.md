# Lesson 13: Cross-Validation Design

## Learning outcomes
Explain k-fold cross-validation; implement stratified and group-aware folds; understand time-series validation; interpret fold variation; and identify when nested validation is useful.

## 1. Why cross-validation?
A single train/test split can produce a result that depends heavily on which observations happened to be selected. **K-fold cross-validation** divides the training data into k parts. Each fold is used once as validation while the remaining folds are used for fitting. The scores are then summarised.

For five-fold cross-validation, the process fits five models. Each model trains on approximately four-fifths of the data and validates on the remaining fifth. Every observation is used for validation once. This provides a more informative view than one arbitrary split, though folds are not independent experiments.

## 2. Select the right splitter
- KFold: general folds without class stratification.
- StratifiedKFold: approximately preserves class proportions.
- GroupKFold: keeps groups together.
- StratifiedGroupKFold: attempts to preserve class proportions while keeping groups intact.
- TimeSeriesSplit: uses earlier observations to validate on later observations.

The splitter must reflect the data structure. Do not choose StratifiedKFold just because it is common if your problem involves future periods or repeated entities.

![Cross-validation folds](/course-assets/ws10/cross-validation.svg)

## 3. Worked example
```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import (
    StratifiedKFold, cross_validate
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import numpy as np

X, y = load_breast_cancer(return_X_y=True)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
model = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=3000)
)

results = cross_validate(
    model, X, y, cv=cv,
    scoring=["accuracy", "precision", "recall", "f1"],
    return_train_score=True
)
for metric in ["test_accuracy", "test_precision", "test_recall", "test_f1"]:
    values = results[metric]
    print(metric, "mean=", round(values.mean(), 3),
          "std=", round(values.std(), 3))
```

The pipeline ensures that scaling is fitted separately within each training fold. The standard deviation describes variation across folds, not a formal confidence interval. Precision and recall depend on the positive class definition, so document which class is treated as positive.

## 4. Nested cross-validation
When the same cross-validation results are used to choose among many hyperparameters and to report the final score, the reported result can be optimistic. Nested CV uses an inner loop for model selection and an outer loop for evaluation. It estimates the performance of the selection procedure rather than a single fixed configuration.

Nested CV costs more computation. It is most useful when data is limited and substantial tuning or feature selection is being performed. A separate untouched test set is another way to obtain a final evaluation.

## 5. Fold variation and uncertainty
Report individual fold scores as well as mean and standard deviation. Large variation may indicate a small dataset, unstable model, rare classes, distribution differences or leakage through groups. Do not interpret the standard deviation across folds as though each fold were an independent random sample.

## 6. Common mistakes
- Using ordinary KFold on imbalanced classification without considering stratification.
- Allowing groups to cross folds.
- Shuffling time-series data.
- Fitting preprocessing before cross-validation.
- Reporting only the best fold.
- Treating fold standard deviation as a universal confidence interval.

## Guided practice
Choose a cross-validation splitter for customer churn, hospital readmission, image classification and daily demand forecasting. Explain why each choice matches or fails the data structure.

## Independent practice
Compare five-fold StratifiedKFold with GroupKFold on a dataset containing repeated customers. Measure whether the estimated performance changes and explain which result answers the intended deployment question.

## Knowledge check
1. How does k-fold CV work?
2. What does StratifiedKFold preserve?
3. Why is GroupKFold different?
4. What is the purpose of nested CV?
5. What might high fold-to-fold variation indicate?

## Lesson summary
Cross-validation estimates how a workflow behaves across different partitions. Its value depends on selecting folds that respect class balance, groups and time, and on fitting every learned step within each fold.

## 6. Deeper reasoning: validation estimates the whole workflow

The object being evaluated is not only the estimator. It is the complete procedure: feature preparation, imputation, encoding, scaling, selection, hyperparameter choice and fitting. If any of these steps learn from held-out observations, the cross-validation score no longer represents a clean evaluation of the procedure.

This is why pipelines are important, but also why the splitter matters. StratifiedKFold is suitable for many independent classification rows because it aims to preserve class proportions. It is not appropriate for every dataset. If one person contributes repeated observations, GroupKFold may be needed. If the target concerns future dates, TimeSeriesSplit may be more appropriate. A model can have excellent stratified scores and still fail on future data if the data-generating process changes over time.

The number of folds is a trade-off. More folds mean each model trains on a larger proportion of the available data, but they also increase computation. With very small datasets, each validation fold may contain too few positive cases to estimate precision or recall reliably. In that situation, report the class counts and interpret fold variation cautiously.

A common misconception is that the average cross-validation score is the exact expected score in production. It is an estimate under the assumptions of the split and sample. If production data differs in geography, time, collection process or user population, the estimate may not transfer. Validation design should be described as part of the result, not hidden in a footnote.