# Lesson 6: Pie, Donut and Part-to-Whole Charts

## Learning outcomes
You should be able to explain part-to-whole comparisons; calculate proportions; create pie charts with `ax.pie()`; customise labels, percentages, start angle, colours and exploded slices; create donut charts; and decide when a bar chart is a better choice.

## 1. What is a part-to-whole question?

A part-to-whole question asks how a total is divided among components. Examples include:
- What share of a department's budget goes to salaries?
- What proportion of orders came from each channel?
- How are survey responses divided among a small set of options?

A pie chart represents the total as a circle. Each slice's angle is proportional to its share of the total. A full circle is 360 degrees. If a category represents 25% of the total, its slice covers 90 degrees.

Pie charts work best when:
- categories are mutually exclusive;
- values are non-negative;
- the categories add to a meaningful total;
- there are only a few categories;
- the audience needs an approximate composition, not precise ranking.

Avoid pie charts with many categories, similar slice sizes, negative values or categories that do not form a complete whole. A sorted bar chart is usually easier for accurate comparisons.

## 2. Calculate proportions before drawing

Suppose a business receives 200 orders: 100 online, 60 in-store and 40 by phone. The shares are:

- Online: 100 / 200 = 0.50 = 50%.
- In-store: 60 / 200 = 0.30 = 30%.
- Phone: 40 / 200 = 0.20 = 20%.

The percentages add to 100% because the categories cover the total and each order belongs to exactly one channel.

## 3. The Matplotlib function: ax.pie()

The basic form is:

```python
ax.pie(values, labels=None, autopct=None, startangle=0,
       explode=None, colors=None, counterclock=True)
```

- `values`: non-negative numeric values for each slice.
- `labels`: text labels for the categories.
- `autopct`: formatting string or function for percentage labels.
- `startangle`: rotation angle for the first slice.
- `explode`: amount each slice is moved away from the centre.
- `colors`: colours for slices.
- `counterclock`: direction in which slices are drawn.
- `wedgeprops`: dictionary of properties passed to the wedge patches.
- `textprops`: dictionary of properties for text.

## 4. Basic pie chart

```python
import matplotlib.pyplot as plt

channels = ["Online", "In-store", "Phone"]
orders = [100, 60, 40]

fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(orders, labels=channels, autopct="%1.1f%%",
       startangle=90)
ax.set_title("Orders by sales channel")
ax.axis("equal")
plt.show()
```

`autopct="%1.1f%%"` displays each slice as a percentage with one decimal place. The percent sign must be written as `%%` inside the formatting string. `startangle=90` rotates the first wedge to make the chart begin from the top. `ax.axis("equal")` ensures the circle is not stretched into an oval.

## 5. Format labels and emphasise a slice

```python
fig, ax = plt.subplots(figsize=(7, 6))
explode = (0.06, 0, 0)

wedges, texts, autotexts = ax.pie(
    orders,
    labels=channels,
    autopct="%1.0f%%",
    startangle=90,
    explode=explode,
    colors=["#4472C4", "#70AD47", "#ED7D31"],
    wedgeprops={"edgecolor": "white", "linewidth": 2},
    textprops={"fontsize": 10}
)
ax.set_title("Order channel mix")
plt.show()
```

The first slice is moved slightly outward because its explode value is 0.06. The other slices remain in place. The returned objects are wedge patches, label text objects and percentage text objects. You can customise these after creation, for example changing percentage text size or weight.

Exploding a slice should be used sparingly. It can imply importance, and it should not be used to exaggerate a small difference.

## 6. Donut charts

A donut chart is a pie chart with a hole in the middle. Matplotlib creates this effect with the `wedgeprops` argument:

```python
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(
    orders,
    labels=channels,
    autopct="%1.0f%%",
    startangle=90,
    wedgeprops={"width": 0.42, "edgecolor": "white"}
)
ax.text(0, 0, "200\norders", ha="center", va="center",
        fontsize=14, weight="bold")
ax.set_title("Orders by channel")
ax.axis("equal")
plt.show()
```

The `width` property controls wedge thickness. The centre can show a total or a short label. Do not use the hole to add unrelated information.

## 7. The denominator must be correct

A part-to-whole chart can be mathematically correct but analytically wrong if the denominator is not defined. Suppose 100 people answered a survey, but 20 skipped a question. If the pie chart shows percentages among the 80 valid responses, say so. If you show the missing responses as another category, explain that decision.

Categories must be mutually exclusive for a simple pie chart. If one customer can select multiple products, product counts may sum to more than the number of customers. Those values do not represent exclusive slices of one whole.

## 8. Why bar charts often win

Humans compare lengths more accurately than angles or areas. If the purpose is to rank categories or distinguish 21% from 24%, a sorted bar chart is usually clearer:

```python
fig, ax = plt.subplots(figsize=(7, 4))
ax.barh(channels, orders, color="slateblue")
ax.set(title="Number of orders by channel",
       xlabel="Orders", ylabel="Channel")
plt.show()
```

Use a pie or donut when the whole and a small number of parts are the main message. Use a bar chart when exact comparison or ranking matters.

## 9. Common mistakes

- Using too many slices.
- Including negative values.
- Showing percentages without the population or denominator.
- Using a pie chart when categories overlap.
- Exploding many slices and making the chart look dramatic.
- Using 3-D pie charts, which distort apparent slice size.
- Assuming that a pie chart is automatically clearer because it is familiar.

## Guided practice

1. Create the basic pie chart.
2. Change the start angle and observe the rotation.
3. Add an exploded slice.
4. Create a donut chart with the total in the centre.
5. Recreate the same data as a horizontal bar chart and compare which makes category differences easier to see.

## Independent practice

Find a dataset with a genuine part-to-whole structure and no more than five exclusive categories. Create a pie or donut chart and a bar chart using the same data. State the denominator, explain why the categories form a whole, and justify which chart better serves the intended audience.

## Knowledge check

1. Why must the values be non-negative?
2. What does `autopct` do?
3. What does `explode` do?
4. What does `wedgeprops={"width": ...}` change?
5. When is a sorted bar chart preferable to a pie chart?

## Lesson summary

Pie and donut charts show composition, not general category ranking. Use them only when categories form a meaningful whole, are mutually exclusive and are few enough to compare. Matplotlib's `pie()` supports labels, percentages, rotation, slice separation and wedge styling; always state the denominator and consider a bar chart for more accurate comparisons.