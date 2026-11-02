# Lesson 3: Building a Reproducible Supervised Workflow

## Learning outcomes
Explain the supervised-learning concept, implement the method in Python, interpret its output and identify assumptions and common failure modes.

## 1. Core explanation
A supervised workflow should be reproducible from raw data to final metric. Keep data loading, validation, splitting, preprocessing, model fitting and evaluation explicit. Use a fixed random seed when a random split is appropriate, but remember that a seed alone does not guarantee full reproducibility across library versions or hardware.

Use scikit-learn Pipelines to combine preprocessing and modelling. This prevents common leakage during cross-validation because the transformer is fitted only on each training fold. Keep the final test data out of feature selection and hyperparameter decisions. Save the split logic, package versions and target definition.

Compare at least one baseline and one candidate. Record the metric, data version, model parameters and evaluation date. If you change the split or target definition, do not compare the score directly with the old result without noting the change.

## 2. Worked example
Use VS Code and a project virtual environment. Install the packages used in this lesson with `python -m pip install numpy pandas matplotlib scikit-learn`.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

data = load_breast_cancer(as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42, stratify=data.target
)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
model.fit(X_train, y_train)
print("Test accuracy:", accuracy_score(y_test, model.predict(X_test)))
```

## 3. Interpretation and diagnostics
Explain what each feature and target represent, the units of the output and how the model was evaluated. Inspect errors and check that all preprocessing was learned from training data only. Never infer causation from predictive coefficients without a suitable causal design.

## 4. Guided practice
Run the example twice. Record the split seed, test size, package version and score. Change the seed and observe whether the score changes. Explain why a single split is only one estimate of generalisation.

## 5. Independent practice
Apply the method to a dataset of your choice. Define the prediction moment, target and feature availability. Compare with a simple baseline and report at least one metric plus an error analysis.

## 6. Knowledge check
1. What does the model estimate?
2. What assumptions or limitations matter most?
3. How could leakage or an inappropriate split inflate performance?
4. What additional analysis is needed before use?

## Lesson summary
Supervised models must be framed around a precise target and evaluated on unseen data. Model complexity and scores matter less than reliable performance for the intended decision.