# Lesson 4: Encoding Categorical Variables

## Learning outcomes

By the end of this lesson, you should be able to Encode nominal categories with one-hot encoding; handle categories not seen during training; combine numeric and categorical transformations with ColumnTransformer; and explain why category codes should not imply false order.

## 1. Core explanation
Most estimators require numeric input. One-hot encoding creates a binary column for each category and is suitable for nominal variables. Ordinal encoding assigns ordered values and should be used only when categories have a genuine order. Target encoding replaces a category with a target-derived statistic and must be carefully cross-fitted to avoid leakage.

Unknown categories may appear in production. OneHotEncoder(handle_unknown="ignore") prevents a runtime failure but does not mean the unseen category has been learned. Rare-category grouping can reduce dimensionality, but the grouping rule should be fitted on training data. High-cardinality identifiers are often not useful categorical predictors.

Use ColumnTransformer to apply different transformations to numeric and categorical columns. Keep the transformer in a Pipeline so cross-validation and deployment use the same schema.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas scikit-learn`.

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

df = pd.DataFrame({"age": [20, 35, 42, 28, 31, 50],
                   "region": ["North", "South", "East", "North", "West", "South"],
                   "renewed": [0, 1, 1, 0, 1, 1]})
prep = ColumnTransformer([
    ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), ["age"]),
    ("cat", OneHotEncoder(handle_unknown="ignore"), ["region"])
])
model = make_pipeline(prep, LogisticRegression())
model.fit(df[["age", "region"]], df["renewed"])
print(model.predict(pd.DataFrame({"age": [29], "region": ["Central"]})))
```

## 3. Interpretation and safeguards
State when each feature is available, how it was derived and whether it can be calculated consistently at prediction time. Fit all learned transformations on training data only. Compare performance using the same validation design and check that transformations do not remove meaningful information.

## 4. Guided practice
Explain why region should be one-hot encoded rather than assigned arbitrary numbers. Add an unseen region and observe how the encoder handles it. Describe what this does and does not guarantee.

## 5. Independent practice
Create a small feature-engineering workflow for a dataset. Include a data dictionary, transformation rationale, pipeline and validation plan. Identify one transformation you decided not to use and explain why.

## 6. Knowledge check
1. What information does this transformation add?
2. Could it leak information from after the prediction time?
3. Does it need to be fitted on training data?
4. How will you test its value and stability?

## Lesson summary
Feature engineering should create meaningful, available and reproducible inputs. Every transformation must be justified and validated within a leakage-safe workflow.