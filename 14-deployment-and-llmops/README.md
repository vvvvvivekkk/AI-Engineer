# Module 14 — Deployment and LLMOps (weeks 22–23)

Turn an AI feature that works in a notebook into a small product other people can use safely: an API, a container, a web page, model serving, tracing, monitoring, guardrails, CI/CD and secrets.

## Learning goals

After this module you can:

1. Explain APIs, HTTP methods and status codes, and build a FastAPI service with routes, pydantic models, async endpoints and tests.
2. Explain images, containers, layers and Compose, and read/write a Dockerfile and `docker-compose.yml` for a Python API.
3. Put a quick UI on an API with Streamlit or Gradio, and say when to use each.
4. Explain in plain English what vLLM does (PagedAttention, continuous batching, OpenAI-compatible server).
5. Trace an LLM request with Langfuse (traces, spans, generations, cost, scores) and choose between cloud and self-hosting.
6. Monitor latency percentiles, error rate, token cost and drift, and write alert rules.
7. Add guardrails: input validation, PII redaction, prompt-injection heuristics, output schema validation.
8. Describe a CI/CD pipeline in GitHub Actions and manage secrets correctly.

## Prerequisites

- Modules 01–02 (Python, functions, dicts, pandas, matplotlib).
- Module 07 (calling LLM APIs, tokens, cost) and ideally 08 (prompt injection) and 09 (RAG).
- No Docker or GPU needed to complete the notebooks.

## Time estimate

- Reading `concepts.md`: 1.5–2 hours
- Notebooks: about 3 hours (four notebooks, 30–60 minutes each)
- Exercises: 3–6 hours
- Classroom session: 2 hours (see `trainer-notes.md`)

## Which tool and why

| Task | Tool | Why |
|---|---|---|
| Notebooks 01–04 | **Google Colab** or local Jupyter | They run offline in under a minute each; no setup in Colab |
| Running the real API, UIs, tests | **VS Code** + terminal on your laptop | You need a terminal for `uvicorn`, `pytest`, `streamlit` and `docker` |
| Docker | Docker Desktop (Windows/macOS) or Docker Engine (Linux) | Colab cannot run Docker |
| vLLM | A cloud machine or Colab with an NVIDIA GPU | vLLM needs a CUDA GPU; read the code otherwise |

## File map

| Path | Contents |
|---|---|
| `concepts.md` | the main lesson (≈5,000 words, 8 diagrams) |
| `notebooks/01-fastapi-from-zero.ipynb` | routes, params, pydantic, HTTPException, async timing, dependencies, TestClient, real uvicorn |
| `notebooks/02-docker-uis-and-serving.ipynb` | Docker layer-cache simulation, Compose parsing, Gradio + Streamlit (headless), batching and PagedAttention simulations |
| `notebooks/03-observability-and-monitoring.ipynb` | home-made tracer, Langfuse (guarded), simulated traffic, percentiles, cost, dashboard, drift (z-score, PSI), alerts, mini eval |
| `notebooks/04-guardrails-ci-and-secrets.ipynb` | validation, regex PII, injection heuristics with precision/recall, pydantic output checks + retry, safe pipeline, `.env`, secret scanner |
| `code/` | a complete, commented FastAPI service with Docker, Compose, UIs, vLLM, Langfuse, dashboard and CI files — see `code/README.md` |
| `slides/14-deployment-and-llmops.pptx` | 18-slide teaching deck with speaker notes |
| `pdf/14-deployment-and-llmops-handout.pdf` | printable handout of `concepts.md` |
| `excel/deployment-checklist.xlsx` | 33-item deployment checklist + 15 monitoring metrics with thresholds and actions |
| `exercises.md` / `solutions/` | 12 exercises (easy → hard) with full solutions |
| `trainer-notes.md` | session plan, common mistakes, check questions |
| `resources.md` | curated links |
| `build.py`, `notebook_sources.py` | regenerate images, notebooks, slides, PDF and Excel |

Rebuild everything: `python 14-deployment-and-llmops/build.py` from the repo root.
