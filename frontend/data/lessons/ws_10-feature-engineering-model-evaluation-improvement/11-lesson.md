# Lesson 11: Pipelines and ColumnTransformer

## Learning outcomes

By the end of this lesson, you should be able to build a preprocessing workflow with Pipeline and ColumnTransformer; keep numeric and categorical steps separate; fit transformations within cross-validation; and inspect the transformed feature space.

## 1. Why pipelines matter

A machine-learning workflow usually contains more than an estimator. Real datasets may have missing values, numeric fields on different scales and categorical labels that a model cannot use directly. You need a repeatable sequence that transforms raw columns into a model-ready representation.

A common mistake is to prepare the entire dataset first and split it afterwards. If an imputer calculates a median using all rows, the test data has influenced the training transformation. That is a form of data leakage. The same risk applies to scaling, feature selection, dimensionality reduction and data-driven category handling.

Scikit-learn's Pipeline connects transformations and an estimator into one object. When cross-validation fits the pipeline on a training fold, each transformation learns its parameters only from that fold. The held-out fold is transformed using those learned parameters.

## 2. Pipeline and ColumnTransformer

A Pipeline runs steps in order. Each intermediate step must implement fit and transform; the final step is usually an estimator with fit and predict.

ColumnTransformer applies different transformations to different columns. This is useful when numeric and categorical fields need different treatment.

Example design:

- Numeric columns: median imputation, then standardisation.
- Categorical columns: most-frequent imputation, then one-hot encoding.
- Final step: a classifier or regressor.

The encoder uses `handle_unknown="ignore"` so an unseen category at prediction time does not crash the transformation. It does not mean the new category is understood; it means the encoder can safely represent the row without a column learned for that category.

## 3. Worked Python example

Run in VS Code. Install packages with `python -m pip install numpy pandas scikit-learn`.

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

df = pd.DataFrame({
    "age": [20, 35, None, 44, 28, 50, 31, 42, 26, 39, 47, 23],
    "income": [25000, 52000, 31000, 68000, 29000, 72000,
               41000, 61000, 27000, 58000, 65000, 33000],
    "region": ["North", "South", "North", "West", "East", "South",
               "West", "East", "North", "South", "West", "East"],
    "renewed": [0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0]
})

numeric_features = ["age", "income"]
categorical_features = ["region"]

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])
categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, numeric_features),
    ("categorical", categorical_pipeline, categorical_features)
])

model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=1000))
])

X = df[numeric_features + categorical_features]
y = df["renewed"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

model.fit(X_train, y_train)
print("Test accuracy:", model.score(X_test, y_test))

new_learner = pd.DataFrame({
    "age": [29],
    "income": [45000],
    "region": ["Central"]  # category not seen during training
})
print("Prediction:", model.predict(new_learner)[0])
```

## 4. Read the workflow

1. We identify numeric and categorical columns explicitly. This prevents the pipeline from treating an identifier or target as a feature by accident.
2. The numeric pipeline fills missing values using the training median and then standardises.
3. The categorical pipeline fills missing labels and one-hot encodes categories.
4. ColumnTransformer applies the right branch to the right columns.
5. Pipeline fits the transformations and logistic regression together.
6. train_test_split happens before model.fit, so the test rows do not determine medians, scaling parameters or categories.
7. The new record contains a category that was not present in training. The encoder handles it without raising an exception.

The test score is only a demonstration on a very small synthetic dataset. It is not a reliable estimate of real-world performance.

## 5. Common errors

- Fitting an imputer or scaler on the full dataset before splitting.
- Including the target column in the feature matrix.
- Applying one-hot encoding to the target by mistake.
- Forgetting to handle unseen categories at inference.
- Using a pipeline in training but manually preprocessing inference inputs differently.
- Assuming that a pipeline removes every kind of leakage: features can still contain future information or duplicated identifiers.

## 6. Guided practice

Change the numeric imputer from median to mean and compare the learned transformation. Add a missing region and observe how the categorical imputer handles it. Add a new region at prediction time and explain what `handle_unknown="ignore"` does and does not guarantee.

## 7. Independent practice

Build a Pipeline for a dataset containing at least two numeric columns and one categorical column. Include missing values in both types. Split the data first, fit the pipeline only on training data, and evaluate on held-out data. Then explain why the exact same pipeline object should be saved and used for inference.

## 8. Knowledge check

1. What is the difference between Pipeline and ColumnTransformer?
2. Why must imputation and scaling be fitted after the train/test split?
3. What happens when the encoder sees a category that was absent during training?
4. Why does a pipeline not automatically prevent target or temporal leakage?

## Lesson summary

Pipeline and ColumnTransformer make preprocessing reproducible and help prevent preprocessing leakage. Keep the raw feature schema explicit, fit all learned transformations inside the training workflow, and use the same fitted pipeline for future predictions.