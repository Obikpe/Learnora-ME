# Lesson 18: Bias-Variance Trade-Off

## Learning outcomes
Explain bias and variance intuitively; recognise underfitting and overfitting; interpret training and validation performance together; and describe how model complexity and regularisation affect generalisation.

## 1. Why training performance is not enough
A model can perform very well on training data but poorly on unseen observations. It may have memorised accidental details instead of learning stable patterns. Conversely, a model can be so simple that it cannot represent important relationships. Reliable modelling seeks a balance.

**Bias** describes error caused by overly restrictive assumptions or a model that cannot capture the underlying pattern. **Variance** describes sensitivity to the particular sample: a high-variance model changes substantially when trained on a different sample.

## 2. Underfitting and overfitting
Underfitting occurs when the model is too simple, the features are inadequate or the training process has not learned enough. Training and validation performance are both poor.

Overfitting occurs when the model captures noise or sample-specific patterns. Training performance is strong but validation performance is noticeably worse.

The goal is not to minimise training error at any cost. It is to find a model that performs well on unseen data and remains stable.

![Bias variance conceptual diagram](/course-assets/ws10/bias-variance.svg)

## 3. What changes complexity?
A deeper decision tree can represent more complex boundaries but may fit noise. A high-degree polynomial can model curves but can also oscillate. A large number of features may allow more flexibility. Regularisation constrains parameters. More representative training data can reduce uncertainty, although it does not fix systematic bias or leakage.

## 4. Worked example: decision tree depth
```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

for depth in [1, 2, 3, 5, 10, None]:
    model = DecisionTreeClassifier(
        max_depth=depth, random_state=42
    )
    model.fit(X_train, y_train)
    train_score = accuracy_score(y_train, model.predict(X_train))
    test_score = accuracy_score(y_test, model.predict(X_test))
    print(depth, round(train_score, 3), round(test_score, 3))
```

A shallow tree may underfit; an unrestricted tree may fit the training data extremely closely. The held-out score helps reveal the generalisation gap. Do not choose a depth from one test set repeatedly; use cross-validation for model selection and reserve the test set for final evaluation.

## 5. Diagnose rather than guess
If both training and validation errors are high, consider richer features, a more flexible model, better data or reduced regularisation. If training error is low and validation error is high, consider stronger regularisation, simpler models, more representative data, leakage checks and data-quality issues.

Learning curves can help: they plot training and validation performance as training sample size increases. They can reveal whether more data may help or whether the model is limited by bias.

## 6. Common mistakes
- Calling every train/validation gap overfitting without checking split quality.
- Assuming a more complex model is always better.
- Using test performance to tune complexity repeatedly.
- Ignoring noisy labels or distribution shift.
- Treating bias and variance as mutually exclusive causes.
- Assuming more data automatically fixes a poor feature definition.

## Guided practice
A model has 98% training accuracy and 72% validation accuracy. List possible explanations and propose checks before changing the model.

## Independent practice
Plot learning curves for a simple and a more complex model. Compare training and validation scores, describe the gap and recommend a next experiment.

## Knowledge check
1. What is bias in model learning?
2. What is variance?
3. What does underfitting look like?
4. What does overfitting look like?
5. Name two ways to reduce variance.

## Lesson summary
Bias and variance describe different sources of generalisation error. Use training and validation behaviour, learning curves and sound split checks to diagnose whether a model is too simple, too flexible or trained on unrepresentative data.