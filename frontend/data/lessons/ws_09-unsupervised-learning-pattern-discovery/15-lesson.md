# Lesson 15: Unsupervised Learning in Practice

## Learning outcomes

By the end of this lesson, you should be able to Plan an unsupervised analysis by defining the observation unit, intended use, feature representation and validation approach; compare methods; and set criteria for reporting inconclusive results.

![A defensible unsupervised workflow from question through validation](/course-assets/ws09/clustering-concepts.svg)

## 1. Core explanation
An unsupervised project needs a clear objective even though it has no labelled target. Define the unit of observation, feature representation, purpose and intended use. Decide whether the output is for exploration, segmentation, anomaly triage or dimensionality reduction. Establish how usefulness will be judged before running algorithms.

Compare a simple baseline or alternative algorithm. Test stability across seeds, samples and reasonable parameter changes. Inspect original records and profiles. Document how preprocessing and distance choices influence the result. If clusters are weak or unstable, report that rather than forcing a narrative.

Communicate what the algorithm discovered under its assumptions and what it did not prove. An unsupervised result does not establish causal drivers, future outcomes or objectively correct categories.

## 2. Worked Python example
Run in VS Code. Install packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`.

```python
project = {
    "purpose": "Explore customer purchasing patterns",
    "unit": "Customer-quarter",
    "features": ["recency", "frequency", "monetary_value"],
    "preprocessing": "Median imputation and standardisation",
    "methods": ["KMeans", "Agglomerative clustering"],
    "validation": ["Silhouette", "Seed stability", "Profile review"]
}
print(project)
```

## 3. Interpretation
Describe the feature representation, model settings and meaning of the output. Validate patterns in original units. Cluster IDs are arbitrary and anomaly flags are not proof of wrongdoing.

## 4. Guided practice
Write a project plan comparing K-means and hierarchical clustering. Include validation and a rule for deciding that no useful clusters have been found.

## 5. Independent practice
Apply the method to a dataset. Compare at least two parameter settings or methods, profile results and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the method attempting to discover?
2. Which assumptions are introduced by the representation or distance?
3. How will you assess stability and usefulness?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Stability, interpretation and practical validation determine whether those patterns deserve to be used.

## Deeper explanation: plan before choosing an algorithm

A credible project starts with a question and decision context, not a favourite algorithm. Define the observation unit, intended use, features, exclusions, preprocessing, candidate methods and validation plan before modelling. Compare against a simple baseline or rule-based grouping. A complicated model is not automatically better than a transparent rule.

Record the data snapshot, code version, parameters and random seeds so the analysis can be reproduced. Test stability across seeds, samples and relevant time periods. Inspect original records and profiles. Document how preprocessing and distance choices influence the result.

Report negative and inconclusive results. If clusters are unstable, overlap heavily or cannot be interpreted, say so. “The current features do not support a stable segmentation” is a valid result. Do not keep changing parameters until a persuasive story appears; that is confirmation bias.

Separate observed output, interpretation and recommendation. State the population, time period and limitations. Avoid causal language unless a separate causal design supports it. An unsupervised result does not establish causal drivers, future outcomes or objectively correct categories.

**Practice:** Produce a one-page analysis charter and ask another learner to challenge the observation unit, feature choices, validation plan and proposed action before fitting a model.

### Worked example: write a defensible results summary

A useful executive summary names the dataset and period, observation unit, method and key settings, validation performed, main observed pattern, uncertainty and next step. It does not start with a cluster label and tell a story unsupported by evidence.

For example: “Using customer-quarter records from the selected period, we compared K-means and agglomerative clustering after median imputation and standardisation. The three-group K-means solution was more stable across seeds, but one group was small. We recommend further testing before using the segments for targeting.” This is more informative than saying “AI discovered three customer types”.

Keep a reproducibility record: source version, code, package versions, parameters, random seeds and transformation details. If the analysis is refreshed, compare results with the previous period and investigate changes rather than assuming they are meaningful.
