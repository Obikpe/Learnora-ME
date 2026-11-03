# Lesson 2: Preparing Data Without a Target

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain why preprocessing has a direct effect on the patterns an unsupervised algorithm discovers.
- Inspect data types, missing values, duplicates, ranges and distributions with pandas.
- Identify identifiers, leakage-like fields, irrelevant variables and redundant features.
- Choose sensible treatments for missing values, categorical data, skew and extreme values.
- Explain standardisation and normalisation and decide when they are appropriate.
- Build a reproducible preprocessing workflow with scikit-learn.

![A structured data preparation workflow](/course-assets/ws09/clustering-concepts.svg)

## 1. Why preparation is especially important in unsupervised learning

In supervised learning, a target provides an external reference for what the model is trying to predict. In unsupervised learning, there is no answer column to guide the algorithm towards the intended meaning. The feature representation therefore plays an unusually important role.

Imagine that you want to group customers according to shopping behaviour. Your table contains customer ID, age, annual spend, number of orders, days since last purchase and postcode. If you include every column without thinking, the algorithm may treat customer ID as a meaningful measurement. It may also allow postcode numbers to create artificial distances. Your output could be mathematically valid but conceptually useless.

Preprocessing is not simply making a dataset look tidy. It is deciding what information the algorithm sees, how that information is represented and how strongly each measurement can influence the result.

## 2. Inspect the dataset before changing it

Start by loading the data and examining its structure.

```python
import pandas as pd

df = pd.read_csv("customers.csv")

print(df.head())
print(df.shape)
print(df.info())
print(df.isna().sum())
print(df.duplicated().sum())
print(df.describe(include="all").T)
```

What each command does:

- `read_csv` reads a comma-separated file into a DataFrame.
- `head()` displays the first five rows by default. It helps you inspect column names and example values.
- `shape` returns a pair: number of rows and number of columns.
- `info()` reports column data types and non-missing counts.
- `isna()` creates a True/False table identifying missing values; `sum()` counts the missing values in each column.
- `duplicated()` identifies rows that exactly repeat earlier rows; `sum()` counts them.
- `describe()` summarises numeric columns by default. With `include="all"`, it also summarises suitable categorical columns. `T` transposes the summary so columns become rows.

Do not delete duplicates automatically. Two customers can have identical measured behaviour and still be different people. A duplicate transaction may be a data error, but repeated identical measurements may be legitimate. First establish what a duplicate means for the dataset's row definition.

## 3. Choose features that represent the question

A feature should have a clear meaning and a defensible connection to the analytical question.

For customer behaviour, possible features include:

- **Recency:** number of days since the customer's most recent purchase.
- **Frequency:** number of purchases in a defined period.
- **Monetary value:** amount spent during that period.
- **Average basket value:** typical spend per transaction.
- **Product diversity:** number of distinct product categories purchased.

Avoid using identifiers such as customer number, invoice ID or row index as ordinary numeric measurements. An ID of 900 is not nine times as much customer behaviour as an ID of 100. It is simply a label.

Categorical codes need similar care. A postcode, product code or department code may be stored as an integer, but the numeric difference between codes does not necessarily represent a meaningful distance. A category such as region may need one-hot encoding or a domain-appropriate similarity method.

Also consider the time at which the analysis will be used. Exclude information that would only become available after the decision being supported. This is often called leakage in predictive modelling, but the same discipline is useful in unsupervised analysis: do not let future information silently define groups that are supposed to represent current behaviour.

## 4. Missing values: understand the absence before filling it

A missing value is not always the same thing. It may mean that a question was not asked, a sensor failed, a customer did not provide information, or a transaction was not applicable. Sometimes missingness itself carries information.

Common strategies include:

- Remove a row when only a very small number of rows are affected and removal is justified.
- Remove a feature when it is mostly missing and cannot be recovered or interpreted responsibly.
- Impute a numeric feature with a statistic such as the median when that is a defensible approximation.
- Impute a categorical feature with the most frequent category or an explicit “Unknown” category when appropriate.
- Add a missingness indicator when the fact that a value is missing may matter.

The median is often more robust than the mean when a numeric feature is skewed or contains extreme values. However, imputation changes the data. It can make different observations look more alike than they really are. Record the choice and compare results if missingness is substantial.

## 5. Scaling: why units can dominate distance

Many clustering algorithms compare observations using distances. Suppose one feature is annual spend in naira, ranging from 10,000 to 800,000, and another is number of orders, ranging from 0 to 30. Under raw Euclidean distance, a difference of 100,000 naira can overwhelm a difference of several orders. The algorithm may behave as if spend is the only important feature.

**Standardisation** transforms a numeric feature by subtracting its mean and dividing by its standard deviation:

```
z = (x - mean) / standard_deviation
```

