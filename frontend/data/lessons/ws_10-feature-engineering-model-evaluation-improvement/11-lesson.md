# Lesson 11: Pipelines and ColumnTransformer

## Learning outcomes
Explain why pipelines matter; build separate numeric and categorical preprocessing paths; compose transformations with an estimator; and use pipelines safely in cross-validation and production.

## 1. The problem with manual preprocessing
A modelling workflow often includes imputation, encoding, scaling, feature selection and an estimator. If each step is run manually, it is easy to fit a transformation on the wrong data, apply inconsistent columns or forget a step when making predictions.

A **Pipeline** chains transformations and a final estimator. During fitting, each transformer learns from the training data and passes transformed output to the next step. During prediction, the already-fitted transformations are applied in the same order. This makes the workflow reproducible and reduces leakage risk.

## 2. ColumnTransformer
Different columns need different treatments. Numeric columns may require median imputation and scaling. Categorical columns may require most-frequent imputation and one-hot encoding. ColumnTransformer applies each specified transformer to its selected columns and combines the outputs.

![ColumnTransformer workflow](/course-assets/ws10/column-transformer.svg)

## 3. Worked end-to-end example
```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

data = pd.DataFrame({
    "age": [22, 35, 41, 29, 52, 46, 31, 60, 38, 25, 55, 44],
    "income": [200, 450, None, 300, 700, 500, 280, 800, 420, 250, 680, 510],
    "channel": ["web", "branch", "web", "app", "branch", "app",
                "web", None, "branch", "app", "web", "branch"],
    "renewed": [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1]
})

X = data.drop(columns="renewed")
y = data["renewed"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

numeric_features = ["age", "income"]
categorical_features = ["channel"]

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
model.fit(X_train, y_train)
predictions = model.predict(X_test)
print(classification_report(y_test, predictions, zero_division=0))
```

The dataset is deliberately small for illustration; its test metrics are not a credible performance estimate. The important design is that the split occurs before fitting, and all preprocessing is inside the model pipeline. The pipeline can be passed directly to cross-validation and hyperparameter search.

## 4. Inspecting and reusing a fitted pipeline
Use `named_steps` to inspect named pipeline components. Use `get_params()` to inspect nested settings. Save a fitted pipeline only with a suitable, secure model-artifact process and record package versions. Never assume a saved model remains compatible with every future library version.

At prediction time, supply the same raw columns expected by the pipeline. Do not manually scale or encode incoming rows if the pipeline already performs those transformations.

## 5. Common mistakes
- Preprocessing before splitting.
- Training on columns in a different order from prediction.
- Fitting a separate encoder on test data.
- Applying a transformation twice.
- Forgetting to include the selector in the pipeline.
- Reporting training score as test performance.

## Guided practice
Extend the example with a missingness indicator for income and explain how it is fitted. Add a new unseen channel to a prediction row and observe how the encoder handles it.

## Independent practice
Build a reusable pipeline for a public dataset. Include preprocessing, an estimator and cross-validation. Save the pipeline configuration and explain how a new raw record passes through every step.

## Knowledge check
1. What does a Pipeline do?
2. Why is ColumnTransformer useful?
3. At what point should the train/test split occur?
4. How do you inspect a named pipeline step?
5. Why should prediction receive raw rather than manually transformed inputs?

## Lesson summary
Pipelines turn preprocessing and modelling into one reproducible object. They help enforce consistent transformations and leakage-safe fitting across validation, testing and deployment.