# Lesson 18: Bias-Variance Trade-Off

## Learning outcomes

By the end of this lesson, you should be able to Explain the bias-variance trade-off; compare training and held-out scores across model complexity; diagnose underfitting and overfitting; and propose a controlled improvement.

## 1. Core explanation
Bias describes systematic error from assumptions that are too restrictive; variance describes sensitivity to the particular training sample. A simple model may underfit with high bias. A very flexible model may overfit with high variance. The goal is to balance the two so performance generalises.

Training and validation curves help diagnose the problem. If both errors are high, the model may underfit. If training error is low but validation error is much higher, the model may overfit. More representative training data, regularisation, simpler models and better features can help depending on the cause.

The bias-variance framework is a conceptual guide, not a complete diagnosis. Label noise, distribution shift, leakage and data quality can also explain poor performance. Change one factor at a time and validate the effect.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

X, y = make_moons(n_samples=500, noise=.25, random_state=3)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.3,
                                      random_state=3, stratify=y)
for depth in [1, 2, 4, 10, None]:
    m = DecisionTreeClassifier(max_depth=depth, random_state=3).fit(Xtr, ytr)
    print(depth, accuracy_score(ytr, m.predict(Xtr)),
          accuracy_score(yte, m.predict(Xte)))
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune a threshold, select features or choose hyperparameters.

## 4. Guided practice
Record training and test scores. Identify underfit and overfit candidates. Suggest one change for each and explain why a perfect training score is not the objective.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.