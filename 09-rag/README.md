# Module 09 — Retrieval-Augmented Generation (RAG) (weeks 15–16)

**In one line:** build a complete, offline question-answering system over a company's documents — load, chunk, embed, index, search (vector + keyword), rerank, assemble a prompt with citations, generate, and measure how well it works.

## Goals — after this module you can

1. Explain why RAG exists (private data, frozen knowledge, hallucination) and draw the pipeline from memory.
2. Load documents with metadata and compare fixed, overlapping and heading-based chunking.
3. Create embeddings with `sentence-transformers` and search them with a FAISS index.
4. Run BM25 keyword search with `rank_bm25` and explain where it beats embeddings.
5. Merge vector and keyword results with Reciprocal Rank Fusion, and rerank with a cross-encoder.
6. Assemble a prompt that makes the model cite its sources, and generate an answer (offline or via API).
7. Evaluate retrieval with hit rate@k and MRR, and check answers for faithfulness.
8. Choose between FAISS, Chroma, Qdrant, pgvector and Pinecone for a given situation.

## Prerequisites

- Module 06 (embeddings and transformers at a high level), module 07 (LLM APIs), module 08 (prompts, context windows, prompt injection).
- Comfortable with Python functions, lists of dictionaries and pandas DataFrames.
- No API key needed. Everything runs offline; real LLM calls run only if you set a key.

## Time estimate

| Part | Time |
|---|---|
| Read `concepts.md` | 75 min |
| Notebook 01 (loading, chunking) | 45 min |
| Notebook 02 (embeddings, FAISS, BM25, hybrid, rerank) | 75 min |
| Notebook 03 (prompt, generation, evaluation) | 75 min |
| Exercises | 5–6 h |
| **Total** | **about 10–12 h** (two weeks at the course pace) |

## Which tool to use, and why

- **Google Colab** — click the badge at the top of a notebook. The notebook downloads the documents and helper code from GitHub automatically. Free CPU is enough.
- **Jupyter or VS Code locally** — best for this module if you can: the models are cached after the first download, and you can set an API key in `.env` to compare the tiny local generator with a real model.
- **VS Code / terminal** for the scripts: `python code/rag_pipeline.py "your question"`, `python code/evaluate_rag.py`.

## File map

| Path | What it is |
|---|---|
| [concepts.md](concepts.md) | The main lesson: why RAG, loading, chunking, embeddings, vector DBs, BM25, hybrid/RRF, reranking, prompts with citations, generation, evaluation, failure modes |
| `data/docs/` | 15 short Markdown policy documents for the fictional shop **Brightleaf Outdoor Gear** (written for this course) |
| `data/eval_questions.json` | 26 hand-written test questions, each with the source document and key facts |
| `data/eval_results.csv` | Measured retrieval results (written by `code/evaluate_rag.py`) |
| `notebooks/01-loading-and-chunking.ipynb` | Load docs; fixed, overlap and heading chunking; visual of where each cuts; size stats |
| `notebooks/02-embeddings-search-hybrid-rerank.ipynb` | Embeddings and similarity heatmap; FAISS; BM25; RRF; cross-encoder reranking; timing |
| `notebooks/03-generation-and-evaluation.ipynb` | Prompt with citations; generation; extractive baseline; faithfulness checks; hit@k and MRR across 12 configurations |
| `code/rag_pipeline.py` | The whole pipeline in one commented file (used by notebooks 02–03) |
| `code/evaluate_rag.py` | Compares 3 chunkers × 4 retrievers and saves the results |
| `code/vector_db_examples.py` | The same tiny index in FAISS, Chroma, Qdrant, pgvector and Pinecone |
| `slides/09-rag.pptx` | 16-slide teaching deck with speaker notes |
| `pdf/09-rag-handout.pdf` | Handout of `concepts.md` |
| `excel/rag-tracker.xlsx` | Eval results, experiment log, vector-DB comparison |
| [exercises.md](exercises.md) / `solutions/` | 12 exercises, easy to hard, with full solutions |
| [trainer-notes.md](trainer-notes.md) | Session plans, common mistakes, check questions |
| [resources.md](resources.md) | Curated further reading |
| `build.py` | Regenerates images, notebooks, slides, Excel and PDF (`build_notebooks.py` holds notebook content) |

## Models used (all free, all small)

| Job | Model | Size |
|---|---|---|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | ~90 MB, 384-number vectors |
| Reranking | `cross-encoder/ms-marco-MiniLM-L-6-v2` | ~90 MB |
| Generation (offline stand-in) | `HuggingFaceTB/SmolLM2-135M-Instruct` | ~270 MB — weak on purpose; set an API key for real answers |
