# Lesson 23: Feature Engineering and Evaluation Project

## Learning outcomes

By the end of this lesson, you should be able to Maintain a reproducible experiment log with hypothesis, data version, code version, split seed, parameters and metrics; change one factor at a time; and document rejected as well as successful experiments.

## 1. Core explanation
The project applies feature engineering and evaluation controls to a real analytical question. Define prediction timestamp, unit of observation, target horizon and action. Audit candidate features for availability, missingness, leakage, redundancy and ethical risk. Build transformations in a Pipeline or ColumnTransformer.

Establish a baseline, then compare at least two feature sets or model workflows using the same cross-validation design. Use metrics suited to the target and inspect errors across relevant groups. Tune only on training data and reserve a final test set. Document transformation decisions and rejected features.

The deliverable is a reproducible report and codebase. Explain whether engineered features improve validation in a stable and practically meaningful way. State limitations, deployment assumptions and monitoring requirements.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
# Project deliverables
# problem_statement.md: decision, target, prediction timestamp, error costs
# data_dictionary.csv: feature, meaning, type, source, availability time
# src/preprocess.py: leakage-safe transformations
# src/train.py: baseline and candidate pipelines
# reports/evaluation.md: CV results, test result, error analysis
# README.md: environment, run instructions, limitations
# Keep preprocessing and model fitting in one sklearn Pipeline.
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune thresholds, select features or choose hyperparameters.

## 4. Guided practice
Submit a feature-engineering project. Rubric: problem framing 15%, leakage prevention 20%, transformation rationale 20%, validation and metrics 20%, error analysis 15%, reproducibility and communication 10%. Include one rejected feature and explain why it was excluded.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.