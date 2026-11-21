# Dockerfile - the recipe Docker follows to build an "image" of our FastAPI app.
# Build:  docker build -t llm-chat-api .
# Run:    docker run --rm -p 8000:8000 --env-file .env llm-chat-api
# Each line below is one "instruction". Docker caches each step as a "layer",
# so steps that change rarely (installing packages) go BEFORE steps that change often (our code).

# 1. Start from an official, small Python image (the "base image").
FROM python:3.13-slim

# 2. Sensible Python settings for containers:
#    - don't write .pyc files, and print logs immediately instead of buffering them.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. All following commands run inside /app in the container.
WORKDIR /app

# 4. Copy ONLY the requirements first, then install. If requirements.txt has not changed,
#    Docker reuses the cached layer and skips this slow step on the next build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Now copy our application code (changes often, so it comes last).
COPY app/ ./app/
COPY tests/ ./tests/

# 6. Do not run as the all-powerful "root" user: create a normal user and switch to it.
RUN useradd --create-home appuser
USER appuser

# 7. Document which port the app listens on (documentation only; -p does the real mapping).
EXPOSE 8000

# 8. Docker can poll this to know whether the app is healthy.
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

# 9. The command that runs when a container starts. 0.0.0.0 = accept connections from outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
