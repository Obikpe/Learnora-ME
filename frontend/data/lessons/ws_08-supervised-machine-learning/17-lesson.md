# Lesson 17: Naive Bayes

## Learning outcomes
Explain the technique, implement the worked example, interpret the output and justify when the method is suitable.

## 1. Core explanation
Naive Bayes applies Bayes' theorem to estimate class probabilities from features. The “naive” assumption is that features are conditionally independent given the class. This assumption is often unrealistic, but the method can still perform well, especially for text classification and high-dimensional sparse data.

Gaussian Naive Bayes models continuous features with a normal distribution within each class. Multinomial Naive Bayes is often used with non-negative count features such as word counts. Bernoulli Naive Bayes is suited to binary feature presence. Choose the variant to match the feature representation.

Naive Bayes is fast and provides a useful baseline. Its probability estimates can be poorly calibrated when independence assumptions fail. Evaluate predictive quality and calibration separately. For text, fit vectorisation on training text only to avoid vocabulary leakage.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may need internet access on first use.

```python
from sklearn.datasets import fetch_20newsgroups
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

data = fetch_20newsgroups(subset="train", categories=["sci.space", "rec.sport.baseball"],
                          remove=("headers", "footers", "quotes"))
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.25, random_state=42, stratify=data.target)
model = make_pipeline(CountVectorizer(), MultinomialNB())
model.fit(Xtr, ytr)
print("Test accuracy:", model.score(Xte, yte))
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report the limitations of the dataset.

## 4. Guided practice
Explain why word counts are non-negative and suit MultinomialNB. Try TF-IDF features and compare. Note that downloading this dataset requires internet access; use a locally saved text sample if offline.

## 5. Independent practice
Extend the example with a second model or a different evaluation view. Keep a record of every change and compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder.

## 6. Knowledge check
1. What does this method optimise or estimate?
2. Which assumptions or settings affect its behaviour?
3. How would you detect overfitting or leakage?
4. What evidence is needed before the model is used?

## Lesson summary
Supervised learning is a complete evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.