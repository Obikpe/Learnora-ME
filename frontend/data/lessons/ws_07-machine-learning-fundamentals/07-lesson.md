# Lesson 7: Mathematics Refresher: Calculus and Optimisation

## Learning outcomes

By the end of this lesson, you should be able to Explain derivatives and gradients intuitively; connect a loss function to an optimisation objective; implement a simple gradient-descent update; and recognise how learning rate and scaling affect convergence.

## 1. Core explanation
Many models learn by minimising a loss function. A loss measures how far predictions are from desired outcomes. Optimisation adjusts model parameters to reduce that loss. A derivative describes how a function changes as its input changes; the gradient collects derivatives for multiple parameters and points toward the direction of steepest increase. Gradient descent moves in the opposite direction.

The update is parameter := parameter − learning_rate × gradient. A learning rate that is too large can overshoot; one that is too small can make learning very slow. The loss surface may be non-convex, so optimisation can depend on initialisation and settings. In simple linear regression with squared error, the objective is convex, making the global minimum easier to reason about.

The model is not learning by magic: it repeatedly evaluates errors and adjusts parameters. Training loss alone is not enough. A flexible model may minimise training loss while performing poorly on unseen data. Generalisation is assessed using separate data.

## 2. Worked Python example
Use a project virtual environment. Install relevant packages with `python -m pip install numpy pandas matplotlib scikit-learn scipy` when required.

```python
import numpy as np

x = np.array([1.0, 2.0, 3.0])
y = np.array([2.0, 4.0, 6.0])
w, b = 0.0, 0.0
learning_rate = 0.05

for step in range(500):
    prediction = w * x + b
    error = prediction - y
    dw = (2 / len(x)) * np.sum(error * x)
    db = (2 / len(x)) * np.sum(error)
    w -= learning_rate * dw
    b -= learning_rate * db

print("Learned weight:", w, "intercept:", b)
```

## 3. Read the result
Do not stop when the code runs. Explain what each input represents, what the output measures and whether the result is plausible. Check data types and shapes. Keep a note of assumptions and information that would not be available at prediction time.

## 4. Guided practice
Change the learning rate to 0.5 and observe whether training remains stable. Then use 0.001 and compare the number of iterations needed. Explain the role of the learning rate and why a low training error does not prove generalisation.

## 5. Independent practice
Find or create a small dataset related to the topic. Define its unit of observation and write a data dictionary. Repeat the technique without copying the worked example. Include a brief interpretation and one limitation.

## 6. Knowledge check
1. Define the key terms in this lesson in your own words.
2. When would this method be inappropriate?
3. What can go wrong if data is not representative or is prepared incorrectly?
4. What evidence would you need before trusting the result?

## Lesson summary
Machine learning depends on a clearly defined problem, appropriate data, sound mathematical reasoning and careful evaluation. Tools make implementation easier, but they do not remove the need for judgement.