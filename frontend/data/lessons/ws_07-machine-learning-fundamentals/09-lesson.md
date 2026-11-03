# Lesson 9: Exploratory Data Analysis for Machine Learning

## Learning outcomes
Explain why EDA is necessary before modelling; inspect rows, columns, data types, missingness, duplicates and target balance; use descriptive statistics and visualisations; identify leakage and sampling problems; and write evidence-based findings.

## 1. What EDA does
Exploratory data analysis is the process of asking questions of a dataset before deciding how to model it. It helps you understand what the rows represent, what values mean, where data is missing, how variables are distributed and whether the target is trustworthy.

EDA is not a hunt for patterns that confirm what you already believe. It is a structured investigation. A chart or summary can reveal a problem, but it rarely proves the cause of that problem.

## 2. Start with structure and quality
```python
import pandas as pd

df = pd.read_csv("data/learners.csv")
print("Shape:", df.shape)
print(df.head())
print(df.sample(min(5, len(df)), random_state=1))
print(df.info())
print(df.describe(include="all").T)
print("Missing values:\n", df.isna().sum())
print("Duplicate rows:", df.duplicated().sum())
```

- shape gives rows and columns.
- head() and sample() show examples; sample() can reveal patterns hidden by row ordering.
- info() shows types and non-null counts.
- describe() summarises numerical and categorical columns.
- isna().sum() counts missing values per column.
- duplicated().sum() counts fully duplicated rows, not necessarily duplicate entities.

A repeated learner ID may indicate multiple legitimate records per learner. Do not delete duplicates until you understand the unit of observation and what constitutes a duplicate.

## 3. Inspect numerical features
For each numeric feature, check minimum, maximum, mean, median, quartiles and standard deviation. Look for impossible values such as attendance of 140%, negative age or a delivery duration below zero. A value can be extreme but valid; confirm its meaning before removing it.

Histograms show the distribution of one numerical variable. Box plots summarise median, quartiles and potential outliers. Scatter plots reveal relationships between two numerical variables. These plots help generate questions, not prove causation.

![EDA distribution and box plot concepts](/course-assets/ws07/09-eda-distributions.svg)

```python
import matplotlib.pyplot as plt

df["study_hours"].hist(bins=20)
plt.xlabel("Study hours per week")
plt.ylabel("Number of learners")
plt.title("Distribution of study hours")
plt.tight_layout()
plt.show()
```
bins=20 requests 20 histogram intervals. The x-axis represents study-hour ranges; the y-axis counts observations. If the distribution is strongly skewed, the mean may not describe a typical learner well.

## 4. Inspect categorical features
```python
print(df["course_level"].value_counts(dropna=False))
print(df["course_level"].value_counts(normalize=True, dropna=False))
```
value_counts() counts each category. normalize=True returns proportions rather than raw counts. dropna=False includes missing values as a category in the summary.

Rare categories may be genuine, data-entry mistakes or inconsistent labels (for example, "Beginner", "beginner" and "Beginners"). Standardise categories only after confirming they mean the same thing.

## 5. Inspect the target
For classification, examine counts and proportions for every class. A target with a 99:1 imbalance needs careful evaluation; accuracy alone can conceal a model that never detects the rare class. For regression, inspect target range, skew, units and extreme values.

```python
target = "completed"
print(df[target].value_counts(dropna=False))
print(df[target].value_counts(normalize=True, dropna=False))
```

Do not assume the label is correct. Ask who created it, when it was recorded, whether the definition changed and whether every row was labelled consistently.

## 6. Missing data
Missing values can occur because a question was not asked, a sensor failed, a value was not applicable or a record was lost. These causes have different meanings. A missing-value percentage is only the beginning of the investigation.

```python
missing = df.isna().mean().sort_values(ascending=False)
print((missing * 100).round(1))
```
The result is the percentage missing in each column. Missingness may be related to the target or to a particular group. Imputation strategy is covered in the next lesson.

## 7. Relationships and leakage
Use scatter plots, grouped summaries and correlations to investigate relationships. Correlation measures association, not causation. A strong association may arise because one variable causes another, because of a third variable, or by coincidence.

Leakage is a particularly important EDA question: is this feature genuinely available at the moment the prediction must be made? A column that reveals the outcome after the fact may make a model appear excellent while being unusable in practice.

## 8. EDA without test-set peeking
Understand the raw dataset and define a sensible split strategy. After splitting, learn preprocessing and feature-selection decisions from training data, then evaluate them using validation or cross-validation. Do not repeatedly inspect test outcomes to make modelling choices. The test set must remain a final, held-out estimate.

## 9. Write findings, not just screenshots
For every finding, state:
- what you checked;
- what you observed;
- why it matters to the modelling task;
- what action or further check is needed;
- what uncertainty remains.

Example: "Attendance is missing for 12% of rows. Missingness is concentrated in records from one delivery centre. We need to investigate the centre's recording process before choosing an imputation strategy."

## Common mistakes
- Deleting every row with a missing value.
- Removing all statistical outliers without checking validity.
- Treating duplicate rows and repeated entities as identical.
- Looking only at the mean.
- Choosing features based on test-set performance.
- Confusing correlation with causation.

## Guided practice
Load a dataset and report its dimensions, data types, missing values, duplicate rows, numerical ranges, categorical frequencies and target proportions. Identify three issues that could affect model quality.

## Independent practice
Create an EDA report with at least four charts. Include a data dictionary, target analysis, missingness summary and a section titled "What we still do not know". Do not train a model until you can explain the dataset.

## Knowledge check
1. What is the difference between a duplicate row and a repeated entity?
2. Why inspect the target distribution?
3. Why can an extreme value be valid?
4. How can a feature leak the target?
5. Why is EDA not proof of causation?

## Lesson summary
EDA is a disciplined way to understand data, expose risks and guide the next steps. Good modelling begins with asking better questions of the dataset.