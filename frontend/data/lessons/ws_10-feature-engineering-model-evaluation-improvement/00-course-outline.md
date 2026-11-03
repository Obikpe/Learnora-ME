# Feature Engineering, Model Evaluation & Improvement

**Course:** ws_10  
**Duration:** 18h  
**Lessons:** 24  
**Environment:** Python 3 in VS Code; course-appropriate libraries and tools.

## Course purpose

This course is a structured self-study programme for data science learners. It moves from foundational ideas to practical implementation, interpretation, evaluation and a final applied task. Learners should be able to follow the notes without relying on a tutor to supply missing explanations. Every lesson should define new terminology, explain why a technique is used, demonstrate it with a small example before increasing complexity, discuss assumptions and common errors, and provide guided and independent practice.

## Learning journey

1. **Feature Engineering as a Modelling Discipline**
2. **Data Leakage and Leakage Prevention**
3. **Missing-Value Strategies**
4. **Encoding Categorical Variables**
5. **Scaling and Transforming Numerical Features**
6. **Date, Time and Text Features**
7. **Binning, Interactions and Polynomial Features**
8. **Feature Selection Fundamentals**
9. **Filter and Wrapper Feature Selection**
10. **Embedded Feature Selection**
11. **Pipelines and ColumnTransformer**
12. **Train/Validation/Test Strategy**
13. **Cross-Validation Design**
14. **Regression Evaluation Metrics**
15. **Classification Evaluation Metrics**
16. **Precision-Recall and ROC Analysis**
17. **Threshold Tuning and Cost-Sensitive Decisions**
18. **Bias-Variance Trade-Off**
19. **Hyperparameter Search**
20. **Randomised and Bayesian Search Concepts**
21. **Learning Curves and Error Diagnosis**
22. **Model Comparison and Statistical Caution**
23. **Reproducible Model Improvement Workflow**
24. **Feature Engineering and Evaluation Project**

## Teaching and assessment standard

Lessons build on earlier concepts and use consistent datasets and terminology where practical. Python examples should be runnable in VS Code, with imports, expected input structure and package requirements stated. Mathematical ideas should be explained intuitively before notation is introduced. Examples must explain both the code and the meaning of its output. Learners should practise checking assumptions, validating results, identifying limitations and communicating conclusions. Visuals should clarify concepts, processes, model behaviour or analytical findings rather than decorate the notes.

Assessment should include frequent short exercises, independent practice and a final applied project or portfolio artefact. Learners must document their data sources, preprocessing decisions, assumptions, evaluation choices and limitations. No result should be presented as causal or generalisable without appropriate evidence.


## Environment setup

Use Python 3.10 or newer in a dedicated VS Code virtual environment. The worked examples use pandas, NumPy, SciPy, Matplotlib and scikit-learn. Install the core packages with:

```bash
python -m pip install pandas numpy scipy matplotlib 'scikit-learn>=1.2'
```

The minimum scikit-learn version supports the `OneHotEncoder(sparse_output=...)` argument used in the notes. Activate the virtual environment before running examples. Where a lesson introduces an optional package or a specialised estimator, install it only when that lesson requires it. Record package versions in the project requirements file so the workflow can be reproduced.
