# Lesson 12: Containerisation Concepts with Docker

## Learning outcomes

By the end of this lesson, you should be able to Explain Docker images, containers and Dockerfiles; build a minimal API image; expose the required port; and identify base-image, privilege, secret and dependency risks.

## 1. Core explanation
A container packages an application with its runtime dependencies so it behaves consistently across environments. A Docker image is the build artefact; a container is a running instance. A Dockerfile describes how to build the image. Containers share the host kernel and are generally lighter than full virtual machines.

A container does not automatically make software secure or reproducible. Use trusted base images, keep them updated, avoid running as root, minimise included files and do not bake secrets into images. Keep model artefacts and datasets separate where appropriate. Expose only required ports.

For an ML API, the image should include application code and runtime dependencies. Decide how the model is supplied: baked into the image for immutable releases or mounted/downloaded from controlled storage with version checks. Document resource requirements.

## 2. Worked example
Create a file named `Dockerfile` in the same project folder as `app.py` and `requirements.txt`. This is a Docker configuration file, not Python code. Docker must be installed and running to build and run the image.

```dockerfile
# Dockerfile example for a FastAPI service
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home appuser
COPY --chown=appuser:appuser app.py .
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run it from the folder containing the Dockerfile:

```bash
docker build -t ml-service .
docker run --rm -p 8000:8000 ml-service
```

Add a `.dockerignore` file so local environments, credentials and data are not copied into the image:

```text
.venv/
__pycache__/
.git/
.env
*.db
data/
```

## 3. Operational interpretation
State what the example demonstrates and what it does not demonstrate. Distinguish a local prototype from a production deployment. Document dependencies, input/output contracts, data handling, failure modes and model version.

## 4. Guided practice
Write a Dockerfile for your API. Explain each instruction, identify where the model file will come from and list three steps to reduce image risk. Do not include credentials in the image.

## 5. Independent practice
Add the lesson's control or component to your own small ML application. Write a short runbook explaining how to test it, monitor it and respond when it fails.

## 6. Knowledge check
1. What can fail outside the model itself?
2. What should be logged and what should remain private?
3. How would you detect a change in behaviour?
4. What is the rollback or fallback plan?

## Lesson summary
Production ML is an engineered service with explicit contracts, versioning, monitoring, security and human accountability. A model score alone is not evidence of production readiness.