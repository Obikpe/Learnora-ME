# Lesson 3: Distance and Similarity Measures

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain why an algorithm needs a definition of similarity before it can group observations.
- Calculate Euclidean and Manhattan distance by hand.
- Explain cosine similarity and why it compares direction rather than magnitude.
- Explain Jaccard similarity for sets and binary attributes.
- Choose a measure that matches the data type and analytical question.
- Recognise the effects of feature scaling, irrelevant dimensions and high dimensionality.

![Teaching diagram: 03](/course-assets/ws09/distance-metrics.svg)

## 1. What does it mean for two observations to be similar?

People use context when deciding whether two things are alike. Two customers may be alike because they buy the same products, spend similar amounts or shop at similar times. A computer does not automatically know which of those meanings matters. We must represent each customer using features and choose a mathematical rule for comparing the resulting rows.

A **distance measure** gives a number describing how far apart two observations are. Smaller distances usually mean greater similarity. A **similarity measure** gives a score describing how alike two observations are. Larger similarity scores usually mean greater similarity.

These scores are not universal truths. They are answers under a chosen representation and formula. If you change the features, scaling or measure, you may change which observations appear close.

## 2. Represent observations as vectors

Suppose a customer is described by two measurements: number of orders and average basket value. One customer might be represented as:

```
Customer A = [4, 250]
Customer B = [6, 300]
```

A vector is an ordered list of numbers. In a dataset with three features, a row becomes a point in three-dimensional feature space. With 20 features, it becomes a point in a 20-dimensional space. We cannot easily draw all those dimensions, but the mathematics can still compare them.

The order of values matters: the first position must represent the same feature for every observation. Never compare vectors if their columns are in a different order.

## 3. Euclidean distance: straight-line distance

Euclidean distance is the ordinary straight-line distance between points. In two dimensions, imagine drawing a line from point A to point B. The horizontal and vertical differences form a right-angled triangle. The Pythagorean theorem gives the length of the diagonal.

For points (A=(a_1,a_2)) and (B=(b_1,b_2)):

```
distance = sqrt((a1 - b1)^2 + (a2 - b2)^2)
```

For A=(1,2) and B=(4,6):

- Difference in the first coordinate: 4 - 1 = 3.
- Difference in the second coordinate: 6 - 2 = 4.
- Square the differences: 3² = 9 and 4² = 16.
- Add them: 9 + 16 = 25.
- Take the square root: √25 = 5.

The Euclidean distance is 5.

For more than two dimensions, square each feature difference, add the squares and take the square root. Every feature contributes to the result. This is why units and scaling matter: a feature measured in hundreds of thousands can dominate one measured in single digits.

## 4. Manhattan distance: movement along a grid

Manhattan distance adds the absolute difference in each coordinate. It is sometimes described as city-block distance: imagine moving along horizontal and vertical streets rather than cutting diagonally across buildings.

For A=(1,2) and B=(4,6):

```
distance = |4 - 1| + |6 - 2| = 3 + 4 = 7
```

Euclidean distance is 5, while Manhattan distance is 7. Neither answer is a mistake. The two formulas define distance differently.

Manhattan distance can be useful when differences across coordinates are naturally additive or when movement is constrained to a grid. It is less affected by one large coordinate difference than the squared terms in Euclidean distance, although it is not immune to scale or poor features.

## 5. Cosine similarity: compare direction

Cosine similarity compares the angle between two vectors. It asks whether two vectors point in a similar direction, rather than how close their endpoints are.

The formula is:

```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```

The dot product (A cdot B) multiplies corresponding coordinates and adds the results. The magnitude (||A||) is the vector's length. The cosine of the angle is 1 when vectors point in exactly the same direction, 0 when they are perpendicular, and -1 when they point in opposite directions.

Consider A=[1,2] and B=[2,4]. B is exactly twice A. Their lengths differ, so Euclidean distance is not zero. However, they point in exactly the same direction, so cosine similarity is 1.

This is useful in text analysis. A long document may contain many more words than a short document, but their word-frequency patterns may have a similar direction. Cosine similarity can compare those patterns without treating total document length as the main signal.

Cosine similarity is not always appropriate. If magnitude matters—for example, total energy use—ignoring vector length can discard important information. A zero vector also has no direction, so cosine similarity is undefined for it; libraries handle this case according to their implementation.

## 6. Jaccard similarity: compare overlap

Jaccard similarity compares sets. A set contains distinct items, without duplicates. Suppose:

- Basket A contains {bread, milk, eggs}.
- Basket B contains {bread, milk, tea}.

The intersection contains items in both sets: {bread, milk}, so its size is 2. The union contains every distinct item in either set: {bread, milk, eggs, tea}, so its size is 4.

