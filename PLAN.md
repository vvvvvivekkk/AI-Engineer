# PLAN — "Python to Pro" AI Engineer Curriculum

This plan lists every module and project, what each one teaches, and how the work is built and checked. It is the spec used to build the repo.

## Who this is for
A **trainer who knows nothing yet**. They study a module from this repo alone, then teach it to students using the slides, notebooks, handout and session plan in that module. Everything is written at true beginner level; every piece of jargon is defined on first use.

## Length and shape
~24 weeks, ~8–10 hours a week for a learner (see ROADMAP.md). Modules 00–03 are foundations, 04–06 are classic ML/DL/NLP, 07–11 are the modern LLM / GenAI engineering core, 12–14 cover training data, fine-tuning and production, 15 is projects, 16 is careers.

## Standard contents of every module
README.md · concepts.md · images/ · notebooks/ · code/ · slides/ (.pptx) · pdf/ (handout) · excel/ (where useful) · exercises.md · solutions/ · trainer-notes.md · resources.md · build.py. Full rules: [tools/MODULE-STANDARD.md](tools/MODULE-STANDARD.md).

## Modules

### 00-setup (week 1)
Python install and versions; VS Code + Python/Jupyter extensions; what Jupyter and `.ipynb` files are; Google Colab (runtimes, GPUs, Drive); terminal basics; Git and GitHub (clone, add, commit, push, branches, pull requests); virtual environments (`venv`), `pip`, `requirements.txt`; API keys, environment variables and `.env` files with `python-dotenv`; **decision guide: when to use Colab vs Jupyter vs VS Code**.
Notebooks: environment check; working with `.env` safely. Excel: setup checklist + troubleshooting table.

### 01-python-basics (weeks 2–3)
Values, variables, types; strings and f-strings; lists, tuples, dicts, sets; conditions; loops; functions; errors and `try/except`; files; modules and imports; classes and objects (light); list comprehensions; reading tracebacks.
Notebooks: basics, collections, functions & errors, mini-project (text-adventure / grade calculator). Excel: Python cheat sheet.

### 02-python-for-data (weeks 4–5)
NumPy arrays, shapes, vectorisation; pandas Series/DataFrame, loading CSV and Excel, cleaning, filtering, groupby, merging; matplotlib charts; reading/writing `.xlsx` with pandas/openpyxl; a mini exploratory data analysis (EDA).
Excel: practice datasets (sales, students) used by the notebooks.

### 03-math-for-ai (week 6) — intuition only
Vectors (arrows / lists of numbers), dot product and similarity; matrices as transformations and as tables of data; probability and distributions, averages and spread; derivatives as "slope", gradients and gradient descent; why these appear in ML and LLMs. Visual matplotlib notebooks; no proofs.

### 04-machine-learning (weeks 7–8)
What ML is; supervised vs unsupervised; features and labels; train/test split; linear regression; logistic regression; decision trees and random forests; k-means; overfitting; metrics (MAE/RMSE, accuracy, precision, recall, F1, confusion matrix, ROC-AUC); cross-validation; pipelines in scikit-learn.

### 05-deep-learning (weeks 9–10)
Neurons, layers, activations; loss; backpropagation intuition; PyTorch tensors, autograd, `nn.Module`, the training loop; MLP on digits; CNNs (convolution, pooling) on 8×8 digits; overfitting tools (dropout, early stopping); GPUs and Colab.

### 06-nlp-and-transformers (weeks 11–12)
Text as data; tokenisation (words, sub-words, BPE); embeddings and similarity; from RNNs to attention; the transformer (self-attention, multi-head, positional encoding) explained visually; Hugging Face `pipeline`, tokenizers, models and the Hub; sentiment analysis and sentence embeddings with tiny models.

### 07-llms-and-genai (week 13)
How LLMs work (next-token prediction, pre-training, instruction tuning, RLHF at a glance); context window, temperature, top-p; using the OpenAI, Anthropic and Gemini APIs (messages, roles, streaming, JSON output); counting tokens and estimating cost; rate limits and errors; running local models with **Ollama**; choosing a model.
Excel: model cost calculator with live formulas.

