# Lesson 2: Data Leakage and Leakage Prevention

## Learning outcomes
Explain target, temporal and preprocessing leakage; recognise leakage through duplicates and group overlap; choose an appropriate split; and use pipelines to keep learned transformations inside training folds.

## 1. What leakage means
**Data leakage** occurs when information that should not be available to a model influences training or evaluation. The model then appears more capable than it will be in real use. Leakage is dangerous because the resulting metric can look excellent while the deployed model fails.

Consider a hospital model intended to predict whether a patient will be admitted to intensive care at the moment of arrival. A column recording the ICU transfer decision would reveal the outcome. It may be strongly associated with the target, but it is recorded after the prediction moment. This is target or temporal leakage.

Leakage can enter through feature construction, splitting, preprocessing, feature selection, hyperparameter tuning or repeated inspection of the test set. It is not limited to suspicious column names.

## 2. Main forms of leakage
**Target leakage:** a feature directly or indirectly contains the answer. A refund status recorded after a purchase cannot be used to predict whether that purchase will be refunded at the moment of sale.

**Temporal leakage:** future events enter a historical prediction. Rolling averages must be shifted or bounded so they only use earlier observations.

**Preprocessing leakage:** an imputer, scaler, encoder or selector learns statistics from validation or test rows before evaluation. For example, calculating the median using the full dataset allows information about the test distribution into training.

**Group or identity leakage:** records from the same person, household, machine or organisation appear in both train and test when the deployment task requires generalisation to unseen groups.

**Duplicate leakage:** duplicate or near-duplicate examples are split across partitions, allowing the model to encounter almost the same record during training and testing.

![Leakage prevention boundary](/course-assets/ws10/leakage-boundary.svg)

## 3. Build the split around the real task
A random split is appropriate only when observations can reasonably be treated as independent and identically distributed for the intended use. If predicting the future, use a chronological split. If predicting for new customers, use group-aware splitting so a customer's records do not cross partitions. For repeated measurements, consider both time and group structure.

The test set is a final estimate, not a workspace for repeated model decisions. Use training data for fitting and cross-validation for selecting transformations and hyperparameters. Consult the final test set after the design is settled.

## 4. Worked example: leakage-safe imputation
Install scikit-learn and pandas: `python -m pip install pandas scikit-learn`.

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression

data = pd.DataFrame({
    "income": [20, 25, None, 40, 45, None, 70, 80, 30, 60],
    "late_payment": [0, 0, 0, 0, 1, 1, 0, 1, 0, 1]
})
X = data[["income"]]
y = data["late_payment"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

model = make_pipeline(
    SimpleImputer(strategy="median"),
    LogisticRegression()
)
model.fit(X_train, y_train)
print("Test accuracy:", model.score(X_test, y_test))
```

The pipeline fits the median using only the training partition, then applies that learned median to test rows. If you impute the full dataset before splitting, the test data has influenced the transformation.

## 5. A practical leakage audit
For every feature ask: when is it created? Who records it? Could it be updated after the outcome? Does it contain a summary that includes future rows? Is it derived from the target? Would it exist for a new prediction? Then inspect split boundaries, entity overlap, duplicates and transformation fitting.

A high score is not evidence that leakage is absent. A suspiciously perfect result is a reason to investigate, not celebrate.

## 6. Common mistakes
- Randomly splitting time-series data and claiming future forecasting ability.
- Fitting a scaler or imputer before splitting.
- Selecting features using the complete dataset.
- Letting the same customer appear in train and test when unseen-customer performance is the goal.
- Repeatedly changing the model after inspecting test errors.
- Removing a suspicious feature without investigating how it was generated.

## 7. Guided practice
A bank wants to predict loan default at application time. Review these fields: application income, credit history, repayment status six months later, date of application, loan decision and customer ID. Classify each as potentially valid, leakage-prone or dependent on the precise prediction question. Explain your reasoning.

## 8. Independent practice
Take a dataset with dates or repeated entities. Design a split that reflects deployment. Write code to check for overlapping customer IDs or duplicated rows across partitions. Explain what your checks do not prove.

## Knowledge check
1. Why can a feature with strong predictive power still be invalid?
2. How does a pipeline reduce preprocessing leakage?
3. When is a chronological split preferable?
4. Why might group-aware splitting be necessary?
5. Why should the test set be used sparingly?

## Lesson summary
Leakage creates false confidence. Define prediction time, investigate feature lineage, split according to the deployment scenario and fit every learned preprocessing step only on the training data within a pipeline.

## 7. Deeper reasoning: leakage is a question about information flow

The central leakage question is not simply “Does this column look suspicious?” It is “Could this exact value have been known at the instant this prediction is supposed to happen?” A variable may be legitimate in one task and leakage in another. A payment status is valid when predicting whether a payment will fail tomorrow if it describes yesterday's payments; it is invalid if it is the final settlement status of the payment being predicted.

Draw a simple timeline for the use case. Mark the prediction timestamp, the period from which the target is measured and the moment each candidate feature becomes available. If the target is whether a customer will cancel within the next 30 days, the model might be scored at the end of each month. A feature such as “support tickets in the previous 60 days” is valid if ticket timestamps are reliable. “Final cancellation reason” is not valid because it is recorded after cancellation.

Leakage can also arise from how records are created. Suppose one customer contributes ten monthly rows. A random row split can put January and February for that customer in training and March in testing. If the task is to predict future months for existing customers, this may be acceptable only if the historical information is available and the validation design reflects the same future prediction process. If the goal is to predict for entirely new customers, all rows for each customer must remain in one partition.

A useful audit therefore includes feature timing, entity relationships, duplicates, target construction and preprocessing. When a model produces an implausibly high score, trace the data flow rather than assuming the algorithm is unusually powerful. Leakage is often a dataset-design problem disguised as a modelling success.