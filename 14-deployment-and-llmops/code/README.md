# code/ — a small, deployable LLM service

Everything here runs **without an API key** (an offline stand-in model answers instead). Add `ANTHROPIC_API_KEY` to a `.env` file to use a real model.

| Path | What it is |
|---|---|
| `app/main.py` | FastAPI app: `GET /health`, `POST /chat`, `GET /metrics` |
| `app/llm.py` | `generate()` — real Anthropic call if a key is set, otherwise offline stand-in; token + cost estimate |
| `app/guardrails.py` | input validation, PII redaction (regex), prompt-injection heuristics, output schema validation (pydantic) |
| `app/metrics.py` | in-memory latency / error / token / cost store |
| `tests/test_main.py` | 7 pytest tests using FastAPI's `TestClient` |
| `smoke_test.py` | runs every piece once, offline |
| `requirements.txt` | pinned packages for the API (used by Docker and CI) |
| `requirements-ui.txt` | optional packages for the UIs |
| `Dockerfile`, `.dockerignore` | build the API image |
| `docker-compose.yml` | run API + Streamlit UI together |
| `.env.example` | copy to `.env` and fill in; never commit `.env` |
| `ui/streamlit_app.py`, `ui/gradio_app.py` | two chat UIs that call the API |
| `serving/vllm_serve.sh`, `serving/vllm_client.py` | start and call an OpenAI-compatible vLLM server (GPU needed) |
| `observability/langfuse_tracing.py` | Langfuse tracing, guarded by env vars; console fallback |
| `monitoring/metrics_dashboard.py` | simulated week of metrics → 4-panel dashboard PNG |
| `ci/github-actions-ci.yml` | GitHub Actions workflow: lint, test, build and push image |

## Run it

```bash
cd 14-deployment-and-llmops/code
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # then edit .env (or leave the key as the placeholder)
uvicorn app.main:app --reload --port 8000              # open http://127.0.0.1:8000/docs
python -m pytest -q                                    # run the tests
```

UIs (second terminal, API still running):

```bash
pip install -r requirements-ui.txt
streamlit run ui/streamlit_app.py      # http://localhost:8501
python ui/gradio_app.py                # http://127.0.0.1:7860
```

Docker:

```bash
docker build -t llm-chat-api .
docker run --rm -p 8000:8000 --env-file .env llm-chat-api
docker compose up --build              # API on 8000 + Streamlit on 8501
```

Note: the Dockerfile and compose file were written and syntax-checked for this course but the build machine had no Docker engine, so build them once yourself before teaching.
