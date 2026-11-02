# Lesson 23: Multi-Class Classification

## Learning outcomes
Explain the technique, implement the example, interpret the output and justify when the method is suitable.

## 1. Core explanation
Multiclass classification predicts one of more than two mutually exclusive classes. One-vs-rest trains a binary classifier for each class; one-vs-one trains classifiers for pairs. Some algorithms handle multiclass natively. Class probabilities should sum to one when the model provides a normalised multiclass probability distribution.

A confusion matrix reveals which classes are confused. Accuracy alone can hide poor recall for a rare class. Macro averaging gives each class equal weight; weighted averaging weights by support. Choose the average based on the application and report per-class results.

Class labels may have a natural hierarchy or order. If errors have different severity, a standard multiclass metric may not reflect the cost. Consider ordinal methods or a cost matrix where justified.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may require internet access on first use.

```python
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report

data = load_wine(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.25, random_state=42, stratify=data.target)
model = RandomForestClassifier(n_estimators=200, random_state=42).fit(Xtr, ytr)
pred = model.predict(Xte)
print(confusion_matrix(yte, pred))
print(classification_report(yte, pred, target_names=data.target_names))
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report dataset limitations.

## 4. Guided practice
Identify the class with the lowest recall. Explain why macro F1 and weighted F1 may differ and choose which should be highlighted when class frequencies are unequal.

## 5. Independent practice
Extend the example with another model or evaluation view. Compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder and state what further validation is required.

## 6. Knowledge check
1. What does the method estimate or optimise?
2. Which assumptions and settings affect its behaviour?
3. How could leakage or an inappropriate split inflate performance?
4. What evidence is needed before use?

## Lesson summary
Supervised learning is an evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.