# Lesson 14: Interpreting and Profiling Segments

## Learning outcomes

By the end of this lesson, you should be able to Profile cluster assignments using original feature units; compare group sizes, medians and distributions; name segments cautiously; and identify evidence needed before taking action.

![Cluster assignments must be interpreted and validated by an analyst](/course-assets/ws09/clustering-concepts.svg)

## 1. Core explanation
Cluster profiling describes how groups differ using original feature units. Compare counts, medians, means, distributions and proportions. A profile should answer what distinguishes a segment, how large it is and whether the difference is stable. Use box plots or summary tables to reveal within-cluster variation, not only averages.

Cluster labels are arbitrary identifiers. Give a descriptive name only after examining evidence and confirming that the label is useful and not misleading. A segment called high-value customers should be based on a defined value measure, not a guess from a cluster number.

Profiles can hide small or internally diverse groups. Report segment sizes and consider privacy when a cluster is tiny. Validate whether segments support a real action and whether that action is fair and appropriate.

## 2. Worked Python example
Run in VS Code. Install packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`.

```python
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

customers = pd.DataFrame({"recency_days": [5,8,12,60,75,90,3,10],
                          "orders_90d": [12,10,8,2,1,0,14,9],
                          "avg_basket": [500,420,380,90,70,30,550,400]})
labels = KMeans(n_clusters=2, n_init=20, random_state=42).fit_predict(
    StandardScaler().fit_transform(customers))
print(customers.assign(segment=labels).groupby("segment").agg(
    size=("recency_days","size"), median_recency=("recency_days","median"),
    mean_orders=("orders_90d","mean"), mean_basket=("avg_basket","mean")))
```

## 3. Interpretation
Describe the feature representation, model settings and meaning of the output. Validate patterns in original units. Cluster IDs are arbitrary and anomaly flags are not proof of wrongdoing.

## 4. Guided practice
Name the segments based on their profiles, then challenge your labels. What additional business outcome or longitudinal evidence would show whether segmentation is useful?

## 5. Independent practice
Apply the method to a dataset. Compare at least two parameter settings or methods, profile results and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the method attempting to discover?
2. Which assumptions are introduced by the representation or distance?
3. How will you assess stability and usefulness?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Stability, interpretation and practical validation determine whether those patterns deserve to be used.

## Deeper explanation: turn cluster IDs into defensible profiles

A cluster profile translates a mathematical assignment into evidence people can inspect. Start with size, then compare distributions—not only means. Means can be distorted by skew and extreme values, so medians and interquartile ranges are often useful. Include proportions for categorical variables and show within-cluster spread.

A useful profile answers: how many observations are in the group; which measured features distinguish it from the overall population; how much variation exists inside it; whether the distinction persists across seeds or time periods; and what action, if any, could reasonably be tested.

Avoid turning a descriptive profile into a psychological story. “Customers with fewer recent orders and longer recency” is grounded. “Disloyal customers” is a judgement that may not be supported. Names should be neutral and tied to measurable behaviour.

If a segment suggests a campaign, run an experiment or careful evaluation. Clustering does not establish that a campaign will work. Check fairness because a segment may proxy for sensitive characteristics or create unequal treatment. Small clusters can create re-identification risks; suppress or aggregate small groups where appropriate.

**Practice:** Write a segment card for each cluster: size, neutral name, distinguishing evidence, uncertainty, proposed low-risk test and what the analysis does not prove.
