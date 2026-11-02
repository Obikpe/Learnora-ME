# Lesson 20: Comparing Models Fairly

## Learning outcomes
Explain the technique, implement the example, interpret the output and justify when the method is suitable.

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