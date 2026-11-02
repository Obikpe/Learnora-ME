# Lesson 15: Unsupervised Learning in Practice

## Learning outcomes

By the end of this lesson, you should be able to Plan an unsupervised analysis by defining the observation unit, intended use, feature representation and validation approach; compare methods; and set criteria for reporting inconclusive results.

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