# Lesson 10: Embedded Feature Selection

## Learning outcomes
Explain how regularisation can select features; interpret L1, L2 and Elastic Net penalties; understand tree-based importance limitations; and compare embedded selection with a baseline.

## 1. Selection during model fitting
Embedded methods select or rank features as part of estimating the model. They are often more efficient than testing every possible subset, and the selection is tied to the estimator's objective.

A common family uses regularisation: a penalty discourages overly large coefficients. This can reduce overfitting and, in some cases, shrink coefficients to exactly zero.

## 2. L1, L2 and Elastic Net
**L1 regularisation (Lasso)** adds a penalty based on the sum of absolute coefficient values. It can set some coefficients to zero, creating a sparse model. With strongly correlated features, it may select one and discard another somewhat arbitrarily.

**L2 regularisation (Ridge)** penalises the sum of squared coefficients. It generally shrinks coefficients towards zero but does not usually make them exactly zero. It can be useful when many correlated features each contribute some signal.

**Elastic Net** combines L1 and L2 penalties. It can provide sparsity while behaving more stably with groups of correlated variables.

The regularisation strength controls the trade-off. Stronger regularisation can simplify the model but may underfit. The best value must be selected using training-only validation.

## 3. Tree-based importance
Decision trees and ensembles can rank features using measures such as impurity reduction. These importances can be useful diagnostics, but they have limitations. Impurity-based importance can favour high-cardinality features and distribute importance unpredictably among correlated features. Importance does not prove causation and may not be stable across samples.

Permutation importance measures how much a chosen evaluation score changes when a feature is shuffled. It should be calculated on held-out data or validation folds, not used to repeatedly optimise against the final test set. Correlated features can mask one another because the model may rely on another correlated variable.

![Regularisation concept](/course-assets/ws10/regularisation.svg)

## 4. Worked example: L1 logistic regression
```python
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True, as_frame=True)
model = make_pipeline(
    StandardScaler(),
    LogisticRegression(
        penalty="l1",
        solver="liblinear",
        C=0.1,
        max_iter=5000
    )
)
model.fit(X, y)

coefficients = model.named_steps["logisticregression"].coef_[0]
selected = X.columns[coefficients != 0]
print("Non-zero features:", selected.tolist())
print("Count:", len(selected))
```

For this estimator, smaller C means stronger regularisation. A coefficient equal to zero indicates that the fitted L1 model does not use that feature in its linear decision function. It does not prove the variable is irrelevant in every model or population. Compare several C values through cross-validation.

## 5. A fair comparison
Compare a model without selection, an L1 model and a tree-based model using the same outer folds and metric. Examine selected-feature stability, calibration and subgroup performance as well as headline score. If a feature is retained only in one fold, its role may be unstable.

## Common mistakes
- Comparing coefficient magnitudes before scaling.
- Treating a zero coefficient as proof of no relationship.
- Assuming tree importance is unbiased.
- Selecting C using the final test set.
- Ignoring correlated predictors.
- Calling feature importance a causal explanation.

## Guided practice
Explain why L1 may choose one of two highly correlated income measures. Describe what L2 might do differently.

## Independent practice
Fit L1 logistic regression over a grid of C values. Record cross-validation performance and the number of non-zero coefficients. Identify whether the same features are selected across folds.

## Knowledge check
1. Which penalty can set coefficients exactly to zero?
2. What is the main difference between L1 and L2?
3. What does C control in scikit-learn logistic regression?
4. Why can impurity-based importance be misleading?
5. Why is selection stability worth reporting?

## Lesson summary
Embedded selection links feature choice to model fitting. Regularisation and tree importance are useful tools, but their results depend on data, model assumptions and validation design.