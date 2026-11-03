# Lesson 19: Hyperparameter Search

## Learning outcomes
Distinguish parameters from hyperparameters; use GridSearchCV; define a meaningful search space; evaluate candidate settings without leakage; and interpret search results critically.

## 1. Parameters and hyperparameters
Model **parameters** are learned from data during fitting. In linear regression, coefficients are parameters. **Hyperparameters** are settings chosen before or around fitting, such as regularisation strength, tree depth, number of neighbours or learning rate.

Hyperparameter search evaluates candidate settings using a validation strategy. The best candidate is the one that performs best under the chosen scoring rule and folds, not necessarily the best model for every future dataset.

## 2. Grid search
GridSearchCV evaluates every combination in a specified parameter grid. It is transparent and useful when the search space is small. Its weakness is combinatorial growth: if five parameters each have ten values, there are 100,000 combinations before cross-validation.

Search spaces should be informed by the algorithm and data. Avoid enormous arbitrary grids. Use sensible ranges, a baseline and a clear scoring metric.

![Hyperparameter search process](/course-assets/ws10/hyperparameter-search.svg)

## 3. Worked example
```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
pipeline = make_pipeline(StandardScaler(), SVC())

param_grid = {
    "svc__C": [0.1, 1, 10],
    "svc__kernel": ["linear", "rbf"],
    "svc__gamma": ["scale", "auto"]
}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
search = GridSearchCV(
    pipeline, param_grid, scoring="f1",
    cv=cv, n_jobs=-1, refit=True
)
search.fit(X, y)

print("Best parameters:", search.best_params_)
print("Best CV score:", search.best_score_)
best_model = search.best_estimator_
```

The double underscore addresses a nested parameter in the pipeline. `refit=True` fits the selected configuration again on all data supplied to `fit`. In a final workflow, supply only the training partition to the search; evaluate `best_model` once on the untouched test partition.

## 4. Search results
Inspect `cv_results_` for mean and standard deviation across folds, fit time and parameter combinations. A tiny difference between two candidates may not be meaningful. Prefer a simpler, cheaper or more stable model when performance is practically equivalent.

## 5. Common mistakes
- Tuning on the final test set.
- Searching an enormous grid without a reason.
- Using a metric that does not reflect the task.
- Forgetting pipeline parameter prefixes.
- Ignoring runtime and model complexity.
- Choosing the maximum mean score without examining fold variation.

## Guided practice
Create a grid for a decision tree using max_depth, min_samples_leaf and criterion. Explain how each parameter affects complexity.

## Independent practice
Search a small hyperparameter grid for a pipeline. Save the full results table and compare the top candidates on mean score, variability and training time. Explain why the winner is a reasonable choice.

## Knowledge check
1. What is the difference between a parameter and hyperparameter?
2. What does GridSearchCV do?
3. Why can a grid become expensive?
4. What does the double underscore mean in a pipeline parameter?
5. Why inspect fold variation rather than only best_score_?

## Lesson summary
Hyperparameter search is structured model selection. Define a manageable search space, evaluate through leakage-safe cross-validation and consider stability and complexity alongside the highest score.

## 6. Deeper reasoning: search results are conditional on the experiment

A hyperparameter search does not discover the objectively best model. It identifies the best configuration among the candidates you supplied, using the metric and validation folds you selected. If the search space excludes a useful region, the best candidate may still be poor. If the metric does not represent the actual task, the search can efficiently optimise the wrong objective.

Parameter ranges should be informed by how the estimator works. Regularisation strengths and learning rates often vary across orders of magnitude, so logarithmic ranges are more sensible than a handful of evenly spaced values. Parameters can also interact: the best gamma for an SVM may depend on C. A search that changes one setting at a time can miss such interactions, while an overly broad grid can become expensive.

Inspect the full cv_results_ table rather than only best_params_. Look at mean test score, standard deviation, rank, fit time and whether several neighbouring configurations perform similarly. If many settings produce almost identical results, prefer a simpler or faster configuration. If the top result is a single isolated spike, it may be sensitive to the particular folds.

The search must be fitted on training data only. If you have a separate validation set, use it for development and reserve test data for the final estimate. For more extensive tuning on limited data, nested cross-validation can estimate the performance of the tuning procedure itself. The search result is evidence under a defined experiment, not a guarantee about future populations.