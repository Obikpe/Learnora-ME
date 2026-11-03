# Lesson 17: Naive Bayes

## Learning outcomes

By the end of this lesson, you should be able to Explain Bayes' theorem and the conditional-independence assumption; distinguish Gaussian, Multinomial and Bernoulli Naive Bayes; build a text-count pipeline; and evaluate class-wise errors.


![classification concept diagram](/course-assets/ws08/classification.svg)

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

## 7. Understand the model before using it

A model does not understand the world represented by its dataset. It learns a mathematical pattern from the examples it receives. The analyst supplies the meaning by defining what one row represents, which information is available at prediction time and what the target means. Explain these definitions before discussing the algorithm.

Interpret outputs carefully. Probabilities express model estimates, not certainty. Feature importance describes how a model uses information, not necessarily causal influence. Evaluation metrics summarise selected errors, not every consequence of using a model. Always connect the result to the decision and the population where it will be applied.

## 8. Build a fair and repeatable experiment

Check data types, missingness, duplicates, unusual values and target distribution. Choose a split that matches deployment: chronological for future prediction, group-aware when people or entities appear repeatedly, and stratified when preserving class proportions is important. Fit imputers, encoders and scalers on training data only. A pipeline helps ensure the same fitted transformations are applied to validation, test and future data.

Start with a baseline. Select model settings using validation data or cross-validation, then evaluate the chosen approach on a held-out test set once. Keep a record of feature definitions, random seeds, package versions, split strategy and parameter values. If the data changes, investigate whether the target definition, population or collection process also changed.

## 9. Worked reasoning example

Imagine predicting whether a learner will need additional support. Define a snapshot date, an outcome window and the intervention. Use only activity recorded before the snapshot. If the same learner appears in several rows, random splitting may put that learner in both training and test sets, making the test easier than the real task. Consider a group-based or time-based split. Inspect not only the average score but also who receives false alerts and who is missed.

## 10. Self-study and independent practice

Explain the method from memory: its purpose, required inputs, learning mechanism, an important setting, one failure mode and an appropriate evaluation strategy. Apply it to a documented dataset and produce a notebook with a precise question, data-quality checks, split rationale, baseline, candidate model, interpreted metrics, error analysis and limitations. Explain why each decision was made.

Do not remove rare observations only because they make performance worse. Determine whether they are errors, valid rare cases or evidence that the method does not work well for an important part of the population.

## 11. Knowledge check

1. What does the method learn from training examples?
2. What assumptions and parameter choices influence its behaviour?
3. What could make an evaluation result misleading?
4. How would you inspect errors beyond a single summary metric?
5. What further validation is needed before using the model in practice?
