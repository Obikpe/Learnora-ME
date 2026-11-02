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