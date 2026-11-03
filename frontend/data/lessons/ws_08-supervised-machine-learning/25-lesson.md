# Lesson 25: Saving and Loading Trained Models

## Learning outcomes

By the end of this lesson, you should be able to Save and reload a complete preprocessing-and-model pipeline with joblib; verify predictions before and after loading; and explain version and trust risks when loading untrusted model files.


![validation concept diagram](/course-assets/ws08/validation.svg)

## 1. Core explanation
A trained model is a software artefact. Save the full preprocessing-and-model Pipeline, not only the estimator, so future inputs receive the same transformations. Record training data version, target definition, feature order, library versions, evaluation report and model identifier.

Python tools such as joblib can persist scikit-learn objects. Only load model files from trusted sources: pickle-based formats can execute arbitrary code during loading. A saved model may not be compatible across library versions. Treat model files as versioned artefacts and test them before use.

Before deployment, test that loading the saved model produces the same predictions as the in-memory object on a known sample. Validate input schema and fail clearly when required columns are missing or types are invalid.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may require internet access on first use.

```python
import joblib
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X = pd.DataFrame({"hours": [1, 2, 3, 4, 5, 6]})
y = [0, 0, 0, 1, 1, 1]
model = make_pipeline(StandardScaler(), LogisticRegression()).fit(X, y)
joblib.dump(model, "supervised_pipeline.joblib")
loaded = joblib.load("supervised_pipeline.joblib")
print(loaded.predict(pd.DataFrame({"hours": [2.5, 5.5]})))
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report dataset limitations.

## 4. Guided practice
Save a complete pipeline and reload it in a new Python process. Compare predictions before and after loading. Record package versions and explain why loading an untrusted pickle/joblib file is unsafe.

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
