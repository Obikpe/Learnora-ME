# Lesson 11: Other Dimensionality Reduction Methods

## Learning outcomes

By the end of this lesson, you should be able to distinguish linear and nonlinear dimensionality reduction; explain the purpose and limitations of t-SNE and UMAP; recognise when random projection or feature selection may be useful; choose a method based on the analytical task; and interpret two-dimensional embeddings cautiously.

![Dimensionality reduction as a map from many features to fewer dimensions](/course-assets/ws09/pca-rotation.svg)

## 1. PCA is not the only way to reduce dimensions

PCA is a linear method. It finds new axes that capture directions of maximum variance. This is useful when the main structure can be represented by linear combinations of the original features.

However, data may have nonlinear structure. Imagine observations arranged along a curved ribbon or spiral. A straight-line projection may not preserve the relationships that matter. Other methods aim to preserve different kinds of neighbourhood or geometric structure.

The key question is not “Which method is the most advanced?” It is “Which relationships do I need the reduced representation to preserve?”

## 2. Feature selection versus feature extraction

These ideas are related but different.

**Feature selection** keeps a subset of the original columns. If a dataset has 100 features and you retain 15, those 15 are still the original measurements. Selection may be based on domain knowledge, redundancy, variance or other criteria.

**Feature extraction** creates new features from the original ones. PCA is feature extraction: PC1 is a combination of original variables, not one of the original columns.

Feature selection is often easier to explain because the retained features keep their original meanings. Feature extraction can compress correlated information but may be harder to interpret.

## 3. t-SNE: preserve local neighbourhoods for visualisation

t-distributed Stochastic Neighbour Embedding (t-SNE) is a nonlinear dimensionality-reduction method commonly used to visualise high-dimensional data in two or three dimensions.

Its main idea is to represent similarity between observations as probabilities of neighbourhood relationships in the original space, then find a low-dimensional arrangement that preserves those local relationships as well as possible.

t-SNE is particularly useful for exploratory visualisation when you want to inspect local groupings. However, it has important limitations:

- Distances between separate islands in a t-SNE plot may not represent meaningful global distances.
- The size and shape of visual clusters can be misleading.
- Results can change with perplexity, random seed and other settings.
- A visible gap does not prove that natural categories exist.
- t-SNE is generally not a simple reusable transformation for arbitrary future observations in the same way as PCA.

The parameter **perplexity** loosely controls the effective number of neighbours considered when constructing local similarities. It is not literally the number of clusters. It should be adjusted with dataset size and tested across reasonable values.

## 4. Run t-SNE with scikit-learn

```python
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE

wine = load_wine()
X = StandardScaler().fit_transform(wine.data)

embedding = TSNE(
    n_components=2,
    perplexity=30,
    learning_rate="auto",
    init="pca",
    random_state=42
).fit_transform(X)

plt.scatter(embedding[:, 0], embedding[:, 1], c=wine.target)
plt.xlabel("t-SNE dimension 1")
plt.ylabel("t-SNE dimension 2")
plt.title("t-SNE visualisation of the Wine dataset")
plt.show()
```

The Wine dataset includes target classes, but the target is used here only to colour the visualisation after the embedding has been created. It is not passed into t-SNE. In a genuinely unlabeled project, you would colour points by a separate descriptive field only if that field is available and its use is clearly explained.

- `n_components=2` requests a two-dimensional embedding.
- `perplexity=30` sets a neighbourhood-related parameter. It must be smaller than the number of observations and should be tested rather than copied blindly.
- `learning_rate="auto"` lets scikit-learn select a learning rate according to its implementation.
- `init="pca"` uses a PCA-based initial arrangement.
- `random_state=42` supports reproducibility.
- `fit_transform` learns the embedding and returns two coordinates per observation.

The plotted coordinates are not measurements in original units. Do not describe a point at x=10 as having a physical value of 10.

## 5. UMAP: preserve neighbourhood structure with a manifold approach

Uniform Manifold Approximation and Projection (UMAP) is another nonlinear dimensionality-reduction method. It constructs a graph representing local neighbourhood relationships and optimises a lower-dimensional representation to preserve aspects of that structure.

Two important parameters are:

