# Lesson 1: What Machine Learning Is and When to Use It

## Learning outcomes

By the end of this lesson, you should be able to Explain when a problem is suitable for machine learning; distinguish rule-based automation from learning patterns from examples; identify a prediction target and available inputs; and describe why a baseline and evaluation plan are needed before modelling.

## 1. Core explanation
Machine learning (ML) is a set of methods that use data to learn a pattern for making predictions or decisions. In conventional programming, a developer writes explicit rules. In supervised ML, an algorithm uses examples containing inputs and known outcomes to estimate a mapping from inputs to outcomes. The learned mapping is a model.

ML is useful when rules are difficult to write manually, patterns are too complex for a small set of hand-coded conditions, and enough representative data exists. It is not automatically the right choice. A simple SQL query, spreadsheet formula or transparent rule may be cheaper, easier to audit and more reliable. ML is a poor fit when labels are unreliable, the target cannot be measured, the data does not represent future cases, or the cost of a wrong prediction is unacceptable.

Distinguish prediction from explanation. A model that predicts which customers may leave does not necessarily identify what causes customers to leave. Predictive association is not causal evidence. Begin with the decision that will use the prediction, define the error costs and compare ML with a simple baseline.

## 2. Worked Python example
Use a project virtual environment. Install relevant packages with `python -m pip install numpy pandas matplotlib scikit-learn scipy` when required.

```python
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

df = pd.DataFrame({
    "visits": [1, 5, 2, 7, 3, 8, 2, 6, 1, 9],
    "support_calls": [0, 2, 1, 3, 0, 4, 1, 2, 0, 4],
    "renewed": [1, 1, 0, 1, 0, 1, 0, 1, 0, 1]
})
X = df[["visits", "support_calls"]]
y = df["renewed"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=7, stratify=y
)
baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(X_train, y_train)
print("Baseline accuracy:", accuracy_score(y_test, baseline.predict(X_test)))
```

## 3. Read the result
Do not stop when the code runs. Explain what each input represents, what the output measures and whether the result is plausible. Check data types and shapes. Keep a note of assumptions and information that would not be available at prediction time.

## 4. Guided practice
Describe a business decision that might benefit from prediction. State the target, when the prediction must be made, what action follows, and the cost of false positives and false negatives. Then argue whether a rule-based approach could be sufficient.

## 5. Independent practice
Find or create a small dataset related to the topic. Define its unit of observation and write a data dictionary. Repeat the technique without copying the worked example. Include a brief interpretation and one limitation.

## 6. Knowledge check
1. Define the key terms in this lesson in your own words.
2. When would this method be inappropriate?
3. What can go wrong if data is not representative or is prepared incorrectly?
4. What evidence would you need before trusting the result?

## Lesson summary
Machine learning depends on a clearly defined problem, appropriate data, sound mathematical reasoning and careful evaluation. Tools make implementation easier, but they do not remove the need for judgement.