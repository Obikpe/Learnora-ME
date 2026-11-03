# Lesson 10: Interpreting PCA and Explained Variance

## Learning outcomes

By the end of this lesson, you should be able to explain explained variance and cumulative explained variance; interpret PCA loadings and component scores; choose a defensible number of components; read a scree plot; reconstruct data conceptually; and explain the limitations of using a fixed variance threshold.

![PCA components and retained information](/course-assets/ws09/pca-rotation.svg)

## 1. PCA gives components; how much information do they retain?

In the previous lesson, you learned that PCA creates new axes called principal components. The first component captures the largest possible amount of variance, the second captures the largest remaining amount while being perpendicular to the first, and later components capture progressively less variance.

But how many components should you keep? If the original dataset has 20 numeric features, you could retain all 20 components, but then you have not reduced the number of dimensions. You could retain only two, but that may discard important structure. Explained variance helps quantify the trade-off.

**Explained variance ratio** is the proportion of the total variance represented by a component. If PC1 explains 55% of the variance, then 55% of the total variation in the transformed feature space lies along that component.

If PC1 explains 55% and PC2 explains 25%, together they explain 80%. This is called cumulative explained variance.

## 2. Calculate cumulative explained variance

Suppose a PCA model produces these ratios:

| Component | Explained variance ratio | Cumulative |
|---|---:|---:|
| PC1 | 0.55 | 0.55 |
| PC2 | 0.25 | 0.80 |
| PC3 | 0.12 | 0.92 |
| PC4 | 0.05 | 0.97 |
| PC5 | 0.03 | 1.00 |

PC1 alone represents 55% of the total variance. PC1 and PC2 together represent 80%. The first three represent 92%. If you retain three components, you reduce five dimensions to three while preserving 92% of the variance under this PCA representation.

This does not mean that 92% of the original facts, business value or predictive usefulness are preserved. Explained variance is a mathematical quantity. A low-variance feature could still contain an important rare signal. PCA does not know which information matters to a particular decision.

## 3. Inspect explained variance in Python

```python
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

wine = load_wine()
X = StandardScaler().fit_transform(wine.data)

pca = PCA()
scores = pca.fit_transform(X)

ratios = pca.explained_variance_ratio_
cumulative = ratios.cumsum()

for number, (ratio, total) in enumerate(zip(ratios, cumulative), start=1):
    print(f"PC{number}: {ratio:.3f} | cumulative: {total:.3f}")

plt.plot(range(1, len(ratios) + 1), cumulative, marker="o")
plt.axhline(0.90, linestyle="--", label="90% reference")
plt.xlabel("Number of components")
plt.ylabel("Cumulative explained variance")
plt.title("PCA cumulative explained variance")
plt.legend()
plt.show()
```

The Wine dataset is included with scikit-learn, so this example does not require downloading a file. It contains numeric chemical measurements for wine samples. We standardise the features because their scales differ.

Calling `PCA()` without setting `n_components` retains all available components (subject to the dimensions of the input). `explained_variance_ratio_` gives each component's share. `cumsum()` adds those shares progressively. The horizontal reference line at 0.90 is a visual aid, not a mandatory rule.

## 4. The scree plot

A scree plot displays the variance explained by each component, usually in descending order. The curve often falls steeply at first and then becomes flatter. The point where the reduction begins to flatten is sometimes called the elbow.

A scree plot helps show diminishing returns from retaining more components. However, like the K-means elbow, the PCA scree elbow can be subjective. Some datasets have no clear bend.

A cumulative explained-variance plot answers a slightly different question: how many components are required to reach a selected total percentage? Both views are useful.

## 5. Component loadings: what do the components combine?

A component is a weighted combination of original features. The weights are commonly called **loadings** in practical PCA interpretation. They show how strongly each original feature contributes to a component direction, with signs indicating direction.

If PC1 has large positive loadings for temperature, pressure and vibration, it may represent a general machine-intensity direction. If PC2 has a positive loading for temperature and negative loading for vibration, it may represent a contrast between those measurements.

