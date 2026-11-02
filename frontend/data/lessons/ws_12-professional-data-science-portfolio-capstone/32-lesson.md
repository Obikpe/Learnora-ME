# Lesson 32: Capstone: Portfolio Publication and Reflection

## Learning outcomes
Apply the professional practice, produce the capstone artefact and communicate evidence and limitations clearly.

## 1. Core explanation
Publishing a capstone makes the work discoverable and reproducible. Review the repository for secrets, private data, broken links, machine-specific paths and undocumented dependencies. Include a README, data source and licence, setup instructions, code, figures and final report. If raw data cannot be redistributed, explain how to obtain it or provide a safe sample.

Write a case study that states your contribution, decisions and limitations. Label the project as completed and distinguish planned extensions. Do not claim production deployment if the work was only run locally. Keep the portfolio page and repository consistent.

Reflection should identify what worked, what failed, what you learned and what you would change with more time. A good reflection is specific and evidence-based, not a generic statement about learning a lot.

## 2. Worked example or template
Run the Python example in VS Code where applicable. Adapt paths and fields to your own dataset; do not publish restricted records.

```python
publication_check = [
    "No credentials or private records",
    "Data source and licence documented",
    "Environment setup tested from clean state",
    "README reproduces main result",
    "Figures and report have source notes",
    "Limitations and contribution stated",
    "Repository links work"
]
for item in publication_check:
    print("[ ]", item)
```

## 3. Capstone application
Maintain a decision log and connect every analysis step to the project charter. Preserve provenance and reproducibility. Separate observed results from interpretation and recommendations.

## 4. Guided practice
Publish your capstone repository and write a 300-word reflection. Include one methodological decision you would change, one skill demonstrated and one limitation future work should address.

## 5. Independent practice
Complete the corresponding capstone deliverable. Ask a reviewer to reproduce or challenge one result and record the changes made in response.

## 6. Knowledge check
1. What evidence does this deliverable provide?
2. Which assumptions or limitations affect the conclusion?
3. How can another person reproduce the work?
4. What is the next responsible action?

## Lesson summary
A capstone demonstrates an end-to-end professional process: a well-framed question, defensible data, reproducible analysis, validation, clear communication and responsible publication.