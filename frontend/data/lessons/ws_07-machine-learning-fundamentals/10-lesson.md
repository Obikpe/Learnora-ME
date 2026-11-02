# Lesson 10: Preparing Data for Learning

## Learning outcomes
Explain the method, implement the example in Python, interpret its result, and identify risks that could invalidate the conclusion.

## 1. Concepts and reasoning
Models generally require consistent numeric inputs. Preparation may include handling missing values, encoding categories, scaling numeric fields and correcting invalid types. These steps should be chosen based on the variable meaning and model requirements, not applied mechanically.

Imputation replaces missing values using a rule such as median, most frequent category or a domain-specific value. Encoding converts categories to numeric representation. One-hot encoding creates indicator columns; ordinal encoding is suitable only when categories have a genuine order and the numeric codes preserve that order. Scaling places numeric features on comparable scales and is important for distance-based and gradient-based algorithms.

Fit each preprocessing step on training data only. If you calculate a median or category vocabulary using all rows before splitting, information from the test set has influenced the training process. Scikit-learn Pipelines help ensure transformations are fitted within each training fold.

## 2. Worked example
Run in VS Code in your course virtual environment. Install packages as required: `python -m pip install numpy pandas scikit-learn matplotlib`.

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

df = pd.DataFrame({
    "age": [22, 35, None, 41],
    "income": [25000, 52000, 31000, None],
    "region": ["North", "South", "North", "West"]
})
numeric = Pipeline([("impute", SimpleImputer(strategy="median")),
                    ("scale", StandardScaler())])
categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                        ("encode", OneHotEncoder(handle_unknown="ignore"))])
prep = ColumnTransformer([("num", numeric, ["age", "income"]),
                          ("cat", categorical, ["region"])])
print(prep.fit_transform(df).shape)
```

## 3. Interpretation
State what was learned from training data and what was measured on unseen data. Check whether the metric answers the real decision question. A technically correct output can still be misleading if the target, split or population is wrong.

## 4. Guided practice
Add a missing value and a previously unseen region. Explain how median imputation and handle_unknown avoid failures. State why an imputation value should be learned from the training partition rather than from the complete dataset.

## 5. Independent practice
Apply the lesson to a small dataset. Record the source, unit of observation, target and feature availability. Save your code and a short report that includes evidence, limitations and the next validation step.

## 6. Knowledge check
1. What assumption is most important in this method?
2. What is the difference between training performance and generalisation?
3. How could leakage or sampling bias affect the result?
4. What would you tell a stakeholder before they use the model?

## Lesson summary
A trustworthy ML workflow is reproducible, uses a suitable baseline and evaluation design, and communicates errors and limitations as carefully as headline performance.