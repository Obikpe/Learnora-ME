# Lesson 7: Regularisation: Ridge and Lasso

## Learning outcomes

By the end of this lesson, you should be able to Explain L1 and L2 regularisation; fit Ridge and Lasso models with scaled features; interpret how the penalty changes coefficients; and compare models using a held-out evaluation design.

## 1. Core explanation
Regularisation discourages unnecessarily large coefficients to reduce model complexity. Ridge regression adds a penalty proportional to the sum of squared coefficients (L2). It shrinks coefficients towards zero but usually does not make them exactly zero. Lasso adds the sum of absolute coefficients (L1) and can set some coefficients to zero, acting as a form of feature selection.

The regularisation strength controls the trade-off between fitting the training data and keeping coefficients small. Stronger regularisation can reduce variance but may increase bias. Feature scaling is important because the penalty otherwise treats coefficients on different units unevenly. Fit the scaler on training data inside a Pipeline.

Tune the penalty strength with cross-validation. Do not choose it by looking at the test score repeatedly. When features are highly correlated, Lasso may select one somewhat arbitrarily; Ridge often distributes weight across correlated predictors.

## 2. Worked example
Use VS Code and a project virtual environment. Install the packages used in this lesson with `python -m pip install numpy pandas matplotlib scikit-learn`.

```python
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, Lasso
from sklearn.metrics import mean_absolute_error

data = load_diabetes(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target, random_state=5)
for model in [Ridge(alpha=1.0), Lasso(alpha=0.1, max_iter=10000)]:
    pipe = make_pipeline(StandardScaler(), model).fit(Xtr, ytr)
    print(type(model).__name__, mean_absolute_error(yte, pipe.predict(Xte)))
```

## 3. Interpretation and diagnostics
Explain what each feature and target represent, the units of the output and how the model was evaluated. Inspect errors and check that all preprocessing was learned from training data only. Never infer causation from predictive coefficients without a suitable causal design.

## 4. Guided practice
Try several alpha values and record test MAE only after selecting alpha by cross-validation on the training data. Compare the coefficient magnitudes and explain the difference between L1 and L2 penalties.

## 5. Independent practice
Apply the method to a dataset of your choice. Define the prediction moment, target and feature availability. Compare with a simple baseline and report at least one metric plus an error analysis.

## 6. Knowledge check
1. What does the model estimate?
2. What assumptions or limitations matter most?
3. How could leakage or an inappropriate split inflate performance?
4. What additional analysis is needed before use?

## Lesson summary
Supervised models must be framed around a precise target and evaluated on unseen data. Model complexity and scores matter less than reliable performance for the intended decision.