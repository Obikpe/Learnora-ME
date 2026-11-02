# Lesson 6: Mathematics Refresher: Statistics and Probability

## Learning outcomes

By the end of this lesson, you should be able to Calculate and interpret mean, median, variance, standard deviation and quantiles; describe probability and conditional probability; inspect class proportions; and explain how sampling variation affects model evaluation.

## 1. Core explanation
Statistics describes data and helps quantify uncertainty. The mean is the arithmetic average; the median is the middle ordered value; variance and standard deviation describe spread around the mean. Quantiles divide ordered data into proportions. A probability is between zero and one and represents uncertainty about an event under a defined model or process.

Conditional probability asks how likely A is when B is known: P(A|B). This is central to classification, where a model estimates the probability of a class given features. Bayes' theorem connects conditional probabilities and is the foundation of Naive Bayes. A probability estimate is not automatically a calibrated probability; calibration must be checked against observed frequencies.

A sample is not necessarily representative of a population. Sampling bias, missingness and class imbalance can distort estimates. Standard errors and confidence intervals describe sampling uncertainty under assumptions; they do not fix biased data collection. Distinguish a descriptive statistic of the observed sample from a claim about a wider population.

## 2. Worked Python example
Use a project virtual environment. Install relevant packages with `python -m pip install numpy pandas matplotlib scikit-learn scipy` when required.

```python
import numpy as np
from scipy import stats

scores = np.array([52, 61, 64, 68, 70, 73, 77, 85])
print("Mean:", scores.mean())
print("Median:", np.median(scores))
print("Standard deviation:", scores.std(ddof=1))
print("Quartiles:", np.quantile(scores, [0.25, 0.5, 0.75]))
print("P(score >= 70):", np.mean(scores >= 70))
```

## 3. Read the result
Do not stop when the code runs. Explain what each input represents, what the output measures and whether the result is plausible. Check data types and shapes. Keep a note of assumptions and information that would not be available at prediction time.

## 4. Guided practice
For a class of 40 learners, 10 did not submit an assignment. Calculate the observed non-submission proportion. Explain why this sample proportion does not automatically describe all learners in the country.

## 5. Independent practice
Find or create a small dataset related to the topic. Define its unit of observation and write a data dictionary. Repeat the technique without copying the worked example. Include a brief interpretation and one limitation.

## 6. Knowledge check
1. Define the key terms in this lesson in your own words.
2. When would this method be inappropriate?
3. What can go wrong if data is not representative or is prepared incorrectly?
4. What evidence would you need before trusting the result?

## Lesson summary
Machine learning depends on a clearly defined problem, appropriate data, sound mathematical reasoning and careful evaluation. Tools make implementation easier, but they do not remove the need for judgement.