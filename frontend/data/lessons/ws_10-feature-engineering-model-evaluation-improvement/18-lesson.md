# Lesson 18: Hyperparameter Search

## Learning outcomes
Explain the technique, implement it in Python and justify the validation choices.

## 1. Core explanation
Hyperparameters are settings chosen before or around model fitting, such as tree depth, regularisation strength or number of neighbours. Grid search evaluates a specified set of combinations; random search samples combinations and can explore broad spaces more efficiently when only a few settings strongly affect performance.

Use cross-validation on training data to select hyperparameters. Put preprocessing in a Pipeline and address parameter names through pipeline steps. Choose a scoring metric linked to the decision. Record search space, folds, random seed and compute time.

Large searches increase selection bias and compute cost. A search may overfit its validation folds if too many choices are tested. Use a final untouched test set once after selection, and consider nested CV when a robust estimate of the entire selection procedure is required.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42, stratify=data.target)
pipe = make_pipeline(StandardScaler(), SVC())
search = GridSearchCV(pipe, {"svc__C": [.1, 1, 10],
    "svc__kernel": ["linear", "rbf"]}, cv=StratifiedKFold(5, shuffle=True, random_state=42),
    scoring="f1", n_jobs=-1)
search.fit(Xtr, ytr)
print(search.best_params_, search.best_score_, search.score(Xte, yte))
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune a threshold, select features or choose hyperparameters.

## 4. Guided practice
Expand the grid with gamma for the RBF kernel. Explain why gamma should not be tuned for a linear kernel and why best_params_ is not itself evidence of test performance.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.