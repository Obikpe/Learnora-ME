# Lesson 13: Decision Trees

## Learning outcomes
Explain the technique, implement the worked example, interpret the output and justify when the method is suitable.

## 1. Core explanation
A decision tree repeatedly splits the feature space using rules such as “age is less than 30”. Each split aims to create child groups that are more homogeneous in their target. Classification trees commonly use Gini impurity or entropy; regression trees reduce squared error or another criterion.

Trees are easy to visualise and can capture non-linear relationships and interactions without feature scaling. However, deep trees can memorise training data. Control complexity with max_depth, min_samples_split and min_samples_leaf. Pruning removes branches that do not improve generalisation.

A split's feature importance is not proof of causal influence. Correlated features can share or distort importance, and impurity-based importance can favour variables with many possible split points. Validate the tree and inspect errors before explaining its rules.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may need internet access on first use.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42, stratify=data.target)
tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=5, random_state=42)
tree.fit(Xtr, ytr)
print("Train:", tree.score(Xtr, ytr), "Test:", tree.score(Xte, yte))
plot_tree(tree, feature_names=data.feature_names, class_names=data.target_names,
          filled=True, max_depth=3)
plt.show()
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report the limitations of the dataset.

## 4. Guided practice
Train trees with depth 2, 4 and no limit. Compare train and test scores. Explain how max_depth changes interpretability and overfitting risk.

## 5. Independent practice
Extend the example with a second model or a different evaluation view. Keep a record of every change and compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder.

## 6. Knowledge check
1. What does this method optimise or estimate?
2. Which assumptions or settings affect its behaviour?
3. How would you detect overfitting or leakage?
4. What evidence is needed before the model is used?

## Lesson summary
Supervised learning is a complete evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.