The transformed values express how far a measurement is from the mean in standard-deviation units. A value of 0 is at the mean; a value of 2 is two standard deviations above it.

**Min-max normalisation** maps a feature into a chosen range, commonly 0 to 1:

```
x_scaled = (x - minimum) / (maximum - minimum)
```

Standardisation is common for K-means, PCA and many distance-based methods. Min-max scaling can be useful when a bounded range is required. Neither method makes a feature meaningful. Scaling a customer ID does not turn it into a valid behavioural measure.

Outliers can strongly affect the mean and standard deviation used by standardisation, and the minimum and maximum used by min-max scaling. Robust scaling, which uses the median and interquartile range, may be more appropriate when extreme values are legitimate but should not dominate the scale.

## 6. Transforming skewed features

A positive feature such as income or annual spend may be strongly right-skewed: most observations are relatively small, while a few are very large. A logarithmic transformation can compress the upper tail:

```python
import numpy as np

df["log_spend"] = np.log1p(df["annual_spend"])
```

`np.log1p(x)` calculates the natural logarithm of (1+x). It is useful when values can be zero because `log(0)` is undefined while `log1p(0)` is zero. It cannot be applied blindly to values less than or equal to -1. A log transformation changes the interpretation of distances, so retain the original column for reporting.

## 7. A reproducible preprocessing example

The following example uses a small synthetic dataset so it runs without downloading a file.

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

customers = pd.DataFrame({
    "customer_id": [101, 102, 103, 104, 105, 106],
    "recency_days": [5, 12, None, 80, 45, 9],
    "orders_90d": [12, 8, 3, 0, 2, 10],
    "average_basket": [500, 420, 180, 90, None, 460],
    "region": ["North", "South", "North", "West", "South", "East"]
})

# IDs identify records; they do not describe behaviour.
X = customers.drop(columns=["customer_id"])

numeric_features = ["recency_days", "orders_90d", "average_basket"]
categorical_features = ["region"]

numeric_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(transformers=[
    ("numeric", numeric_pipeline, numeric_features),
    ("categorical", categorical_pipeline, categorical_features)
])

X_prepared = preprocessor.fit_transform(X)
print("Prepared matrix shape:", X_prepared.shape)
```

### Understand the pipeline

A pipeline is a sequence of transformations executed in order. The numeric pipeline first fills missing values with the median, then standardises the resulting numeric columns. The categorical pipeline fills missing categories using the most frequent category, then converts categories into indicator columns.

`OneHotEncoder` creates a separate binary feature for each category observed during fitting. A row from the North region receives 1 in the North column and 0 in the other region columns. `handle_unknown="ignore"` prevents the transformer from failing if a new category appears later; unseen categories are represented by zeros across the known category columns.

`ColumnTransformer` applies different transformations to selected columns. This matters because a numeric variable and a category should not necessarily be processed in the same way.

The ID is removed before preprocessing. The pipeline is fitted once and should be retained for future data so the same medians, means, standard deviations and category mapping are reused. Do not independently fit a new scaler every time you analyse a new batch if you need results to remain comparable.

## 8. Mixed data and the limits of one-hot encoding

One-hot encoding is convenient, but it changes the geometry of the data. A category with many possible values creates many columns. Two observations from different categories may become equally distant even if domain knowledge says some categories are more alike than others.

For mixed numeric and categorical datasets, consider whether a distance designed for mixed types is more appropriate. The right choice depends on the algorithm, feature meanings and scale. Do not assume that converting everything to numbers automatically makes the representation sensible.

## 9. Guided practice

Create a table with annual spend, number of purchases, customer ID and region. Decide which fields should be included for a behaviour-based clustering exercise. Explain how you would treat region, missing spend and extreme spend values. State why your choices are reasonable and what they may distort.

## 10. Independent practice

Use a public or synthetic dataset with numeric and categorical features. Produce a preparation report containing row meaning, data types, missing-value counts, duplicate checks, feature definitions, exclusions, transformations and scaling choices. Compare clustering results with and without scaling and explain what changed.

## 11. Knowledge check

1. Why is feature selection part of the modelling decision rather than a purely technical cleaning step?
2. Why should a customer ID normally be excluded from distance-based clustering?
3. Explain the difference between standardisation and min-max scaling.
4. Why might median imputation be preferable to mean imputation for a skewed feature?
5. What does one-hot encoding do, and what limitation can it introduce?
6. Why should a fitted preprocessing pipeline be reused for later observations?

## Lesson summary

Preprocessing defines the representation that an unsupervised algorithm analyses. Inspect the data, understand the observation unit, choose features for a clear reason, handle missingness carefully, encode categories appropriately and scale measurements when the method depends on distance or variance. Keep original values for interpretation and preserve the fitted transformations for reproducibility.
