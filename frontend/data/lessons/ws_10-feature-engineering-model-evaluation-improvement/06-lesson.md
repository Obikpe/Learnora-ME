# Lesson 6: Date, Time and Text Features

## Learning outcomes
Extract useful calendar and elapsed-time features; create lag and rolling-window features without future information; represent simple text characteristics; and explain why time-aware feature engineering requires careful ordering.

## 1. Date and time are structured information
A timestamp can encode several useful concepts: day of week, month, hour, season, elapsed time since an event and time between events. A raw timestamp may be difficult for a model to use directly, so analysts often derive interpretable components.

For a delivery service, day of week may help capture demand patterns. For subscription churn, days since last activity may be useful. For equipment monitoring, time since last maintenance may matter. These features are meaningful only if their calculation matches the prediction moment.

## 2. Calendar and elapsed-time features
Calendar features include year, month, day, weekday, hour and weekend indicators. Elapsed-time features include days since signup, hours between events and age of an account at prediction time. Use timezone-aware timestamps when records originate in multiple regions. Daylight-saving changes and inconsistent timezones can create subtle errors.

Cyclical variables such as hour of day wrap around: 23:00 is close to 00:00, not far away. One approach is sine/cosine encoding:

`sin(2π × hour / 24)` and `cos(2π × hour / 24)`

This represents the cycle on a circle so neighbouring times remain close.

## 3. Lag and rolling features
A **lag feature** uses a previous observation, such as yesterday's sales. A **rolling feature** summarises a trailing window, such as the average of the previous seven days. Sort by entity and timestamp before calculating them. Shift the series so the current target period is not included.

![Temporal feature window](/course-assets/ws10/temporal-features.svg)

## 4. Worked time-series example
```python
import pandas as pd
import numpy as np

daily = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=12, freq="D"),
    "sales": [10, 12, 9, 15, 18, 20, 17, 22, 19, 25, 23, 28]
})
daily["weekday"] = daily["date"].dt.dayofweek
daily["month"] = daily["date"].dt.month
daily["day_of_year"] = daily["date"].dt.dayofyear
daily["sales_lag_1"] = daily["sales"].shift(1)
daily["sales_mean_previous_3"] = (
    daily["sales"].shift(1).rolling(window=3).mean()
)
daily["hour_sin"] = np.sin(2 * np.pi * 12 / 24)
daily["hour_cos"] = np.cos(2 * np.pi * 12 / 24)
print(daily)
```

The shift happens before rolling. Therefore the feature for a date uses earlier sales rather than including that date's sales. The first row has missing lag and rolling values because no prior observations exist. Do not fill these blindly; the missingness is a consequence of the window definition.

## 5. Text-derived features
Text can be represented using simple features such as character count, word count, number of exclamation marks, presence of a keyword or TF-IDF values. TF-IDF represents terms according to how informative they are within a document collection. It creates a sparse numerical representation and is commonly used with linear classifiers.

Text preprocessing must be learned appropriately. A vocabulary fitted on all documents before splitting can leak information about the held-out distribution. Use a text vectorizer inside a Pipeline. Avoid assuming that word counts or sentiment scores capture meaning perfectly.

## 6. Common mistakes
- Calculating rolling averages that include the target period.
- Forgetting to sort by entity and timestamp.
- Mixing timezones or treating local time as UTC.
- Using a timestamp recorded after the outcome.
- Treating cyclic hours as a simple linear number without considering wrap-around.
- Fitting a text vocabulary before splitting.

## Guided practice
Create weekday, weekend, account-age and days-since-last-login features. State the prediction timestamp and identify any fields that could be recorded after that timestamp.

## Independent practice
Using daily sales, build lag-1, lag-7 and previous-7-day mean features. Verify one row manually. Then build a text classification pipeline with TF-IDF and a linear classifier using a train/test split.

## Knowledge check
1. What is a lag feature?
2. Why is shift applied before rolling?
3. Why should observations be sorted by entity and time?
4. What is cyclical encoding designed to preserve?
5. Why should a text vectorizer be part of a pipeline?

## Lesson summary
Dates, sequences and text contain structure that can become useful model inputs. Respect ordering, timezones and prediction boundaries so features describe only information legitimately available at the moment of prediction.

## 7. Deeper reasoning: time features must respect event order

Time-dependent features are particularly easy to get wrong because the current row may contain both predictors and the outcome period. Suppose the task is to predict tomorrow's sales using today's information. A seven-day rolling average that includes tomorrow's sales is leakage. A rolling window that includes today's sales may be valid if today's sales are already complete at the moment the forecast is made. The correct calculation depends on the exact forecast timestamp, not simply on whether a column is called “sales”.

When data contains several stores or customers, calculate lags separately within each entity. A lag created after sorting the whole table can accidentally take the previous row from another store. In pandas, group by the entity and then shift or roll within each group. Also decide how to handle missing calendar dates. If a store has no row on Sunday, the previous row may be Saturday, not “one day ago” in a continuous daily series.

Cyclical encoding is useful when the end and beginning of a scale are neighbours. Hour 23 and hour 0 are only one hour apart, but their raw numeric difference is 23. Sine and cosine represent the position around a circle. The same idea can apply to day of week or month of year. The pair of values is needed because a single sine value cannot uniquely identify every point in a cycle.

Text features have similar timing and reproducibility requirements. A vocabulary or TF-IDF weighting is learned from a document collection, so it belongs inside the pipeline. A keyword feature should be based on text available before the prediction, not on a later customer-service note that describes the outcome.