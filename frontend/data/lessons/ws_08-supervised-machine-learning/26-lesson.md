# Lesson 26: End-to-End Regression Case Study

## Learning outcomes

By the end of this lesson, you should be able to Complete a regression case study using a bundled dataset; compare a dummy baseline with a candidate model; report MAE and RMSE; inspect residuals; and explain the dataset's limits and target meaning.

## 1. Core explanation
This case study predicts a continuous target using the diabetes progression dataset bundled with scikit-learn. Its target is a quantitative measure of disease progression one year after baseline in the study dataset; it is not a diagnosis, an individual risk probability or a clinical treatment recommendation. The purpose is to practise a regression workflow, not to create a medical decision-support product. The dataset is small and historical, so its relationships should not be generalised to current patients or used for clinical decisions.

Define the target, split the data, build a baseline, train a pipeline, evaluate with MAE and RMSE, and inspect residuals. If a dataset has geographic or temporal structure, a random split may overstate performance on genuinely new locations or future periods. Discuss the intended generalisation setting.

A good report explains target units, test sample, baseline, candidate model and error profile. Avoid presenting one metric as a guarantee for every subgroup or a different population.

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
Write the regression case-study report. Include target units, split rationale, baseline comparison, MAE and RMSE, residual limitations and a statement that the demonstration is not a clinical prediction system.

## 5. Independent practice
Extend the example with another model or evaluation view. Compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder and state what further validation is required.

## 6. Knowledge check
1. What does the method estimate or optimise?
2. Which assumptions and settings affect its behaviour?
3. How could leakage or an inappropriate split inflate performance?
4. What evidence is needed before use?

## Lesson summary
Supervised learning is an evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.

## 7. Turn the case study into a defensible analysis

An end-to-end project is not a competition to obtain the largest score. It is a documented chain of decisions. Begin by explaining the practical question and why the target is meaningful. Define the observation unit, prediction time and outcome window. Describe where the data came from, who or what it represents, and which populations may be missing. Check whether the target was recorded consistently and whether any feature contains information from after the prediction moment.

Create a baseline before trying a more complex estimator. A baseline reveals how much value the candidate adds beyond a simple reference strategy. Select models and parameters with training and validation data. Keep the final test set separate until the approach is fixed. Choose metrics that reflect the problem: regression errors should be interpreted in target units; classification evaluation should consider class balance, threshold choice and the costs of false positives and false negatives.

## 8. Explain results and limitations

A useful report includes the question, target definition, data description, split design, preprocessing, baseline, model, parameter choices, evaluation results, error analysis and limitations. Include enough detail for another analyst to reproduce the work. Avoid causal language unless the study design supports causal conclusions. A high score on a small or unrepresentative dataset does not guarantee performance on a different population, future period or operational setting.

## 9. Independent project extension

Re-run the project after changing one defensible choice: the split design, feature set, preprocessing, model family or decision threshold. Compare the new result with the original using the same evaluation design. Inspect examples where predictions are wrong and explain what the model appears to struggle with. State what further data or validation would be required before deployment.

## 10. Knowledge check

1. What decision is this model intended to support?
2. How is the target defined and when is the prediction made?
3. Why is the baseline necessary?
4. What does the evaluation metric mean in the original problem's units?
5. Which limitations prevent you from claiming that the result will generalise everywhere?
