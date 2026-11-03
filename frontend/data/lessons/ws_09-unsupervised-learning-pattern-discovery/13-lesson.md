# Lesson 13: Association Patterns and Co-Occurrence

## Learning outcomes

By the end of this lesson, you should be able to Calculate support, confidence and lift for item associations; explain the transaction unit and minimum support; and distinguish co-occurrence from causation.

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

## Deeper explanation: derive support, confidence and lift

Suppose 100 baskets exist. Bread appears in 40, butter in 30, and both appear together in 18. Support of the pair is 18/100 = 18%. Confidence of bread → butter is 18/40 = 45%. Lift is 0.45/0.30 = 1.5. Butter is 1.5 times as common among bread baskets as in the overall population. This is association, not causation.

For a rule A → B, support is the proportion of transactions containing both A and B. Confidence is the proportion of A transactions that also contain B. Lift divides that confidence by the overall frequency of B. Lift above 1 indicates positive association under this measure; 1 indicates independence; below 1 indicates negative association.

Always report support alongside confidence and lift. A rule can have high confidence because the consequent is common. Association mining can generate thousands of rules, so thresholds should reflect transaction volume and the decision. Check duplicate items, returns, basket definition and time window. Changing the transaction unit from checkout to customer-month changes the measures.

**Practice:** Calculate milk → bread and bread → milk for the example baskets. Pair support is the same in both directions, but confidence differs because the antecedent base rates differ. Explain the asymmetry.
