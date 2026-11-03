# Lesson 4: Datasets, Features and Targets

## Learning outcomes
Explain observations, features and targets; distinguish numerical, categorical and temporal variables; identify identifiers, proxies and leakage; inspect a dataset with Pandas; and build a feature matrix and target vector.

## 1. Understand the table
In a tabular dataset, rows usually represent cases and columns represent variables. But the meaning of a row must be explicit: one row may represent a learner, purchase, learner-week or sensor reading.

![Features and target in a dataset](/course-assets/ws07/04-features-target.svg)

Suppose each row represents one learner:
- study_hours: study time per week;
- attendance_rate: percentage of sessions attended;
- course_level: enrolled course level;
- completed: whether the learner completed the course.

If completion is the outcome to predict, it is the target. The other fields may be features if they are known at the prediction time.

## 2. Numerical variables
Discrete variables are counts, such as number of assignments. Continuous variables are measurements, such as time spent studying. A numerical-looking column is not necessarily a measurement: an ID code such as 10027 is not a quantity. Taking its average is meaningless.

Measurement scales also matter. A temperature in Celsius has meaningful differences but no absolute zero; duration has a meaningful zero. Consider units when interpreting coefficients and errors.

## 3. Categorical variables
Nominal categories have no natural order, such as region or course name. Ordinal categories have an order, such as beginner, intermediate and advanced. Binary variables have two categories, such as yes/no.

Do not encode nominal categories as arbitrary numbers and assume the model understands the category meaning. Later lessons explain one-hot encoding and other approaches.

## 4. Dates, text and other data
Dates can be transformed into useful features such as day of week, month or elapsed time. Only derive them from timestamps available at prediction time. Text can be represented using word counts or embeddings. Images and audio require specialised representations, but the core question remains: what input is available, and what outcome are we predicting?

## 5. Identifiers, proxies and leakage
An identifier distinguishes records. It often should not be used as a feature because it may encode arbitrary ordering or accidental patterns. Some identifiers reveal groups or time, however, so investigate before excluding.

A proxy indirectly represents another characteristic. A postcode, for example, may encode socioeconomic conditions. A proxy may be predictive but create privacy or fairness concerns.

Leakage occurs when information unavailable at the intended prediction time enters the model. Examples include using a final exam score to predict pass/fail before the exam, or an investigation outcome to score a transaction immediately.

## 6. Inspect data with Pandas
```python
import pandas as pd

df = pd.DataFrame({
    "learner_id": [101, 102, 103, 104, 105, 106],
    "study_hours": [2.5, 1.0, 5.0, 3.5, None, 4.0],
    "attendance_rate": [80, 45, 95, 70, 60, 88],
    "course_level": ["Beginner", "Beginner", "Advanced",
                     "Intermediate", "Intermediate", "Advanced"],
    "completed": [1, 0, 1, 1, 0, 1]
})
print(df.head())
print("Shape:", df.shape)
print(df.info())
print(df.describe(include="all"))
print(df.isna().sum())
print(df.nunique())
```

head() previews rows. shape gives row and column counts. info() shows data types and non-null counts. describe() summarises numerical and categorical columns. isna().sum() counts missing values. nunique() counts distinct values.

## 7. Separate features and target
```python
feature_columns = ["study_hours", "attendance_rate", "course_level"]
X = df[feature_columns]
y = df["completed"]
print("X:", X.shape)
print("y:", y.shape)
```

X is the feature matrix; y is the target vector. Each row in X must correspond to the same row in y. The ID is deliberately excluded because it is an identifier rather than a meaningful measurement.

## 8. Check target quality
For classification, inspect class counts and proportions:
```python
print(y.value_counts(dropna=False))
print(y.value_counts(normalize=True, dropna=False))
```
A dataset with 98% class 0 can produce 98% accuracy by always predicting 0, while failing to detect class 1. This is why target balance matters.

For regression, inspect target units, range, skew and extreme values. Ask whether the outcome is measured consistently and whether every row has a valid label.

## 9. Create a data dictionary
| Column | Meaning | Type | Values / unit | Available when? | Role |
|---|---|---|---|---|---|
| study_hours | Weekly study time | Numerical | Hours | End of week 2 | Feature |
| attendance_rate | Attendance | Numerical | 0–100% | End of week 2 | Feature |
| course_level | Enrolled level | Categorical | Three levels | Enrolment | Feature |
| completed | Finished course | Binary | 0 or 1 | Course end | Target |
| learner_id | Record identifier | Identifier | Unique code | Enrolment | Audit key |

The dictionary makes assumptions visible and helps another analyst understand how the model could be used.

## Common mistakes
- Treating IDs as numerical measurements.
- Mixing up feature and target columns.
- Failing to define what one row represents.
- Using future information as an input.
- Ignoring target imbalance or inconsistent labels.
- Separating X and y in different row orders.

## Guided practice
Inspect a dataset and identify its unit of observation. Classify every column, nominate a target and explain which columns should be excluded and why.

## Independent practice
Create a data dictionary with at least eight columns: an identifier, two categorical variables, three numerical variables, a date field and a target. State when each feature becomes available.

## Knowledge check
1. What does one row represent?
2. Why is an ID usually not a measurement?
3. How does ordinal data differ from nominal data?
4. Give an example of leakage.
5. Why must X and y remain aligned?

## Lesson summary
Understanding the dataset is a modelling skill. Clear observation units, well-defined features, trustworthy targets and prediction-time awareness prevent many failures before training begins.