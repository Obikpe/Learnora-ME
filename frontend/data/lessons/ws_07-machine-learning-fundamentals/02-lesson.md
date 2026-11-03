# Lesson 2: Types of Machine Learning

## Learning outcomes
Distinguish supervised, unsupervised, semi-supervised and reinforcement learning; explain classification and regression; identify clustering and dimensionality reduction; and match a learning setup to a problem.

## 1. Why are there different types?
Machine learning is a family of methods. The learning setup depends on what information is available and what the system must do. The first question is often: do we have known outcome labels for the examples?

![Machine learning learning paradigms](/course-assets/ws07/02-learning-paradigms.svg)

## 2. Supervised learning
Supervised learning uses examples with known target values. The algorithm learns a relationship between input features and the target.

### Classification predicts categories
Examples:
- spam or not spam;
- learner completes or does not complete;
- transaction legitimate or potentially fraudulent;
- image contains a cat, dog or bird.

Binary classification has two classes. Multiclass classification has more than two mutually exclusive classes. Multilabel classification allows several labels for one observation, such as a news article tagged both business and politics.

A classifier may return a class label or probabilities. A probability score is not automatically the final decision; a threshold or decision policy is needed.

### Regression predicts numerical values
Regression predicts a numerical quantity, such as rent, delivery duration, monthly sales or energy demand. The output is a number rather than a category.

Do not confuse regression with logistic regression. Despite its name, logistic regression is commonly used for classification.

## 3. Unsupervised learning
Unsupervised learning looks for structure in features without a supplied target label.

### Clustering
Clustering groups observations based on a similarity rule. Customer segmentation is one example. A clustering algorithm may group customers with similar purchase frequency and average spend.

A cluster is not automatically a real-world customer type. Results depend on feature choice, scaling, distance measure and algorithm. A person must inspect whether the groups are meaningful and useful.

### Dimensionality reduction
Dimensionality reduction represents data using fewer variables while trying to preserve important information or structure. It can help visualise high-dimensional data, reduce redundancy or support later modelling. Principal Component Analysis (PCA) is a common linear technique.

### Anomaly detection
Anomaly detection identifies observations that differ from an expected pattern. An unusual transaction is not automatically fraudulent; a rare legitimate event can be an anomaly, while a carefully disguised fraud may look ordinary.

## 4. Semi-supervised learning
Semi-supervised learning combines a relatively small labelled dataset with a larger unlabelled dataset. It can be useful when labels are expensive, such as specialist annotation of medical images. The unlabelled examples do not magically contain correct answers; the method relies on assumptions about the structure of the data.

## 5. Reinforcement learning
Reinforcement learning studies an agent that interacts with an environment. The agent chooses actions, receives rewards or penalties and learns a policy for choosing actions.

- Agent: the learner or decision-making system.
- Environment: the world it interacts with.
- State: information describing the current situation.
- Action: a choice the agent can make.
- Reward: feedback about the outcome.
- Policy: a strategy mapping states to actions.

![Reinforcement learning interaction](/course-assets/ws07/02-reinforcement-loop.svg)

A reward is a proxy for what we value. Poor reward design can encourage harmful behaviour even when the agent is optimising exactly as specified.

## 6. Match the task to the learning setup
| Problem | Likely approach |
|---|---|
| Predict whether a learner passes | Supervised classification |
| Estimate a property's rent | Supervised regression |
| Group customers without predefined segments | Unsupervised clustering |
| Compress hundreds of variables into fewer dimensions | Dimensionality reduction |
| Find unusual sensor readings | Anomaly detection |
| Learn from a few labelled and many unlabelled images | Semi-supervised learning |
| Train a robot to navigate by acting and receiving rewards | Reinforcement learning |

## 7. Python examples: classification and regression
```python
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, mean_absolute_error

# Classification: target values are class labels.
Xc, yc = make_classification(
    n_samples=300, n_features=4, n_informative=3,
    n_redundant=0, random_state=12
)
X_train, X_test, y_train, y_test = train_test_split(
    Xc, yc, test_size=0.2, random_state=12, stratify=yc
)
classifier = LogisticRegression(max_iter=1000)
classifier.fit(X_train, y_train)
print("Classification accuracy:",
      accuracy_score(y_test, classifier.predict(X_test)))

# Regression: target values are numerical.
Xr, yr = make_regression(
    n_samples=300, n_features=4, noise=15, random_state=12
)
X_train, X_test, y_train, y_test = train_test_split(
    Xr, yr, test_size=0.2, random_state=12
)
regressor = LinearRegression()
regressor.fit(X_train, y_train)
print("Regression MAE:",
      mean_absolute_error(y_test, regressor.predict(X_test)))
```

make_classification creates a synthetic classification dataset; make_regression creates a synthetic numerical target. LogisticRegression predicts classes; LinearRegression predicts numerical values. Accuracy measures exact class agreement, while MAE measures average absolute numerical error in target units.

## Common misunderstandings
- Classification predicts categories; regression predicts numbers.
- Clustering does not use known class labels in the supervised way.
- A cluster is not necessarily a natural group.
- An anomaly does not prove wrongdoing.
- Reinforcement learning is not just supervised learning with another name.
- A probability is not itself an action.

## Guided practice
Identify the likely learning setup for: student pass/fail; monthly rent estimation; customer grouping without labels; unusual sensor detection; and a robot learning to navigate. Explain your reasoning.

## Independent practice
Create a table of five real problems. State available data, target if any, learning type, expected output and one limitation.

## Knowledge check
1. What makes data labelled?
2. Explain classification versus regression.
3. Why can feature scaling affect clustering?
4. What does reward do in reinforcement learning?
5. Why is an anomaly not necessarily fraud?

## Lesson summary
The learning paradigm depends on the available information and desired output. Choosing the correct setup is the first step toward an appropriate model.