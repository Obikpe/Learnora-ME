# Lesson 1: Understanding Unsupervised Learning

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain machine learning in plain language and distinguish supervised from unsupervised learning.
- Explain what a target variable is and why an unsupervised dataset does not require one.
- Recognise clustering, dimensionality reduction, anomaly detection and association analysis as different unsupervised tasks.
- Describe the difference between an algorithmic pattern and a useful real-world discovery.
- Frame an unsupervised-learning question with a clear observation unit, purpose and limitation.

![An overview of the unsupervised-learning workflow](/course-assets/ws09/clustering-concepts.svg)

## 1. Begin with the problem: what is machine learning?

Machine learning is a way of using examples and mathematical procedures to make a computer identify patterns or produce useful outputs without writing a separate hand-made rule for every possible situation. The computer does not understand the world as a person does. It receives data represented as numbers, applies an algorithm, and produces a result according to the objective and assumptions built into that algorithm.

Imagine a shop with thousands of customers. A manager wants to understand purchasing behaviour. One possible approach is to write rules: customers who spend more than ₦100,000 are high spenders; customers who have not purchased for 60 days are inactive. Rules can be useful, but the thresholds are chosen by people in advance. Machine learning offers another approach: examine several measured behaviours together and look for recurring patterns that are difficult to see by inspecting individual rows.

The important phrase is **measured behaviours**. A model cannot discover a meaningful concept that the data does not represent. If the spreadsheet contains only customer names and phone numbers, it cannot reliably discover purchasing habits. If it contains recency, order frequency, basket value and product categories, it has information that may represent behaviour.

## 2. Supervised learning compared with unsupervised learning

A dataset is commonly organised as rows and columns. Each row represents an observation; each column represents a measured property of that observation.

In supervised learning, the dataset contains input features and a known answer called the **target** or **label**. For example, a bank may have past loan applications with features such as income, repayment history and loan amount, plus a target showing whether each borrower defaulted. The algorithm learns a relationship between the input features and the known target. Later, it can estimate the target for a new application.

In unsupervised learning, there is no supplied answer column that tells the algorithm the correct group or outcome for each row. The algorithm looks for structure in the input features themselves.

| Question | Supervised learning | Unsupervised learning |
|---|---|---|
| Is a target supplied? | Yes | No target is required |
| Main aim | Learn to predict a known outcome | Discover structure or represent data differently |
| Example | Predict whether a customer will churn | Explore groups of customers with similar behaviour |
| Typical evaluation | Compare predictions with known outcomes | Examine structure, stability, usefulness and domain evidence |

A useful way to remember the difference is this: supervised learning is like practising with questions and answer keys; unsupervised learning is like receiving a large collection of objects and being asked to organise them according to similarities you can justify.

No target does not mean no purpose. The analyst must still define the question. “Find something interesting” is too vague. “Explore whether customers show distinct purchasing patterns using their last 90 days of behaviour” is more useful.

## 3. Four major families of unsupervised tasks

### 3.1 Clustering

Clustering groups observations that are similar according to a chosen representation and similarity measure. A customer-segmentation exercise might group customers using recency, number of orders and average basket value.

The algorithm does not know that a group is “loyal”, “new” or “at risk”. It only assigns observations to groups based on its mathematical rules. The analyst studies the group profiles and decides whether a neutral, evidence-based description is justified.

### 3.2 Dimensionality reduction

A dataset may contain dozens, hundreds or thousands of features. Some features may overlap in the information they contain. Dimensionality reduction creates a smaller representation that retains selected structure from the original data.

For example, a dataset containing 30 measurements of a machine may be represented using two or three derived dimensions for visual exploration. The reduced dimensions are not automatically new physical measurements. They are mathematical combinations of the original features.

### 3.3 Anomaly detection

An anomaly-detection method identifies observations that are unusual under a chosen definition of normality. A sensor reading far outside the usual range may deserve inspection. An unusually large transaction may deserve review.

An anomaly is not proof of fraud, error or danger. It is a signal that something differs from the pattern used by the method. The difference may be a genuine rare event, a data-entry error, a new operating condition or a harmless exception.

### 3.4 Association analysis

Association analysis finds items or events that frequently occur together. A retailer may examine baskets to learn that bread and milk often appear in the same transaction. This can support merchandising hypotheses, but it does not prove that buying one item causes a customer to buy the other.

## 4. The observation unit: what does one row mean?

Before choosing an algorithm, establish the **unit of observation**. This is the real-world thing represented by one row.

A table with one row per transaction describes transactions. A table with one row per customer describes customers. A table with one row per customer per month describes customer-months. The same person may therefore appear in several rows.

This distinction controls what the result means. If you cluster transaction rows, you have grouped transactions; you have not automatically segmented customers. If you want customer segments, first construct one row per customer using an appropriate aggregation period.

A second important concept is the **feature**. A feature is a measured input used to represent an observation. Features should be relevant to the question, measured consistently and available at the time the analysis is intended to be used.

