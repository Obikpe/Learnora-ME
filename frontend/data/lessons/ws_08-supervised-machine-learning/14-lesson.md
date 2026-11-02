# Lesson 14: Random Forests

## Learning outcomes
Explain the technique, implement the worked example, interpret the output and justify when the method is suitable.

## 1. Core explanation
A random forest combines many decision trees. Each tree is trained on a bootstrap sample, and each split considers a random subset of features. Classification combines votes; regression averages predictions. The diversity among trees reduces variance compared with a single deep tree.

Important parameters include n_estimators (number of trees), max_features (features considered at each split), max_depth and min_samples_leaf. More trees often stabilise predictions but increase compute. Random forests usually do not require standardisation, but still need missing-value and categorical handling appropriate to the implementation.

Feature importance can be estimated by impurity reduction or permutation. Permutation importance measures how much a validation score drops when a feature is shuffled. Correlated predictors complicate interpretation because one may substitute for another. Use importance as a diagnostic, not a causal explanation.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may need internet access on first use.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42, stratify=data.target)
model = RandomForestClassifier(n_estimators=300, min_samples_leaf=2,
                               random_state=42, n_jobs=-1)
model.fit(Xtr, ytr)
print("Test accuracy:", model.score(Xte, yte))
imp = permutation_importance(model, Xte, yte, n_repeats=10, random_state=42)
print(sorted(zip(data.feature_names, imp.importances_mean),
             key=lambda x: x[1], reverse=True)[:5])
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report the limitations of the dataset.

## 4. Guided practice
Change min_samples_leaf and compare train/test performance. Explain why a forest can be more stable than one tree but is not automatically unbiased or fair.

## 5. Independent practice
Extend the example with a second model or a different evaluation view. Keep a record of every change and compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder.

## 6. Knowledge check
1. What does this method optimise or estimate?
2. Which assumptions or settings affect its behaviour?
3. How would you detect overfitting or leakage?
4. What evidence is needed before the model is used?

## Lesson summary
Supervised learning is a complete evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.