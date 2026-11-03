# Lesson 4: Encoding Categorical Variables

## Learning outcomes
Explain why most estimators require numeric inputs; distinguish nominal and ordinal categories; apply one-hot and ordinal encoding; handle unseen categories; and avoid misleading numeric order.

## 1. Categories are not automatically numbers
A categorical variable records membership in a set of labels. Examples include payment method, product family, region and subscription tier. Many machine-learning estimators operate on numeric matrices, so categories must be represented numerically.

First decide whether the category is **nominal** or **ordinal**. Nominal categories have no natural order: Lagos, Kano and Enugu are not ranked values. Ordinal categories do have a meaningful order: low, medium and high. The encoding should preserve the meaning rather than invent one.

## 2. One-hot encoding
One-hot encoding creates a binary column for each category. If payment method is {card, transfer, cash}, the representation might be:
- card: (1, 0, 0)
- transfer: (0, 1, 0)
- cash: (0, 0, 1)

This does not claim that cash is larger than card. It simply indicates category membership. It can create many columns when a feature has thousands of distinct values, so high-cardinality variables need special consideration.

## 3. Ordinal encoding
Ordinal encoding maps ordered categories to integers, for example low=0, medium=1, high=2. Use it only when the order is defensible. The numerical distances may still imply more than the original labels support: the gap from low to medium is not necessarily equal to the gap from medium to high.

For nominal labels, assigning 1, 2 and 3 can create a false ordering. A tree model may split on "category code <= 2", treating the arbitrary code as meaningful.

![Categorical encoding comparison](/course-assets/ws10/categorical-encoding.svg)

## 4. Worked example
```python
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

customers = pd.DataFrame({
    "region": ["North", "South", "East", "South"],
    "satisfaction": ["high", "medium", "low", "high"]
})

nominal_encoder = OneHotEncoder(
    handle_unknown="ignore",
    sparse_output=False
)
region_encoded = nominal_encoder.fit_transform(customers[["region"]])
print(nominal_encoder.get_feature_names_out(["region"]))
print(region_encoded)

ordinal_encoder = OrdinalEncoder(
    categories=[["low", "medium", "high"]]
)
satisfaction_encoded = ordinal_encoder.fit_transform(
    customers[["satisfaction"]]
)
print(satisfaction_encoded)
```

`fit_transform` learns the category mapping from the supplied training data and applies it. In production, call `transform` using the fitted encoder; do not refit on each incoming batch. In older scikit-learn versions, the dense-output argument was named `sparse`; current versions use `sparse_output`. If using an older environment, consult the installed version's documentation.

## 5. Unknown and rare categories
A model may encounter a new region or product type after training. With `handle_unknown="ignore"`, OneHotEncoder produces zeros for the unknown category across the learned columns. This prevents an exception, but it does not teach the model what the new category means. Monitor unseen-category rates and decide whether categories should be grouped, retrained or handled through a business rule.

Rare categories can create unstable estimates. Grouping them into "Other" may be reasonable, but define the grouping rule using training data and preserve the ability to apply it consistently later.

## 6. Put encoding in a pipeline
Use a ColumnTransformer to apply different operations to numeric and categorical columns. This prevents manual train/test mismatch and ensures the encoder is fitted only on training folds. Never one-hot encode the full dataset before cross-validation if category discovery itself could expose validation information.

## 7. Common mistakes
- Encoding nominal categories as arbitrary integers.
- Assuming ordinal labels have equal spacing.
- Fitting the encoder separately on train and test.
- Ignoring unseen categories in production.
- Creating hundreds of sparse columns without considering dimensionality.
- Treating a high-cardinality identifier as a normal category without evaluating its generalisation risk.

## Guided practice
Encode a dataset containing region, browser, education level and satisfaction rating. Identify which fields are nominal and which are ordinal. Explain your ordering for any ordinal field.

## Independent practice
Build a ColumnTransformer that imputes and one-hot encodes categorical features while scaling numeric features. Split the data first, fit on training data, and demonstrate that the pipeline can transform a row with an unseen category.

## Knowledge check
1. What is the difference between nominal and ordinal data?
2. Why is one-hot encoding suitable for nominal categories?
3. What assumption can ordinal encoding introduce?
4. What does `handle_unknown="ignore"` do?
5. Why should encoders be fitted within the pipeline?

## Lesson summary
Encoding is a representation decision. Choose a method that respects category meaning, anticipate unseen and rare labels, and fit the encoder only on training data.

## 7. Deeper reasoning: encoding defines what the model can infer

Encoding is not a neutral conversion from words to numbers. It determines which relationships the model is allowed to perceive. With one-hot encoding, a linear model can estimate a separate contribution for each category relative to a reference representation. It does not assume that the categories are ordered. With ordinal encoding, the integer mapping may cause an estimator to treat a higher code as a larger quantity, even when the original categories are labels without rank.

For example, assigning North=0, South=1 and East=2 creates an artificial numeric order. A linear model may interpret the difference between North and South as the same kind of step as the difference between South and East. There is no business reason for that assumption. One-hot encoding is generally safer for nominal values, though it increases the number of columns.

High-cardinality features need more thought. A product identifier may have thousands of categories. One-hot encoding could create a very wide matrix, and the model may memorise products seen during training rather than learn generalisable product properties. If new products appear regularly, consider whether product attributes, category hierarchy, frequency grouping or a suitable specialised encoding is more appropriate. Any target-informed encoding must be performed inside cross-validation to prevent leakage.

Also distinguish a genuinely new category from a data-cleaning inconsistency. “Lagos”, “lagos” and “LAGOS” may be the same region written three ways. Normalise spelling and whitespace using documented rules before encoding. Otherwise the model learns separate categories that reflect data-entry habits rather than meaningful differences.