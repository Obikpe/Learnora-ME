# Lesson 11: Training, Validation and Test Sets

## Learning outcomes
Explain the method, implement the example in Python, interpret its result, and identify risks that could invalidate the conclusion.

## 1. Concepts and reasoning
A model's performance on training data is usually optimistic because the model has already used those examples to learn. A test set estimates performance on unseen observations. A validation set or cross-validation is used to compare models and tune choices. The test set should be consulted once at the end, after the modelling decisions are fixed.

For classification, stratification preserves approximate class proportions in each split. For repeated measurements, split by person, device or other group to prevent related rows appearing in both partitions. For future prediction, use a time-based split: train on the past and test on later observations. Random splitting would allow future patterns to influence a past prediction.

A split is part of the experiment design. Document its random seed, proportions and grouping logic. If the dataset is small, repeated cross-validation can make better use of the training data, but it does not eliminate the need for a final unbiased assessment.

## 2. Worked example
Run in VS Code in your course virtual environment. Install packages as required: `python -m pip install numpy pandas scikit-learn matplotlib`.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

data = load_breast_cancer(as_frame=True)
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print("Train:", X_train.shape, "Test:", X_test.shape)
print("Train positive rate:", y_train.mean())
print("Test positive rate:", y_test.mean())
```

## 3. Interpretation
State what was learned from training data and what was measured on unseen data. Check whether the metric answers the real decision question. A technically correct output can still be misleading if the target, split or population is wrong.

## 4. Guided practice
Create both a random split and a time-ordered split for a time-stamped dataset. Compare what each test set represents. Explain why a random split can produce an unrealistically easy test when predicting future demand.

## 5. Independent practice
Apply the lesson to a small dataset. Record the source, unit of observation, target and feature availability. Save your code and a short report that includes evidence, limitations and the next validation step.

## 6. Knowledge check
1. What assumption is most important in this method?
2. What is the difference between training performance and generalisation?
3. How could leakage or sampling bias affect the result?
4. What would you tell a stakeholder before they use the model?

## Lesson summary
A trustworthy ML workflow is reproducible, uses a suitable baseline and evaluation design, and communicates errors and limitations as carefully as headline performance.