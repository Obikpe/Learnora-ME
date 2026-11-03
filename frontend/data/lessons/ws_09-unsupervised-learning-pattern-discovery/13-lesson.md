# Lesson 13: Association Patterns and Co-Occurrence

## Learning outcomes

By the end of this lesson, you should be able to explain transaction-based association analysis; define itemsets and association rules; calculate support, confidence and lift by hand; use mlxtend's Apriori workflow; interpret rule direction; and explain why co-occurrence does not prove causation.

![Association rules and co-occurrence measures](/course-assets/ws09/association-metrics.svg)

## 1. What is association analysis?

Association analysis searches for items or events that occur together more often than might be expected under a simple independence assumption. A familiar example is market-basket analysis: a supermarket examines which products are often purchased in the same shopping basket.

The aim is not to predict a numeric target. Instead, the analysis discovers recurring combinations and expresses them as rules. For example:

```
{bread} -> {butter}
```

This rule asks whether transactions containing bread also tend to contain butter. It does not say that bread causes customers to buy butter. Both items may be common, a promotion may affect both, or another factor may explain their co-occurrence.

Association analysis can also be used for web-page co-visitation, medical symptom co-occurrence, product bundles and event sequences. The transaction definition must be meaningful for the problem.

## 2. What is a transaction?

A transaction is a defined collection of items or events. In a retail example, one transaction may be one checkout basket. The data can be represented as a list of sets:

```python
transactions = [
    {"bread", "milk"},
    {"bread", "butter"},
    {"bread", "milk", "butter"},
    {"milk"},
    {"bread", "milk"}
]
```

Each set contains the distinct items in one basket. The same item should not appear twice in one set if the question is simply whether the item was present. If quantity matters, that is a different analytical representation.

Be careful about the transaction unit. One checkout, one customer per week and one customer per month can produce different associations. A customer who buys bread on Monday and butter on Friday has not necessarily purchased them together in one basket. Do not combine separate events unless the time window and business question justify it.

## 3. Itemsets and association rules

An **itemset** is a collection of one or more items. A one-item set might be {bread}. A two-item set might be {bread, milk}. A three-item set might be {bread, milk, eggs}.

An **association rule** has an antecedent and a consequent:

```
Antecedent -> Consequent
A -> B
```

The antecedent is the condition on the left. The consequent is the item or itemset on the right. The rule is directional. A → B and B → A have the same pair support but can have different confidence because their antecedent frequencies differ.

## 4. Support: how common is the combination?

Support is the proportion of all transactions that contain the complete itemset.

```
support(A) = transactions containing A / total transactions
support(A and B) = transactions containing both A and B / total transactions
```

Suppose there are 100 baskets. Bread appears in 40 baskets, butter appears in 30, and both appear together in 18.

- Support(bread) = 40/100 = 0.40 or 40%.
- Support(butter) = 30/100 = 0.30 or 30%.
- Support(bread and butter) = 18/100 = 0.18 or 18%.

Support tells you how frequently the itemset occurs in the full transaction population. It helps prevent a rule from looking important simply because it is based on one or two baskets.

## 5. Confidence: how often does B appear when A appears?

Confidence for A → B is the proportion of transactions containing A that also contain B.

```
confidence(A -> B) = support(A and B) / support(A)
```

Using the example:

```
confidence(bread -> butter) = 0.18 / 0.40 = 0.45
```

So 45% of baskets containing bread also contain butter.

Confidence is directional. If butter appears in 30 baskets, then:

```
confidence(butter -> bread) = 0.18 / 0.30 = 0.60
```

Thus 60% of butter baskets also contain bread. Pair support is the same in both directions, but confidence differs because the antecedent base rate differs.

## 6. Lift: compare confidence with the baseline

Confidence can be misleading when the consequent is already common. Lift compares the rule's confidence with the overall support of the consequent:

```
lift(A -> B) = confidence(A -> B) / support(B)
```

In the example:

```
lift(bread -> butter) = 0.45 / 0.30 = 1.5
```

A lift of 1.5 means butter is 1.5 times as common among bread baskets as it is in the full transaction population.

