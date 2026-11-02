# Lesson 5: Scaling and Transforming Numerical Features

## Learning outcomes

By the end of this lesson, you should be able to Compare standard, min-max and robust scaling; inspect the influence of outliers; choose a transformation suited to the model and data; and fit scaling only on training partitions.

## 1. Core explanation
Scaling changes the numerical range of features. StandardScaler subtracts the training mean and divides by the training standard deviation. MinMaxScaler maps values to a chosen range. RobustScaler uses the median and interquartile range and can be less sensitive to outliers. Normalisation scales each row to unit norm and is common in text or vector similarity tasks.

Scaling matters for distance-based algorithms, SVMs, KNN and many gradient-based models. Tree splits generally depend on ordering and are not usually sensitive to monotonic scaling. Log transformations can reduce right skew for positive values, but require non-negative or strictly positive inputs depending on the transform.

Fit the scaler on training data only. Outliers can make standardised values extreme; investigate them rather than assuming scaling solves their effect. Explain the transformed units when interpreting coefficients.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas scikit-learn`.

```python
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

X = pd.DataFrame({"income": [20000, 25000, 30000, 35000, 500000]})
for scaler in [StandardScaler(), MinMaxScaler(), RobustScaler()]:
    print(type(scaler).__name__, scaler.fit_transform(X).ravel().round(2))
```

## 3. Interpretation and safeguards
State when each feature is available, how it was derived and whether it can be calculated consistently at prediction time. Fit all learned transformations on training data only. Compare performance using the same validation design and check that transformations do not remove meaningful information.

## 4. Guided practice
Compare the three scalers and explain how the extreme income value affects each. Choose a scaler for a distance-based model and justify your choice.

## 5. Independent practice
Create a small feature-engineering workflow for a dataset. Include a data dictionary, transformation rationale, pipeline and validation plan. Identify one transformation you decided not to use and explain why.

## 6. Knowledge check
1. What information does this transformation add?
2. Could it leak information from after the prediction time?
3. Does it need to be fitted on training data?
4. How will you test its value and stability?

## Lesson summary
Feature engineering should create meaningful, available and reproducible inputs. Every transformation must be justified and validated within a leakage-safe workflow.