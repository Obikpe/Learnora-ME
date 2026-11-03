# Lesson 23: Reproducible Model Improvement Workflow

## Learning outcomes
Create a baseline-first experiment process; record data and environment versions; organise preprocessing and model code; preserve evaluation boundaries; and communicate a reproducible model improvement decision.

## 1. Why reproducibility matters
A model result is useful only if another person can understand how it was produced and, where possible, reproduce it. Reproducibility requires more than saving a notebook. Record the dataset source and version, target definition, feature definitions, split strategy, random seeds, package versions, preprocessing, model settings and metrics.

A reproducible workflow also reduces accidental changes. If the dataset changes, the result may change. If a library changes, an algorithm implementation may change. Versioning makes these differences visible.

## 2. Start with a baseline
A baseline is a simple reference point. For classification, it might be a majority-class predictor or a simple logistic regression. For regression, it might predict the training mean or median. A complex model should demonstrate improvement over a relevant baseline.

Define the decision and metric before tuning. Document what counts as an acceptable error and what limitations are known. This prevents selecting metrics after seeing results.

## 3. Experiment log
Record one row per experiment:
- experiment ID and date;
- dataset version or hash;
- target and feature set;
- split and cross-validation configuration;
- preprocessing and estimator;
- hyperparameters;
- metric by fold and summary;
- runtime;
- observations and next decision.

Do not overwrite failed experiments. A failed or rejected approach is useful evidence.

![Reproducible workflow](/course-assets/ws10/reproducible-workflow.svg)

## 4. Suggested project structure
```text
model-improvement/
├── README.md
├── requirements.txt
├── data/
│   └── README.md
├── notebooks/
│   └── exploration.ipynb
├── src/
│   ├── features.py
│   ├── preprocessing.py
│   ├── train.py
│   └── evaluate.py
└── reports/
    ├── feature_dictionary.csv
    ├── experiment_log.csv
    └── model_evaluation.md
```

Keep source code separate from exploratory notebooks. Do not commit private data, API keys, passwords or personally identifiable information. Explain how to obtain data legally and safely.

## 5. Reproducible Python setup
Create and activate a virtual environment, then install the required packages. For example:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install pandas numpy scikit-learn matplotlib
python -m pip freeze > requirements.txt
```

The requirements file records installed versions, but a fully reproducible environment may also require Python version, operating system details and external data version. Pin dependencies deliberately for a project rather than copying every unrelated package from a personal environment.

## 6. Controlled improvement cycle
1. Audit the data and define prediction time.
2. Create a baseline pipeline.
3. Establish a split and metric.
4. Propose one feature or modelling change.
5. Evaluate using the same folds.
6. Record results and inspect errors.
7. Keep, reject or investigate the change.
8. Select the final workflow.
9. Evaluate once on the untouched test set.
10. Document limitations and monitoring needs.

## 7. Common mistakes
- Saving only the final notebook and losing experiment history.
- Using different folds for each experiment.
- Failing to record data versions.
- Committing credentials or private datasets.
- Reporting training metrics as final performance.
- Treating a random seed as a complete reproducibility guarantee.

## Guided practice
Create an experiment log template for a churn model. Include fields that let another analyst reconstruct the feature and validation choices.

## Independent practice
Organise a small project using the suggested structure. Write a README with setup instructions, data provenance, target definition, evaluation design and final limitations. Re-run the pipeline from a clean environment.

## Knowledge check
1. Why is a baseline important?
2. What information belongs in an experiment log?
3. Why record the dataset version?
4. What does requirements.txt capture and what might it miss?
5. Why should failed experiments be preserved?

## Lesson summary
Reproducible modelling turns isolated experiments into an auditable process. Preserve data provenance, environment details, feature logic, validation design and experiment decisions so results can be checked and maintained.

## 7. Deeper reasoning: reproducibility includes the decision trail

A reproducible project should let another analyst answer not only “How did you train the final model?” but also “Why did you make these choices?” Preserve the baseline, rejected experiments and the reason each change was accepted or rejected. This decision trail helps prevent the team from repeating unproductive work and makes it easier to revisit a choice when new data becomes available.

A random seed supports repeatability for operations that use randomness, but it is not a complete guarantee. Different library versions, hardware, parallel execution and algorithm implementations can affect results. Record the Python and package versions, the random seeds, the operating environment and any relevant configuration. For high-assurance work, capture the data version or checksum and the exact code revision used for the experiment.

Reproducibility also requires data governance. If the dataset contains personal or restricted information, do not commit it simply to make the repository self-contained. Instead, document the approved access process, expected schema and steps needed to create a reproducible training extract. Keep credentials in secure environment configuration, never in notebooks or source files.

Finally, a model artifact should be accompanied by its feature contract: expected columns, data types, units, category handling and preprocessing assumptions. A saved estimator without this information is difficult to use safely. Treat the pipeline, feature definitions, evaluation report and environment record as one deliverable.