### 08-prompt-and-context-engineering (week 14)
Prompt anatomy; zero/few-shot; chain-of-thought style reasoning prompts; structured output; system prompts; prompt templates and versioning; context engineering (what goes in the window, ordering, compression, memory); prompt injection and defence; evaluating prompts.
**Analysis of real AI-tool system prompts** (Cursor, Devin, Lovable, Manus, Perplexity, etc.) — our own write-up of the recurring patterns, linking to source 2. No prompt text is copied.

### 09-rag (weeks 15–16)
Why RAG; document loading; chunking strategies; embeddings; vector databases (FAISS, Chroma, pgvector, Qdrant — what and when); similarity search; hybrid search (BM25 + vectors); reranking; prompt assembly with citations; evaluating RAG (retrieval hit rate, faithfulness, answer relevance).
Notebooks build a full RAG pipeline offline with MiniLM embeddings + FAISS + BM25.

### 10-agentic-ai (weeks 17–18)
What an agent is (LLM + tools + loop); tool use / function calling (JSON schemas); the ReAct loop; LangGraph (state graphs, nodes, edges, checkpoints); CrewAI (roles, tasks, crews); multi-agent patterns; memory (short-term, long-term); the **Model Context Protocol (MCP)** — servers, clients, tools/resources; safety and human-in-the-loop.

### 11-ai-automation (week 19)
Automation vs agents; n8n (nodes, triggers, credentials, self-hosting with Docker); example workflows (email triage, lead enrichment, RAG bot over Slack); webhooks; browser-use and computer-use agents (Playwright, browser-use, Anthropic computer use) and when they are worth it.
Includes importable n8n workflow JSON files.