## 5. A first practical example in Python

We will use a small, transparent customer dataset. It is deliberately tiny so you can inspect every row. Real projects require more observations and stronger validation.

Install the packages in the VS Code terminal:

```bash
python -m pip install pandas scikit-learn
```

Create a file named `first_unsupervised_example.py`:

```python
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Each row represents one customer.
customers = pd.DataFrame({
    "recency_days": [5, 8, 12, 65, 75, 90, 3, 10],
    "orders_90d": [12, 10, 8, 2, 1, 0, 14, 9],
    "average_basket": [500, 420, 380, 90, 70, 30, 550, 400]
})

# Convert columns to a comparable numeric scale.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(customers)

# Ask K-means to form two groups.
model = KMeans(n_clusters=2, random_state=42, n_init=10)
cluster_labels = model.fit_predict(X_scaled)

# Attach group IDs to the original, readable measurements.
result = customers.assign(cluster=cluster_labels)
print(result)
print("\nGroup profiles:")
print(result.groupby("cluster").mean(numeric_only=True).round(1))
```

### Understand every important line

- `import pandas as pd` loads pandas, a library for working with tabular data. The word `as` creates the short alias `pd`; it does not change the library.
- `DataFrame` creates a table. Each dictionary key becomes a column name, and each list supplies the values in that column.
- `StandardScaler` is a preprocessing tool. It learns the mean and standard deviation of each column and uses them to put values on comparable scales.
- `fit_transform` first learns the scaling values from the supplied data (`fit`) and then applies the transformation (`transform`).
- `KMeans` is a clustering algorithm. `n_clusters=2` asks it to form two groups. This is a modelling choice, not proof that two natural customer types exist.
- `random_state=42` makes the random initialisation reproducible. The number 42 has no special statistical meaning.
- `n_init=10` asks the implementation to try multiple initial centroid initialisations and keep a strong solution.
- `fit_predict` fits the model and returns a cluster identifier for each row.
- `assign` adds the labels to the original table. We deliberately profile the unscaled values so the output remains understandable in days, orders and currency.

The printed group IDs may be 0 and 1, but group 1 is not necessarily better than group 0. If you rerun a different algorithm or change the data, the numbers can be swapped. Interpret the feature profiles, not the numeric ID.

## 6. What makes a discovered pattern useful?

A model can always produce output if its input and parameters are valid. That does not mean the output is valuable. Evaluate a proposed pattern from several angles:

1. **Mathematical structure:** does the method identify a pattern under its objective?
2. **Stability:** does a similar pattern appear when reasonable settings, random seeds or samples change?
3. **Interpretability:** can you describe the pattern using the original features?
4. **Domain plausibility:** does the pattern make sense in the context of how the data was collected?
5. **Practical usefulness:** could it support a responsible decision or a worthwhile next investigation?
6. **Risk:** could the result unfairly disadvantage people, expose private information or encourage unsupported conclusions?

A cluster may be mathematically compact but too small to support a useful business action. An anomaly detector may flag a legitimate seasonal peak. A two-dimensional projection may make groups look separate even when the original high-dimensional data overlaps.

## 7. Common beginner mistakes

- Treating cluster numbers as rankings.
- Assuming every dataset contains natural clusters.
- Calling an anomaly fraudulent without investigation.
- Forgetting to define what each row represents.
- Including IDs or arbitrary codes as if they were meaningful measurements.
- Using a model because it is popular rather than because it answers the question.
- Describing association as causation.
- Reporting only a colourful chart without explaining the data and limitations.

## 8. Guided practice

A supermarket wants to understand shopping patterns but has no customer-type labels.

1. Define whether one row should represent a transaction or a customer.
2. Suggest four possible features and explain what each measures.
3. Identify two columns that should probably be excluded and explain why.
4. Describe one possible use of the analysis.
5. Write one sentence stating what clustering cannot prove.

## 9. Independent practice

Find or create a small dataset with at least three meaningful numeric features. Write a short analysis plan before running any algorithm. State the question, observation unit, features, exclusions, intended use and limitations. Run the K-means example, inspect the profiles, and explain whether the result is useful or merely computable.

## 10. Knowledge check

1. What is the main difference between supervised and unsupervised learning?
2. Why does unsupervised learning still need a clearly defined question?
3. Explain the difference between clustering and dimensionality reduction.
4. If a model labels a transaction as an anomaly, what can you safely conclude?
5. Why does the observation unit matter when describing clusters?
6. Why should cluster IDs not be described as rankings?

## Lesson summary

Unsupervised learning searches for structure in data without requiring a supplied target. Clustering, dimensionality reduction, anomaly detection and association analysis solve different kinds of problems. The algorithm's output is a mathematical result, not automatically a real-world truth. Strong analysis begins with a clear question, a meaningful observation unit and defensible features, then checks stability, interpretation, usefulness and risk.
