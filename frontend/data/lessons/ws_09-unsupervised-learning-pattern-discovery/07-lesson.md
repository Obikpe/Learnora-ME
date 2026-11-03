# Lesson 7: DBSCAN and Density-Based Clustering

## Learning outcomes

By the end of this lesson, you should be able to Explain density-based clustering; configure DBSCAN's eps and min_samples; identify noise points; and describe how scale and density variation affect its results.

## 1. Core explanation
DBSCAN groups points in dense regions and marks isolated points as noise. It uses eps (the neighbourhood radius) and min_samples (the minimum neighbours needed for a core point). Unlike K-means, it does not require a cluster count and can identify non-spherical shapes.

DBSCAN is sensitive to feature scaling and parameter choice. If eps is too small, many points become noise; if too large, distinct groups may merge. It struggles when clusters have very different densities. In high-dimensional spaces, distance becomes less informative.

Noise points are not necessarily errors or fraudulent records. They are observations that do not fit a dense region under the selected parameters. Investigate them and validate whether they represent rare behaviour, data quality issues or a different population.

## 2. Worked Python example
Run in VS Code. Install relevant packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`. Some scikit-learn dataset loaders may require internet access on first use.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

X, _ = make_moons(n_samples=350, noise=.06, random_state=8)
Z = StandardScaler().fit_transform(X)
labels = DBSCAN(eps=.22, min_samples=6).fit_predict(Z)
plt.scatter(Z[:, 0], Z[:, 1], c=labels)
plt.title("DBSCAN clusters (-1 indicates noise)")
plt.xlabel("Scaled feature 1"); plt.ylabel("Scaled feature 2")
plt.show()
```

## 3. Interpretation
Describe the feature representation, distance or objective, model settings and what the output means. Cluster IDs are arbitrary. An anomaly flag is a prompt for investigation, not proof of misconduct. Validate any discovered pattern in original units and with domain knowledge.

## 4. Guided practice
Change eps to .1, .22 and .5. Compare number of clusters and noise points. Explain why a single parameter set may not fit data with varying densities.

## 5. Independent practice
Choose a dataset and state the purpose of the unsupervised analysis. Compare at least two parameter settings. Profile the resulting groups or flagged cases and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the algorithm attempting to discover?
2. Which assumptions are introduced by the distance or representation?
3. How can you tell whether the result is useful rather than merely computable?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Human interpretation, stability checks and practical validation determine whether those patterns deserve to be used.

## Deeper explanation: density is local

DBSCAN identifies dense regions separated by areas of lower density. Its eps parameter defines the neighbourhood radius; min_samples defines how many observations must be in that neighbourhood for a point to qualify as a core point. A border point lies within a core point's neighbourhood but does not itself have enough neighbours. A noise point is not assigned to a dense cluster and is labelled -1 by scikit-learn.

DBSCAN can discover irregularly shaped groups and does not require the number of clusters in advance. However, one global eps can struggle when groups have very different densities. In high dimensions, distance becomes less informative and parameter selection becomes harder.

Scale meaningful numeric features before using Euclidean distance. A k-distance plot can help: calculate each observation's distance to its min_samples-th nearest neighbour, sort those distances and inspect a possible bend. The bend is a diagnostic, not an automatic answer. Test nearby values and inspect cluster sizes and the noise proportion.

A point labelled noise is not necessarily erroneous or suspicious. It may be a legitimate rare case, a new behaviour or an artefact of poor scaling. Review original records before taking action.

**Practice:** Run DBSCAN with two eps values and two min_samples values. Record cluster count, noise proportion and profiles. Explain whether the change reflects a meaningful density structure or parameter sensitivity.
