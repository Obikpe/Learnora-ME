# Lesson 13: Association Patterns and Co-Occurrence

## Learning outcomes
Explain the unsupervised method, implement the example and judge whether the discovered structure is meaningful.

## 1. Core explanation
Association analysis searches for items that occur together in transactions. Support is the proportion of transactions containing an itemset. Confidence estimates how often B occurs when A occurs. Lift compares that confidence with the baseline frequency of B; lift greater than one indicates co-occurrence above independence under the measure.

Association rules are descriptive, not causal. A rule bread -> butter does not mean bread causes butter purchases. Rare itemsets can have high confidence but tiny support, so inspect all three measures. Minimum support controls which itemsets are considered; too high misses rare patterns, too low creates a huge number of rules.

The transaction definition matters. A basket might be one checkout, one customer-day or one account-month. Combining transactions incorrectly changes support and confidence. Protect customer privacy and avoid sensitive inferences about individuals.

## 2. Worked Python example
Run in VS Code. Install packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`.

```python
transactions = [
    {"bread", "milk"}, {"bread", "butter"}, {"bread", "milk", "butter"},
    {"milk"}, {"bread", "milk"}, {"butter", "milk"}
]
def support(itemset):
    return sum(itemset.issubset(t) for t in transactions) / len(transactions)
s_a, s_b = support({"bread"}), support({"butter"})
s_ab = support({"bread", "butter"})
print("Support", s_ab, "Confidence", s_ab/s_a, "Lift", (s_ab/s_a)/s_b)
```

## 3. Interpretation
Describe the feature representation, model settings and meaning of the output. Validate patterns in original units. Cluster IDs are arbitrary and anomaly flags are not proof of wrongdoing.

## 4. Guided practice
Calculate milk -> bread support, confidence and lift. Explain why high confidence can occur because bread is common and why lift adds context.

## 5. Independent practice
Apply the method to a dataset. Compare at least two parameter settings or methods, profile results and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the method attempting to discover?
2. Which assumptions are introduced by the representation or distance?
3. How will you assess stability and usefulness?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Stability, interpretation and practical validation determine whether those patterns deserve to be used.