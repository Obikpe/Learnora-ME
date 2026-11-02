# Lesson 10: Interpreting PCA and Explained Variance

## Learning outcomes

By the end of this lesson, you should be able to Calculate explained-variance ratios and cumulative variance; read a scree plot; inspect component loadings; and explain why retained variance is not the same as target relevance.

## 1. Core explanation
Explained variance ratio is the fraction of total variance captured by each component. The cumulative sum indicates how much total variance is retained by the first k components. A scree plot shows the variance explained by each component and can reveal diminishing returns.

PCA loadings describe the contribution of each original feature to a component. The sign of a component can flip without changing the mathematical solution, so do not attach meaning to a positive or negative sign without considering the full loading pattern. Features with large absolute loadings contribute strongly.

High explained variance does not guarantee that components preserve information needed for a specific prediction. Variance is not the same as relevance to a target. Interpret PCA as a summary of feature variation, not as proof of causal factors or latent constructs.

## 2. Worked Python example
Run in VS Code. Install relevant packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`. Some scikit-learn dataset loaders may require internet access on first use.

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
Describe the feature representation, distance or objective, model settings and what the output means. Cluster IDs are arbitrary. An anomaly flag is a prompt for investigation, not proof of misconduct. Validate any discovered pattern in original units and with domain knowledge.

## 4. Guided practice
Choose the number of components needed to retain at least 90% of variance. Inspect loadings and write a cautious plain-language description of the first component.

## 5. Independent practice
Choose a dataset and state the purpose of the unsupervised analysis. Compare at least two parameter settings. Profile the resulting groups or flagged cases and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the algorithm attempting to discover?
2. Which assumptions are introduced by the distance or representation?
3. How can you tell whether the result is useful rather than merely computable?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Human interpretation, stability checks and practical validation determine whether those patterns deserve to be used.