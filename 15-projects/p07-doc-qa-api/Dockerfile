# Dockerfile - a recipe for a container image that runs the Q&A API anywhere Docker runs.
# Build:  docker build -t doc-qa-api .
# Run:    docker run -p 8000:8000 doc-qa-api      then open http://localhost:8000/docs

# 1. Start from a small official Python image.
FROM python:3.13-slim

# 2. Sensible Python settings for containers (no .pyc files, logs appear immediately).
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HF_HOME=/app/.hf-cache

WORKDIR /app

# 3. Install the CPU-only build of PyTorch first (the default wheel bundles GPU libraries and is several GB).
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.15.0

# 4. Install the remaining pinned packages. Copying requirements.txt on its own first lets
#    Docker cache this slow layer when only the code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Download the embedding model at build time so the container starts fast and works offline.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# 6. Copy the code and the sample PDFs.
COPY src ./src
COPY data ./data

# 7. Run as a normal user, not root (safer if the app is ever compromised).
RUN useradd --create-home appuser && mkdir -p /app/logs && chown -R appuser /app
USER appuser

EXPOSE 8000
# 8. Docker checks /health every 30 s and marks the container unhealthy if it stops answering.
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
