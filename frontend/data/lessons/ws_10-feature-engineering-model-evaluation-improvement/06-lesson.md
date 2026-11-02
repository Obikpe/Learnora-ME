# Lesson 6: Date, Time and Text Features

## Learning outcomes
Explain the feature-engineering method, implement it in Python and identify leakage, reproducibility and interpretation risks.

## 1. Core explanation
Dates and text contain useful structure but need transformations. Date features may include day of week, month, elapsed time, weekend flag or time since a prior event. Cyclical fields such as hour or month can be represented with sine and cosine so that December and January are close on the circle. Avoid creating a future-derived feature.

Text can be represented using token counts, TF-IDF or embeddings. Tokenisation, lowercasing and stop-word handling depend on language and task. Fit vocabulary and weighting on training text only. Text features can be high-dimensional and sparse, so regularised linear models are useful baselines.

Respect temporal availability and privacy. Do not extract sensitive personal details unless there is a lawful and necessary purpose. Check whether text includes target leakage such as a resolution note written after the event.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas scikit-learn`.

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({"timestamp": pd.to_datetime([
    "2026-01-01 08:00", "2026-01-15 20:00", "2026-02-01 12:00"
])})
df["hour"] = df.timestamp.dt.hour
df["hour_sin"] = np.sin(2*np.pi*df.hour/24)
df["hour_cos"] = np.cos(2*np.pi*df.hour/24)
df["weekday"] = df.timestamp.dt.dayofweek
print(df)
```

## 3. Interpretation and safeguards
State when each feature is available, how it was derived and whether it can be calculated consistently at prediction time. Fit all learned transformations on training data only. Compare performance using the same validation design and check that transformations do not remove meaningful information.

## 4. Guided practice
Create cyclical encodings for month and hour. Explain why month 12 should be close to month 1. Identify a text field that might contain information entered after the target event.

## 5. Independent practice
Create a small feature-engineering workflow for a dataset. Include a data dictionary, transformation rationale, pipeline and validation plan. Identify one transformation you decided not to use and explain why.

## 6. Knowledge check
1. What information does this transformation add?
2. Could it leak information from after the prediction time?
3. Does it need to be fitted on training data?
4. How will you test its value and stability?

## Lesson summary
Feature engineering should create meaningful, available and reproducible inputs. Every transformation must be justified and validated within a leakage-safe workflow.