# Lesson 10: Embedded Feature Selection

## Learning outcomes

By the end of this lesson, you should be able to Explain Lasso as an embedded sparse-selection method; fit coefficients with scaled features; count non-zero coefficients; and explain why selected features are not automatically causal or universally important.

## 1. Core explanation
Embedded methods perform selection as part of model fitting. Lasso can shrink some coefficients exactly to zero. Tree-based models can rank variables by split contribution, although impurity importance has known biases. Elastic Net combines L1 and L2 penalties and can be more stable when predictors are correlated.

Embedded selection is model-dependent. A feature not selected by a linear model may still matter to a tree or neural network. Correlated features may substitute for one another. Do not interpret a zero coefficient as proof that a variable has no real-world relationship with the outcome.

Tune regularisation or model settings using cross-validation and report selection stability. Keep all selection inside the training workflow. If the purpose is causal explanation rather than prediction, predictive feature selection is not a causal variable-selection strategy.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas scikit-learn`.

```python
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

data = load_diabetes(as_frame=True)
pipe = make_pipeline(StandardScaler(), Lasso(alpha=.08, max_iter=20000))
pipe.fit(data.data, data.target)
coef = pipe.named_steps["lasso"].coef_
print("Non-zero coefficients:", (coef != 0).sum(), "of", len(coef))
print(list(zip(data.feature_names, coef.round(3))))
```

## 3. Interpretation and safeguards
State when each feature is available, how it was derived and whether it can be calculated consistently at prediction time. Fit all learned transformations on training data only. Compare performance using the same validation design and check that transformations do not remove meaningful information.

## 4. Guided practice
Change alpha and observe how the number of non-zero coefficients changes. Explain the trade-off between sparsity, predictive performance and stability.

## 5. Independent practice
Create a small feature-engineering workflow for a dataset. Include a data dictionary, transformation rationale, pipeline and validation plan. Identify one transformation you decided not to use and explain why.

## 6. Knowledge check
1. What information does this transformation add?
2. Could it leak information from after the prediction time?
3. Does it need to be fitted on training data?
4. How will you test its value and stability?

## Lesson summary
Feature engineering should create meaningful, available and reproducible inputs. Every transformation must be justified and validated within a leakage-safe workflow.