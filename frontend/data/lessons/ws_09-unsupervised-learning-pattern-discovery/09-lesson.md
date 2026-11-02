# Lesson 9: Principal Component Analysis

## Learning outcomes
Explain the unsupervised-learning concept, implement the worked example, interpret the output and assess whether the discovered structure is meaningful.

## 1. Core explanation
Principal Component Analysis (PCA) is a linear dimensionality-reduction method. It finds orthogonal directions (principal components) that capture as much variance as possible. The first component captures the largest possible variance; each later component captures the largest remaining variance subject to being orthogonal to earlier components.

PCA is affected by feature scale. Standardise numeric features when units differ, then fit PCA on training data in a predictive workflow. PCA transforms original features into combinations of them. A component is not usually a directly interpretable business variable; loadings show how original variables contribute.

PCA is useful for visualising high-dimensional data, reducing redundancy and sometimes improving model efficiency. It may discard low-variance information that is important for a target. Choose component count based on explained variance and the task, not solely a round percentage threshold.

## 2. Worked Python example
Run in VS Code. Install relevant packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`. Some scikit-learn dataset loaders may require internet access on first use.

```python
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

data = load_iris(as_frame=True)
Z = StandardScaler().fit_transform(data.data)
pca = PCA(n_components=2)
components = pca.fit_transform(Z)
print("Explained variance ratios:", pca.explained_variance_ratio_)
print("Total retained:", pca.explained_variance_ratio_.sum())
```

## 3. Interpretation
Describe the feature representation, distance or objective, model settings and what the output means. Cluster IDs are arbitrary. An anomaly flag is a prompt for investigation, not proof of misconduct. Validate any discovered pattern in original units and with domain knowledge.

## 4. Guided practice
Inspect the explained variance ratios. Explain what is lost when four original features become two components. State why the PCA model should be fitted on training data only if it is part of a predictive workflow.

## 5. Independent practice
Choose a dataset and state the purpose of the unsupervised analysis. Compare at least two parameter settings. Profile the resulting groups or flagged cases and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the algorithm attempting to discover?
2. Which assumptions are introduced by the distance or representation?
3. How can you tell whether the result is useful rather than merely computable?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Human interpretation, stability checks and practical validation determine whether those patterns deserve to be used.