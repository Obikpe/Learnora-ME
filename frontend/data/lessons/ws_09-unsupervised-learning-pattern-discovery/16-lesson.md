# Lesson 16: Unsupervised Learning Project

## Learning outcomes

By the end of this lesson, you should be able to deliver a complete, reproducible unsupervised-learning project; justify the method and feature representation; compare at least two methods or meaningful parameter settings; validate structure and stability; interpret results in original units; communicate limitations; and present a responsible recommendation.

![The end-to-end unsupervised project workflow](/course-assets/ws09/clustering-concepts.svg)

## 1. Project purpose

This final project brings together the ideas from the entire course. You will use an unsupervised method to investigate a dataset without relying on a supplied target label to define the groups.

Choose one project direction:

- **Customer or product segmentation:** discover recurring behaviour or product profiles.
- **Sensor-pattern exploration:** group operating conditions or detect unusual readings.
- **Anomaly review:** identify observations that deserve investigation.
- **Dimensionality reduction:** create a smaller representation and explain what it retains.
- **Association analysis:** identify frequent co-occurrence patterns in transactions.

Use public, synthetic or properly authorised data. Do not upload private customer records or sensitive personal information to a public repository.

## 2. Required project stages

### Stage 1: Define the question

Write a concise problem statement. Identify the audience, intended use and decision context. Explain why an unsupervised method is appropriate and what a useful result would look like.

### Stage 2: Define the observation unit

State exactly what one row represents. Examples include one customer over 90 days, one retail transaction, one machine-hour or one product. If the unit is unclear, the results will be difficult to interpret.

### Stage 3: Describe and inspect the data

Include:
- Source and licence.
- Collection period.
- Number of rows and columns.
- Data types.
- Feature definitions and units.
- Missingness and duplicate findings.
- Data-quality concerns.
- Privacy and ethical considerations.

### Stage 4: Prepare the representation

Explain why each feature is included or excluded. Document imputation, encoding, transformations and scaling. Preserve the raw data and make the preparation process reproducible.

### Stage 5: Fit and compare methods

Use at least two methods or materially different parameter settings. Examples include K-means with different K values, K-means compared with hierarchical clustering, or Isolation Forest compared with LOF.

Do not compare methods only by one score. Consider the geometry, cluster sizes, noise points, stability, interpretability and intended use.

### Stage 6: Validate

For clustering, consider silhouette, Davies–Bouldin, Calinski–Harabasz, stability and cluster profiles. For anomaly detection, inspect flagged records, compare methods and document the review process. For PCA, show explained variance and loadings. For association rules, report support, confidence and lift.

Use metrics appropriate to the task. Do not force a clustering score onto an association-analysis project or treat a visual embedding as a validation metric.

### Stage 7: Interpret and communicate

Show results using readable tables and relevant charts. Explain what the algorithm found under its assumptions, what the pattern may mean, what action could be tested and what the result cannot prove.

## 3. Suggested project: customer behaviour exploration

If you need a structured starting point, use a synthetic customer dataset with:
- Days since last purchase.
- Number of orders in a fixed 90-day period.
- Average basket value.
- Number of product categories purchased.

Define one row as one customer over the same 90-day period. Exclude customer ID from the model. Compare K-means for several K values with an agglomerative method. Scale the numeric features, validate the groups, and profile the result in original units.

The project should not claim to predict churn. You may propose a controlled experiment if a segment suggests a possible re-engagement action.

## 4. Suggested code workflow

The following is a starting structure. Adapt it to your selected dataset and explain every change.

```python
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score

# Load a prepared table; one row must represent the chosen observation unit.
df = pd.read_csv("data/processed/observations.csv")

feature_columns = [
    "feature_one",
    "feature_two",
    "feature_three"
]
X = df[feature_columns]

# Fit preprocessing on the analysis data.
preparation = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])
X_scaled = preparation.fit_transform(X)

# Method A: K-means.
kmeans = KMeans(n_clusters=3, n_init=20, random_state=42)
kmeans_labels = kmeans.fit_predict(X_scaled)

# Method B: hierarchical clustering.
hierarchical = AgglomerativeClustering(
    n_clusters=3,
    metric="euclidean",
    linkage="ward"
)
hierarchical_labels = hierarchical.fit_predict(X_scaled)

print("K-means silhouette:",
      silhouette_score(X_scaled, kmeans_labels))
print("Hierarchical silhouette:",
      silhouette_score(X_scaled, hierarchical_labels))

# Attach labels to original values for profiling.
profile_data = df[feature_columns].copy()
profile_data["kmeans_cluster"] = kmeans_labels
profile_data["hierarchical_cluster"] = hierarchical_labels

print(profile_data.groupby("kmeans_cluster").median(numeric_only=True))
```

