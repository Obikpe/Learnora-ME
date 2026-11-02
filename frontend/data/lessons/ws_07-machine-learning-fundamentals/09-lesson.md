# Lesson 9: Exploratory Data Analysis for ML

## Learning outcomes

By the end of this lesson, you should be able to Profile an ML dataset's dimensions, types, missing values, duplicates and target distribution; inspect numeric summaries; identify imbalance and suspicious fields; and record data-quality issues before training.

## 1. Concepts and reasoning
Exploratory data analysis (EDA) checks whether a dataset is suitable for modelling and helps uncover errors before they become model behaviour. Inspect dimensions, data types, duplicate rows, missingness, ranges, category frequencies and target distribution. Use descriptive statistics and visualisations to detect skew, impossible values and unusual subgroups.

EDA must respect the prediction timeline. Do not use test-set information to make modelling decisions. It is acceptable to inspect basic data quality and define a split, but detailed feature selection, imputation decisions and transformations should be learned from training data and validated without peeking at the test outcomes. In a real deployment, the test set represents future unseen cases.

Ask whether each feature is available at prediction time, whether the target is defined consistently, and whether the sample reflects the population in which the model will be used. A clean-looking table may still contain sampling bias, duplicate entities or leakage.

## 2. Worked example
Run in VS Code in your course virtual environment. Install packages as required: `python -m pip install numpy pandas scikit-learn matplotlib`.

```python
import pandas as pd
from sklearn.datasets import load_breast_cancer

data = load_breast_cancer(as_frame=True)
df = data.frame
print("Shape:", df.shape)
print(df.dtypes.value_counts())
print("Missing values:", df.isna().sum().sum())
print("Duplicate rows:", df.duplicated().sum())
print(df.describe().T.head())
print("Target proportions:")
print(df["target"].value_counts(normalize=True))
```

## 3. Interpretation
State what was learned from training data and what was measured on unseen data. Check whether the metric answers the real decision question. A technically correct output can still be misleading if the target, split or population is wrong.

## 4. Guided practice
Perform EDA on a dataset you select. Write down at least five checks and what each check could reveal. Find one variable whose distribution is skewed and decide whether a transformation may be useful. Explain why you should not choose a model based only on a few plots.

## 5. Independent practice
Apply the lesson to a small dataset. Record the source, unit of observation, target and feature availability. Save your code and a short report that includes evidence, limitations and the next validation step.

## 6. Knowledge check
1. What assumption is most important in this method?
2. What is the difference between training performance and generalisation?
3. How could leakage or sampling bias affect the result?
4. What would you tell a stakeholder before they use the model?

## Lesson summary
A trustworthy ML workflow is reproducible, uses a suitable baseline and evaluation design, and communicates errors and limitations as carefully as headline performance.