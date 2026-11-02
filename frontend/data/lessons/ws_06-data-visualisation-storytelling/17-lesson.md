# Lesson 17: Visualising Missing Data and Data Quality

## Learning outcomes
You should be able to inspect missingness, duplicates, invalid values and outliers; visualise missing data by field and group; create quality summaries and missingness heatmaps; distinguish absence from zero; and explain how data-quality problems affect interpretation.

## 1. Why visualise data quality?
A chart can be technically beautiful and still be wrong if the underlying data is incomplete or invalid. Before plotting results, inspect missing values, duplicates, impossible values, inconsistent categories, incorrect types, outliers and missing time periods.

A visualisation of data quality can reveal patterns that a row count alone hides. For example, missing scores may be concentrated in one cohort. Dropping those rows could make that cohort look better or worse than it really is.

## 2. Inspect a DataFrame
```python
import pandas as pd

df = pd.DataFrame({
    "learner": ["A", "B", "C", "D", "E", "E"],
    "age": [21, 24, None, 19, 150, 150],
    "score": [70, 82, 65, None, 91, 91],
    "region": ["North", "South", "North", None, "West", "West"]
})
print(df.info())
print(df.isna().sum())
print(df.duplicated().sum())
print(df.describe(include="all"))
```

- `info()` shows data types and non-missing counts.
- `isna().sum()` counts missing cells per column.
- `duplicated().sum()` counts exact duplicate rows.
- `describe()` summarises numerical and categorical fields.

A duplicate is not always an error. It depends on what one row represents and the rules of the data source.

## 3. Plot missing percentages
```python
import matplotlib.pyplot as plt

missing_pct = df.isna().mean().mul(100).sort_values()
fig, ax = plt.subplots(figsize=(7, 4))
ax.barh(missing_pct.index, missing_pct.values)
ax.set(title="Missing values by field",
       xlabel="Missing records (%)", ylabel="Field")
ax.set_xlim(0, 100)
plt.show()
```

`isna()` returns True for missing cells. The mean of a boolean column is the proportion of True values because True behaves as 1 and False as 0. Multiplying by 100 expresses the proportion as a percentage.

## 4. Missingness heatmap
```python
import seaborn as sns
fig, ax = plt.subplots(figsize=(8, 4))
sns.heatmap(df.isna(), cbar=False, yticklabels=False,
            cmap=["#2A9D8F", "#E76F51"], ax=ax)
ax.set_title("Missing-value pattern by record and field")
ax.set_xlabel("Field")
ax.set_ylabel("Record")
plt.show()
```

Each cell indicates whether a value is missing. This can reveal blocks or patterns. With millions of rows, the full matrix becomes unreadable; sample or aggregate carefully and disclose the method.

## 5. Missingness by group
```python
missing_by_region = (
    df.assign(age_missing=df["age"].isna())
      .groupby("region", dropna=False)["age_missing"]
      .mean()
      .mul(100)
)
print(missing_by_region)
```

This calculates the percentage of missing age values by region, including missing region labels as a group. A difference may indicate a collection process problem or a population difference. It does not by itself explain why data is missing.

## 6. Outliers: investigate, do not automatically delete
An outlier is an observation far from the main body of values under some definition. It may be a data-entry error, measurement failure, genuine rare case or member of a different population.

A box plot may flag points beyond the 1.5 × IQR whiskers. This is a screening rule, not an automatic deletion rule. Check source records, units, plausible ranges and context.

## 7. Validate values
```python
# Example domain check; the acceptable age range must be justified.
invalid_age = df[df["age"].notna() &
                 ((df["age"] < 0) | (df["age"] > 110))]
print(invalid_age)

# Standardise category whitespace and capitalisation.
df["region_clean"] = df["region"].str.strip().str.title()

# Inspect all members of duplicated rows.
duplicates = df[df.duplicated(keep=False)]
print(duplicates)
```

Do not apply an age limit blindly to every dataset. Preserve raw data and document any correction or exclusion.

## 8. Missing is not zero
Missing revenue does not necessarily mean revenue was zero. An unrecorded attendance value does not mean a learner was absent. Replacing missing values with zero can create false patterns.

Ask why the value is missing, whether missingness differs by group, whether it relates to the outcome and how a proposed treatment changes the population being analysed.

## 9. Common mistakes
- Replacing every missing value with zero.
- Removing all outliers without checking them.
- Treating duplicates as errors without understanding the unit of observation.
- Ignoring quality differences across groups.
- Plotting millions of missingness cells without aggregation.
- Hiding cleaning decisions from the final report.

## Guided practice
1. Inspect the example DataFrame.
2. Plot missing percentages by field.
3. Create a missingness heatmap.
4. Calculate missingness by region.
5. Investigate the age outlier and state what evidence is needed before correction.

## Independent practice
Use a dataset with missing values or create a controlled example. Produce a data-quality report with missing percentages, duplicate counts, invalid-value checks and at least one visual. Explain which decisions require domain knowledge.

## Knowledge check
1. What does `isna().mean()` calculate?
2. Why is missing not the same as zero?
3. Does an outlier always mean an error?
4. Why might dropping incomplete rows bias a group comparison?
5. Why preserve raw data?

## Lesson summary
Visualising data quality prevents misleading analysis. Inspect missingness, duplicates, invalid values and unusual observations before drawing conclusions. Document cleaning decisions and never replace unknown values with zero without a defensible reason.