Interpretation requires care:
- A large absolute loading indicates a stronger contribution to that component direction.
- A positive or negative sign indicates direction relative to the component.
- The sign of an entire component can be flipped without changing the PCA solution's meaning.
- Loadings depend on scaling and the feature set.
- A component may combine features in a way that has no simple real-world name.

Inspect loadings:

```python
import pandas as pd
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

wine = load_wine(as_frame=True)
X_scaled = StandardScaler().fit_transform(wine.data)

pca = PCA(n_components=3)
pca.fit(X_scaled)

loadings = pd.DataFrame(
    pca.components_.T,
    index=wine.feature_names,
    columns=["PC1", "PC2", "PC3"]
)
print(loadings.round(3))
```

`components_` is arranged with one row per component and one column per original feature. The transpose `.T` changes the orientation so the DataFrame has one row per original feature and one column per component. This makes it easier to inspect which variables contribute to PC1, PC2 and PC3.

## 6. Scores and loadings are not the same thing

A **loading** describes how an original feature contributes to a component direction. A **score** describes where one observation lies along that component.

For example, the loading table may show that temperature contributes strongly to PC1. A particular machine may have a high PC1 score, meaning it lies far along the positive direction of that component. The score is not a probability and is not automatically a risk rating.

A biplot can display both observations and feature directions in the same two-dimensional PCA view. It can be useful, but interpretation depends on scaling and plotting conventions. Do not assume every arrow length or angle has the same meaning across different biplot implementations.

## 7. Choosing how many components to retain

Possible approaches include:

- Retain enough components to reach a chosen cumulative variance, such as 85%, 90% or 95%.
- Inspect the scree plot for diminishing returns.
- Consider whether the reduced representation preserves the patterns needed for the task.
- Evaluate downstream performance if PCA is part of a later predictive pipeline.
- Consider interpretability and computational cost.

There is no universal percentage. A visualisation may use two components even if they explain only 60% of the variance, provided the chart is clearly described as a partial projection. A compression task may require a higher retained proportion. A predictive task should assess whether the retained representation preserves information useful for prediction, not merely total variance.

## 8. Reconstruction and information loss

PCA transforms observations into component scores. If you retain all components, you can reconstruct the centred input (up to numerical precision). If you retain only a subset, the reconstruction is an approximation. The omitted components contain the discarded variance.

This is the basis of dimensionality reduction: keep the dominant directions and discard smaller ones. But a small-variance direction may contain an important rare event. Always consider the purpose and the consequences of information loss.

## 9. Common mistakes

- Saying 90% explained variance means 90% accuracy.
- Assuming the first two components always show all important structure.
- Treating component loadings as causal effects.
- Naming a component without inspecting its loadings and context.
- Using a fixed 95% rule for every problem.
- Forgetting that a component's sign can be reversed without changing its essential direction.

## 10. Guided practice

Use the sample variance ratios [0.50, 0.30, 0.12, 0.05, 0.03]. Calculate the cumulative total after each component. How many components are needed to retain at least 90%? Explain why the answer does not prove that 90% of decision-relevant information has been retained.

## 11. Independent practice

Run PCA on a dataset with at least six numeric features. Produce a scree plot and cumulative explained-variance plot. Inspect the loadings for the first three components and write a plain-language interpretation with caveats. Compare a two-component projection with a higher-dimensional representation.

## 12. Knowledge check

1. What does explained variance ratio measure?
2. How is cumulative explained variance calculated?
3. What is a scree plot used for?
4. What is the difference between component scores and loadings?
5. Why is a 90% variance threshold not a universal rule?
6. Can a low-variance component still be important? Explain.
7. What happens to reconstruction when components are discarded?

## Lesson summary

Explained variance quantifies how much total variance each principal component represents. Cumulative variance helps assess the trade-off between fewer dimensions and retained variation. Loadings describe the component directions; scores describe observations in the new space. Choose components based on purpose, interpretability and evidence—not a fixed percentage alone.
