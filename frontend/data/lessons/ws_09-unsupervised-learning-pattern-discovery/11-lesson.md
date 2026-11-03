# Lesson 11: Other Dimensionality Reduction Methods

## Learning outcomes

By the end of this lesson, you should be able to Compare PCA with t-SNE and UMAP; configure a 2-D embedding; explain neighbourhood preservation and parameter sensitivity; and avoid interpreting map distances or visual islands as proof of clusters.

## 1. Core explanation
PCA is linear, so it may not preserve non-linear structure. t-SNE focuses on preserving local neighbourhoods for visualisation; UMAP also aims to preserve neighbourhood structure and can often scale better. These methods can reveal visual groupings but their axes generally have no direct physical meaning.

Parameters matter. In t-SNE, perplexity controls a notion of neighbourhood size; different values and random seeds can change the map. UMAP's n_neighbors and min_dist affect local/global structure and cluster compactness. Distances between far-apart islands in a 2-D embedding should not automatically be interpreted as meaningful global distances.

Use embeddings for exploration, not proof that natural clusters exist. Validate patterns in the original feature space and test stability. A 2-D embedding is not a substitute for robust model evaluation.

## 2. Worked Python example
Run in VS Code. Install the core packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`. For the optional UMAP section, also run `python -m pip install umap-learn`.

```python
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

data = load_digits()
Z = StandardScaler().fit_transform(data.data)

# PCA is a linear projection and is a useful baseline.
pca_coords = PCA(n_components=2, random_state=42).fit_transform(Z)

# t-SNE emphasises local neighbourhoods. Perplexity must be smaller
# than the number of observations; 30 is suitable for this dataset.
tsne_coords = TSNE(
    n_components=2, perplexity=30, init="pca", random_state=42
).fit_transform(Z)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, coords, title in [
    (axes[0], pca_coords, "PCA: linear projection"),
    (axes[1], tsne_coords, "t-SNE: local neighbourhoods")
]:
    points = ax.scatter(coords[:, 0], coords[:, 1],
                        c=data.target, s=8, cmap="tab10")
    ax.set_title(title)
    ax.set_xlabel("Component 1")
    ax.set_ylabel("Component 2")
fig.colorbar(points, ax=axes, label="Digit class")
plt.tight_layout()
plt.show()

# Optional UMAP comparison. Install umap-learn first.
try:
    import umap
except ImportError:
    print("To run UMAP: python -m pip install umap-learn")
else:
    umap_coords = umap.UMAP(
        n_components=2, n_neighbors=15, min_dist=0.1,
        random_state=42
    ).fit_transform(Z)
    plt.scatter(umap_coords[:, 0], umap_coords[:, 1],
                c=data.target, s=8, cmap="tab10")
    plt.title("UMAP: neighbourhood-preserving embedding")
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    plt.show()
```

## 3. Interpreting the maps
PCA chooses directions that capture as much total variance as possible. t-SNE attempts to keep nearby observations near one another in the low-dimensional map. UMAP also builds a neighbourhood graph and optimises a low-dimensional representation. These are different objectives, so the layouts need not agree.

The colour labels in this example are known digit classes used only to inspect the embedding. They are not supplied to PCA or t-SNE during fitting. A visually separated colour group is evidence that the representation exposes some class structure, not proof that a classifier will perform well. The axes have no direct unit such as centimetres or income. Do not compare the numerical coordinates between separate runs.

## 4. Guided practice
Run the optional UMAP block and compare its map with PCA and t-SNE. Repeat t-SNE with a different perplexity (for example 10 and 40) and random seed. Record which local groupings remain visible. Explain why a map that looks more separated is not automatically a better predictive representation.

## 5. Independent practice
Apply the method to a dataset. Compare at least two parameter settings or methods, profile results and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the method attempting to discover?
2. Which assumptions are introduced by the representation or distance?
3. How will you assess stability and usefulness?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Stability, interpretation and practical validation determine whether those patterns deserve to be used.

## Deeper explanation: compare PCA, t-SNE and UMAP

PCA is a linear projection that preserves directions of high global variance. t-SNE and UMAP are nonlinear embedding methods designed primarily to represent neighbourhood relationships in a low-dimensional map. They answer different questions, so their layouts need not agree.

t-SNE converts pairwise similarities into probability distributions and tries to preserve neighbourhood relationships in the map. Perplexity affects the effective neighbourhood scale. Different seeds and perplexities can change the layout. UMAP constructs a weighted neighbourhood graph and optimises a low-dimensional representation. n_neighbors influences local versus broader structure; min_dist influences how tightly points may pack together.

A two-dimensional map can make groups look separated even when separation is weak in the original space. Distances between distant islands, empty gaps and apparent group area should not automatically be interpreted quantitatively. The axes generally have no physical units. Use embeddings for exploration, not proof that natural clusters exist.

Fit PCA as an interpretable baseline, then compare t-SNE or UMAP with documented settings. Repeat with nearby parameter values. Check whether local neighbours remain similar and return to original features for profiling and validation. If labels are used as colours to inspect a map, do not pass them into the unsupervised fitting step.

**Practice:** Create a comparison figure and caption explaining each method's objective. Include a warning that the map is exploratory and does not prove natural clusters.
