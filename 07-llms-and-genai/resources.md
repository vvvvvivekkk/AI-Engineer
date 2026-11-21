# Module 07 - Resources

Links chosen from the course link catalogue (built from the nine source lists; see the root `SOURCES.md`) plus official provider pages. Model names, prices and limits change often — the official pages are the source of truth.

## Official API documentation

| Resource | Why |
|---|---|
| [OpenAI platform docs](https://platform.openai.com/docs/concepts) | Core concepts (tokens, models, Responses and Chat Completions APIs) behind the API most tutorials assume. |
| [Claude (Anthropic) API docs](https://platform.claude.com/docs/en/api/overview) | Official reference for the Messages API, streaming, structured outputs and tool use. (The older [docs.anthropic.com](https://docs.anthropic.com/en/docs/welcome) address redirects here.) |
| [Claude Python SDK](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python) | Install, client options, retries and the exception classes used in notebook 02. |
| [Claude API errors](https://platform.claude.com/docs/en/api/errors) | Every HTTP error code, which ones to retry, and the SDK's automatic retry behaviour. |
| [Claude rate limits](https://platform.claude.com/docs/en/api/rate-limits) | How request and token limits and spend caps work. |
| [Claude structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) | Getting JSON that matches a schema (`output_config.format` / `messages.parse`). |
| [Claude models overview](https://platform.claude.com/docs/en/models/overview) | Current model names, context windows and capabilities. |
| [Gemini API (Google AI for Developers)](https://ai.google.dev/gemini-api) | The `google-genai` SDK and a generous free tier, so every exercise can be done at zero cost. |
| [Ollama](https://ollama.com) | Download page, model library and docs for running open models locally. |
| [Ollama REST API reference](https://github.com/ollama/ollama/blob/main/docs/api.md) | Every endpoint (`/api/chat`, `/api/generate`, `/api/tags` ...) used in `code/ollama_rest.py`. |
| [tiktoken](https://github.com/openai/tiktoken) | The tokenizer library used for counting tokens and estimating cost. |

## Official pricing pages (use these in the Excel calculator)

| Provider | Link |
|---|---|
| OpenAI | https://openai.com/api/pricing/ |
| Anthropic | https://platform.claude.com/docs/en/about-claude/pricing |
| Google Gemini | https://ai.google.dev/gemini-api/docs/pricing |

## Courses and cookbooks

| Resource | Type | Why |
|---|---|---|
| [Anthropic courses](https://github.com/anthropics/courses/tree/master) | Free notebooks | API fundamentals, prompting and tool use, from the model vendor. |
| [Anthropic cookbook](https://github.com/anthropics/anthropic-cookbook) | Repo | Copy-ready recipes: classification, RAG, tool use, vision. |
| [OpenAI Cookbook](https://cookbook.openai.com/) | Repo | Large set of worked examples; many patterns transfer to other providers. |
| [Generative AI for Beginners (Microsoft)](https://github.com/microsoft/generative-ai-for-beginners) | Free course | Multi-lesson course on building GenAI apps end to end. |
| [LLM Course (mlabonne)](https://github.com/mlabonne/llm-course) | Free course | Roadmap plus Colab notebooks for LLM fundamentals, the "scientist" and "engineer" tracks. |
| [Generative AI with LLMs (Coursera)](https://www.coursera.org/learn/generative-ai-with-llms) | Course (free to audit) | The LLM lifecycle: pre-training, fine-tuning, RLHF, deployment. Good depth on section 5 of `concepts.md`. |
| [LLM Bootcamp (Full Stack Deep Learning)](https://fullstackdeeplearning.com/llm-bootcamp/) | Free videos | Building LLM products: UX, evaluation, deployment. |

## Local and open models

| Resource | Why |
|---|---|
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | CPU-friendly quantised inference, the engine underneath many local-LLM apps (including ideas Ollama builds on). |
| [Open WebUI](https://github.com/open-webui/open-webui) | Self-hosted ChatGPT-style interface on top of Ollama; good for demos. |
| [Gemma (open models)](https://ai.google.dev/gemma) | Small open-weight models that run locally. |
| [Llama docs](https://llama.meta.com/docs/overview) | Docs for a widely used open-weight model family. |
| [LiteLLM](https://github.com/BerriAI/litellm) | One OpenAI-style interface to many providers, so switching models is a one-line change. |

## Reading for AI engineers

| Resource | Type | Why |
|---|---|---|
| [The Rise of the AI Engineer](https://www.latent.space/p/ai-engineer) | Article | Defines the role this curriculum trains for. |
| [Patterns for Building LLM-based Systems](https://eugeneyan.com/writing/llm-patterns/) | Article | Recurring patterns (evals, RAG, caching, guardrails) with trade-offs. |
| [What We've Learned From A Year of Building with LLMs](https://applied-llms.org/) | Article | Practitioner lessons on tactics, operations and strategy. |
| [Simon Willison's blog](https://simonwillison.net/) | Blog | Frequent hands-on notes on new models, tools and prompt-injection risks. |
| [AI Engineering (Chip Huyen)](https://learning.oreilly.com/library/view/-/9781098166298/) | Paid book | Comprehensive guide to building applications on foundation models. |
| [Awesome LLM](https://github.com/Hannibal046/Awesome-LLM) | Repo | Wide index of LLM papers, models and tools. |
| [Awesome AI Engineering playbook (Eric-LLMs)](https://github.com/Eric-LLMs/awesome-ai-engineering) | Repo (CC-BY-4.0) | Mind maps and decks summarising the LLM-in-production stack. |

Licence note: all links point to the original authors. Nothing is copied from these resources into this module; descriptions are our own.
