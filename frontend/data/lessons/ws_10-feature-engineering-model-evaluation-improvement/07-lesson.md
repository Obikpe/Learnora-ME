# Lesson 7: Binning, Interactions and Polynomial Features

## Learning outcomes

By the end of this lesson, you should be able to Create bins, polynomial terms and interaction features; explain what new structure they represent; compare interpretability and complexity; and avoid data-driven binning leakage.

## 1. Core explanation
Binning converts a continuous feature into intervals. It can simplify non-linear relationships and produce interpretable groups, but loses information and depends on chosen cut points. Use domain-defined thresholds where possible; otherwise learn quantile or uniform bins from training data.

Interaction features represent the effect of one variable depending on another, such as price sensitivity varying by customer segment. Polynomial features add powers and combinations to represent curvature. These features can increase dimensionality quickly and create multicollinearity. Regularisation and validation are important.

All data-dependent cut points and transformations must be fitted inside the training pipeline. Avoid choosing bins after looking at test outcomes. Explain how the transformed feature maps back to the original variables.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas scikit-learn`.

```python
import pandas as pd
from sklearn.preprocessing import KBinsDiscretizer, PolynomialFeatures

X = pd.DataFrame({"age": [18, 22, 30, 42, 55, 68],
                  "income": [20, 25, 35, 48, 60, 75]})
binner = KBinsDiscretizer(n_bins=3, encode="ordinal", strategy="quantile")
print("Age bins:", binner.fit_transform(X[["age"]]).ravel())
poly = PolynomialFeatures(degree=2, include_bias=False)
print("Polynomial feature names:", poly.fit(X).get_feature_names_out())
```

## 3. Interpretation and safeguards
State when each feature is available, how it was derived and whether it can be calculated consistently at prediction time. Fit all learned transformations on training data only. Compare performance using the same validation design and check that transformations do not remove meaningful information.

## 4. Guided practice
Create an interaction between study hours and attendance. Explain a plausible interpretation and why the interaction should be validated against a model without it.

## 5. Independent practice
Create a small feature-engineering workflow for a dataset. Include a data dictionary, transformation rationale, pipeline and validation plan. Identify one transformation you decided not to use and explain why.

## 6. Knowledge check
1. What information does this transformation add?
2. Could it leak information from after the prediction time?
3. Does it need to be fitted on training data?
4. How will you test its value and stability?

## Lesson summary
Feature engineering should create meaningful, available and reproducible inputs. Every transformation must be justified and validated within a leakage-safe workflow.