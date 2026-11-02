# Lesson 20: Learning Curves and Error Diagnosis

## Learning outcomes
Explain the technique, implement it in Python and justify the validation choices.

## 1. Core explanation
A learning curve shows training and validation performance as the amount of training data increases. If both scores are poor and close, the model may have high bias. If training is strong and validation is weak, the model may have high variance. If validation continues improving with more data, collecting more representative examples may help.

Validation curves show performance as one hyperparameter changes. They help identify under- and over-complex settings. Use a suitable cross-validation splitter and a metric aligned with the problem. Learning curves can be noisy, especially with small datasets or rare classes.

Do not interpret a learning curve without checking the split and data quality. A validation score that improves with more data does not prove the dataset is representative of deployment. Combine curves with error analysis and domain review.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import learning_curve, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import numpy as np

data = load_breast_cancer(as_frame=True)
sizes, train_scores, val_scores = learning_curve(
    make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
    data.data, data.target, cv=StratifiedKFold(5, shuffle=True, random_state=2),
    scoring="accuracy", train_sizes=np.linspace(.2, 1, 5), n_jobs=-1)
plt.plot(sizes, train_scores.mean(axis=1), marker="o", label="Training")
plt.plot(sizes, val_scores.mean(axis=1), marker="o", label="Validation")
plt.xlabel("Training examples"); plt.ylabel("Accuracy"); plt.legend(); plt.show()
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune a threshold, select features or choose hyperparameters.

## 4. Guided practice
Interpret the gap between curves at small and large training sizes. State whether more data, a simpler model or better features appear most promising, and what evidence is still missing.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.