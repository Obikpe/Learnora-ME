# Lesson 1: Feature Engineering as a Modelling Discipline

## Learning outcomes
By the end of this lesson, you should be able to define a feature and feature engineering; distinguish raw fields from useful model inputs; define the observation grain and prediction time; construct basic behavioural features; and explain why a feature must be meaningful, available and reproducible.

## 1. What is a feature?
A machine-learning model receives information in a structured form. A **feature** is one measured input variable used by the model. In a customer dataset, examples include age, number of purchases, average order value and days since the last purchase. A target is the outcome the model is being trained to estimate, such as whether the customer will cancel a subscription.

Raw data is not always ready to become useful features. A transaction table may contain one row per purchase, while the business question concerns customers. The analyst must decide how to turn many transaction records into a customer-level representation. This process is feature engineering: creating, transforming or selecting variables so that they represent information relevant to the modelling problem.

A useful feature is not merely mathematically possible. It should have a clear meaning, a reliable source, consistent units and a defensible relationship to the question. More columns do not automatically mean a better model. Irrelevant, duplicated or unreliable columns can add noise and make the model harder to maintain.

## 2. Define the observation before creating features
The **observation unit**, or grain, is what one row represents. It might be one customer, one transaction, one machine reading, one patient visit or one customer-month. If your table has one row per transaction, clustering or predicting directly on those rows answers a transaction-level question. It does not automatically answer a customer-level question.

Next define the **prediction time**: the moment at which the model is expected to make a prediction. Imagine predicting on 1 March whether a customer will purchase during March. Features may use information available up to the end of February, but must not use purchases made later in March. This time boundary is central to reliable feature engineering.

![Feature engineering workflow](/course-assets/ws10/feature-engineering-workflow.svg)

## 3. Common feature patterns
- **Counts:** number of orders, support tickets or website sessions in a defined window.
- **Recency:** elapsed time since the most recent event.
- **Frequency:** events per day, week or month.
- **Aggregates:** sum, mean, median, minimum, maximum or standard deviation.
- **Ratios:** returned units divided by purchased units, with zero-denominator handling.
- **Differences and changes:** current month compared with the previous month.
- **Interactions:** a combination of two variables, such as price multiplied by quantity.
- **Domain indicators:** a rule-based flag whose meaning is documented.

Always state the time window. “Orders” is ambiguous; “number of completed orders in the 90 days before the snapshot date” is precise.

## 4. Worked Python example
Install the packages in your VS Code environment with `python -m pip install pandas numpy scikit-learn`.

```python
import pandas as pd

orders = pd.DataFrame({
    "customer_id": [1, 1, 1, 2, 2, 3],
    "order_date": pd.to_datetime([
        "2026-01-03", "2026-01-18", "2026-02-10",
        "2026-01-20", "2026-02-02", "2026-02-25"
    ]),
    "amount": [40, 65, 35, 120, 80, 25]
})

snapshot_date = pd.Timestamp("2026-03-01")
recent = orders.loc[orders["order_date"] < snapshot_date].copy()

features = recent.groupby("customer_id").agg(
    order_count=("amount", "size"),
    total_spend=("amount", "sum"),
    average_order_value=("amount", "mean"),
    last_order_date=("order_date", "max")
)
features["recency_days"] = (
    snapshot_date - features["last_order_date"]
).dt.days

print(features.round(2))
```

`groupby("customer_id")` creates a group for each customer. `agg()` calculates several summaries in one operation. `size` counts rows, `sum` totals spending, `mean` calculates the average, and `max` finds the latest order date. The final subtraction calculates recency in days. Notice that the example explicitly limits records to dates before the snapshot.

## 5. Interpret and challenge the result
A customer with high order count and low recency has purchased often and recently. A customer with low order count and high recency has purchased less often and not recently. These descriptions are supported by the measurements; labels such as “loyal” or “at risk” require further business evidence.

Check that each feature is available when the prediction is made. Confirm that the customer identifier is used for grouping but is not accidentally treated as a meaningful numeric quantity. Check units, impossible values, missing dates and duplicated transactions. Preserve raw columns so transformations can be audited.

## 6. Common mistakes
- Aggregating transaction rows when the intended prediction unit is a customer.
- Using all-time totals when the task requires a fixed historical window.
- Including events recorded after prediction time.
- Creating ratios without handling a zero denominator.
- Assuming a feature is useful simply because it improves one score.
- Manually transforming training and test files differently.

## 7. Guided practice
Create customer-level features for a fictional online shop: number of orders in 30 days, total spend in 30 days, average basket value and days since last order. State the snapshot date and explain why every included record is eligible.

## 8. Independent practice
Choose a public dataset and write a small feature dictionary. For each feature, document its definition, unit, source column, time window, missing-value meaning and earliest availability time. Propose two additional features and explain why they might help.

## Knowledge check
1. What is the difference between a raw field and an engineered feature?
2. Why must the observation grain be defined before aggregation?
3. What does prediction time mean?
4. Why is “number of orders” an incomplete feature definition?
5. Give one example of a feature that would leak future information.

## Lesson summary
Feature engineering translates raw records into meaningful model inputs. Strong features have a defined observation grain, clear calculation, consistent units and legitimate prediction-time availability. Every feature should be documented and tested rather than accepted because it produces a convenient score.