### 12-data-annotation-and-rlhf (week 20)
Why labelled data matters; annotation types (classification, NER, bounding boxes, ranking, preference pairs); tools (Label Studio, Argilla, CVAT, doccano); quality control (guidelines, inter-annotator agreement, Cohen's kappa); RLHF pipeline (SFT → reward model → PPO); DPO and why it is simpler; evaluations (benchmarks, LLM-as-judge, human evals); **AI trainer jobs** — what the work is, platforms, how to get hired.
Excel: annotation guideline template + kappa calculator; AI-trainer job platform tracker.

### 13-fine-tuning (week 21)
When to fine-tune vs prompt vs RAG; datasets for supervised fine-tuning (chat format); full fine-tuning vs parameter-efficient; **LoRA** explained visually; **QLoRA** (4-bit quantisation); Hugging Face `transformers` + `peft` + `trl`; evaluating the result; merging and sharing adapters.
CPU notebook: LoRA on a tiny model; Colab-only notebook: QLoRA on a small instruct model.

### 14-deployment-and-llmops (weeks 22–23)
APIs with FastAPI; containers with Docker; quick UIs with Streamlit and Gradio; serving open models with vLLM; observability with Langfuse (traces, costs, evals); monitoring (latency, errors, drift, cost); guardrails (input/output validation, PII, prompt-injection filters); CI/CD basics; secrets management.

### 15-projects (throughout, capstone weeks 23–24)
Ten projects, beginner → advanced (final list is chosen from source 6 and others in phase 2; see section below). Each has README (what it does, architecture diagram, setup for Colab and local, file-by-file explanation, how to explain it in an interview), pinned `requirements.txt`, `.env.example`, working code, sample data.

### 16-careers (week 24)
Roles: AI trainer / data annotator, prompt engineer, AI engineer, ML engineer, LLMOps; skills matrix by role; portfolio (GitHub, READMEs, demos, writing); resumes and LinkedIn; job boards and AI-trainer platforms; interview prep (Python, ML, LLM/RAG system design, behavioural) with a question bank and answers.

## Projects (15-projects)
Chosen from ideas in source 6 (and sources 1, 4, 5, 7, 8, 9); every project is **reimplemented by us on small offline data** (bundled scikit-learn datasets or synthetic data generated by a script in the project). LLM steps default to a small local Hugging Face model so they run with no API key; Ollama or a hosted API (Claude/OpenAI/Gemini) can be switched in via `.env`.

| # | Folder | Level | What it does | Key tech | Modules |
|---|---|---|---|---|---|
| P1 | `p01-ml-classifier-pipeline` | Beginner | Wine/iris/breast-cancer classifiers in a proper scikit-learn Pipeline with cross-validation and a metrics report | pandas, scikit-learn | 02–04 |
| P2 | `p02-regression-and-segmentation` | Beginner | Disease-progression regression (incl. hand-written gradient descent) + K-means customer segmentation | NumPy, scikit-learn | 03–04 |
| P3 | `p03-digit-recognizer-cnn` | Beginner→Int. | MLP then CNN in PyTorch on 8×8 digits; early stopping, confusion matrix, misclassified examples | PyTorch | 05 |
| P4 | `p04-sentiment-classic-vs-neural` | Intermediate | Same reviews dataset with TF-IDF+LogReg, a small neural net, and a zero-shot transformer; compare | scikit-learn, PyTorch, HF | 05–06 |
| P5 | `p05-rag-course-chatbot` | Intermediate | Chatbot over this curriculum's own notes with citations, follow-up rewriting, simple eval | sentence-transformers, FAISS, Gradio | 07–09 |
| P6 | `p06-response-rating-tool` | Intermediate | Pairwise rating app → HH-RLHF-style preference JSONL → LLM-judge agreement (kappa) | Streamlit, pandas, scikit-learn | 12 |
| P7 | `p07-doc-qa-api` | Int.→Adv. | PDF policy Q&A with hybrid search + page citations, served by FastAPI in Docker with tests | pypdf, BM25, FAISS, FastAPI, Docker, pytest | 09, 14 |
| P8 | `p08-data-analyst-agent-mcp` | Advanced | Agent answering business questions via SQL/pandas/chart tools; same tools exposed as an MCP server | tool calling, SQLite, MCP SDK | 10 |
| P9 | `p09-support-inbox-automation` | Advanced | Email triage: structured extraction, routing, human-approval queue; Python version + n8n version | Pydantic, FastAPI, n8n | 11 |
| P10 | `p10-finetune-lora-dpo` | Advanced | LoRA-SFT a small model to output strict JSON, then DPO on preference pairs; compare to prompting | Transformers, PEFT, TRL | 13 |

How they connect: P5's retriever is reused by P7 and P9; P6's preference data feeds P10's DPO step; P9's emails feed P10's SFT data — one coherent portfolio.

## Root files
README.md (overview + visual roadmap image) · ROADMAP.md (week by week, 24 weeks) · TRAINER-GUIDE.md (how a team of trainers splits and runs the course) · RESOURCES-MASTER.xlsx (every resource: module, link, type, level, free/paid) · SOURCES.md (each source's URL and licence) · requirements.txt · .gitignore · LICENSE.

## How it is built
1. **Phase 1** — clone and study the nine sources; record licences in SOURCES.md; write this plan.
2. **Phase 2** — build modules in parallel (one builder per pair of modules) following the module standard; each module has a `build.py` that regenerates diagrams, notebooks, slides, PDF and Excel.
3. **Verification** — `python tools/check_module.py <module> --run` checks structure, broken image links, secrets, the markdown-before-code rule, the Colab badge, and executes every notebook top to bottom. A module is committed only when it passes.
4. **Phase 3** — projects, root files, RESOURCES-MASTER.xlsx, final full check, pull request.

## Copyright rules followed
Resources are linked and explained in our own words. Nothing is copied in bulk. For source 2 (system prompts of AI tools), no prompt text is copied into this repo — module 08 contains only our own analysis of patterns, with links.
