# Lesson 2: Types of Machine Learning

## Learning outcomes
By the end of this lesson, you should be able to explain the key concepts, identify when they apply, implement the worked example in VS Code, and recognise the method's limitations.

## 1. Core explanation
Supervised learning uses labelled examples: each training row has input features and a known target. Regression predicts a numeric target such as delivery time; classification predicts a class such as late/on-time. Unsupervised learning has no target label and searches for structure, such as customer segments or unusual records. Reinforcement learning studies an agent that takes actions and receives rewards over time.

The distinction is about the learning signal, not the software package. Clustering a dataset is not classification simply because the clusters are numbered. A cluster ID is a model-generated grouping, not a known class label. Semi-supervised learning combines a small labelled dataset with a larger unlabelled one. Self-supervised learning creates training targets from the data itself and is important in modern language and vision systems.

Choose the learning setup from the question and available evidence. If a reliable outcome is available, supervised learning may fit. If the task is to explore structure without known outcomes, unsupervised methods may help. If decisions influence future states and rewards, reinforcement learning may be relevant.

## 2. Worked Python example
Use a project virtual environment. Install relevant packages with `python -m pip install numpy pandas matplotlib scikit-learn scipy` when required.

```python
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import numpy as np

# Supervised regression: inputs paired with known numeric outcomes.
X = np.array([[1], [2], [3], [4], [5]])
y = np.array([2, 4, 6, 8, 10])
reg = LinearRegression().fit(X, y)
print("Predicted value at x=6:", reg.predict([[6]])[0])

# Unsupervised clustering: no target labels are supplied.
groups = KMeans(n_clusters=2, random_state=4, n_init=10).fit_predict(X)
print("Cluster assignments:", groups)
```

## 3. Read the result
Do not stop when the code runs. Explain what each input represents, what the output measures and whether the result is plausible. Check data types and shapes. Keep a note of assumptions and information that would not be available at prediction time.

## 4. Guided practice
For each scenario, identify the learning type and explain why: predicting house price, grouping shoppers by behaviour, detecting fraudulent transactions from confirmed historical labels, and training a robot to navigate using reward feedback.

## 5. Independent practice
Find or create a small dataset related to the topic. Define its unit of observation and write a data dictionary. Repeat the technique without copying the worked example. Include a brief interpretation and one limitation.

## 6. Knowledge check
1. Define the key terms in this lesson in your own words.
2. When would this method be inappropriate?
3. What can go wrong if data is not representative or is prepared incorrectly?
4. What evidence would you need before trusting the result?

## Lesson summary
Machine learning depends on a clearly defined problem, appropriate data, sound mathematical reasoning and careful evaluation. Tools make implementation easier, but they do not remove the need for judgement.