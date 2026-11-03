# Lesson 8: Feature Selection Fundamentals

## Learning outcomes
Explain why feature selection is used; distinguish selection from extraction; identify redundancy and irrelevant inputs; and describe how selection can affect performance, cost and interpretability.

## 1. What feature selection does
Feature selection chooses a subset of the original input variables. It does not create a new representation; it decides which existing columns should be retained. This differs from dimensionality reduction, which transforms original variables into new components.

A dataset may contain hundreds of columns. Some are irrelevant, some repeat information, some are unreliable and some may only be available after the prediction moment. Removing unsuitable variables can reduce noise, simplify the model, lower data-collection cost and make explanations easier.

More features are not always better. Irrelevant variables can make distance calculations less meaningful, increase variance and create more opportunities for leakage or data-quality problems. However, removing a useful feature can also reduce predictive power. Selection is an empirical and domain-informed decision.

## 2. Three broad families
**Filter methods** score features using statistical properties before fitting a particular model. Examples include correlation, mutual information and chi-square tests. They are often fast but may miss combinations that matter only jointly.

**Wrapper methods** evaluate subsets by repeatedly training a model. Recursive Feature Elimination is an example. They can capture model-specific usefulness but may be computationally expensive and prone to overfitting if selection is not nested within validation.

**Embedded methods** perform selection during model fitting. L1-regularised linear models can shrink some coefficients to zero; tree-based models can provide importance measures. These depend on model assumptions and are not universal measures of feature value.

## 3. Correlation is not a complete selector
Two features can be highly correlated and carry overlapping information. Removing one may simplify a model. But low pairwise correlation with the target does not prove a feature is useless: it may have a non-linear or interaction effect. Correlation also does not imply causation.

Feature selection should be performed using training data only. If you use the target to calculate scores, the selection step must be repeated inside each training fold. Selecting once on the full dataset leaks information from validation and test targets.

![Feature selection families](/course-assets/ws10/feature-selection.svg)

## 4. Worked example: a filter method
```python
import pandas as pd
from sklearn.feature_selection import SelectKBest, mutual_info_classif

data = pd.DataFrame({
    "age": [22, 25, 31, 35, 42, 48, 55, 61, 29, 51],
    "visits": [1, 2, 3, 5, 4, 7, 8, 9, 2, 6],
    "noise": [8, 1, 7, 2, 9, 3, 6, 4, 5, 10],
    "renewed": [0, 0, 0, 1, 0, 1, 1, 1, 0, 1]
})
X = data.drop(columns="renewed")
y = data["renewed"]

selector = SelectKBest(
    score_func=mutual_info_classif,
    k=2
)
selected = selector.fit_transform(X, y)
print("Selected columns:", X.columns[selector.get_support()].tolist())
print("Scores:", selector.scores_)
```

This small example illustrates the API only. In a real workflow, put the selector inside a pipeline and evaluate it with cross-validation. Mutual information can detect some non-linear dependence, but its estimate depends on sample size and settings. A high score is association, not proof of causation.

## 5. Selection and the modelling objective
A feature may improve a score but be expensive to collect, sensitive, unstable or unavailable for some users. A production decision should consider predictive performance, latency, cost, fairness, privacy, reliability and explainability. Keep a record of selected features and why they were retained.

## Common mistakes
- Selecting features on the full dataset before splitting.
- Treating correlation as proof of usefulness or uselessness.
- Assuming feature importance is causal.
- Keeping only the top-ranked features without testing interactions.
- Ignoring data collection cost and availability.
- Reporting selection results from one split as universal truth.

## Guided practice
A churn dataset contains account age, total logins, last login date, customer ID, support tickets, cancellation date and monthly fee. Identify features that may be useful, redundant, identifier-like or leakage-prone.

## Independent practice
Create a baseline model, then compare it with a model using a filter selector inside a pipeline. Use identical cross-validation folds. Report the selected features and the stability of selection across folds.

## Knowledge check
1. How does feature selection differ from dimensionality reduction?
2. What is the main advantage of a filter method?
3. Why can a low correlation score be misleading?
4. Why must target-informed selection be inside cross-validation?
5. Name two non-accuracy considerations when selecting features.

## Lesson summary
Feature selection can reduce noise and complexity, but its value depends on the model, data and deployment context. Selection is part of model fitting and must be validated without exposing held-out targets.

## 7. Deeper reasoning: selection is part of the learning process

Feature selection is often described as a preparation step, but when it uses data values or the target to decide which columns survive, it is learning from the sample. This means it belongs inside the model evaluation procedure. If you calculate feature-target associations using every row, select the top ten columns and only then split the data, information from the future test labels has influenced the selected feature set. The model has indirectly seen part of the test answer.

Selection also depends on the estimator and the intended use. A feature that helps a tree model may not help a linear model in the same way. A variable that is weak by itself may become useful when combined with another feature. Conversely, two highly predictive variables may be redundant. Therefore, selection should be judged by the complete pipeline's held-out performance and stability, not by a score table alone.

There is also a difference between predictive selection and governance-based exclusion. Some variables may be prohibited or inappropriate because of privacy, fairness, legal or operational requirements even if they improve prediction. Other variables may be too costly to collect at scale. These constraints should be considered before searching for the numerically best subset.

When reporting selected features, describe the selection method and its stability. If a feature is selected in every fold, that is stronger evidence of consistency than if it appears in only one fold. It is still not proof that the feature causes the outcome. Selection identifies useful information for a particular model and dataset under a particular validation design.