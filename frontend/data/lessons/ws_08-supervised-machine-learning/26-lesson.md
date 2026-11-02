# Lesson 26: End-to-End Regression Case Study

## Learning outcomes
Explain the technique, implement the example, interpret the output and justify when the method is suitable.

## 1. Core explanation
This case study predicts a continuous target using the diabetes progression dataset bundled with scikit-learn. Its target is a quantitative measure of disease progression one year after baseline in the study dataset; it is not a diagnosis, an individual risk probability or a clinical treatment recommendation. The purpose is to practise a regression workflow, not to create a medical decision-support product. The dataset is small and historical, so its relationships should not be generalised to current patients or used for clinical decisions.

Define the target, split the data, build a baseline, train a pipeline, evaluate with MAE and RMSE, and inspect residuals. If a dataset has geographic or temporal structure, a random split may overstate performance on genuinely new locations or future periods. Discuss the intended generalisation setting.

A good report explains target units, test sample, baseline, candidate model and error profile. Avoid presenting one metric as a guarantee for every neighbourhood or property type.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas matplotlib scikit-learn`. The diabetes dataset is bundled with scikit-learn and does not require a separate download.

```python
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

data = load_diabetes(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42)
models = [DummyRegressor(strategy="median"),
          RandomForestRegressor(n_estimators=150, min_samples_leaf=3, random_state=42)]
for model in models:
    model.fit(Xtr, ytr)
    p = model.predict(Xte)
    print(type(model).__name__, "MAE", mean_absolute_error(yte, p),
          "RMSE", mean_squared_error(yte, p)**.5)
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report dataset limitations.

## 4. Guided practice
Write the regression case-study report. Include target units, split rationale, baseline comparison, MAE and RMSE, residual limitations and a statement that the demonstration is not a deployable valuation system.

## 5. Independent practice
Extend the example with another model or evaluation view. Compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder and state what further validation is required.

## 6. Knowledge check
1. What does the method estimate or optimise?
2. Which assumptions and settings affect its behaviour?
3. How could leakage or an inappropriate split inflate performance?
4. What evidence is needed before use?

## Lesson summary
Supervised learning is an evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.