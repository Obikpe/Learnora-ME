# Lesson 3: Missing-Value Strategies

## Learning outcomes
Explain the feature-engineering method, implement it in Python and identify leakage, reproducibility and interpretation risks.

## 1. Core explanation
Missing data can arise because a value was not measured, was not applicable, was refused or was lost. These mechanisms have different implications. Before imputation, quantify missingness by field, group and time. Ask whether missingness itself contains information and whether it may be related to the target.

Simple strategies include median imputation for skewed numeric data and most-frequent imputation for categorical fields. A missingness indicator can preserve information that a value was absent. More advanced methods include iterative imputation, but complexity does not guarantee less bias. Never replace all missing values with zero unless zero is the true meaning.

Fit imputation using training data only. For a model evaluation, place the imputer in a Pipeline so each fold learns from its own training subset. Report how much data was missing and perform sensitivity checks when missingness is substantial.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas scikit-learn`.

```python
import pandas as pd
from sklearn.impute import SimpleImputer, MissingIndicator

X = pd.DataFrame({"income": [25000, None, 42000, 50000, None],
                  "age": [22, 31, 28, None, 45]})
imputer = SimpleImputer(strategy="median", add_indicator=True)
result = imputer.fit_transform(X)
print(result)
```

## 3. Interpretation and safeguards
State when each feature is available, how it was derived and whether it can be calculated consistently at prediction time. Fit all learned transformations on training data only. Compare performance using the same validation design and check that transformations do not remove meaningful information.

## 4. Guided practice
Compare mean and median imputation on a skewed income column. Add a missingness indicator and explain when absence itself may carry information. State why imputation does not recover the true unobserved values.

## 5. Independent practice
Create a small feature-engineering workflow for a dataset. Include a data dictionary, transformation rationale, pipeline and validation plan. Identify one transformation you decided not to use and explain why.

## 6. Knowledge check
1. What information does this transformation add?
2. Could it leak information from after the prediction time?
3. Does it need to be fitted on training data?
4. How will you test its value and stability?

## Lesson summary
Feature engineering should create meaningful, available and reproducible inputs. Every transformation must be justified and validated within a leakage-safe workflow.