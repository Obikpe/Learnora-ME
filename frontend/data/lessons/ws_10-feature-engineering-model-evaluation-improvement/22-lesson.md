# Lesson 22: Reproducible Model Improvement Workflow

## Learning outcomes

By the end of this lesson, you should be able to Compare model scores on identical folds; inspect paired differences and variability; distinguish statistical from practical significance; and consider operational cost, fairness and maintainability.

## 1. Core explanation
An improvement workflow is a controlled experiment. Start with a baseline and a written hypothesis, change one meaningful factor, evaluate using the same split and metric, and record the result. Examples include adding a feature, changing regularisation, adjusting class weights or using a different model family.

Keep experiment records: dataset version, code commit, package versions, split seed, preprocessing, hyperparameters, metric and date. Do not delete failed experiments; they explain decisions. Ensure each candidate is compared on identical evaluation data.

The final improvement should be meaningful, reproducible and defensible. If improvement is within normal score variability, report that honestly. Re-run the selected workflow from a clean environment and preserve the untouched test set for final evaluation.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
import pandas as pd
experiments = pd.DataFrame([
    {"id": "baseline", "change": "Dummy median", "mae": 12.4, "seed": 42},
    {"id": "e01", "change": "Ridge alpha=1", "mae": 10.8, "seed": 42},
    {"id": "e02", "change": "Ridge alpha=10", "mae": 11.1, "seed": 42}
])
print(experiments.sort_values("mae"))
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune thresholds, select features or choose hyperparameters.

## 4. Guided practice
Create an experiment log for three model changes. State the hypothesis before each run, use identical validation folds and write a decision note explaining which change to retain.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.