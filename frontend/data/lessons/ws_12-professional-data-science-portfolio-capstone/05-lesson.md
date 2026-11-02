# Lesson 5: Data Ethics, Privacy and Licensing

## Learning outcomes
Explain the professional practice, apply it to a data-science project and produce evidence that another person can review.

## 1. Core explanation
Ethical data work begins with purpose. Collect only information needed for a defined task, use it for compatible purposes, restrict access and retain it only as long as justified. Personal data can remain identifiable even after obvious names are removed, especially when records contain combinations of location, dates and rare attributes.

Check the legal basis and consent requirements applicable to the context, along with source licence and redistribution conditions. Publicly accessible data is not automatically free of restrictions. Respect copyright, database rights, contractual terms and privacy obligations. Avoid publishing raw personal records in portfolios.

Consider who may be harmed by errors, exclusion or inference. Use aggregation, de-identification and synthetic examples where appropriate, while recognising that these techniques do not guarantee anonymity. Document ethical decisions and seek specialist review for high-risk data.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

```python
ethics_check = {
    "purpose_defined": True,
    "minimum_fields_collected": True,
    "lawful_use_and_licence_checked": False,
    "access_restricted": True,
    "retention_defined": False,
    "portfolio_data_sanitised": False
}
for check, status in ethics_check.items():
    print("PASS" if status else "REVIEW", check)
```

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Complete an ethics and licensing checklist for a public health dataset. Identify which fields should not appear in a public GitHub repository and what permissions must be checked before redistribution.

## 5. Independent practice
Create the corresponding artefact in your project repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.