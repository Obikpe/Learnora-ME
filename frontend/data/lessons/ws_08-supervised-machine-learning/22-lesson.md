# Lesson 22: Error Analysis and Diagnostics

## Learning outcomes

By the end of this lesson, you should be able to Inspect false positives, false negatives or large residuals; identify patterns in error cases; compare errors across meaningful subgroups; and propose evidence-based improvements without tuning on the test set.

## 1. Core explanation
Error analysis asks where and why a model fails. For regression, inspect residuals against predictions, features, time and important groups. For classification, examine false positives and false negatives, confidence scores and subgroup metrics. Read misclassified examples where permitted and look for systematic patterns.

Errors may come from poor labels, missing features, distribution shift, data quality, an unsuitable objective or a model that is too simple. Do not immediately add complexity. First verify that target and features are correct and that the evaluation split represents the intended use.

Prioritise errors by impact. A model can have a strong overall score but fail badly on a small, important group. Document what is known, what is hypothesised and what needs further evidence. Avoid exposing personal data in debugging reports; use secure, minimal examples.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may require internet access on first use.

```python
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42, stratify=data.target)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(Xtr, ytr)
errors = Xte.copy()
errors["actual"] = yte
errors["predicted"] = model.predict(Xte)
print(errors[errors.actual != errors.predicted].head())
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report dataset limitations.

## 4. Guided practice
Inspect misclassified rows. Look for a feature range or subgroup where errors concentrate. State one hypothesis, then design a validation analysis that could confirm or reject it.

## 5. Independent practice
Extend the example with another model or evaluation view. Compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder and state what further validation is required.

## 6. Knowledge check
1. What does the method estimate or optimise?
2. Which assumptions and settings affect its behaviour?
3. How could leakage or an inappropriate split inflate performance?
4. What evidence is needed before use?

## Lesson summary
Supervised learning is an evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.