- **n_neighbors:** controls the approximate size of local neighbourhoods. Smaller values emphasise very local structure; larger values incorporate broader relationships.
- **min_dist:** controls how tightly points may be packed in the low-dimensional representation. Lower values can create more tightly packed visual groups.

UMAP is often faster than t-SNE on larger datasets and can support transforming new observations when using a fitted implementation. However, the visual result still depends on parameters, randomisation and data representation. It does not automatically reveal objectively true clusters.

UMAP is commonly installed separately:

```bash
python -m pip install umap-learn
```

```python
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
import umap

wine = load_wine()
X = StandardScaler().fit_transform(wine.data)

reducer = umap.UMAP(
    n_components=2,
    n_neighbors=15,
    min_dist=0.1,
    random_state=42
)
embedding = reducer.fit_transform(X)

plt.scatter(embedding[:, 0], embedding[:, 1], c=wine.target)
plt.xlabel("UMAP dimension 1")
plt.ylabel("UMAP dimension 2")
plt.title("UMAP visualisation of the Wine dataset")
plt.show()
```

The parameter meanings are not interchangeable with t-SNE's perplexity. UMAP's `n_neighbors` controls the neighbourhood scale; `min_dist` influences how tightly points are arranged in the embedding. Test multiple values and report the choices.

## 6. Random projection

Random projection reduces dimensions by multiplying the original feature matrix by a randomly generated projection matrix. Under suitable conditions, distances between observations can be approximately preserved even when the number of dimensions is reduced.

It can be computationally efficient for high-dimensional data, especially when exact interpretability of the new dimensions is not required. But the new axes are random combinations, so they are not naturally named or interpreted.

Scikit-learn provides `GaussianRandomProjection` and `SparseRandomProjection`. A random projection should be evaluated by comparing pairwise distances before and after projection on a manageable sample.

## 7. Choosing a dimensionality-reduction method

| Method | Main idea | Useful for | Important limitation |
|---|---|---|---|
| PCA | Linear directions of maximum variance | Compression, correlated numeric features, baseline visualisation | May miss nonlinear structure |
| t-SNE | Preserve local neighbourhood relationships | Exploratory visualisation | Global distances and cluster sizes can mislead |
| UMAP | Graph-based neighbourhood representation | Visualisation and some reusable embeddings | Sensitive to parameters and representation |
| Random projection | Random linear mapping with approximate distance preservation | Efficient dimension reduction | New dimensions are hard to interpret |
| Feature selection | Keep a subset of original columns | Simplicity and interpretability | May discard useful combined information |

Do not choose a method because its chart looks attractive. Decide which relationships need to be preserved, how the representation will be used and what evidence will support interpretation.

## 8. A crucial warning about visual clusters

A two-dimensional embedding is a map, not the territory. It compresses information. Apparent islands may be influenced by the method's objective and settings. Before claiming clusters exist, examine the original features, compare methods, test stability and use clustering validation where appropriate.

If you intend to cluster the original data, do not automatically cluster the two-dimensional t-SNE map. The embedding may distort global distances. It may be useful to cluster in the original or a carefully selected representation and use a two-dimensional embedding only for visual inspection.

## 9. Guided practice

Take a dataset with at least 10 numeric columns. Explain what PCA, t-SNE and UMAP would each attempt to preserve. State which one you would use for a first visual exploration and what you would not infer from its plot.

## 10. Independent practice

Run PCA and either t-SNE or UMAP on the same scaled dataset. Compare the plots and note which local and global patterns appear different. Change at least one parameter and describe the effect. Write a cautious interpretation that separates visible structure from evidence of real categories.

## 11. Knowledge check

1. What is the difference between feature selection and feature extraction?
2. What kind of structure does t-SNE try to preserve?
3. What does UMAP's n_neighbors parameter influence?
4. Why should distances between t-SNE islands be interpreted cautiously?
5. Why is a visually separated embedding not proof of natural clusters?
6. When might PCA be more appropriate than t-SNE?
7. Why might random projection be useful for high-dimensional data?

## Lesson summary

PCA, t-SNE, UMAP and random projection reduce dimensions in different ways. PCA captures linear variance; t-SNE and UMAP focus on neighbourhood structure; random projection provides an efficient approximate mapping; feature selection retains original columns. Choose based on the relationships you need to preserve, and treat low-dimensional plots as exploratory representations rather than unquestionable evidence.
