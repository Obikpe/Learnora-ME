# Lesson 14: Interpreting and Profiling Segments

## Learning outcomes

By the end of this lesson, you should be able to profile clusters using original feature values; compare counts, medians, means and distributions; create useful segment summaries and visualisations; name segments cautiously; recognise small-group and fairness risks; and translate findings into testable recommendations.

![Teaching diagram: 14](/course-assets/ws09/segment-profiling.svg)

## 1. A cluster label is only the beginning

When a clustering algorithm finishes, it returns labels such as 0, 1 and 2. These are identifiers assigned by the implementation. They do not explain what the groups represent.

The analyst's next task is **cluster profiling**: describing how the observations in each group differ using the original features. Profiling connects the mathematical output to the real question.

Suppose a customer dataset contains recency, number of orders and average basket value. A cluster profile might show that one group has a median recency of 8 days, a median of 10 orders in 90 days and a median basket value of ₦420. Another group might have a median recency of 75 days, one order and a median basket of ₦70.

Those measurements support a descriptive statement about purchasing behaviour. They do not automatically prove loyalty, future churn or customer value over a lifetime.

## 2. Begin with group size

Always calculate the number and percentage of observations in each cluster. A group containing 3 records out of 10,000 should not be treated with the same confidence as a group containing 2,000 records.

Small clusters may represent rare but meaningful patterns, data-quality problems, unusual cases or an unstable model artefact. Inspect them. If they contain sensitive information, consider privacy risks before publishing detailed profiles.

```python
result = customers.assign(cluster=labels)

counts = result["cluster"].value_counts().sort_index()
percentages = result["cluster"].value_counts(normalize=True).sort_index() * 100

summary = pd.DataFrame({
    "count": counts,
    "percentage": percentages.round(1)
})
print(summary)
```

`value_counts` counts how often each label occurs. With `normalize=True`, it returns proportions rather than counts. Multiplying by 100 expresses those proportions as percentages.

## 3. Compare distributions, not only averages

The mean is useful, but it can be distorted by extreme values. The median is the middle value when observations are ordered. The interquartile range describes the middle 50% of values. These measures can reveal differences that an average hides.

For example, two customer groups may have the same average spend. One group may have most customers spending around ₦300; the other may contain many low spenders and a few very high spenders. Their means could match even though their distributions differ.

Use:
- Count and percentage to show group size.
- Mean to describe arithmetic average.
- Median to describe the typical middle observation.
- Standard deviation or IQR to describe spread.
- Minimum and maximum to inspect extremes, with caution.
- Proportions to describe categorical features.

```python
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

customers = pd.DataFrame({
    "recency_days": [5, 8, 12, 65, 75, 90, 3, 10],
    "orders_90d": [12, 10, 8, 2, 1, 0, 14, 9],
    "average_basket": [500, 420, 380, 90, 70, 30, 550, 400]
})

X_scaled = StandardScaler().fit_transform(customers)
labels = KMeans(n_clusters=2, n_init=20, random_state=42).fit_predict(X_scaled)
result = customers.assign(cluster=labels)

profile = result.groupby("cluster").agg(
    customers=("recency_days", "size"),
    mean_recency=("recency_days", "mean"),
    median_recency=("recency_days", "median"),
    mean_orders=("orders_90d", "mean"),
    median_orders=("orders_90d", "median"),
    median_basket=("average_basket", "median")
)
print(profile.round(1))
```

The `groupby` operation separates rows by cluster label. `agg` calculates multiple summary statistics for selected columns. The output should use original, unscaled values.

## 4. Visualise cluster profiles

A table is precise, but charts can make differences easier to see. Possible visuals include:
- Box plots for distributions and outliers.
- Bar charts for group sizes.
- Heatmaps of standardised cluster profiles.
- Small multiples for comparing feature distributions.
- Scatter plots for selected pairs of features.

If you use scaled values in a heatmap, label them clearly. A z-score of 1.2 means the group mean is 1.2 standard deviations above the overall feature mean; it does not mean 1.2 naira or 1.2 orders.

```python
import matplotlib.pyplot as plt

result.boxplot(column="recency_days", by="cluster")
plt.title("Recency distribution by cluster")
plt.suptitle("")
plt.xlabel("Cluster")
plt.ylabel("Days since last purchase")
plt.show()
```

A box plot shows the median, quartiles and potential extreme values under the plotting convention. Do not remove outliers from the chart simply because they make a group look less tidy. They may be important to the interpretation.

## 5. Name segments with evidence

A useful segment name is short, neutral and directly supported by its profile. Examples:
- “Frequent recent purchasers”
- “Low-frequency customers”
- “Higher basket-value group”
- “Longer purchase recency”

Avoid judgemental or unsupported names such as “bad customers”, “disloyal customers” or “future churners”. A cluster based on historical purchasing behaviour cannot prove a customer's intentions or future actions.

A good segment description includes:
1. The number and percentage of observations.
2. The features that distinguish it.
3. The amount of variation inside the group.
4. How stable the group is.
5. The limitations of the interpretation.

## 6. From profile to action: propose a test, not a certainty

A segment may suggest an action. For example, a group with longer recency and fewer recent orders may be a candidate for a re-engagement experiment. But clustering does not show that a campaign will cause customers to return.

A responsible recommendation might be: “Test a low-cost re-engagement message with a random subset of customers in this segment and compare their return rate with a control group.” This separates the descriptive segmentation from the causal question about campaign effectiveness.

## 7. Fairness, privacy and potential proxies

Features such as location, purchase category or service usage may act as proxies for sensitive characteristics. A cluster can therefore reproduce or amplify unequal treatment even if the model never receives an explicit sensitive field.

Review:
- Which features were included and why.
- Whether sensitive information or proxies are present.
- Whether the proposed action is proportionate.
- Whether small groups could expose identities.
- Whether people can be unfairly excluded or targeted.
- Whether the result is appropriate for the decision being considered.

Unsupervised learning is not automatically neutral. The data, features, distance measure and decisions made from the output all reflect choices.

## 8. Common mistakes

- Naming clusters before examining their profiles.
- Reporting only means.
- Ignoring cluster size.
- Describing historical patterns as future behaviour.
- Treating a cluster as a fixed identity for a person.
- Publishing detailed profiles for very small groups.
- Recommending an intervention without testing its effect.

## 9. Guided practice

Take a two-cluster customer result. Prepare a segment card for each group with count, percentage, median recency, median orders, median basket value and one chart. Give each group a neutral descriptive name. Write one proposed low-risk experiment and one limitation.

## 10. Independent practice

Apply a clustering method to a dataset. Produce a profile table and at least two visuals. Write a one-page interpretation for a non-technical reader, separating measured observations, your interpretation, recommended next step and what the analysis cannot establish.

## 11. Knowledge check

1. Why are cluster IDs not meaningful descriptions?
2. Why should cluster size be reported?
3. When is a median more informative than a mean?
4. What is the difference between a descriptive segment name and an unsupported label?
5. Why does a cluster not prove future behaviour?
6. How can small groups create privacy risks?
7. How could a proposed campaign be evaluated more rigorously?

## Lesson summary

Profiling turns cluster assignments into evidence that people can inspect. Use original feature units, group sizes, robust summaries and clear visuals. Name groups neutrally, acknowledge uncertainty and propose experiments rather than claiming that a cluster proves future behaviour or causes an outcome.
