# Lesson 20: Randomised and Bayesian Search Concepts

## Learning outcomes
Explain why random search can outperform a coarse grid; implement RandomizedSearchCV; understand Bayesian optimisation conceptually; and choose a search method based on cost and available evidence.

## 1. Why search strategy matters
Grid search tests every combination in a fixed list. If only a few hyperparameters strongly influence performance, a grid may waste many evaluations on unimportant dimensions. Random search samples combinations from defined distributions and can explore more distinct values with a fixed budget.

Random search is not guaranteed to find the global optimum. Its strength is efficient exploration when the search space is broad and the evaluation budget is limited.

## 2. Bayesian optimisation
Bayesian optimisation builds a probabilistic model of how hyperparameter settings relate to validation performance. It uses previous evaluations to decide which setting to test next, balancing exploration of uncertain regions with exploitation of promising regions.

The process is sequential: evaluate a candidate, update the surrogate model, then choose another candidate. It can be useful when each model evaluation is expensive. It adds complexity and requires care with noisy validation estimates.

![Randomised search process](/course-assets/ws10/hyperparameter-search.svg)

## 3. Worked example: random search
```python
from scipy.stats import loguniform, randint
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
pipeline = make_pipeline(StandardScaler(), SVC())
distributions = {
    "svc__C": loguniform(1e-2, 1e2),
    "svc__gamma": loguniform(1e-4, 1e0),
    "svc__kernel": ["rbf"]
}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
search = RandomizedSearchCV(
    pipeline, distributions, n_iter=25,
    scoring="roc_auc", cv=cv, random_state=42,
    n_jobs=-1, refit=True
)
search.fit(X, y)
print(search.best_params_)
print(search.best_score_)
```

A log-uniform distribution samples across orders of magnitude, which is often sensible for parameters such as C and gamma. `n_iter` controls the number of sampled configurations. The search still needs an untouched final test set.

## 4. Practical search budgets
Decide how many evaluations are affordable. Start with broad ranges and a baseline. Inspect whether good values are near the boundary; if so, expand or shift the range. Avoid spending computation on parameters that do not affect the chosen estimator. Fix random seeds for reproducibility where supported, but remember that one seed does not reveal all variability.

## 5. Common mistakes
- Sampling parameters on a linear scale when orders of magnitude matter.
- Setting an enormous n_iter without estimating runtime.
- Treating Bayesian optimisation as guaranteed to find the global optimum.
- Comparing search results from different folds.
- Repeatedly tuning based on the test set.
- Ignoring noisy scores and model training failures.

## Guided practice
A model has regularisation values ranging from 0.001 to 1000. Explain why a log scale is more informative than trying only evenly spaced linear values.

## Independent practice
Compare a small GridSearchCV with RandomizedSearchCV under the same cross-validation design and a similar evaluation budget. Compare score, runtime and the diversity of settings explored.

## Knowledge check
1. How does random search differ from grid search?
2. When is log-uniform sampling useful?
3. What does Bayesian optimisation learn from previous evaluations?
4. Why does a fixed evaluation budget matter?
5. Why is search performance still an estimate rather than a guarantee?

## Lesson summary
Randomised and Bayesian methods can explore broad search spaces more efficiently than exhaustive grids. Their value depends on sensible distributions, evaluation budgets and reliable validation.

## 6. Deeper reasoning: the search budget is part of the method

Grid search, random search and Bayesian optimisation spend evaluation effort differently. A grid is predictable and easy to audit, but its candidates are fixed before results are known. Random search samples settings from a distribution and can explore a wider variety of values when only a limited number of trials are affordable. Bayesian optimisation uses earlier outcomes to guide later evaluations, which can be attractive when each fit is expensive.

The search space should reflect parameter meaning. A parameter such as regularisation strength may work across several orders of magnitude, so a log-uniform distribution is often more useful than uniform sampling between 0 and 100. A parameter such as maximum tree depth may be discrete and bounded. Some parameters are conditional: gamma matters for an RBF SVM but not for a linear kernel. Avoid searching combinations that the estimator will ignore.

Random search is stochastic. A different random seed can sample different configurations. If the best result is unstable, run a second search or examine whether the top region is broad enough to be credible. Do not repeatedly search until a lucky score appears and then report only that run. Record the number of trials, distributions, seed and validation method.

Bayesian optimisation also depends on a surrogate model and acquisition strategy. It can be efficient, but noisy cross-validation scores may mislead the search process. A more sophisticated search method does not compensate for a poor metric, leakage or an unrepresentative split. The most important resource is not the number of tools used; it is the quality of the experiment design.