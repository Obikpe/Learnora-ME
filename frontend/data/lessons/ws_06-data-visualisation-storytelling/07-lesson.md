# Lesson 7: Distributions and Univariate Analysis

## Learning outcomes
Explain a numerical distribution, compare centre and spread, choose a useful plot, and recognise how outliers and bin width affect interpretation.

## 1. Understand one variable
Univariate analysis studies one variable at a time. Describe its centre, spread, shape and unusual values. The mean is the arithmetic average and is sensitive to extreme observations. The median is the middle ordered value and is more resistant. The range uses only the minimum and maximum; the interquartile range (IQR) covers the middle half of the observations.

A histogram groups numeric values into bins. Wide bins can hide structure; narrow bins can create noisy detail. A density curve smooths the distribution and depends on a bandwidth choice. A box plot summarises the median, quartiles and potential outliers, but hides multimodality and detailed shape. Use complementary views when distribution shape matters.

For categories, show counts or proportions. Include the denominator when comparing proportions: 20 cases out of 25 is not equivalent to 20 out of 2,000. Inspect missing values separately because dropping missing records can change the apparent distribution.

## 2. Worked example
Install packages in the VS Code terminal with `python -m pip install seaborn matplotlib`.

```python
import seaborn as sns
import matplotlib.pyplot as plt

scores = [42, 55, 58, 61, 63, 65, 67, 68, 70, 72, 75, 91]
fig, axes = plt.subplots(1, 2, figsize=(9, 4))
sns.histplot(scores, bins=6, ax=axes[0])
axes[0].set_title("Score distribution")
sns.boxplot(x=scores, ax=axes[1])
axes[1].set_title("Score summary")
plt.tight_layout()
plt.show()
```

The histogram shows the shape and possible gaps. The box plot gives a compact summary. Neither plot alone explains why a learner scored unusually high or low.

## 3. Guided investigation
Calculate the mean and median. Add one extreme value such as 200 and recalculate them. The mean changes substantially because it uses every value and its distance from the centre. The median is less affected because it depends on the ordered middle position.

Change the histogram bin count. Notice that the same observations can look smooth, clustered or irregular depending on the binning. A charting choice should not be selected merely because it produces the most attractive shape.

## 4. Independent practice
Use a real numeric field such as transaction amount, learner score or delivery time. Report mean, median, standard deviation and IQR. Create a histogram and box plot. Explain skew, unusual values and missingness. Do not delete outliers without investigating whether they are data errors or valid rare observations.

## 5. Knowledge check
1. Why is the median often preferable for a strongly skewed variable?
2. What information does a histogram show that a box plot hides?
3. How can bin width change the visual impression?
4. Why should missingness be inspected before interpreting a distribution?

## Lesson summary
A distribution is more than an average. Examine centre, spread, shape, outliers and missingness together, and explain how plotting choices affect what a reader sees.