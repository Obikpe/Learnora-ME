# Lesson 5: Scaling and Transforming Numerical Features

## Learning outcomes
Explain feature scale and distribution; distinguish standardisation from min-max scaling; recognise when scaling matters; apply transformations safely; and interpret transformed values.

## 1. Why scale can matter
Numerical features can use very different units. Income might range from 20,000 to 2,000,000, while a rating ranges from 1 to 5. Algorithms that use distances, dot products or regularisation may be dominated by the large-scale variable even when it is not more important.

Scaling changes numerical representation; it does not make a feature more informative. It should be selected according to the algorithm and the data. Tree-based models such as decision trees and random forests generally do not require standard scaling because their splits depend on ordering and thresholds, not Euclidean distance.

## 2. Standardisation
Standardisation subtracts the training mean and divides by the training standard deviation:

`z = (x - mean) / standard_deviation`

A value of 0 is at the training mean; +1 is one standard deviation above it. Standardised values are not percentages or probabilities. The transformed data is not guaranteed to be normally distributed.

## 3. Min-max scaling
Min-max scaling maps values to a chosen range, often [0, 1]:

`x_scaled = (x - minimum) / (maximum - minimum)`

It is sensitive to extreme values. If a new observation exceeds the training maximum, its transformed value can exceed 1 unless clipping is explicitly configured. The min and max must be learned from training data only.

## 4. Robust scaling and distribution transforms
RobustScaler uses the median and interquartile range, making it less affected by extreme values. Log transformations can reduce right skew for positive variables, but zero and negative values require a deliberate approach. Power transformations can make some distributions more symmetric. Do not transform values mechanically: understand the variable and preserve interpretability.

![Scaling methods](/course-assets/ws10/scaling-methods.svg)

## 5. Worked example
```python
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

X = pd.DataFrame({
    "annual_income": [25000, 30000, 42000, 50000, 250000],
    "rating": [2, 3, 3, 4, 5]
})

for name, scaler in {
    "standard": StandardScaler(),
    "min_max": MinMaxScaler(),
    "robust": RobustScaler()
}.items():
    transformed = scaler.fit_transform(X)
    print(f"\n{name}:")
    print(pd.DataFrame(transformed, columns=X.columns).round(2))
```

The last income is an extreme value. Notice how it can influence the standard deviation and min-max range. Robust scaling uses median and interquartile range, which reduces that influence. This does not mean robust scaling is always best; it is a candidate to compare.

## 6. When scaling is usually important
Scaling is often important for K-nearest neighbours, K-means, support vector machines, principal component analysis and many gradient-based models. It is usually less important for tree-based methods. Regularised linear models can also benefit because penalty terms are affected by feature scale.

Fit the scaler on training data and apply the same fitted transformation to validation and test data. Put it inside a Pipeline so cross-validation repeats this correctly.

## 7. Common mistakes
- Scaling before splitting the data.
- Assuming standardisation makes data normal.
- Applying log to zero or negative values without a plan.
- Using min-max scaling when extreme outliers dominate the range.
- Scaling one dataset independently from another and comparing the results as if the units matched.
- Scaling identifiers or arbitrary category codes as if they were measurements.

## Guided practice
Take columns for monthly income, number of purchases, customer rating and days since last order. Decide which models may need scaling and explain which scaler you would test first.

## Independent practice
Compare StandardScaler, MinMaxScaler and RobustScaler inside the same cross-validation design for a distance-based model. Record the distribution and metric for each candidate. Do not choose solely from the highest single fold.

## Knowledge check
1. What does a standardised value of +2 mean?
2. Why can min-max scaling be sensitive to outliers?
3. Which algorithms commonly depend on feature scale?
4. Why do tree models often need no scaling?
5. Why must the scaler be fitted within each training fold?

## Lesson summary
Scaling makes numerical units more comparable for algorithms sensitive to magnitude. Select the transformation based on the algorithm, distribution and intended interpretation, and never learn scaling parameters from held-out data.