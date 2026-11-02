# Lesson 4: Datasets, Features and Targets

## Learning outcomes
By the end of this lesson, you should be able to explain the key concepts, identify when they apply, implement the worked example in VS Code, and recognise the method's limitations.

## 1. Core explanation
A dataset is a structured collection of observations. A row is an observation or example; a column is a variable. Features (often written X) are inputs available to the model. The target (often written y) is the outcome the model is asked to estimate. The unit of observation must be explicit: one row might represent a customer, a customer-month or a transaction. These are not interchangeable.

Feature availability is time-dependent. A field may exist in the final database record but not be known at the moment the prediction is required. For example, a delivery outcome cannot be used to predict whether the same delivery will be late before it occurs. This is target leakage. Create a prediction-time data dictionary listing field meaning, type, source, missingness and availability timestamp.

Avoid identifiers as predictive features unless there is a defensible reason. A customer ID can encode arbitrary patterns or memorisation. Also check whether multiple rows belong to the same entity; splitting rows independently can put the same person in both training and test sets.

## 2. Worked Python example
Use a project virtual environment. Install relevant packages with `python -m pip install numpy pandas matplotlib scikit-learn scipy` when required.

```python
import pandas as pd

df = pd.DataFrame({
    "customer_id": [101, 102, 103, 104],
    "months_active": [3, 18, 2, 24],
    "support_tickets": [4, 1, 6, 0],
    "renewed": [0, 1, 0, 1]
})
X = df[["months_active", "support_tickets"]]  # features
y = df["renewed"]                              # target
print("Feature shape:", X.shape)
print("Target distribution:")
print(y.value_counts(normalize=True))
```

## 3. Read the result
Do not stop when the code runs. Explain what each input represents, what the output measures and whether the result is plausible. Check data types and shapes. Keep a note of assumptions and information that would not be available at prediction time.

## 4. Guided practice
Create a data dictionary for a loan-default prediction table. Mark each field as feature, target, identifier or post-outcome field. Explain why a payment made after the loan decision must not be used as a feature for that decision.

## 5. Independent practice
Find or create a small dataset related to the topic. Define its unit of observation and write a data dictionary. Repeat the technique without copying the worked example. Include a brief interpretation and one limitation.

## 6. Knowledge check
1. Define the key terms in this lesson in your own words.
2. When would this method be inappropriate?
3. What can go wrong if data is not representative or is prepared incorrectly?
4. What evidence would you need before trusting the result?

## Lesson summary
Machine learning depends on a clearly defined problem, appropriate data, sound mathematical reasoning and careful evaluation. Tools make implementation easier, but they do not remove the need for judgement.