# Lesson 11: Other Dimensionality Reduction Methods

## Learning outcomes
Explain the unsupervised method, implement the example and judge whether the discovered structure is meaningful.

## 1. Core explanation
PCA is linear, so it may not preserve non-linear structure. t-SNE focuses on preserving local neighbourhoods for visualisation; UMAP also aims to preserve neighbourhood structure and can often scale better. These methods can reveal visual groupings but their axes generally have no direct physical meaning.

Parameters matter. In t-SNE, perplexity controls a notion of neighbourhood size; different values and random seeds can change the map. UMAP's n_neighbors and min_dist affect local/global structure and cluster compactness. Distances between far-apart islands in a 2-D embedding should not automatically be interpreted as meaningful global distances.

Use embeddings for exploration, not proof that natural clusters exist. Validate patterns in the original feature space and test stability. A 2-D embedding is not a substitute for robust model evaluation.

## 2. Worked Python example
Run in VS Code. Install packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`.

```python
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

data = load_digits()
Z = StandardScaler().fit_transform(data.data)
coords = PCA(n_components=2, random_state=42).fit_transform(Z)
plt.scatter(coords[:, 0], coords[:, 1], c=data.target, s=8, cmap="tab10")
plt.title("Digits projected into two PCA components")
plt.xlabel("PC1"); plt.ylabel("PC2"); plt.show()
```

## 3. Interpretation
Describe the feature representation, model settings and meaning of the output. Validate patterns in original units. Cluster IDs are arbitrary and anomaly flags are not proof of wrongdoing.

## 4. Guided practice
If umap-learn is installed, create a UMAP embedding and compare it with PCA. Explain why visual separation in a 2-D map does not guarantee predictive accuracy.

## 5. Independent practice
Apply the method to a dataset. Compare at least two parameter settings or methods, profile results and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the method attempting to discover?
2. Which assumptions are introduced by the representation or distance?
3. How will you assess stability and usefulness?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Stability, interpretation and practical validation determine whether those patterns deserve to be used.