# Lesson 9: Logistic Regression

## Learning outcomes

By the end of this lesson, you should be able to Explain the sigmoid probability model; fit logistic regression for a binary target; interpret predicted probabilities and coefficients cautiously; and evaluate classification errors.

## 1. Core explanation
Logistic regression is a classification algorithm despite its name. It calculates a weighted sum of features and passes it through the logistic (sigmoid) function to produce a probability between zero and one. A threshold converts the probability into a class prediction. The model is linear in log-odds, not in probability.

The coefficient sign indicates the direction of association with the log-odds, holding other features fixed. Exponentiating a coefficient gives an odds ratio for a one-unit feature increase, under the fitted model. This interpretation requires care: an odds ratio is not a probability difference and does not establish causation.

Scale numeric features when appropriate and encode categories. Fit preprocessing inside a Pipeline. The default threshold of 0.5 is only a starting point; the best threshold depends on error costs, class prevalence and available intervention capacity.

## 2. Worked example
Use VS Code and a project virtual environment. Install the packages used in this lesson with `python -m pip install numpy pandas matplotlib scikit-learn`.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(
    data.data, data.target, test_size=.25, random_state=42, stratify=data.target
)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
model.fit(Xtr, ytr)
print(classification_report(yte, model.predict(Xte)))
```

## 3. Interpretation and diagnostics
Explain what each feature and target represent, the units of the output and how the model was evaluated. Inspect errors and check that all preprocessing was learned from training data only. Never infer causation from predictive coefficients without a suitable causal design.

## 4. Guided practice
Use predict_proba to inspect probabilities for several test rows. Explain why two cases with probabilities 0.51 and 0.95 receive the same class at threshold 0.5 but represent different confidence levels.

## 5. Independent practice
Apply the method to a dataset of your choice. Define the prediction moment, target and feature availability. Compare with a simple baseline and report at least one metric plus an error analysis.

## 6. Knowledge check
1. What does the model estimate?
2. What assumptions or limitations matter most?
3. How could leakage or an inappropriate split inflate performance?
4. What additional analysis is needed before use?

## Lesson summary
Supervised models must be framed around a precise target and evaluated on unseen data. Model complexity and scores matter less than reliable performance for the intended decision.