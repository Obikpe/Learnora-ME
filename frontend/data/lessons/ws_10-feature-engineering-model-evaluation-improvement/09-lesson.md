# Lesson 9: Filter and Wrapper Feature Selection

## Learning outcomes
Use variance and statistical filters appropriately; distinguish mutual information and chi-square selection; understand recursive feature elimination; and compare selection strategies without contaminating validation data.

## 1. Filter methods in more detail
Filter methods evaluate features using a score independent of the final estimator. They are usually faster than wrapper methods and can be useful as an initial screening step. Their limitation is that a feature's score is often calculated one column at a time, so interactions may be missed.

A **variance threshold** removes features with little or no variation. A constant column cannot distinguish observations. However, low variance does not automatically mean useless: a rare indicator can be highly informative in a specific problem.

**Correlation filtering** can identify highly redundant numeric features. Choose a threshold as a diagnostic, not a law. Correlation may be linear and pairwise, so it can miss non-linear or conditional relationships.

**Chi-square selection** measures dependence between non-negative features and a categorical target. It is often used for count or frequency features, and inputs must meet its non-negativity requirement.

**Mutual information** measures how much knowing a feature reduces uncertainty about the target. It can detect non-linear dependence, but estimates can be noisy with small datasets.

## 2. Wrapper methods
A wrapper evaluates a subset by fitting a model and measuring performance. Recursive Feature Elimination (RFE) repeatedly fits an estimator, ranks features and removes the least important ones until the requested number remains. RFECV adds cross-validation to estimate a suitable number of features.

Wrapper methods can be computationally expensive because many models are fitted. Their performance estimate can be optimistic if feature selection and hyperparameter tuning are not properly nested. The outer validation loop must evaluate the complete selection process.

![Filter and wrapper selection](/course-assets/ws10/filter-wrapper-selection.svg)

## 3. Worked example: RFE
```python
from sklearn.datasets import load_breast_cancer
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True, as_frame=True)

selector = RFE(
    estimator=LogisticRegression(max_iter=5000),
    n_features_to_select=10,
    step=1
)
pipeline = make_pipeline(StandardScaler(), selector)
pipeline.fit(X, y)

support = pipeline.named_steps["rfe"].get_support()
print("Selected:", X.columns[support].tolist())
print("Ranking:", pipeline.named_steps["rfe"].ranking_)
```

RFE needs an estimator that exposes feature coefficients or importance. Logistic regression supplies coefficients, but scaling is important because coefficient magnitudes depend on feature scale. The example fits the selector on all supplied data for demonstration; use a train/test split and cross-validation in a real evaluation.

## 4. Use nested evaluation when needed
If you select features and tune a model using the same cross-validation results that you report as final performance, you may overfit the validation process. Nested cross-validation uses an inner loop for selection/tuning and an outer loop to estimate the full procedure. It is more expensive, but useful when data is limited and many choices are being compared.

## 5. Common mistakes
- Applying chi-square to negative or standardised values.
- Removing every low-variance feature without considering rare-event meaning.
- Assuming RFE is cheap on thousands of columns.
- Selecting features once before cross-validation.
- Comparing methods on different folds.
- Treating selected features as causal drivers.

## Guided practice
For a text dataset represented by word counts, decide whether chi-square or mutual information may be appropriate. Explain what must be checked before applying chi-square.

## Independent practice
Compare SelectKBest with mutual information and RFECV on a classification dataset. Put selection inside the evaluation process, record runtime and selected-feature stability, and discuss the trade-off between performance and simplicity.

## Knowledge check
1. What does a variance threshold remove?
2. What type of input does chi-square selection expect?
3. What does mutual information measure?
4. How does RFE choose which feature to remove?
5. Why might nested cross-validation be required?

## Lesson summary
Filter methods provide efficient screening, while wrapper methods evaluate subsets through model fitting. Both must be embedded in a sound validation design; neither produces a universally correct feature list.

## 6. Deeper reasoning: a selector's score is not the final answer

A filter score is a screening signal. Mutual information, for example, estimates how much knowing a feature helps reduce uncertainty about the target. It does not tell you whether the feature is available at prediction time, stable across months, fair to all groups or inexpensive to maintain. A very high score may even be a warning if the feature was created after the target event.

Wrapper methods ask a more direct question: does this subset help this estimator under this scoring procedure? The cost is repeated fitting. If there are many columns, RFE can become slow because the estimator is fitted repeatedly as features are removed. RFECV adds another layer of cross-validation to choose the subset size. On large datasets, begin with a sensible filter to reduce obviously irrelevant columns, then test a wrapper on a manageable set.

The evaluation design must include the selector. Imagine five-fold cross-validation. In each fold, the selector should calculate its scores using only the four training folds, choose features and fit the model. It then transforms the held-out fold using that learned selection. This means the selected columns may differ from fold to fold. That is not an error; it reveals selection instability.

For a final model, the selection process is fitted again using the full training partition after model choices have been made. The test set is transformed by that fitted selection without influencing it. Document the final selected features, but also report how consistently they appeared during validation.