This is a template, not a complete project solution. Replace the placeholder feature names with real columns, confirm the data types and missingness, and justify whether median imputation is appropriate. Do not use the same K or linkage automatically for every dataset.

The silhouette scores provide a geometric comparison, but they do not decide the winner. Inspect cluster sizes, original-unit profiles and stability. If the data contains irregular density or noise, DBSCAN may be a more suitable comparison.

## 5. Required deliverables

Submit the following:

1. **README:** project question, setup instructions, data source, method and summary.
2. **Data dictionary:** one definition, unit and meaning for each feature.
3. **Preparation record:** missingness, duplicates, exclusions, encoding, scaling and transformations.
4. **Reproducible code:** scripts or notebook that can be rerun.
5. **Method comparison:** at least two methods or meaningful parameter settings.
6. **Validation:** appropriate metrics, stability checks and qualitative review.
7. **Visualisations:** charts with clear titles, labelled axes, legends where required and explanatory captions.
8. **Interpretation:** profiles or anomaly investigations in original units.
9. **Limitations and ethics:** what is uncertain, what could be harmful and what the model cannot prove.
10. **Recommendation:** a justified next step, including the option not to use the model.

## 6. Suggested folder structure

```
ws09-final-project/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
│   ├── prepare.py
│   ├── model.py
│   └── validate.py
├── outputs/
│   ├── tables/
│   └── figures/
└── report/
    └── final-report.md
```

Keep restricted data outside the repository. If you cannot share the dataset, provide instructions for obtaining it legally and a small synthetic dataset that demonstrates the expected input structure.

## 7. Assessment rubric

| Area | Weight | What strong work demonstrates |
|---|---:|---|
| Problem framing and provenance | 15% | Clear question, observation unit, source and licence |
| Data preparation and feature reasoning | 20% | Defensible features, careful missingness handling and scaling |
| Method selection and implementation | 15% | Appropriate methods and correct, reproducible code |
| Validation and stability | 20% | Relevant metrics, sensitivity checks and honest evaluation |
| Interpretation and communication | 15% | Original-unit profiles, clear visuals and cautious conclusions |
| Reproducibility, ethics and limitations | 15% | Complete setup, documented choices, privacy and risk awareness |

A high score does not require discovering a dramatic pattern. A well-executed project that demonstrates the data does not support stable clusters can be stronger than a project that forces an attractive but misleading result.

## 8. Presentation structure

Prepare a five-to-seven-minute presentation:

1. The problem and intended use.
2. The dataset and observation unit.
3. Feature selection and preparation.
4. Methods and parameter choices.
5. Validation and stability.
6. Main profiles or patterns.
7. Limitations and responsible next step.

Use charts to explain evidence, not to decorate slides. Every visual should answer a question. State when a plot is a two-dimensional projection of higher-dimensional data.

## 9. Final reflection

Answer these questions in your report:

- What did the algorithm identify under the chosen representation?
- Which preprocessing decision had the greatest effect?
- Did different methods or settings produce similar results?
- Which finding is strongest, and which is most uncertain?
- What could the model not establish?
- What would you do next if the result were unstable?
- Would a simpler descriptive or rule-based approach be more appropriate?

## 10. Final knowledge check

1. Why must an unsupervised project still begin with a clear question?
2. Why is the observation unit essential?
3. What evidence should accompany a clustering result?
4. Why is a high silhouette score insufficient on its own?
5. Why should results be profiled in original feature units?
6. What is the difference between an observation and an interpretation?
7. Why is “no stable pattern found” an acceptable conclusion?

## Course completion standard

Your project is complete when another learner can understand the question, obtain the data legally, reproduce the preparation and modelling steps, inspect the validation evidence, interpret the output and understand its limitations. The aim is not to make an algorithm produce a result at any cost. The aim is to make a defensible analytical decision.

## Lesson summary

This project demonstrates the full unsupervised-learning workflow: define the problem, establish the observation unit, prepare meaningful features, select and compare methods, validate structure, profile results, communicate uncertainty and recommend a responsible next step. A trustworthy analyst values evidence more than an attractive cluster plot.
