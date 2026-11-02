# Lesson 8: Git and GitHub for Data Work

## Learning outcomes

By the end of this lesson, you should be able to Explain Git repositories, commits and branches; use a basic add/commit/push workflow; create a useful .gitignore; and avoid committing secrets, environments or restricted data.

## 1. Core explanation
Git records changes to files over time. A repository contains the project history; a commit is a named snapshot. Branches allow isolated work, while a pull request supports review before changes are merged. GitHub adds collaboration, issue tracking and project documentation.

Use meaningful commit messages and commit small coherent changes. Do not commit secrets, personal data, large generated files or environment folders. A .gitignore file excludes local artefacts such as .venv, caches and private data. If a secret is committed, deleting it in a later commit is not sufficient; rotate the credential and follow the repository's history-cleanup process.

A public repository is a professional artefact. Check that it can be cloned, dependencies are documented, paths work and the README accurately describes the project. Do not claim work you did not complete.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

```python
# Example .gitignore entries
.venv/
__pycache__/
.ipynb_checkpoints/
.env
*.log
data/private/
data/raw/restricted/
# Basic workflow:
# git init
# git add README.md src/
# git commit -m "Add project structure and documentation"
```

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Create a Git repository for a project. Add a .gitignore, make three meaningful commits and write a README. Explain how you would respond if an API key was accidentally committed.

## 5. Independent practice
Create the corresponding artefact in your project repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.