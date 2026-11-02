# Lesson 17: Naive Bayes

## Learning outcomes

By the end of this lesson, you should be able to Explain Bayes' theorem and the conditional-independence assumption; distinguish Gaussian, Multinomial and Bernoulli Naive Bayes; build a text-count pipeline; and evaluate class-wise errors.

## 1. Core explanation
Naive Bayes applies Bayes' theorem to estimate class probabilities from features. The “naive” assumption is that features are conditionally independent given the class. This assumption is often unrealistic, but the method can still perform well, especially for text classification and high-dimensional sparse data.

Gaussian Naive Bayes models continuous features with a normal distribution within each class. Multinomial Naive Bayes is often used with non-negative count features such as word counts. Bernoulli Naive Bayes is suited to binary feature presence. Choose the variant to match the feature representation.

Naive Bayes is fast and provides a useful baseline. Its probability estimates can be poorly calibrated when independence assumptions fail. Evaluate predictive quality and calibration separately. For text, fit vectorisation on training text only to avoid vocabulary leakage.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas matplotlib scikit-learn`. This example uses a small local teaching corpus, so it runs without downloading a dataset.

```python
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report

# Small local teaching corpus: no download or internet connection needed.
texts = [
    "space mission rocket orbit astronaut satellite",
    "astronomy telescope planet galaxy space science",
    "rocket launch spacecraft lunar exploration",
    "satellite orbit mission space station",
    "planet astronomy stars telescope observation",
    "astronaut spacecraft launch moon mission",
    "baseball pitcher strikes batter inning game",
    "baseball team scored runs home plate",
    "pitcher threw ball and batter hit a home run",
    "baseball league season team championship",
    "catcher and pitcher prepared for the next inning",
    "baseball player hit a double and scored",
]
labels = ["space"] * 6 + ["baseball"] * 6
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.33, random_state=42, stratify=labels
)
model = make_pipeline(CountVectorizer(), MultinomialNB())
model.fit(X_train, y_train)
predictions = model.predict(X_test)
print(classification_report(y_test, predictions, zero_division=0))
print("Example prediction:", model.predict(["rocket launch and orbit"])[0])
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report the limitations of the dataset.

## 4. Guided practice
Explain why word counts are non-negative and suit MultinomialNB. Try TF-IDF features and compare. Change the local text examples, keep labels aligned with the texts, and compare how the vocabulary changes. This small corpus is only for learning the workflow; it is too small to support a real-world performance claim.

## 5. Independent practice
Extend the example with a second model or a different evaluation view. Keep a record of every change and compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder.

## 6. Knowledge check
1. What does this method optimise or estimate?
2. Which assumptions or settings affect its behaviour?
3. How would you detect overfitting or leakage?
4. What evidence is needed before the model is used?

## Lesson summary
Supervised learning is a complete evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.