# Lesson 12: K-Nearest Neighbours

## Learning outcomes

By the end of this lesson, you should be able to Explain distance-based K-nearest neighbours; standardise numeric features; compare neighbourhood sizes; and describe the effect of feature scale, distance and the choice of k.

## 1. Core explanation
K-nearest neighbours (KNN) predicts from the labels or values of the closest training observations. For classification, it uses a majority vote among the k neighbours; for regression, it averages their target values. “Closeness” is defined by a distance measure such as Euclidean distance.

KNN is sensitive to feature scales. If income ranges into millions and age ranges into tens, income can dominate Euclidean distance. Standardise numeric features using a scaler fitted on training data. KNN also becomes expensive as the training set grows because it must compare new points with stored examples.

Small k values create flexible decision boundaries and may overfit; large k values smooth predictions and may underfit. Select k through cross-validation. Consider the curse of dimensionality: in many dimensions, distances become less informative and the concept of nearest can lose meaning.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may need internet access on first use.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42, stratify=data.target)
for k in [3, 5, 15, 31]:
    model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k))
    model.fit(Xtr, ytr)
    print(k, accuracy_score(yte, model.predict(Xte)))
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report the limitations of the dataset.

## 4. Guided practice
Compare k values and explain the trend. Remove the scaler and rerun. Why might performance change? Explain why the scaler must be inside the Pipeline during cross-validation.

## 5. Independent practice
Extend the example with a second model or a different evaluation view. Keep a record of every change and compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder.

## 6. Knowledge check
1. What does this method optimise or estimate?
2. Which assumptions or settings affect its behaviour?
3. How would you detect overfitting or leakage?
4. What evidence is needed before the model is used?

## Lesson summary
Supervised learning is a complete evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.

## 7. Understand the model before using it

A machine-learning algorithm is a procedure for finding a useful pattern in examples. It does not understand the real-world meaning of a row. That meaning comes from the way the analyst defines the observation, target, features and prediction time. Begin by describing these in plain language. Then explain what the algorithm changes during training and what it produces for an unseen observation.

Interpret every output in context. A probability is not a guarantee; a coefficient is not automatically a causal effect; a feature-importance score is not proof that changing the feature will change the target. Evaluation metrics summarise selected aspects of performance and can hide important errors. Translate them into practical consequences.

## 8. A disciplined modelling workflow

Inspect the target and feature columns before fitting. Check data types, missing values, duplicated observations, unusual values and class balance. Decide how the data should be split based on how the model will be used. Random splitting is not always appropriate: future forecasting usually requires time-ordered evaluation, while repeated observations from the same person may require group-aware splitting.

Fit preprocessing steps on training data only. Keep transformations and estimators together in a pipeline so the same operations are applied consistently at prediction time. Establish a simple baseline, train a candidate, select settings using validation or cross-validation, and reserve the test set for final evaluation. Record package versions, random seeds, feature definitions and modelling choices.

## 9. Worked reasoning example

Suppose an analyst is predicting late repayment. One row represents an account at the end of a billing period, and the target indicates whether repayment becomes more than 30 days late in the next period. Current balance and previous repayment behaviour may be available; the actual next-period payment is not. Including that future payment would leak the answer. A model must be evaluated on accounts and time periods that reflect its intended use. Its errors should then be reviewed in terms of the operational cost of unnecessary alerts and missed late payments.

## 10. Self-study and independent practice

Explain the technique from memory, including its purpose, the information it requires, its central learning mechanism, an important setting, a likely failure mode and a suitable evaluation approach. Then apply it to a documented dataset. Include a clear problem statement, data-quality checks, a defensible split, baseline comparison, explained metrics, error inspection and limitations. Record why each preprocessing decision was made; do not delete difficult observations merely to improve the score.

## 11. Knowledge check

1. What does the technique learn, and what does it output?
2. Which assumptions or parameter choices matter most?
3. What would constitute leakage in this problem?
4. How would you know whether the model generalises?
5. What additional evidence is needed before using the result to support a real decision?

Explain your reasoning in complete sentences. If you cannot justify a modelling choice in ordinary language, revisit the lesson before moving on.