Common interpretation:
- Lift greater than 1: positive association under this measure.
- Lift equal to 1: the antecedent and consequent occur at the rate expected under independence.
- Lift less than 1: negative association under this measure.

Lift is not a causal effect and does not show that placing items together will increase sales.

## 7. Find frequent itemsets with Apriori

Apriori is an algorithm for finding frequent itemsets. It uses the principle that if an itemset is frequent, all of its non-empty subsets must also be frequent. Conversely, if a subset is infrequent, any larger itemset containing it cannot be frequent at the same minimum support threshold.

This property helps reduce the search space. Rather than testing every possible combination blindly, Apriori grows candidate itemsets from smaller frequent itemsets.

Install mlxtend:

```bash
python -m pip install pandas mlxtend
```

Create a transaction indicator table, often called a one-hot encoded basket matrix:

```python
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

transactions = [
    ["bread", "milk"],
    ["bread", "butter"],
    ["bread", "milk", "butter"],
    ["milk"],
    ["bread", "milk"],
    ["butter", "milk"],
    ["bread", "butter"]
]

all_items = sorted({item for basket in transactions for item in basket})

basket_matrix = pd.DataFrame(
    [{item: item in basket for item in all_items} for basket in transactions]
)

frequent_itemsets = apriori(
    basket_matrix,
    min_support=0.25,
    use_colnames=True
)

rules = association_rules(
    frequent_itemsets,
    num_itemsets=len(basket_matrix),
    metric="confidence",
    min_threshold=0.4
)

print(frequent_itemsets.sort_values("support", ascending=False))
print(rules[["antecedents", "consequents", "support", "confidence", "lift"]])
```

The basket matrix has one row per transaction and one column per item. A True value means the item is present in that basket; False means it is absent.

- `min_support=0.25` keeps itemsets appearing in at least 25% of transactions.
- `use_colnames=True` displays actual item names rather than numeric column positions.
- `association_rules` derives directional rules from the frequent itemsets.
- `metric="confidence"` tells the function which rule measure to threshold.
- `min_threshold=0.4` retains rules with confidence at least 0.4.

The threshold choices are illustrative. A high threshold can hide useful lower-confidence rules; a low threshold can produce too many weak rules. Always examine support and lift as well.

## 8. Practical interpretation and responsible use

A useful association report includes the transaction definition, time period, number of transactions, support, confidence and lift. It should also describe whether promotions, seasonality, product availability or store layout could influence the result.

Avoid presenting rules based on very few baskets as reliable. If thousands of rules are generated, multiple comparisons and chance patterns become a concern. Use sensible thresholds, test whether rules persist in another time period and validate any proposed intervention through an experiment.

Protect privacy. Item combinations can sometimes reveal sensitive behaviour, particularly in small groups. Aggregate and suppress small counts where appropriate.

## 9. Common mistakes

- Confusing support with confidence.
- Treating confidence as symmetric.
- Ignoring lift and the overall frequency of the consequent.
- Changing the transaction definition without documenting it.
- Calling co-occurrence a causal relationship.
- Reporting rules supported by very few transactions.
- Assuming a high lift guarantees commercial value.

## 10. Guided practice

Using the 100-basket example, calculate support for bread and butter, confidence for bread → butter, confidence for butter → bread, and lift for bread → butter. Explain why the two confidence values differ.

## 11. Independent practice

Create a small transaction dataset or use a public market-basket dataset. Generate frequent itemsets with at least two minimum-support settings. Create association rules and compare support, confidence and lift. Identify three rules worth investigating and explain why none should be described as causal.

## 12. Knowledge check

1. What is a transaction?
2. What is an itemset?
3. How is support calculated?
4. Why is confidence directional?
5. What does lift greater than 1 indicate?
6. What is the Apriori principle?
7. Why does a high-lift rule still need a minimum support check?

## Lesson summary

Association analysis finds recurring co-occurrence patterns. Support measures how common an itemset is, confidence measures how often the consequent appears when the antecedent appears, and lift compares that confidence with the consequent's baseline frequency. Apriori efficiently finds frequent itemsets, but rules remain hypotheses about association—not evidence of causation.
