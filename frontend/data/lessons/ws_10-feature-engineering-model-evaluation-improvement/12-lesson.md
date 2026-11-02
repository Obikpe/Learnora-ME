# Lesson 12: Train/Validation/Test Strategy

## Learning outcomes

By the end of this lesson, you should be able to Build a preprocessing workflow with Pipeline and ColumnTransformer; keep numeric and categorical steps separate; fit transformations within cross-validation; and inspect the transformed feature space.

## 1. Core explanation
The training set fits model parameters. Validation data or cross-validation supports model and hyperparameter selection. The test set estimates final performance on unseen data and must remain untouched until the choices are fixed. Repeatedly checking test performance turns the test set into another validation set and creates optimism.

Random splitting is suitable only when observations are independent and future data resembles the sample. Use group-aware splitting when a person, account or device has repeated records. Use time-ordered splitting when predicting future outcomes. Stratify classification splits when preserving class proportions is appropriate.

Document the split unit, dates, random seed and proportions. If the real deployment setting is new customers, the test must represent new customers. If deployment is next month's demand, the test should represent a later time period.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

data = load_breast_cancer(as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=.2, random_state=42, stratify=data.target
)
print(X_train.shape, X_test.shape)
print(y_train.mean(), y_test.mean())
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune a threshold, select features or choose hyperparameters.

## 4. Guided practice
Describe a repeated-customer dataset. Design a split that prevents the same customer appearing in training and test. Explain how your choice changes the question the test score answers.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.