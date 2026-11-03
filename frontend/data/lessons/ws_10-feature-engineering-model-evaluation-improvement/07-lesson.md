# Lesson 7: Binning, Interactions and Polynomial Features

## Learning outcomes
Explain discretisation and its trade-offs; construct interaction and polynomial terms; recognise overfitting risk; and decide when engineered combinations are justified.

## 1. Binning numerical values
Binning converts a continuous variable into intervals. Age might be grouped into ranges, or transaction value into low, medium and high bands. Binning can simplify interpretation and represent non-linear relationships, but it discards detail and introduces boundaries.

Equal-width bins divide the numerical range into intervals of equal size. Quantile bins aim for similar numbers of observations per bin. Neither is universally superior. Quantile bins can produce different boundaries in different samples; equal-width bins can leave some bins nearly empty when data is skewed.

## 2. Interactions
An interaction feature represents a combined effect. Suppose the relationship between advertising spend and sales differs by campaign channel. A model with only two additive terms may not represent that difference. An interaction such as spend multiplied by a channel indicator can allow a different slope for that channel.

Interactions should be motivated by domain reasoning or exploratory evidence, not generated indiscriminately. With many variables, the number of possible pairwise interactions grows rapidly.

## 3. Polynomial features
Polynomial expansion can add squared terms and interactions. For a feature x, a degree-2 expansion may include x, x² and interactions with other features. This allows a linear model to represent some curved relationships while remaining linear in its learned coefficients.

The number of terms can increase quickly. For p input features and degree d, expansion may produce many combinations. High-dimensional expansion can overfit, increase computation and make interpretation harder. Regularisation and cross-validation become important.

![Feature combinations](/course-assets/ws10/feature-combinations.svg)

## 4. Worked example
```python
import pandas as pd
from sklearn.preprocessing import KBinsDiscretizer, PolynomialFeatures

X = pd.DataFrame({
    "age": [19, 24, 31, 42, 55, 67],
    "income": [20, 28, 35, 55, 80, 95]
})

binner = KBinsDiscretizer(
    n_bins=3, encode="ordinal", strategy="quantile"
)
age_band = binner.fit_transform(X[["age"]])
print("Age bands:", age_band.ravel())
print("Learned edges:", binner.bin_edges_[0])

poly = PolynomialFeatures(degree=2, include_bias=False)
expanded = poly.fit_transform(X[["age", "income"]])
print(poly.get_feature_names_out(["age", "income"]))
print(expanded)
```

The bin edges are learned from the data supplied to `fit`; in evaluation they must be learned from training folds only. `include_bias=False` avoids adding a constant column because most estimators already handle an intercept. The expanded names reveal the generated terms, such as squared age and age multiplied by income.

## 5. Choosing whether to engineer
Ask what relationship you expect the new feature to represent. Is the effect plausible? Can the feature be computed at prediction time? Does it create a stable improvement across folds? Is the resulting model still understandable enough for its use? Compare a baseline with one controlled change at a time.

## 6. Common mistakes
- Treating bin boundaries as natural facts.
- Binning every numeric variable and losing useful precision.
- Creating all pairwise interactions without a rationale.
- Expanding features without checking dimensionality.
- Evaluating a transformed dataset using a split that allowed the transformation to learn from test data.
- Interpreting a polynomial coefficient without considering the other terms and feature scale.

## Guided practice
For a model predicting delivery time, propose one binned feature, one interaction and one squared term. Explain the real-world relationship each might capture.

## Independent practice
Compare a baseline linear regression with a pipeline that includes degree-2 polynomial features and regularisation. Use identical cross-validation folds and inspect both error and model complexity.

## Knowledge check
1. What information can binning discard?
2. What is an interaction feature?
3. Why can polynomial expansion overfit?
4. What does `include_bias=False` control?
5. How would you test whether an engineered term is useful?

## Lesson summary
Binning, interactions and polynomial terms let models represent patterns that simple raw columns may not express. Use them selectively, preserve prediction-time validity and verify improvements across reliable validation folds.

## 7. Deeper reasoning: complexity grows faster than intuition suggests

Polynomial expansion can increase the number of columns much more quickly than a learner expects. With p original features and degree two, the expanded matrix includes the original terms, squared terms and pairwise products. With dozens of original columns, this can create hundreds or thousands of candidate terms. Higher degrees increase the number further. The result may be computationally expensive and difficult to interpret.

An interaction is meaningful when the effect of one feature plausibly depends on another. For example, the effect of delivery distance on delivery time may differ by vehicle type. A distance-by-vehicle interaction could represent that difference. However, an interaction term should not be added merely because two columns exist. It needs a hypothesis and a way to evaluate whether the additional complexity helps.

Binning has a different trade-off. It can make a relationship easier to communicate, but it creates discontinuities. Two customers aged 39 and 40 might be placed in different bands even though their ages are nearly identical. The model may then treat them as more different than customers aged 40 and 59 within the same band. If boundaries are chosen from business rules, document why. If boundaries are learned from quantiles or data distributions, fit them within training folds.

A sound experiment compares a baseline with a carefully chosen transformation and examines both score and stability. If a feature expansion improves one fold but harms others, it may be fitting sample-specific noise. Regularisation can help, but it cannot rescue a poorly defined prediction problem or a leaky feature.