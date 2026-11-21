# Module 07 - LLMs and Generative AI

**Week 13 of the course.** What a large language model really does, how its settings change its behaviour, how it is trained, and how to use one from Python: through the OpenAI, Anthropic and Gemini APIs, and locally with Ollama. Also: counting tokens, estimating cost, and choosing a model.

## Learning goals

After this module a learner can:

1. Explain **next-token prediction** and show the top-k next-token probabilities of a real (small) model.
2. Explain and demonstrate **temperature**, **top-p** and the **context window** (the maximum number of tokens a model handles at once).
3. Describe pre-training, instruction tuning (SFT) and preference tuning (RLHF / DPO) in plain words.
4. Call the OpenAI, Anthropic and Gemini APIs with their official Python SDKs: messages and roles, system prompts, multi-turn history, streaming, structured JSON output.
5. Handle errors correctly: know which HTTP errors to retry, use exponential backoff, configure SDK retries.
6. Keep API keys out of code using environment variables and `.env` files.
7. Count tokens with `tiktoken`, estimate monthly cost with the Excel calculator, and look up current prices on official pages.
8. Install and use **Ollama** (terminal, REST API, Python client) to run open models locally.
9. Choose a model for a task using privacy, difficulty, context length, latency and budget.

## Prerequisites

- Module 06 (tokens, embeddings, transformers).
- Module 00 (environment variables, `.env`, `pip`) and Module 01 (functions, `try/except`, dictionaries).

## Time estimate

| Part | Time |
|---|---|
| Read `concepts.md` | 75-90 min |
| Notebooks 01-03 | 2.5-3 hours |
| Exercises | 3-4 hours |
| Taught session (see `trainer-notes.md`) | 2 hours |

## Which tool to use, and why

- **Google Colab** for the notebooks: nothing to install, and the Secrets panel (key icon) stores API keys safely. Everything also runs with **no keys** thanks to the offline fallback.
- **VS Code + terminal** for the `code/` scripts and for real API work. Copy `.env.example` to `.env`, add your keys, and run e.g. `python code/anthropic_basics.py` from inside `code/`.
- **Your own laptop** for Ollama — it is a desktop program and cannot run in Colab or on the course server. A laptop with 8 GB RAM runs 1-3 billion-parameter models comfortably.

**API keys:** you do not need any to follow the module. To try real calls, a free-tier Gemini key is the cheapest start; OpenAI and Anthropic need a paid account with a small credit. Never commit `.env`.

## File map

| Path | What it is |
|---|---|
| `concepts.md` | The main lesson. Start here. |
| `.env.example` | Placeholder keys and model names; copy to `.env` |
| `notebooks/01-how-llms-work.ipynb` | Next-token probabilities, the generation loop, temperature, top-p, `generate()` sampling, context-window growth and trimming, chat templates |
| `notebooks/02-calling-llm-apis.ipynb` | OpenAI / Anthropic / Gemini helpers with offline fallback, roles, history, streaming, structured JSON + validation, real SDK error handling, retries |
| `notebooks/03-tokens-cost-and-local-models.ipynb` | tiktoken counting, cost estimates (example prices), the Excel calculator, usage logging, Ollama check with fallback, memory sizing, model-choice helper |
| `code/llm_clients.py` | One helper per provider with the same inputs/outputs and offline fallback |
| `code/openai_basics.py`, `code/anthropic_basics.py`, `code/gemini_basics.py` | Each SDK: system prompt, multi-turn, streaming, structured output, errors |
| `code/next_token_demo.py`, `code/sampling_demo.py` | Top-k probabilities and greedy steps; temperature and top-p |
| `code/retry_backoff.py` | Exponential backoff with jitter on a simulated flaky API |
| `code/token_cost.py` | Token counting and cost estimate (you supply current prices) |
| `code/ollama_commands.sh`, `code/ollama_rest.py`, `code/ollama_client.py` | Ollama terminal commands, REST API and Python client (+ OpenAI-compatible endpoint) |
| `excel/07-llm-cost-calculator.xlsx` | Cost calculator with live formulas; prices are yellow input cells linked to official pricing pages |
| `images/` | Diagrams (`.mmd` = editable Mermaid sources) |
| `slides/07-llms-and-genai.pptx` | Teaching deck with speaker notes |
| `pdf/07-llms-and-genai-handout.pdf` | Printable version of `concepts.md` |
| `exercises.md` / `solutions/` | 10 exercises, easy to hard, with full solutions |
| `trainer-notes.md` | How to teach the module, with a timed session plan |
| `resources.md` | The best external links, each with a reason |
| `build.py` | Regenerates images, notebooks, slides, PDF and Excel |

## A note on fast-changing facts

Model names, prices, context sizes and SDK features change every few months. This module reads model names from environment variables (defaults are examples as of late 2026), never hard-codes prices, and links the official pages. The SDK calls were checked against `openai` 3.57, `anthropic` 2.12 and `google-genai` 3.6.1 by building real requests offline. If a call fails with a newer SDK version, check that provider's API reference.

## Rebuild the generated files

```bash
python 07-llms-and-genai/build.py
python tools/check_module.py 07-llms-and-genai --run
```
