# Lesson 22: Technical Interview Preparation

## Learning outcomes
Apply the professional practice, produce the capstone artefact and communicate evidence and limitations clearly.

## 1. Core explanation
Technical interviews assess problem-solving, communication and practical judgement. Prepare to explain core statistics, SQL, Python, data cleaning, visualisation, model evaluation and project decisions. Practise writing code clearly and explaining time and space complexity where relevant.

For project questions, describe the problem, data, method, validation, result and limitation. Expect follow-ups such as why a metric was selected, how leakage was prevented or what you would change with more time. If you do not know an answer, explain how you would investigate rather than bluffing.

Use timed practice, then review mistakes. Focus on explaining reasoning, not memorising isolated definitions. Prepare questions about the team's data maturity, success criteria, review process and how model outputs are used.

## 2. Worked example or template
Run the Python example in VS Code where applicable. Adapt paths and fields to your own dataset; do not publish restricted records.

```python
interview_prompts = [
    "Explain the difference between precision and recall.",
    "How would you detect data leakage?",
    "When would you use a median instead of a mean?",
    "Describe a project where you changed your approach.",
    "How would you validate a model on future data?"
]
for q in interview_prompts:
    print("-", q)
```

## 3. Capstone application
Maintain a decision log and connect every analysis step to the project charter. Preserve provenance and reproducibility. Separate observed results from interpretation and recommendations.

## 4. Guided practice
Answer each prompt aloud in two minutes. For one project, prepare a deeper technical explanation and a plain-language explanation for a non-technical interviewer.

## 5. Independent practice
Complete the corresponding capstone deliverable. Ask a reviewer to reproduce or challenge one result and record the changes made in response.

## 6. Knowledge check
1. What evidence does this deliverable provide?
2. Which assumptions or limitations affect the conclusion?
3. How can another person reproduce the work?
4. What is the next responsible action?

## Lesson summary
A capstone demonstrates an end-to-end professional process: a well-framed question, defensible data, reproducible analysis, validation, clear communication and responsible publication.