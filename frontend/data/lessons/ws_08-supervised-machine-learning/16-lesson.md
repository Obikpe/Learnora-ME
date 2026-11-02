# Lesson 16: Support Vector Machines

## Learning outcomes
Explain the technique, implement the worked example, interpret the output and justify when the method is suitable.

## 1. Core explanation
A support vector machine (SVM) seeks a decision boundary with a large margin between classes. Support vectors are the observations closest to the boundary. A linear SVM uses a straight boundary; kernel methods allow non-linear boundaries by computing similarities in a transformed feature space.

The C parameter controls the trade-off between a wider margin and classification errors. Kernel parameters such as gamma affect how local the decision boundary becomes. SVMs are sensitive to feature scaling, so standardise numeric features inside a Pipeline. Probability estimates may require additional calibration and can be computationally expensive.

SVMs can work well on medium-sized, high-dimensional datasets, but training may be slow for very large samples. Always compare against simpler baselines and inspect per-class metrics. A complex kernel boundary may fit noise and be difficult to explain.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may need internet access on first use.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42, stratify=data.target)
for kernel in ["linear", "rbf"]:
    model = make_pipeline(StandardScaler(), SVC(C=1.0, kernel=kernel))
    model.fit(Xtr, ytr)
    print(kernel, model.score(Xte, yte))
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report the limitations of the dataset.

## 4. Guided practice
Compare linear and RBF kernels. Then vary C. Explain how scaling affects the margin and why test score should not be used repeatedly to tune parameters.

## 5. Independent practice
Extend the example with a second model or a different evaluation view. Keep a record of every change and compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder.

## 6. Knowledge check
1. What does this method optimise or estimate?
2. Which assumptions or settings affect its behaviour?
3. How would you detect overfitting or leakage?
4. What evidence is needed before the model is used?

## Lesson summary
Supervised learning is a complete evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.