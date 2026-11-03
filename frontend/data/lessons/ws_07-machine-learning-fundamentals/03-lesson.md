# Lesson 3: The End-to-End Machine Learning Workflow

## Learning outcomes
Describe a complete ML project; explain why problem framing and data understanding come before algorithms; distinguish training, validation and testing; recognise leakage; and document reproducible decisions.

## 1. ML is a workflow, not a fit() call
A common beginner mistake is to load a dataset, call model.fit(), print accuracy and declare success. A reliable project has important stages before and after training. An algorithm cannot rescue an invalid target, contaminated data or an evaluation that does not represent future use.

![End-to-end machine learning workflow](/course-assets/ws07/03-ml-workflow.svg)

## 2. Frame the problem
Translate a broad request into a testable prediction task. "Use AI to improve student performance" is vague. A clearer question is: "Using information available at the end of week two, estimate whether an enrolled learner will complete the course by its scheduled end date."

Define the decision, unit of observation, target, prediction time, intended user, error costs and success measure. This forces you to consider what information exists when the prediction must be made.

## 3. Understand the data
Identify the source, ownership, permission, collection process and time period. Inspect rows, columns, data types, missingness, duplicates, ranges, category frequencies and target distribution.

Ask what a row represents. A table with one row per transaction differs from one row per customer. Joining customer-level data to transaction-level data can duplicate values and change the effective weighting of observations.

Create a data dictionary recording variable name, meaning, type, unit, allowed values, source and availability time.

## 4. Split data to simulate future use
A test set estimates performance on unseen cases. If you use it to choose features, tune hyperparameters or decide when to stop, it is no longer an untouched final test.

Random splitting may suit independent rows. Time-dependent tasks need chronological splitting. Repeated records from the same person or device may require group splitting so related records do not appear in both training and test sets.

![Train validation and test split](/course-assets/ws07/03-data-splitting.svg)

## 5. Establish a baseline
A baseline is a simple reference prediction. For classification, predict the most frequent training class. For regression, predict the training mean or median. A useful business baseline may be the existing human process or a simple rule. A sophisticated model should demonstrate a meaningful improvement.

## 6. Prepare data without leakage
Typical steps include imputing missing values, encoding categories, scaling numeric features and engineering useful variables. Fit preprocessing on training data only. For example, calculate a scaler's mean from training data, then reuse that same mean for validation and test data.

Scikit-learn pipelines keep transformations and the model together. This reduces the chance of accidentally learning preprocessing information from held-out data.

## 7. Train and validate
Training estimates model parameters. Validation compares candidate models and settings. Hyperparameters are choices such as tree depth or regularisation strength. Use validation or cross-validation to select them, not the final test set.

## 8. Evaluate errors
Choose metrics based on the task. Classification may require precision, recall, F1, ROC-AUC or PR-AUC. Regression may require MAE, RMSE or R-squared. Inspect confusion matrices, residuals and examples of incorrect predictions. Average performance can hide serious weaknesses for a subgroup.

## 9. Communicate, deploy and monitor
Document data, split, preprocessing, model, metrics, limitations and intended use. Deployment makes the model available to a workflow; it does not make the model permanently correct. Data and behaviour can change. Monitor input distributions, errors, outcomes and impact. Have a plan to retrain, roll back or stop using the system.

## 10. A compact baseline workflow
```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.metrics import classification_report

df = pd.DataFrame({
    "study_hours": [1, 2, 3, 4, 5, 1, 6, 2, 7, 3, 8, 4],
    "attendance": [40, 55, 65, 70, 85, 35, 90, 50, 95, 60, 98, 75],
    "passed": [0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1]
})
X = df[["study_hours", "attendance"]]
y = df["passed"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=5, stratify=y
)
baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(X_train, y_train)
print(classification_report(
    y_test, baseline.predict(X_test), zero_division=0
))
```

This is an intentionally simple baseline on invented data. It demonstrates input/target separation, splitting, fitting and held-out evaluation. It is not a student-risk system.

## 11. Reproducibility
Record package versions, random seeds, data source and version, preprocessing, feature definitions, split strategy, model parameters and evaluation results. A seed makes certain random operations repeatable; it does not guarantee identical results across every library version or hardware environment.

## Common mistakes
- Splitting after fitting preprocessing on the full dataset.
- Using future information as a feature.
- Tuning repeatedly against the test set.
- Randomly splitting time-series rows.
- Reporting one metric without examining errors.
- Forgetting monitoring after deployment.

## Guided practice
Draw the workflow for predicting delivery delays. Mark when the target becomes known, what data is available at prediction time, how records should be split and what false predictions might cost.

## Independent practice
Write a project plan for a dataset you can access. For every stage, state its output and one risk to check before proceeding.

## Knowledge check
1. Why must the test set remain untouched during model selection?
2. What is data leakage?
3. When is chronological splitting preferable?
4. What does a baseline tell us?
5. Why does a deployed model need monitoring?

## Lesson summary
A dependable model comes from a well-designed workflow. Framing, data quality, leakage-safe evaluation and communication matter as much as the algorithm.