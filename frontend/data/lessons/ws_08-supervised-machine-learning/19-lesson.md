# Lesson 19: Cross-Validation for Supervised Models

## Learning outcomes
Explain the technique, implement the example, interpret the output and justify when the method is suitable.

## 1. Core explanation
Cross-validation estimates performance by repeatedly dividing available training data into folds. In k-fold cross-validation, each fold acts as validation once while the others train. Scores are summarised across folds. StratifiedKFold preserves class proportions; GroupKFold keeps related groups together; TimeSeriesSplit respects temporal order.

Cross-validation is useful for model and hyperparameter selection, especially when data is limited. It does not create more independent observations and cannot correct a biased dataset. If rows are grouped by customer or patient, ordinary random folds can leak information. Choose a splitter that matches the data-generation process.

Preprocessing must be inside a Pipeline so each fold learns imputation, scaling and encoding from its own training partition. Use the final test set only after model selection is complete.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may require internet access on first use.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

data = load_breast_cancer(as_frame=True)
pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(pipe, data.data, data.target, cv=cv, scoring="f1")
print("Fold scores:", scores)
print("Mean F1:", scores.mean(), "Std:", scores.std())
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report dataset limitations.

## 4. Guided practice
Compare stratified folds with a group-aware split for repeated customers. Explain why the correct splitter depends on how future predictions will be made.

## 5. Independent practice
Extend the example with another model or evaluation view. Compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder and state what further validation is required.

## 6. Knowledge check
1. What does the method estimate or optimise?
2. Which assumptions and settings affect its behaviour?
3. How could leakage or an inappropriate split inflate performance?
4. What evidence is needed before use?

## Lesson summary
Supervised learning is an evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.