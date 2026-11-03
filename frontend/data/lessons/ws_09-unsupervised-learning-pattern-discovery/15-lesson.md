# Lesson 15: Unsupervised Learning in Practice

## Learning outcomes

By the end of this lesson, you should be able to plan an unsupervised project from question to report; select an appropriate method; create a reproducible workflow; compare models and settings; document data and modelling decisions; communicate uncertainty; and recognise when a simpler analysis is preferable.

![Teaching diagram: 15](/course-assets/ws09/unsupervised-workflow.svg)

## 1. Start with a question and a decision context

An unsupervised project still needs a clear purpose. “Run clustering on this spreadsheet” is not a good problem statement. It identifies a tool but not the question.

A stronger question is: “Can we identify recurring patterns in customer purchasing behaviour that help us design and test more relevant service messages?” This gives the analysis a context without promising that clusters will definitely exist.

Before writing code, clarify:
- Who will use the result?
- What decision or investigation might it support?
- What is the unit of observation?
- What period does each observation cover?
- What would make the analysis useful?
- What would make the result inconclusive or unsafe to use?

## 2. Select the method based on the task

Use the analytical question to guide the method:
- Clustering groups similar observations.
- Dimensionality reduction creates a smaller representation.
- Anomaly detection flags unusual observations.
- Association analysis identifies recurring co-occurrence.

Then consider the data type, size, dimensionality, expected shape, noise and computational constraints. Do not use K-means simply because it is familiar. A density-based method may suit irregular spatial patterns; PCA may suit correlated numeric features; association analysis may suit transaction baskets.

## 3. Create an analysis charter

An analysis charter records the plan before modelling. It reduces the temptation to change the question after seeing a convenient result.

Example:

```python
project_plan = {
    "question": "Explore recurring customer purchasing patterns",
    "observation_unit": "One customer over a fixed 90-day period",
    "purpose": "Exploratory segmentation for a controlled test",
    "candidate_features": [
        "days_since_last_purchase",
        "order_count_90d",
        "average_basket_value"
    ],
    "excluded_fields": ["customer_id", "future_campaign_response"],
    "preprocessing": [
        "inspect missingness",
        "median imputation if justified",
        "standardise numeric features"
    ],
    "candidate_methods": ["KMeans", "AgglomerativeClustering"],
    "validation": [
        "silhouette",
        "cluster-size review",
        "stability across seeds",
        "original-unit profiling"
    ],
    "limitations": [
        "clusters do not predict churn",
        "historical behaviour may change"
    ]
}

for key, value in project_plan.items():
    print(f"{key}: {value}")
```

This dictionary is a simple planning artefact, not a machine-learning model. Its purpose is to make decisions visible and reviewable.

## 4. Build a reproducible project structure

A clear folder structure makes it easier for another analyst to understand and rerun the work.

```
unsupervised-project/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
│   ├── prepare_data.py
│   ├── clustering.py
│   └── evaluate.py
├── reports/
│   ├── figures/
│   └── final-report.md
└── outputs/
```

Keep raw data unchanged. Save processed data separately and document how it was produced. Do not commit private customer data, secrets or restricted datasets to a public repository. Follow the source licence and data-protection requirements.

A `requirements.txt` file records the libraries needed to run the project. Pin versions when reproducibility requires it, and state the Python version used.

## 5. Separate preparation, modelling and interpretation

A practical workflow has distinct stages:

1. Load and validate the source data.
2. Confirm the observation unit and data dictionary.
3. Explore missingness, duplicates, distributions and unusual values.
4. Select and transform features.
5. Fit a baseline or simple method.
6. Fit alternative methods or parameter settings.
7. Evaluate geometry, stability and group sizes.
8. Profile results in original units.
9. Interpret limitations and possible actions.
10. Write a report and preserve the code and settings.

Keeping these stages separate makes it easier to identify whether a change in output came from new data, different features, scaling or a different algorithm.

## 6. Compare methods without cherry-picking

A comparison table should record the method, parameters, preprocessing, number of clusters or noise points, validation metrics, stability and interpretation.

Do not keep changing parameters until you find a result that confirms your preferred narrative. Decide what evidence matters before testing, document the settings explored and report disappointing results.

A model with a slightly better silhouette score may be less useful if it creates tiny groups that cannot be interpreted. A simpler model may be preferable if it is stable and supports the intended task.

## 7. Reproducibility and versioning

Record:
- Data source and extraction date.
- Data version or checksum where possible.
- Observation-unit definition and time window.
- Feature list and exclusions.
- Missing-value and scaling decisions.
- Algorithm and parameters.
- Random seed.
- Python and package versions.
- Evaluation results and limitations.

Random seeds help reproduce stochastic procedures, but they do not guarantee identical results across every software version or computing environment. Reproducibility also depends on preserving data and preprocessing decisions.

## 8. Communicate what the result does and does not show

A good report separates:
- **Observation:** what the output and profiles show.
- **Interpretation:** what the pattern may mean in context.
- **Recommendation:** what should be tested or investigated next.
- **Limitation:** what the analysis cannot establish.

For example: “The three-group K-means solution identified one group with longer purchase recency and lower recent order frequency. The group remained broadly similar across tested seeds, but its membership does not prove that customers will churn. We recommend a controlled re-engagement test before operational use.”

This is stronger than saying “AI found customers who are about to leave.”

## 9. When a simpler method is better

Unsupervised learning is not always necessary. A descriptive summary, rule-based segmentation, business-defined categories or a carefully designed chart may answer the question more transparently.

If the dataset is small, poorly measured, unstable or unsuitable for the chosen method, do not force a model. Report the limitation and recommend better data collection or a simpler analysis.

## 10. Guided practice

Write an analysis charter for a dataset of machine sensor readings. Define the observation unit, intended use, features, exclusions, candidate method, validation approach and conditions under which you would report no useful clusters.

## 11. Independent practice

Create a reproducible mini-project using a public or synthetic dataset. Include a README, data dictionary, preparation script, at least two model settings or methods, validation results, original-unit profiles, visuals and a short report. Ask another learner to reproduce the result using your instructions.

## 12. Knowledge check

1. Why should the question be defined before selecting an algorithm?
2. What belongs in an analysis charter?
3. Why should raw data be kept separate from processed data?
4. What is cherry-picking in model comparison?
5. Why record random seeds and package versions?
6. How should a report distinguish observation from interpretation?
7. When might a descriptive table be better than clustering?

## Lesson summary

A strong unsupervised project is more than a fitted algorithm. It has a clear question, a defensible observation unit, meaningful features, documented preparation, fair comparisons, validation, interpretation and reproducible reporting. Be willing to report that the data does not support a useful pattern.
