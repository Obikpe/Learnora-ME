# Lesson 22: Feature Importance and Interpretation

## Learning outcomes
Explain the technique, implement the example, interpret the output and justify when the method is suitable.

## 1. Core explanation
Interpretation explains how a model uses inputs. Linear coefficients describe changes in the model output under the fitted parameterisation. Tree importance often measures impurity reduction. Permutation importance measures the decline in a validation score when one feature is shuffled. SHAP-style methods attribute individual predictions, but explanations depend on assumptions about feature dependence and the background distribution.

Importance is not causality. Correlated features can substitute for one another, making individual importance appear small. A high-importance feature may be a proxy for a sensitive attribute or encode leakage. Check whether a feature is available and appropriate at prediction time.

Use global interpretation to understand overall model behaviour and local interpretation to inspect individual cases. Explain the model version, dataset and metric. Do not present an explanation as a guaranteed account of the real-world process that generated the outcome.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may require internet access on first use.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42, stratify=data.target)
model = RandomForestClassifier(n_estimators=200, random_state=42).fit(Xtr, ytr)
result = permutation_importance(model, Xte, yte, n_repeats=8, random_state=42)
ranking = sorted(zip(data.feature_names, result.importances_mean),
                 key=lambda item: item[1], reverse=True)
print(ranking[:8])
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report dataset limitations.

## 4. Guided practice
Investigate one highly ranked feature: its definition, units, missingness and availability at prediction time. Identify a correlated feature and explain how correlation complicates ranking.

## 5. Independent practice
Extend the example with another model or evaluation view. Compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder and state what further validation is required.

## 6. Knowledge check
1. What does the method estimate or optimise?
2. Which assumptions and settings affect its behaviour?
3. How could leakage or an inappropriate split inflate performance?
4. What evidence is needed before use?

## Lesson summary
Supervised learning is an evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.