# Lesson 14: Baseline Models and Evaluation

## Learning outcomes
Explain the method, implement the example in Python, interpret its result, and identify risks that could invalidate the conclusion.

## 1. Concepts and reasoning
A baseline is a simple reference model that establishes what “good” means. For regression, predicting the training-set mean or median is a useful starting point. For classification, predicting the most frequent class is a simple baseline. A useful operational baseline might instead be the existing business rule or current human process.

Choose metrics according to the task. MAE reports average absolute error in target units. RMSE penalises large errors more strongly and is in target units. Accuracy is the proportion of correct classifications, but can be misleading with imbalanced classes. Compare a candidate model against the baseline on the same held-out data.

A model that barely beats a naive baseline may not justify its complexity or maintenance cost. Report the metric, split strategy, sample size and uncertainty. Never compare numbers produced using different test sets as if they were directly comparable.

## 2. Worked example
Run in VS Code in your course virtual environment. Install packages as required: `python -m pip install numpy pandas scikit-learn matplotlib`.

```python
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

data = load_diabetes(as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)
for model in [DummyRegressor(strategy="median"),
              RandomForestRegressor(n_estimators=100, random_state=42)]:
    model.fit(X_train, y_train)
    print(type(model).__name__, mean_absolute_error(y_test, model.predict(X_test)))
```

## 3. Interpretation
State what was learned from training data and what was measured on unseen data. Check whether the metric answers the real decision question. A technically correct output can still be misleading if the target, split or population is wrong.

## 4. Guided practice
Compare the two MAE values. If the random forest improves MAE only slightly, list costs (latency, interpretability, maintenance, compute) that should be considered before selecting it.

## 5. Independent practice
Apply the lesson to a small dataset. Record the source, unit of observation, target and feature availability. Save your code and a short report that includes evidence, limitations and the next validation step.

## 6. Knowledge check
1. What assumption is most important in this method?
2. What is the difference between training performance and generalisation?
3. How could leakage or sampling bias affect the result?
4. What would you tell a stakeholder before they use the model?

## Lesson summary
A trustworthy ML workflow is reproducible, uses a suitable baseline and evaluation design, and communicates errors and limitations as carefully as headline performance.