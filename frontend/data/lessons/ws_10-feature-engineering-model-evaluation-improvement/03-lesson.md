# Lesson 3: Missing-Value Strategies

## Learning outcomes
Distinguish missingness from zero; inspect missing-value patterns; explain MCAR, MAR and MNAR; select a defensible imputation strategy; and implement imputation without leakage.

## 1. Why values are missing
A missing value means that a measurement is unavailable in the dataset. It does not automatically mean zero, “not applicable” or “no”. If a customer has no recorded middle name, that may be structurally absent. If income is blank, it may mean the customer declined to provide it, the system failed to capture it or the value has not yet been verified. Those situations have different meanings.

Three classical missingness mechanisms are useful:
- **MCAR (Missing Completely At Random):** missingness is unrelated to observed or unobserved values. Example: random file corruption affects a small set of rows.
- **MAR (Missing At Random):** missingness depends on observed information. Example: income is more often missing for a particular application channel.
- **MNAR (Missing Not At Random):** missingness depends on the missing value itself or unobserved factors. Example: people with very high income are less likely to disclose it.

These categories are assumptions, not labels that can always be proven from a spreadsheet. Missingness can itself carry information, but using it requires care.

## 2. Inspect before filling
Start by counting missing values by column and calculating their proportion. Inspect whether missingness is concentrated in groups, dates or target classes. Check whether a blank is encoded as an empty string, "unknown", -1 or another sentinel value. Convert such placeholders deliberately; do not blindly replace legitimate values.

![Missing value decision path](/course-assets/ws10/missing-value-strategies.svg)

## 3. Common strategies
**Deletion** may be reasonable when only a small number of rows are missing and deletion does not distort the population. It can be harmful when missingness is systematic.

**Mean imputation** replaces missing numeric values with the training mean. It is simple but sensitive to outliers and reduces variance.

**Median imputation** is more robust to skew and extreme values. It is often a sensible baseline for numeric variables.

**Mode or constant imputation** can be used for categorical fields. A constant such as "Unknown" can preserve the fact that the category was unavailable, provided that "Unknown" is a meaningful representation and not confused with a real category.

**Missingness indicators** add a separate binary feature showing whether the original value was missing. This can help when the act of not recording a value is informative.

**Model-based imputation** estimates missing values from other variables. It can preserve more complex relationships but is more complicated and still must be fitted within training data.

## 4. Worked example with a pipeline
```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

data = pd.DataFrame({
    "age": [22, 35, None, 48, 29, 51, None, 40],
    "income": [250, 400, 300, None, 280, 600, 320, 450],
    "channel": ["web", "branch", "web", None, "app", "branch", "app", "web"],
    "approved": [0, 1, 0, 1, 0, 1, 0, 1]
})

X = data.drop(columns="approved")
y = data["approved"]

numeric = ["age", "income"]
categorical = ["channel"]

numeric_pipe = make_pipeline(
    SimpleImputer(strategy="median", add_indicator=True),
    StandardScaler()
)
categorical_pipe = make_pipeline(
    SimpleImputer(strategy="most_frequent"),
    OneHotEncoder(handle_unknown="ignore")
)
preprocessor = ColumnTransformer([
    ("numeric", numeric_pipe, numeric),
    ("categorical", categorical_pipe, categorical)
])
model = make_pipeline(preprocessor, LogisticRegression())
model.fit(X, y)
print("Training score:", model.score(X, y))
```

The example demonstrates preprocessing structure, not a reliable performance estimate: the dataset is tiny and the score is measured on training rows. In a real evaluation, split first and evaluate on held-out data. `add_indicator=True` creates indicators for columns that had missing values during fitting. `handle_unknown="ignore"` prevents a previously unseen category from crashing transformation.

## 5. How to choose
Consider the variable's meaning, missingness proportion, mechanism, distribution, model type and operational process. For an income field, median imputation plus a missingness indicator may be a useful baseline. For a field where missing means "not applicable", a separate category may be more honest. Do not impute a target variable as though it were an ordinary feature; missing targets often require excluding those rows from supervised training or defining a separate data-collection process.

## 6. Common mistakes
- Replacing missing values with zero without checking meaning.
- Computing imputation statistics before the train/test split.
- Assuming missingness is random because it is convenient.
- Using a categorical mode for a high-cardinality identifier.
- Evaluating a model on training data and presenting the score as generalisation.
- Forgetting to monitor missingness rates after deployment.

## Guided practice
For a dataset containing age, salary, occupation, customer rating and purchase amount, propose an approach for each field. Explain when "Unknown" is preferable to mode imputation.

## Independent practice
Create a missingness report with counts, percentages and at least one visual. Compare median imputation with median-plus-indicator using the same cross-validation folds. Record the assumptions and limitations.

## Knowledge check
1. Why is missing not equivalent to zero?
2. What distinguishes MAR from MNAR?
3. Why is median often preferred to mean for skewed data?
4. What does a missingness indicator represent?
5. Why must imputation be fitted inside the training workflow?

## Lesson summary
Missing data requires diagnosis before treatment. Choose an approach that respects the field's meaning and missingness process, and keep learned imputation statistics inside the leakage-safe modelling pipeline.

## 7. Deeper reasoning: imputation changes the data, not just the blank cells

Imputation is an assumption about what an unavailable value should be represented by. Replacing a missing salary with the median does not recover the person's true salary. It creates a consistent numerical placeholder so an estimator can operate. The analyst must therefore explain what information is lost and whether the missingness itself is informative.

Consider two customers with missing income. One may have skipped the question; the other may be a student for whom the field is not applicable. Giving both the same median value can hide a meaningful distinction. A missingness indicator can preserve the fact that a value was absent, while a separate category or rule may be more suitable for structurally inapplicable data. These choices should be based on how the field is collected and used.

Imputation can also distort distributions. Mean and median imputation create repeated values at one point and usually reduce observed variance. This can affect correlations and downstream model behaviour. More sophisticated methods can preserve relationships better, but they introduce extra assumptions and may be unstable when the dataset is small. Begin with a transparent baseline, compare alternatives using the same folds and do not claim that a complex imputer must be better.

In a deployed system, monitor missingness after training. If the proportion of missing income rises from 5% to 40%, the model is now receiving a different input pattern. The original imputation strategy may still run, but its predictions may be less reliable. Missingness is therefore both a preprocessing concern and a data-quality signal that deserves operational monitoring.