```
Jaccard similarity = size(intersection) / size(union)
                   = 2 / 4
                   = 0.5
```

A score of 1 means the sets are identical. A score of 0 means they have no shared items, provided the union is non-empty.

Jaccard is useful for shopping baskets, tags, binary preferences and other presence/absence data. It is not a general measure for continuous measurements such as income or temperature.

## 7. Calculate distances and similarities with Python

Install the packages:

```bash
python -m pip install numpy scikit-learn
```

```python
import numpy as np
from sklearn.metrics.pairwise import (
    euclidean_distances,
    manhattan_distances,
    cosine_similarity
)

customers = np.array([
    [1, 2],
    [2, 4],
    [8, 1]
])

print("Euclidean distance:")
print(euclidean_distances(customers).round(2))

print("\nManhattan distance:")
print(manhattan_distances(customers))

print("\nCosine similarity:")
print(cosine_similarity(customers).round(3))
```

The input is a two-dimensional NumPy array: each row is an observation and each column is a feature. The pairwise functions compare every row with every other row and return a square matrix.

The diagonal of a distance matrix is zero because each observation is zero distance from itself. The matrix is symmetric because distance from A to B equals distance from B to A. Similarity matrices are also symmetric for cosine similarity.

The first two vectors point in the same direction, so their cosine similarity is 1 (subject to rounding). Their Euclidean distance is not zero because their magnitudes differ.

For sets, Python can calculate Jaccard similarity directly:

```python
basket_a = {"bread", "milk", "eggs"}
basket_b = {"bread", "milk", "tea"}

intersection = basket_a & basket_b
union = basket_a | basket_b

jaccard = len(intersection) / len(union)
print("Shared items:", intersection)
print("Jaccard similarity:", jaccard)
```

The ampersand operator `&` finds the intersection of sets; the vertical bar `|` finds their union. The final calculation divides the number of shared items by the number of distinct items across both baskets.

## 8. Scaling and feature weighting

Distance measures treat the supplied coordinates according to their formulas. If annual spend ranges from 5,000 to 500,000 and order count ranges from 0 to 20, raw Euclidean distance can be dominated by spend. Standardisation can reduce this unit effect, but it does not make every feature equally important in a business sense.

Sometimes a feature should receive more weight because the analytical question justifies it. For example, a health-monitoring project may give a carefully justified greater role to a clinically important measurement. Weighting should be explicit, documented and tested. Do not adjust weights simply to make a preferred cluster appear.

## 9. The curse of dimensionality

As the number of features grows, the geometry of the space changes. In high-dimensional data, the nearest and farthest observations can become less distinguishable under common distance measures. Irrelevant features also add noise to comparisons.

This is one reason why selecting meaningful features and sometimes reducing dimensions can help. More columns do not automatically mean better analysis. A dataset with 100 weak features may be less useful than one with 8 carefully chosen features.

## 10. How to choose a measure

| Data and question | Possible measure | Important caution |
|---|---|---|
| Continuous numeric features | Euclidean | Scale and outliers matter |
| Additive coordinate differences | Manhattan | Still depends on feature units |
| Sparse text or direction-based vectors | Cosine similarity | Magnitude is largely ignored |
| Sets or binary presence/absence | Jaccard | Not for arbitrary continuous values |
| Mixed numeric and categorical features | A mixed-data method | Define category and numeric contributions carefully |

The correct choice is not simply the most popular formula. Ask what it means for two observations to be similar in the real problem.

## 11. Guided practice

Calculate Euclidean and Manhattan distance between A=(2,3) and B=(6,6). Then compare vectors (1,3) and (2,6) using cosine similarity. Explain why the second pair has the same direction even though its values differ.

## 12. Independent practice

Choose a dataset with at least three features. Calculate pairwise Euclidean distances before and after standardisation. Select two observations and explain which features contribute most to their distance. If the data is categorical or text-based, explain why a set-based or cosine comparison may be more suitable.

## 13. Knowledge check

1. What is the difference between a distance measure and a similarity measure?
2. Calculate Euclidean distance between (0,0) and (3,4).
3. Calculate Manhattan distance between (0,0) and (3,4).
4. Why can cosine similarity be high even when Euclidean distance is large?
5. What is the Jaccard similarity of two sets with 3 shared items and 6 distinct items in their union?
6. Why can adding irrelevant features make clustering worse?

## Lesson summary

Similarity is defined by mathematics, not by the algorithm's ability to produce a number. Euclidean and Manhattan distances compare coordinate differences; cosine compares direction; Jaccard compares set overlap. Select a measure that matches the meaning of the data, scale features where necessary and remember that every feature and transformation changes what the model considers close.
