# Lesson 19: Cross-Validation for Supervised Models

## Learning outcomes

By the end of this lesson, you should be able to Explain k-fold and stratified cross-validation; choose group-aware or time-aware splitters when needed; keep preprocessing inside a pipeline; and interpret fold-level variation.

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
