# Lesson 12: Train, Validation and Test Strategy

## Learning outcomes
Distinguish training, validation and test data; choose a split strategy based on the data-generating process; explain stratification and group/time splitting; and protect the final test set from repeated model decisions.

## 1. Why split data?
A model can memorise patterns in its training data. The real question is how well it performs on observations it has not used to fit its parameters. A holdout set provides evidence about generalisation, provided the split resembles the intended deployment scenario.

The **training set** is used to fit model parameters and learned preprocessing. The **validation set** supports model selection and tuning. The **test set** is reserved for a final estimate after decisions are complete. In cross-validation, the validation role is repeated across folds.

Not every project needs three permanent partitions. With limited data, cross-validation may provide a better use of observations. The key principle remains: do not repeatedly optimise decisions against the same data and then present its score as an unbiased final estimate.

## 2. Choose a split that matches deployment
**Random split:** useful when observations are approximately independent and identically distributed.

**Stratified split:** preserves approximate class proportions for classification. It does not solve group leakage or time leakage.

**Group split:** keeps all rows from a group, such as a customer or patient, in one partition. Use it when the goal is generalisation to unseen groups.

**Time split:** trains on earlier observations and evaluates on later observations. Use it when predicting future periods.

![Data splitting strategies](/course-assets/ws10/splitting-strategies.svg)

## 3. Worked example
```python
import pandas as pd
from sklearn.model_selection import (
    train_test_split, GroupShuffleSplit, TimeSeriesSplit
)

# Stratified random split for independent classification rows
X = pd.DataFrame({"value": range(20)})
y = pd.Series([0] * 12 + [1] * 8)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)
print(y_train.value_counts(normalize=True))
print(y_test.value_counts(normalize=True))

# Group split: keep each customer in one partition
groups = pd.Series([1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10])
group_split = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
train_idx, test_idx = next(group_split.split(X, y, groups))
print("Group overlap:", set(groups.iloc[train_idx]) & set(groups.iloc[test_idx]))

# TimeSeriesSplit creates expanding historical training windows
time_cv = TimeSeriesSplit(n_splits=3)
for train_idx, test_idx in time_cv.split(X):
    print("Train ends:", train_idx[-1], "test starts:", test_idx[0])
```

Stratification preserves class proportions but not time order. GroupShuffleSplit preserves groups but does not necessarily preserve class balance. TimeSeriesSplit respects chronology, but you must still consider whether the gap between training and test windows is sufficient to prevent overlapping labels or look-ahead features.

## 4. How much data belongs in each partition?
There is no universal 70/15/15 rule. The correct allocation depends on dataset size, class balance, number of groups, time horizon and uncertainty you can tolerate. A very small test set produces a noisy metric. A large test set leaves less data for learning. Explain your choice.

## 5. Common mistakes
- Using a random split for a forecasting problem.
- Stratifying repeated customer records but allowing the same customer in both sets.
- Tuning repeatedly on the final test set.
- Splitting after feature selection or preprocessing.
- Ignoring class imbalance.
- Forgetting that a test score has sampling uncertainty.

## Guided practice
For each scenario choose a split: predicting next month's demand, predicting churn for existing customers, classifying independent product images, predicting outcomes for new hospitals. Explain the unit of separation.

## Independent practice
Implement random stratified, group and chronological splits on suitable example data. Verify class proportions, group overlap and date ordering. Write a paragraph explaining which split best reflects the intended use of your chosen dataset.

## Knowledge check
1. What is the role of the training set?
2. Why should the final test set be protected?
3. What does stratification preserve?
4. When is group splitting required?
5. Why is a chronological split important for future prediction?

## Lesson summary
A valid metric depends on a valid split. Choose partitions according to how future predictions will be made, and protect held-out data from every fitting and selection step.