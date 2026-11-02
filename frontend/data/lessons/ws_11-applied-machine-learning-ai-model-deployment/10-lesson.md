# Lesson 10: Packaging and Environment Management

## Learning outcomes
Explain the applied ML engineering concept, implement the example and identify operational risks.

## 1. Core explanation
A deployable service needs a reproducible Python environment. Use a virtual environment and record dependencies. Pin versions for important libraries, but update them through a tested process rather than freezing an insecure environment indefinitely. Keep development dependencies separate from runtime dependencies where practical.

A requirements file or modern project metadata describes dependencies. The application should start from a clean environment using documented commands. Avoid relying on packages installed globally or files outside the project. Use environment variables for configuration and secret managers for credentials; never commit secrets.

Packaging also includes source code, model artefacts, data schema, documentation and startup configuration. Test installation and startup from a clean environment before deployment.

## 2. Worked Python example
Use VS Code and a project virtual environment. Install the relevant packages with `python -m pip install pandas scikit-learn fastapi uvicorn joblib httpx` as required.

```text
# requirements.txt
fastapi>=0.110,<1
uvicorn[standard]>=0.27,<1
pydantic>=2.6,<3
scikit-learn>=1.4,<2
pandas>=2.1,<4
joblib>=1.3,<2
httpx>=0.27,<1
```

Create a file named `requirements.txt` with those dependency declarations. Then run these commands in the VS Code terminal:

```bash
python -m venv .venv
# Activate .venv using the command for your operating system.
python -m pip install -r requirements.txt
python -m pip freeze > requirements-lock.txt
```

## 3. Engineering checks
Check schema compatibility, dependency versions, error handling, privacy and reproducibility. Distinguish a local demonstration from a production service. Never claim deployment readiness from a notebook score alone.

## 4. Guided practice
Create a clean virtual environment and install your project dependencies from a requirements file. Document the exact run command and explain why global packages can hide missing dependencies.

## 5. Independent practice
Extend the example into a small, testable module. Document its input/output contract, setup instructions, expected failure behaviour and limitations. Add at least two tests.

## 6. Knowledge check
1. What responsibility belongs to the model and what belongs to the service?
2. What should happen when input is invalid?
3. Which information should be logged, and what should not?
4. What operational test would you run before release?

## Lesson summary
An applied ML product includes data transformations, model artefacts, validation, service contracts, tests, security and monitoring. The estimator is only one component.