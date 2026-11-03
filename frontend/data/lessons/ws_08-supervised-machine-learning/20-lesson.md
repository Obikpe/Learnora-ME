# Lesson 20: Comparing Models Fairly

## Learning outcomes

By the end of this lesson, you should be able to Compare candidate models on identical folds and metrics; report score variability; avoid selecting on the final test set; and consider simplicity, latency, fairness and maintainability alongside score.

## 1. Core explanation
A fair comparison uses the same target definition, observations, split strategy and metric. If one model is evaluated on an easier subset, its score cannot be compared directly. Compare a simple baseline, a transparent model and more complex candidates. Record training time and inference cost when relevant.

Use cross-validation on training data to compare candidates. Then refit the selected workflow on the full training partition and evaluate once on the held-out test set. Avoid selecting a model because it has the highest score among many test-set experiments; that indirectly overfits the test set.

Report uncertainty and practical significance. A small gain may be noise or may matter at very large scale. Consider subgroup performance, calibration, latency, maintainability and interpretability. The best model meets decision requirements reliably, not necessarily the highest single metric.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may require internet access on first use.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

data = load_breast_cancer(as_frame=True)
models = {
    "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
    "forest": RandomForestClassifier(n_estimators=200, random_state=42)
}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for name, model in models.items():
    scores = cross_validate(model, data.data, data.target, cv=cv,
                            scoring=["accuracy", "f1", "roc_auc"])
    print(name, {m: scores["test_"+m].mean()
                 for m in ["accuracy", "f1", "roc_auc"]})
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report dataset limitations.

## 4. Guided practice
Create a comparison table with mean cross-validation score, variability, training time, interpretability and inference cost. Explain why a small metric advantage may not justify a much more complex model.

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
