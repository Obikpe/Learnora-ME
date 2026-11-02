# Lesson 11: Interpreting PCA and Explained Variance

## Learning outcomes
Explain the unsupervised method, implement the example and judge whether the discovered structure is meaningful.

## 1. Core explanation
Explained variance ratio is the fraction of total variance captured by each principal component. The cumulative sum indicates how much variance is retained by the first k components. A scree plot shows variance explained by each component and can reveal diminishing returns.

PCA loadings describe each original feature's contribution to a component. The sign of a component can flip without changing the solution, so do not attach meaning to a positive or negative sign without considering the full loading pattern. Features with large absolute loadings contribute strongly.

High explained variance does not guarantee that components preserve information needed for a prediction. Variance is not the same as target relevance. Interpret PCA as a summary of feature variation, not proof of causal factors.

## 2. Worked Python example
Run in VS Code. Install packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`.

```python
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

data = load_iris(as_frame=True)
Z = StandardScaler().fit_transform(data.data)
pca = PCA().fit(Z)
cum = pca.explained_variance_ratio_.cumsum()
plt.plot(range(1, len(cum)+1), cum, marker="o")
plt.xlabel("Number of components"); plt.ylabel("Cumulative explained variance")
plt.ylim(0, 1.05); plt.grid(alpha=.2); plt.show()
print(pca.components_)
```

## 3. Interpretation
Describe the feature representation, model settings and meaning of the output. Validate patterns in original units. Cluster IDs are arbitrary and anomaly flags are not proof of wrongdoing.

## 4. Guided practice
Choose the number of components needed to retain at least 90% of variance. Inspect loadings and write a cautious plain-language description of the first component.

## 5. Independent practice
Apply the method to a dataset. Compare at least two parameter settings or methods, profile results and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the method attempting to discover?
2. Which assumptions are introduced by the representation or distance?
3. How will you assess stability and usefulness?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Stability, interpretation and practical validation determine whether those patterns deserve to be used.