# Lesson 02 - Rows, Columns and Observations

Course: ws_04 — Data Cleaning, Preparation & Exploratory Analysis  
ID: ws_04_l02  
Level: Beginner to intermediate  
Suggested duration: 40–50 minutes

## Learning goal
Explain what each row represents and why the unit of analysis matters.

By the end, you should explain the idea plainly, apply it with Python and Pandas, validate the result and communicate the practical consequence of your choice.

## 1. Understand the idea
Rows usually represent observations and columns attributes. One row could mean a customer, order, order item or payment. Confusing these units inflates counts and totals.

Think of data cleaning as checking ingredients before cooking. If an ingredient is mislabelled or counted twice, the dish may look fine but still be wrong. The aim is not to make data look neat at any cost; it is to make it fit for a defined purpose while preserving evidence and documenting uncertainty.

## 2. Real-world example
An order-items table may have three rows for one order. Counting rows as orders overstates order volume.

Before changing any value, ask: What does this field mean in the real process? What evidence supports the change? How will I verify the change improved the data rather than hiding a problem?

## 3. Try it in Python
Install dependencies if needed: `pip install pandas matplotlib openpyxl`. Load your own data first and adapt sample column names.

```python
import pandas as pd

orders = pd.DataFrame({'order_id':['A1','A1','A2'],'product':['Rice','Oil','Beans'],'quantity':[1,2,1]})
print('Rows:',len(orders),'Unique orders:',orders.order_id.nunique())
print(orders.groupby('order_id').quantity.sum())
```

### Read the output, do not just run the code
- Check output against expected row and column counts.
- Inspect affected records, not only the final count.
- Check how missing values, unusual values and categories are represented.
- Investigate surprising results before proceeding.

## 4. Common mistakes
- Treating every unusual value as an error without checking context.
- Deleting or changing data without recording the reason or preserving source values.
- Assuming successful code execution proves the result is correct.
- Reporting an average or percentage without stating which records were included.

## 5. Guided practice
Use a small dataset such as shop orders, student results, customer records or delivery transactions. State what one row represents. Count records affected before changing anything, apply the method, then compare before and after. Mark unresolved issues as unresolved rather than inventing values.

## 6. Assignment
Create a five-row table, state its unit of analysis and explain why row count and unique-entity count may differ.

### Required deliverables
1. Python code or notebook with clear comments.
2. Explanation of the method and why it fits the data.
3. Evidence of the result, including counts or a table/chart where useful.
4. A limitation, possible side effect or issue requiring further investigation.

## 7. Self-check
- [ ] Explain the concept without reading the notes.
- [ ] Apply the method with Pandas.
- [ ] Inspect examples and validate the output.
- [ ] Explain the effect on interpretation or downstream decisions.
- [ ] Reproduce the result and document assumptions.

## Key takeaway
Good analysis depends on careful questions, defensible rules and checks that expose mistakes. Cleaning is not simply deleting imperfect rows; it is making data trustworthy enough for the question while being honest about what remains uncertain.
