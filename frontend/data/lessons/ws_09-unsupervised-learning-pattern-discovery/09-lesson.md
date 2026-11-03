# Lesson 9: Principal Component Analysis (PCA)

## Learning outcomes

By the end of this lesson, you should be able to explain why dimensionality reduction is useful; describe variance and correlated features intuitively; explain principal components as new axes; distinguish fitting PCA from transforming data; use scikit-learn's PCA; and explain why PCA components are not automatically meaningful real-world variables.

![PCA rotates the coordinate system to capture directions of variation](/course-assets/ws09/pca-rotation.svg)

## 1. Why reduce the number of dimensions?

A feature is one measured property of an observation. A dataset with 3 columns has 3 dimensions; a dataset with 100 columns has 100 dimensions. When there are many features, analysis becomes harder to visualise, computationally expensive and sometimes less effective because many columns contain overlapping or irrelevant information.

Imagine measuring the same machine every minute using temperature, vibration, pressure, motor speed, current and several related sensor readings. Some measurements may rise and fall together because they reflect a shared underlying process. Instead of analysing every measurement independently, we may want a smaller representation that captures much of the variation.

**Dimensionality reduction** transforms data from a larger number of features into fewer derived dimensions. It can help visualisation, compression, noise reduction and downstream modelling. But reducing dimensions always involves a trade-off: some information is retained and some may be discarded.

## 2. What does variance mean?

Variance describes how spread out values are around their mean. If every student in a class scored exactly 70, the score has zero variance. If scores range from 20 to 100, they have greater variance.

In data analysis, a feature with high variance changes substantially across observations. PCA looks for directions in the data along which the observations vary most.

High variance is not the same as high importance. A feature may vary widely because of measurement noise or because it uses a large scale. PCA does not know which variation matters to a business or scientific question. Scaling and feature choice are therefore important.

## 3. Correlation and overlapping information

Suppose two sensor features rise together. When temperature is high, pressure is also usually high. These columns contain related information. A scatter plot may show points following a diagonal pattern rather than filling the whole two-dimensional plane.

PCA can rotate the coordinate system so that the first new axis follows the direction of greatest variation. A second axis is perpendicular to the first and captures as much remaining variation as possible. In two dimensions, this can describe the same observations using two new axes that may align better with the shape of the data.

PCA does not simply delete one of the original columns. It creates new variables called **principal components**, each formed as a weighted combination of the original features.

## 4. Principal components, intuitively

Imagine a cloud of points on a sheet of paper. The cloud is long and narrow, tilted diagonally. The original x-axis and y-axis are not aligned with the cloud's longest direction.

PCA finds a new first axis pointing along the cloud's greatest spread. This is the first principal component (PC1). It then finds a second axis at right angles to PC1, capturing the greatest remaining variation. This is PC2.

In higher dimensions, the same idea extends to additional mutually orthogonal directions. The components are ordered: PC1 captures the greatest variance possible, PC2 captures the greatest remaining variance subject to being perpendicular to PC1, and so on.

The component scores are the coordinates of each observation in this new coordinate system. These scores can be used for visualisation or as a reduced feature representation.

## 5. What does PCA calculate?

At a high level, PCA:

1. Centres each feature by subtracting its mean.
2. Often standardises features first when their units and scales differ.
3. Examines how features vary together, commonly through a covariance or correlation matrix.
4. Finds eigenvectors and eigenvalues of that matrix, or uses an equivalent singular value decomposition.
5. Orders components by the amount of variance they explain.
6. Projects the original observations onto the selected component directions.

An **eigenvector** gives a direction (the component loading direction). Its associated **eigenvalue** describes how much variance lies along that direction. You do not need to derive the full linear algebra immediately, but you should understand the relationship: direction plus variance.

## 6. Run PCA with scikit-learn

Install the packages:

```bash
python -m pip install numpy pandas matplotlib scikit-learn
```

```python
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

measurements = pd.DataFrame({
    "temperature": [20, 22, 24, 26, 28, 30, 32, 34],
    "pressure": [100, 105, 111, 116, 123, 128, 134, 140],
    "vibration": [2, 2.2, 2.5, 2.6, 3.0, 3.1, 3.5, 3.7]
})

# PCA is sensitive to scale, so standardise these different units.
X_scaled = StandardScaler().fit_transform(measurements)

pca = PCA(n_components=2)
scores = pca.fit_transform(X_scaled)

print("Explained variance ratio:", pca.explained_variance_ratio_)
print("Component directions:")
print(pca.components_)

plt.scatter(scores[:, 0], scores[:, 1])
plt.xlabel("Principal component 1")
plt.ylabel("Principal component 2")
plt.title("Observations represented in two PCA dimensions")
plt.show()
```

### Understand the code

- `StandardScaler` transforms each feature to a mean near zero and standard deviation near one.
- `PCA(n_components=2)` asks PCA to retain two principal components.
- `fit_transform` learns the component directions from the input and projects each observation into the new coordinate system.
- `explained_variance_ratio_` reports the fraction of total variance represented by each retained component.
- `components_` contains the component directions as weighted combinations of the original columns.
- The scatter plot uses the first and second component scores as x and y coordinates.

The axes are not temperature and pressure. They are derived combinations of the original measurements. Do not label PC1 as “temperature” unless the component interpretation is genuinely supported by its loadings and domain context.

## 7. Why scaling matters for PCA

PCA is based on variance. A feature measured in large numerical units can dominate the directions of maximum variance. For example, annual income in naira may have values in the hundreds of thousands, while age ranges from 18 to 80. Without scaling, income may dominate the first component simply because of its numerical scale.

Standardisation can make features more comparable, but it is not always the right choice. If the original units and variances are meaningful and intentionally weighted, centring without standardising may be appropriate. The decision should reflect the analytical question.

## 8. PCA limitations

- Components are combinations of original features and may be difficult to interpret.
- PCA captures linear directions of variance; it may miss nonlinear structure.
- High variance does not guarantee relevance to the outcome or decision.
- Scaling choices can change the components.
- Reducing dimensions loses some information unless all components are retained.
- PCA is sensitive to extreme values because covariance and variance are sensitive to outliers.
- PCA does not create clusters; it creates a new representation.

## 9. Guided practice

Imagine a dataset with height, weight and waist circumference. Explain why these features may be correlated. Describe what the first principal component might represent and why it would be incorrect to call it “health” without further evidence.

## 10. Independent practice

Use a dataset with at least five numeric features. Compare PCA with and without standardisation. Plot the first two components and inspect component loadings. Explain which original features contribute strongly to each component and what information may have been lost.

## 11. Knowledge check

1. What problem does dimensionality reduction attempt to address?
2. What does variance measure?
3. What is a principal component?
4. Why is PC2 perpendicular to PC1?
5. What does `explained_variance_ratio_` report?
6. Why should you not automatically interpret PC1 as a real-world concept?
7. Why can feature scaling change PCA results?

## Lesson summary

PCA creates new, orthogonal directions that capture as much variance as possible in descending order. It can compress correlated numeric features and make high-dimensional data easier to explore. Its components are mathematical combinations, not automatically meaningful concepts, and their interpretation depends on feature selection, scaling, loadings and domain knowledge.
