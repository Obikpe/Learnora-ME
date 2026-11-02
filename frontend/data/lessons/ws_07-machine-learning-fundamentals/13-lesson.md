# Lesson 13: Underfitting, Overfitting and Generalisation

## Learning outcomes
Explain the method, implement the example in Python, interpret its result, and identify risks that could invalidate the conclusion.

## 1. Concepts and reasoning
Underfitting occurs when a model is too simple to capture the important structure in the data. It performs poorly on both training and unseen data. Overfitting occurs when a model learns noise or accidental details in the training sample. It performs well on training data but poorly on new examples. Generalisation is the ability to perform on data drawn from the intended future population.

Model complexity can increase training performance while reducing test performance. More features, deeper trees or more flexible functions can lower training error but may increase variance. Regularisation, simpler models, more representative data and careful validation can help. More training data can help when the current sample is limited and representative, but it cannot fix systematic bias in collection.

The bias-variance trade-off is a useful conceptual framework: high bias often accompanies underfitting; high variance often accompanies overfitting. The objective is not to make the training score perfect. It is to find a model that performs reliably on new data.

## 2. Worked example
Run in VS Code in your course virtual environment. Install packages as required: `python -m pip install numpy pandas scikit-learn matplotlib`.

```python
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

X, y = make_moons(n_samples=500, noise=0.25, random_state=3)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=3, stratify=y
)
for depth in [1, 2, 4, 10, None]:
    model = DecisionTreeClassifier(max_depth=depth, random_state=3)
    model.fit(X_train, y_train)
    print(depth, accuracy_score(y_train, model.predict(X_train)),
          accuracy_score(y_test, model.predict(X_test)))
```

## 3. Interpretation
State what was learned from training data and what was measured on unseen data. Check whether the metric answers the real decision question. A technically correct output can still be misleading if the target, split or population is wrong.

## 4. Guided practice
Run the example and record training and test accuracy for each depth. Identify a depth where the training score is high but test score is lower. Explain why a deeper tree is not automatically a better model.

## 5. Independent practice
Apply the lesson to a small dataset. Record the source, unit of observation, target and feature availability. Save your code and a short report that includes evidence, limitations and the next validation step.

## 6. Knowledge check
1. What assumption is most important in this method?
2. What is the difference between training performance and generalisation?
3. How could leakage or sampling bias affect the result?
4. What would you tell a stakeholder before they use the model?

## Lesson summary
A trustworthy ML workflow is reproducible, uses a suitable baseline and evaluation design, and communicates errors and limitations as carefully as headline performance.