# Module 08 — Prompt and Context Engineering (week 14)

**In one line:** learn to write prompts that work, assemble the right context for every model call, defend against prompt injection, and test prompts like code — then study how real AI products structure their system prompts and write your own.

## Goals — after this module you can

1. Name the seven building blocks of a prompt and rewrite a vague prompt into a strong one.
2. Use zero-shot, few-shot and chain-of-thought prompting, and explain when each helps.
3. Get **structured output** (JSON) from a model and validate it with Pydantic, retrying on errors.
4. Keep prompts as **versioned templates** with fingerprints.
5. Build a context within a **token budget**: pick, order, summarise and trim its ingredients.
6. Explain **prompt injection** (direct and indirect) and apply layered defences.
7. Evaluate prompt versions on a small **test set** and record results in a tracker.
8. Describe the recurring patterns in real AI products' system prompts and write your own system prompt from our template.

## Prerequisites

- Module 01 (Python basics) and 02 (pandas) — you read and run Python and DataFrames.
- Module 07 (LLMs and GenAI) — you know what tokens, temperature and chat APIs are.
- No API key needed. Every notebook runs offline with a tiny local model; real API calls run only if you set a key.

## Time estimate

| Part | Time |
|---|---|
| Read `concepts.md` | 75 min |
| Read `system-prompt-analysis.md` | 30 min |
| Four notebooks | 2–3 h |
| Exercises | 3–4 h |
| **Total** | **about 8 h** (one week at the course pace) |

## Which tool to use, and why

- **Google Colab** — easiest: click the badge at the top of each notebook. Nothing to install. The free CPU runtime is enough.
- **Jupyter / VS Code locally** — use this if you want to set real API keys in a `.env` file (copy `.env.example` from module 00) and compare the tiny model with a real one.
- **VS Code** for the scripts in `code/` (run them with `python code/<file>.py`).

## File map

| Path | What it is |
|---|---|
| [concepts.md](concepts.md) | The main lesson: anatomy, few-shot, reasoning, structured output, system prompts, templates, context engineering, injection, evaluation, real-prompt patterns |
| [system-prompt-analysis.md](system-prompt-analysis.md) | Our own analysis of real AI tools' system prompts (no copied text), with charts |
| [templates/system-prompt-template.md](templates/system-prompt-template.md) | Our template for writing a system prompt, with a filled-in example |
| `notebooks/01-prompt-anatomy-and-few-shot.ipynb` | Vague vs structured prompts, chat templates, zero vs few-shot measured, templates, temperature |
| `notebooks/02-structured-output-and-reasoning.ipynb` | Pydantic schemas, validate-and-retry, label scoring, chain-of-thought, self-consistency, real API code |
| `notebooks/03-context-engineering.ipynb` | Token counting, trimming tool output, summarising history, memory recall, budgeted packing, budget chart |
| `notebooks/04-injection-and-prompt-evaluation.ipynb` | Injection demo, three defence layers, a test set with attacks, scoring, tracker CSV, LLM-as-judge |
| `code/llm_client.py` | One `call_llm()` for Anthropic / OpenAI / offline local model |
| `code/prompt_templates.py` | Versioned prompt templates with fingerprints (v1, v2, v3 ticket classifier) |
| `code/prompt_eval.py` | Runs all template versions on a test set and writes `prompt_eval_results.csv` |
| `code/context_builder.py` | Budgeted context packing, history summarising, middle-truncation |
| `code/injection_guard.py` | Input scan, untrusted-text wrapper, output checks |
| `code/analyse_prompt_patterns.py` | Counts pattern keywords in a clone of the system-prompts repo (numbers only) |
| `slides/08-prompt-and-context-engineering.pptx` | 17-slide teaching deck with speaker notes |
| `pdf/` | Handouts of `concepts.md` and `system-prompt-analysis.md` |
| `excel/prompt-test-tracker.xlsx` | Prompt test-case tracker with pass-rate formulas, plus our pattern counts |
| [exercises.md](exercises.md) / `solutions/` | 12 exercises, easy to hard, with full solutions |
| [trainer-notes.md](trainer-notes.md) | Session plan, common mistakes, check questions |
| [resources.md](resources.md) | Curated further reading |
| `build.py` | Regenerates images, notebooks, slides, Excel and PDFs (`build_notebooks.py` holds notebook content) |

## A note on the offline model

The notebooks use **SmolLM2-135M-Instruct**, a very small model, so they run anywhere for free. Its answers are often poor. That is deliberate and useful: weak models make the effect of good prompting easy to see (for example, few-shot examples took its format-following from 0% to 75% on our test set). With a real API key the same code calls a strong model.
