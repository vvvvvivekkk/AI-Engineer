# Module 14 — Resources

Curated links for deployment and LLMOps. Most come from the course's source catalogue (`source-notes/14-deployment-and-llmops.md`); a few are official documentation roots added for topics this module teaches (Streamlit, Gradio, pydantic, uvicorn, GitHub Actions). Tools and prices change quickly — as of late 2026, always check the official page.

## Start here (beginner)

| Resource | Why it is useful |
|---|---|
| [FastAPI documentation](https://fastapi.tiangolo.com) | The official tutorial is one of the best-written beginner guides in Python; follow "Tutorial - User Guide" alongside notebook 01. |
| [pydantic documentation](https://docs.pydantic.dev) | Reference for `BaseModel`, `Field` rules and validation errors used in our request models and output guardrails. |
| [uvicorn](https://www.uvicorn.org) | The server that runs FastAPI apps; settings for host, port, workers and reload. |
| [Docker documentation](https://docs.docker.com/) | "Get started" walks through images, containers and Compose step by step. |
| [Docker Compose docs](https://docs.docker.com/compose/) | Reference for every key in `docker-compose.yml` (services, ports, volumes, depends_on). |
| [Streamlit docs](https://docs.streamlit.io) | Widgets, `session_state`, chat elements and free Community Cloud hosting. |
| [Gradio docs](https://www.gradio.app/docs) | `ChatInterface`, `Blocks` and deploying demos to Hugging Face Spaces. |
| [Ollama](https://ollama.com) | The simplest way to run an open model locally behind an OpenAI-style API (see module 07). |
| [GitHub Actions docs](https://docs.github.com/en/actions) | Workflow syntax, runners, and how to store secrets for CI. |

## Model serving and gateways (intermediate → advanced)

| Resource | Why it is useful |
|---|---|
| [vLLM documentation](https://docs.vllm.ai) | The standard high-throughput open-model server: PagedAttention, continuous batching, OpenAI-compatible API, supported models. |
| [vLLM (repo)](https://github.com/vllm-project/vllm) | Source code, examples and release notes for the serving engine. |
| [SGLang](https://github.com/sgl-project/sglang) | A fast alternative to vLLM, strong at reusing shared prompt prefixes and structured generation. |
| [text-generation-inference (Hugging Face)](https://github.com/huggingface/text-generation-inference) | Hugging Face's production text-generation server — another option to compare with vLLM. |
| [LiteLLM](https://www.litellm.ai/) | A gateway with one API over many providers, plus routing, fallbacks, budgets and spend tracking. |

## Observability and evaluation

| Resource | Why it is useful |
|---|---|
| [Langfuse](https://langfuse.com) | Open-source tracing, prompt versions, evals and cost dashboards; cloud or self-hosted. Docs cover the Python SDK used in `code/observability/`. |
| [LangSmith](https://www.langchain.com/langsmith) | Hosted tracing and dataset-based evaluation, closely tied to LangChain/LangGraph. |
| [Arize Phoenix](https://github.com/Arize-ai/phoenix) | Open-source tracing plus RAG and agent evaluation that runs locally. |
| [W&B Weave](https://wandb.ai/site/weave/) | Lightweight instrumentation and eval harnesses with dataset versioning. |
| [Your AI Product Needs Evals (Hamel Husain)](https://hamel.dev/blog/posts/evals/) | The clearest argument for why evals drive iteration speed, and how to start. |
| [AI Evals FAQ (Husain & Shankar)](https://hamel.dev/blog/posts/evals-faq/) | Practical answers on error analysis, LLM-as-judge and how big an eval set should be. |
| [Evaluating LLM-Evaluators (Eugene Yan)](https://eugeneyan.com/writing/llm-evaluators/?utm_source=pocket_saves) | Evidence on when LLM-as-judge can be trusted and how to calibrate it. |
| [DeepEval](https://github.com/confident-ai/deepeval) | Pytest-style LLM tests that slot straight into CI (exercise 12 is a home-made version). |
| [Promptfoo](https://github.com/promptfoo/promptfoo) | Declarative regression tests and red-teaming for prompts and apps, CI-friendly. |
| [Hugging Face Evaluate](https://huggingface.co/docs/evaluate/en/index) | Standard metrics (accuracy, BLEU, ROUGE) with one consistent API. |
| [Inspect (UK AI Security Institute)](https://inspect.ai-safety-institute.org.uk/) | A rigorous open-source framework for model and agent evaluations, including safety tests. |

## Guardrails and security

| Resource | Why it is useful |
|---|---|
| [Microsoft Presidio](https://github.com/microsoft/presidio) | ML + rules PII detection and anonymisation — the next step after our regex redactor. |
| [LLM Guard](https://github.com/protectai/llm-guard) | Scanners for prompt injection, PII and secrets in inputs and outputs. |
| [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) | Programmable input, output and retrieval "rails" around a chatbot. |
| [garak](https://github.com/NVIDIA/garak) | Automated vulnerability scanning (red-team probes) for LLM apps. |

## Going deeper

| Resource | Why it is useful |
|---|---|
| [LLMOps short course (DeepLearning.AI)](https://www.deeplearning.ai/short-courses/llmops/) | A guided introduction to pipelines, versioning and deployment for LLM apps. |
| [awesome-production-machine-learning](https://github.com/EthicalML/awesome-production-machine-learning) | A big map of MLOps tools: serving, monitoring, feature stores, orchestration. |

Licence note: all links point to the original authors' pages; nothing from them is copied into this module.
