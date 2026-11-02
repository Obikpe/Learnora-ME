# Lesson 6: Polynomial Regression and Non-Linearity

## Learning outcomes

By the end of this lesson, you should be able to Create polynomial features to represent a curved relationship; compare polynomial degrees; explain the risk of excessive complexity; and evaluate generalisation rather than judging only the fitted training curve.

## 1. Core explanation
A straight line cannot represent every relationship. Polynomial regression adds powers of a feature, such as x squared or x cubed, allowing a curved fitted function while remaining linear in the coefficients. The model can represent curvature, but higher degrees increase flexibility and risk overfitting.

Create polynomial features inside a Pipeline so the transformation is fitted within each training fold. Scale polynomial features when useful, particularly when powers create very different magnitudes. Compare degrees using validation or cross-validation, not training error alone. Plot predictions only across a sensible feature range.

Polynomial regression is not a universal cure for non-linearity. Inspect residual patterns and consider domain-informed transformations or other models. Avoid extrapolating a high-degree polynomial: its behaviour outside the training range can become extreme.

## 2. Worked example
Use VS Code and a project virtual environment. Install the packages used in this lesson with `python -m pip install numpy pandas matplotlib scikit-learn`.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import LinearRegression

x = np.linspace(0, 6, 80).reshape(-1, 1)
y = 2 + 1.5*x.ravel() + 0.8*x.ravel()**2 + np.random.default_rng(4).normal(0, 2, 80)
for degree in [1, 2, 5]:
    model = make_pipeline(PolynomialFeatures(degree), StandardScaler(),
                          LinearRegression()).fit(x, y)
    plt.plot(x, model.predict(x), label=f"Degree {degree}")
plt.scatter(x, y, s=15, alpha=.5)
plt.legend(); plt.xlabel("x"); plt.ylabel("y"); plt.show()
```

## 3. Interpretation and diagnostics
Explain what each feature and target represent, the units of the output and how the model was evaluated. Inspect errors and check that all preprocessing was learned from training data only. Never infer causation from predictive coefficients without a suitable causal design.

## 4. Guided practice
Compare degrees 1, 2 and 5. Describe which captures curvature and which may follow noise. Use cross-validation to compare them and explain why a higher training fit is not sufficient.

## 5. Independent practice
Apply the method to a dataset of your choice. Define the prediction moment, target and feature availability. Compare with a simple baseline and report at least one metric plus an error analysis.

## 6. Knowledge check
1. What does the model estimate?
2. What assumptions or limitations matter most?
3. How could leakage or an inappropriate split inflate performance?
4. What additional analysis is needed before use?

## Lesson summary
Supervised models must be framed around a precise target and evaluated on unseen data. Model complexity and scores matter less than reliable performance for the intended decision.