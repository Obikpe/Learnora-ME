# Lesson 26: Professional Conduct and Responsible Data Practice

## Learning outcomes
Apply the professional practice, produce the capstone artefact and communicate evidence and limitations clearly.

## 1. Core explanation
Professional conduct includes honesty, confidentiality, respect, competence and accountability. Do not claim expertise beyond your ability or present unverified results as facts. Protect access credentials and confidential material. Follow organisational policies and relevant laws. Escalate risks that exceed your competence or authority.

Responsible data practice includes documenting data sources, checking licences, minimising personal information and considering fairness. Avoid publishing screenshots or files that expose names, emails, account IDs or private records. Use synthetic or appropriately anonymised examples for public demonstrations, and understand that simple masking may not guarantee anonymity.

Keep a record of decisions and disclose conflicts of interest. If an analysis could cause harm, seek review and consider whether the project should proceed. Professional responsibility continues after delivery through correction, monitoring and incident response.

## 2. Worked example or template
Run the Python example in VS Code where applicable. Adapt paths and fields to your own dataset; do not publish restricted records.

```python
conduct_checks = [
    "I can substantiate every claim in my report",
    "I have permission to use and share the data",
    "Secrets and personal records are excluded",
    "Limitations and conflicts are disclosed",
    "I know who owns the output after handover"
]
for item in conduct_checks:
    print("[ ]", item)
```

## 3. Capstone application
Maintain a decision log and connect every analysis step to the project charter. Preserve provenance and reproducibility. Separate observed results from interpretation and recommendations.

## 4. Guided practice
Review a portfolio repository for privacy and licensing risks. Identify one issue that would require removing a file or rotating a credential and explain the correct response.

## 5. Independent practice
Complete the corresponding capstone deliverable. Ask a reviewer to reproduce or challenge one result and record the changes made in response.

## 6. Knowledge check
1. What evidence does this deliverable provide?
2. Which assumptions or limitations affect the conclusion?
3. How can another person reproduce the work?
4. What is the next responsible action?

## Lesson summary
A capstone demonstrates an end-to-end professional process: a well-framed question, defensible data, reproducible analysis, validation, clear communication and responsible publication.