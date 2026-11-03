# Lesson 11: Training, Validation and Test Sets

## Learning outcomes
Explain the distinct roles of training, validation and test data; choose a suitable splitting strategy; use stratification and group/time splits appropriately; explain cross-validation; and recognise leakage between related observations.

## 1. Why split data?
A model's purpose is to make predictions for cases it has not learned from. If we evaluate it on the same examples used for fitting, we measure how well it fits known data—not how well it is likely to perform on new cases.

A held-out dataset provides an estimate of generalisation. The estimate is only meaningful if the held-out examples represent the intended future use and were not used to make modelling decisions.

![Training validation and test split](/course-assets/ws07/11-train-validation-test.svg)

## 2. Three different roles
- **Training set:** used to fit model parameters and learn preprocessing transformations.
- **Validation set:** used to compare models, select hyperparameters, choose thresholds and make development decisions.
- **Test set:** held back until the end to estimate final performance after decisions are complete.

A common split might be 70% training, 15% validation and 15% test, but there is no universal ratio. With limited data, cross-validation on the development data can be more efficient. Keep a final test set where possible.

## 3. Random train/test split
```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

data = load_iris(as_frame=True)
X, y = data.data, data.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(X_train.shape, X_test.shape)
print(y_train.value_counts(normalize=True))
print(y_test.value_counts(normalize=True))
```

- test_size=0.2 reserves 20% for testing.
- random_state makes the random selection repeatable.
- stratify=y attempts to preserve class proportions in both sets.
- X and y are split together so each feature row remains paired with its target.

Stratification is useful for classification when class proportions matter. It does not solve every sampling problem and may not be appropriate for every grouped or time-dependent dataset.

## 4. When random splitting is wrong
### Time-dependent data
If the task is to predict next month's demand, training on randomly selected future rows and testing on earlier rows can create an unrealistic evaluation. Train on the past and test on later periods.

### Grouped data
If a learner has multiple weekly records, randomly splitting rows can put the same learner in both training and test sets. The model may recognise learner-specific patterns and appear better than it would on new learners. Split by learner ID when the intended use is new learners.

![Random split leakage versus group split](/course-assets/ws07/11-group-time-split.svg)

## 5. Group-based splitting
```python
from sklearn.model_selection import GroupShuffleSplit
import numpy as np

X = np.arange(24).reshape(12, 2)
y = np.array([0, 1] * 6)
groups = np.repeat(np.arange(4), 3)

splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=4)
train_idx, test_idx = next(splitter.split(X, y, groups=groups))
print("Train groups:", np.unique(groups[train_idx]))
print("Test groups:", np.unique(groups[test_idx]))
```
GroupShuffleSplit keeps groups separate. Its test_size is based on groups, not necessarily the exact percentage of rows. Inspect the resulting class balance and sample size.

## 6. Time-based splitting
Sort by timestamp and reserve the latest period for testing. For repeated evaluation, TimeSeriesSplit creates expanding training windows and later validation windows. Do not shuffle time-series observations when chronology is part of the prediction problem.

## 7. Cross-validation
In k-fold cross-validation, training data is divided into k folds. The model is trained on k−1 folds and validated on the remaining fold; this repeats so each fold serves as validation once. Scores are then summarised. Cross-validation can reduce dependence on one random split, but the folds must respect groups or chronology when relevant.

```python
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
pipeline = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="accuracy")
print("Fold scores:", scores)
print("Mean:", scores.mean(), "Std:", scores.std())
```

Each fold gives a validation score. The mean summarises performance across folds; the standard deviation describes variation among fold scores, not a formal confidence interval. Preprocessing belongs inside the pipeline so it is refitted separately within each fold.

## 8. The danger of repeatedly checking the test set
If you try ten models and choose the one with the highest test score, the test set has influenced your choice. The reported score can become optimistically biased. Use validation or cross-validation during development. Evaluate on the test set once the approach is fixed.

## Common mistakes
- Evaluating only on training data.
- Randomly splitting future prediction tasks.
- Allowing related people or devices into both sets.
- Using the test set for hyperparameter tuning.
- Forgetting preprocessing must be refitted within each CV fold.
- Assuming stratification solves sampling bias.

## Guided practice
Use a dataset with a timestamp or repeated learner IDs. Compare a random split with a time- or group-based split. Explain which better represents the intended deployment situation and why.

## Independent practice
Design an evaluation plan for a student completion model. Specify the prediction date, unit of observation, split strategy, validation method and final test period. Explain how you will prevent the same learner from appearing across partitions if the intended use is new learners.

## Knowledge check
1. What is the role of each of the three data sets?
2. What does stratify=y do?
3. When should you use group splitting?
4. Why can a random split be misleading for time series?
5. Why must preprocessing be inside the cross-validation pipeline?

## Lesson summary
Splitting is part of experimental design. The right split imitates the real prediction setting and protects the evaluation from information leakage.