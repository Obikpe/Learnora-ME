# Lesson 3: The End-to-End Machine Learning Workflow

## Learning outcomes
By the end of this lesson, you should be able to explain the key concepts, identify when they apply, implement the worked example in VS Code, and recognise the method's limitations.

## 1. Core explanation
A defensible ML workflow begins before fitting an algorithm. First translate the request into a measurable problem and define the prediction moment. Next identify the unit of observation, target, features, population and time window. Acquire and inspect data, split it correctly, establish a baseline, train candidate models, evaluate on held-out data, analyse errors and document limitations.

The order matters. If the same customer appears in both training and test data, a model may memorise customer-specific patterns and appear stronger than it will be on new customers. If the task predicts future events, randomly mixing future and past records can leak information. Use time-aware or group-aware splitting where needed.

Keep a final test set untouched until model decisions are complete. Use training data to fit; validation or cross-validation to select; test data for the final estimate. After evaluation, consider deployment, monitoring and feedback. Performance can degrade as users, policies or environments change.

## 2. Worked Python example
Use a project virtual environment. Install relevant packages with `python -m pip install numpy pandas matplotlib scikit-learn scipy` when required.

```python
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error

data = load_diabetes(as_frame=True)
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
baseline = DummyRegressor(strategy="mean")
baseline.fit(X_train, y_train)
pred = baseline.predict(X_test)
print("Baseline MAE:", mean_absolute_error(y_test, pred))
```

## 3. Read the result
Do not stop when the code runs. Explain what each input represents, what the output measures and whether the result is plausible. Check data types and shapes. Keep a note of assumptions and information that would not be available at prediction time.

## 4. Guided practice
Draw the workflow as a sequence from business question to monitoring. At each stage write one possible failure (unclear target, leakage, unrepresentative split, unsuitable metric, drift) and one control that would reduce the risk.

## 5. Independent practice
Find or create a small dataset related to the topic. Define its unit of observation and write a data dictionary. Repeat the technique without copying the worked example. Include a brief interpretation and one limitation.

## 6. Knowledge check
1. Define the key terms in this lesson in your own words.
2. When would this method be inappropriate?
3. What can go wrong if data is not representative or is prepared incorrectly?
4. What evidence would you need before trusting the result?

## Lesson summary
Machine learning depends on a clearly defined problem, appropriate data, sound mathematical reasoning and careful evaluation. Tools make implementation easier, but they do not remove the need for judgement.