# Lesson 9: Filter and Wrapper Feature Selection

## Learning outcomes
Explain the feature-engineering method, implement it in Python and identify leakage, reproducibility and interpretation risks.

## 1. Core explanation
Filter methods score features using statistical properties before fitting a model. Examples include correlation, chi-square and ANOVA F-tests. They are fast but may miss interactions and can be sensitive to assumptions. Chi-square requires non-negative feature values; do not apply it blindly to standardised negative values.

Wrapper methods evaluate feature subsets by repeatedly training a model. Recursive Feature Elimination removes less useful features iteratively. Wrappers can capture model-specific interactions but are computationally expensive and may overfit if selection is not nested inside validation.

Use feature selection within cross-validation. If you tune the number of features and evaluate on the same folds without nesting, the score can be optimistic. Consider stability: if a feature is selected in only one of many folds, its role may be uncertain.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas scikit-learn`.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

data = load_breast_cancer(as_frame=True)
selector = RFE(LogisticRegression(max_iter=3000), n_features_to_select=8)
pipe = make_pipeline(StandardScaler(), selector)
pipe.fit(data.data, data.target)
print("Selected feature mask:", selector.support_)
```

## 3. Interpretation and safeguards
State when each feature is available, how it was derived and whether it can be calculated consistently at prediction time. Fit all learned transformations on training data only. Compare performance using the same validation design and check that transformations do not remove meaningful information.

## 4. Guided practice
Compare filter selection with RFE. Record computation time and selected variables. Explain why the selection result depends on the estimator and dataset sample.

## 5. Independent practice
Create a small feature-engineering workflow for a dataset. Include a data dictionary, transformation rationale, pipeline and validation plan. Identify one transformation you decided not to use and explain why.

## 6. Knowledge check
1. What information does this transformation add?
2. Could it leak information from after the prediction time?
3. Does it need to be fitted on training data?
4. How will you test its value and stability?

## Lesson summary
Feature engineering should create meaningful, available and reproducible inputs. Every transformation must be justified and validated within a leakage-safe workflow.