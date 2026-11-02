# Lesson 20: Randomised and Bayesian Search Concepts

## Learning outcomes

By the end of this lesson, you should be able to Use GridSearchCV to tune hyperparameters; build a search around a leakage-safe pipeline; define a suitable scoring metric and cross-validation splitter; and report the best configuration without test-set tuning.

## 1. Core explanation
Randomised search samples hyperparameter combinations from defined distributions rather than testing every point in a grid. It is useful when some parameters have wide ranges or when model training is expensive. Log-uniform distributions are often suitable for parameters spanning orders of magnitude, such as regularisation strength.

Bayesian optimisation builds a surrogate model of the relationship between settings and validation performance, then chooses promising settings to evaluate. It can use evaluations more efficiently but adds complexity and still depends on the quality of the search space and validation procedure.

Neither method can rescue a poorly framed problem or unrepresentative validation data. Define sensible bounds, set a budget, record the random seed and compare with a baseline search. Avoid spending excessive compute to chase negligible score changes.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from scipy.stats import loguniform

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42, stratify=data.target)
pipe = make_pipeline(StandardScaler(), SVC())
search = RandomizedSearchCV(pipe, {"svc__C": loguniform(1e-2, 1e2),
    "svc__gamma": loguniform(1e-4, 1e0)}, n_iter=20, cv=4,
    scoring="f1", random_state=42, n_jobs=-1)
search.fit(Xtr, ytr)
print(search.best_params_, search.best_score_)
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune a threshold, select features or choose hyperparameters.

## 4. Guided practice
Compare a 20-iteration random search with a small grid search under the same evaluation budget. Record elapsed time and performance; explain why a Bayesian search is not guaranteed to find the global best setting.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.