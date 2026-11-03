# Lesson 16: Support Vector Machines

## Learning outcomes

By the end of this lesson, you should be able to Explain support vector classification and the margin concept; compare linear and RBF kernels; standardise inputs; and describe how C and kernel choice affect the decision boundary.

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

## 7. Understand the model before using it

A model does not understand the world represented by its dataset. It learns a mathematical pattern from the examples it receives. The analyst supplies the meaning by defining what one row represents, which information is available at prediction time and what the target means. Explain these definitions before discussing the algorithm.

Interpret outputs carefully. Probabilities express model estimates, not certainty. Feature importance describes how a model uses information, not necessarily causal influence. Evaluation metrics summarise selected errors, not every consequence of using a model. Always connect the result to the decision and the population where it will be applied.

## 8. Build a fair and repeatable experiment

Check data types, missingness, duplicates, unusual values and target distribution. Choose a split that matches deployment: chronological for future prediction, group-aware when people or entities appear repeatedly, and stratified when preserving class proportions is important. Fit imputers, encoders and scalers on training data only. A pipeline helps ensure the same fitted transformations are applied to validation, test and future data.

Start with a baseline. Select model settings using validation data or cross-validation, then evaluate the chosen approach on a held-out test set once. Keep a record of feature definitions, random seeds, package versions, split strategy and parameter values. If the data changes, investigate whether the target definition, population or collection process also changed.

## 9. Worked reasoning example

Imagine predicting whether a learner will need additional support. Define a snapshot date, an outcome window and the intervention. Use only activity recorded before the snapshot. If the same learner appears in several rows, random splitting may put that learner in both training and test sets, making the test easier than the real task. Consider a group-based or time-based split. Inspect not only the average score but also who receives false alerts and who is missed.

## 10. Self-study and independent practice

Explain the method from memory: its purpose, required inputs, learning mechanism, an important setting, one failure mode and an appropriate evaluation strategy. Apply it to a documented dataset and produce a notebook with a precise question, data-quality checks, split rationale, baseline, candidate model, interpreted metrics, error analysis and limitations. Explain why each decision was made.

Do not remove rare observations only because they make performance worse. Determine whether they are errors, valid rare cases or evidence that the method does not work well for an important part of the population.

## 11. Knowledge check

1. What does the method learn from training examples?
2. What assumptions and parameter choices influence its behaviour?
3. What could make an evaluation result misleading?
4. How would you inspect errors beyond a single summary metric?
5. What further validation is needed before using the model in practice?
