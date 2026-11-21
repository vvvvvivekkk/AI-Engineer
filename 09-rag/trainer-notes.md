# Module 09 — Trainer notes

This module spans two weeks. Below is a plan for two 2-hour sessions (one per week), plus a one-session version.

## 1. What students should be able to do after the sessions

- Explain why RAG exists and draw the indexing and answering pipelines.
- Load documents and chunk them three ways; explain the trade-offs of chunk size and overlap.
- Embed text, explain cosine similarity, and build and query a FAISS index.
- Run BM25, explain when it beats embeddings, and merge results with RRF.
- Explain bi-encoders vs cross-encoders and why reranking is a second stage.
- Build a prompt that forces citations and a fallback answer.
- Compute hit@k and MRR, check faithfulness, and read failures to decide what to fix.
- Recommend a vector store (FAISS, Chroma, Qdrant, pgvector, Pinecone) for a scenario and justify it.

## 2. Teaching sequence

### Session 1 (2 hours) — from documents to search

| Time | Activity | Materials | Notes for you |
|---|---|---|---|
| 0:00–0:10 | Hook: ask a public chatbot a question about Brightleaf's returns window; it cannot know. Open-book exam analogy | Slides 1–2 | Write "librarian" and "student" on the board; keep referring back |
| 0:10–0:20 | The pipeline, both halves | Slide 3 | Students copy the diagram; exercise 1 later checks it |
| 0:20–0:45 | Loading and chunking | Slides 4–5, notebook 01 | Run the "where each strategy cuts" plot; ask which chunk would answer "how long is the tent warranty?" |
| 0:45–0:55 | Break | | |
| 0:55–1:20 | Embeddings and FAISS | Slides 6–7, notebook 02 sections 1–2 | The similarity heatmap is the "aha" moment: guarantee vs warranty |
| 1:20–1:40 | BM25 and where each wins | Slide 9, notebook 02 sections 3–4 | Let students invent a query that fools embeddings (exact code) and one that fools BM25 (synonym) |
| 1:40–1:55 | RRF + reranking | Slide 10, notebook 02 sections 5–7 | Do the RRF worked example on the board before running code |
| 1:55–2:00 | Homework: exercises 2–5 | | |

### Session 2 (2 hours) — answers, evaluation, and choosing a stack

| Time | Activity | Materials | Notes for you |
|---|---|---|---|
| 0:00–0:10 | Recap quiz (questions below 1–4) | | |
| 0:10–0:30 | Prompt assembly with citations | Slide 11, notebook 03 sections 1–2 | Point out how module 08 ideas reappear: tags, data-not-instructions, fallback sentence |
| 0:30–0:50 | Generation and honest failure; faithfulness checks; extractive baseline | Slide 12, notebook 03 sections 2–3 | If the tiny model hallucinates live, celebrate it — then show the check catching it |
| 0:50–1:00 | Break | | |
| 1:00–1:30 | Evaluation: hit@k, MRR; run the 12-configuration comparison; read failures | Slides 13–14, notebook 03 sections 4–5 | Start the slow cell first, then explain the metrics while it runs |
| 1:30–1:50 | Vector databases: which one and why | Slide 8, `excel/rag-tracker.xlsx` comparison sheet, `code/vector_db_examples.py` | Give three scenarios (student project, company on Postgres, startup with no ops team) and let pairs choose |
| 1:50–2:00 | Failure modes, recap, assign exercises 6–12 | Slides 15–16 | |

**One-session (2 h) version:** pipeline (10 min) → chunking plot only (10) → embeddings heatmap + FAISS (20) → BM25 + RRF + rerank, quick (25) → break → prompt with citations + generation (20) → metrics with the pre-computed results in the Excel tracker instead of running the loop (20) → vector DB choice (10) → recap (5).

## 3. Common student mistakes and how to fix them

1. **Mistake:** embedding questions with a different model from the chunks (or forgetting to normalise). **Fix:** show that scores become meaningless; one `Embedder` object for both, `normalize_embeddings=True`.
2. **Mistake:** forgetting that FAISS returns *positions*, not texts, and mixing up the chunk list order. **Fix:** keep the chunk list and the index built from the same list in the same order; never sort one without the other.
3. **Mistake:** chunks with no context ("It lasts 5 years."). **Fix:** prefix each chunk with `title > section`; show the retrieval difference.
4. **Mistake:** adding raw BM25 scores to cosine scores. **Fix:** explain scales; use RRF (ranks only) or normalise scores first.
5. **Mistake:** concluding "RAG works" from three hand-picked questions. **Fix:** insist on the question set and hit@k/MRR; read failures.
6. **Mistake:** believing the generated answer because it has a citation. **Fix:** run the citation checker (exercise 11) — a real id can be attached to a claim it does not support.
7. **Mistake:** expecting the extractive baseline or the tiny model to say "I don't know". **Fix:** retrieval always returns something; add a relevance threshold (exercise 9).
8. **Mistake:** changing the documents but not re-indexing. **Fix:** exercise 8 — any document change means re-chunk, re-embed, rebuild BM25.
9. **Mistake:** reaching for a heavy vector database on day one. **Fix:** FAISS/Chroma until you need filtering, persistence across services or scale.

## 4. Questions to check understanding (with answers)

1. **Name three problems RAG solves.** — Private data the model never saw; knowledge frozen at training time; hallucination (answers can be grounded and cited).
2. **Why chunk documents instead of embedding them whole?** — A whole-document embedding is a blurry average; small focused chunks match specific questions and fit in the prompt.
3. **What does overlap protect against, and what does it cost?** — Facts split across a chunk boundary; costs more chunks and duplicated storage/tokens.
4. **What does cosine similarity of 0.9 vs 0.1 mean?** — Very similar meaning vs unrelated.
5. **When does BM25 beat embeddings?** — Exact codes, names, numbers, rare jargon (e.g. "TG3-26A").
6. **Why does RRF use ranks instead of scores?** — BM25 and cosine scores are on different scales; ranks are comparable.
7. **Why not use the cross-encoder for all chunks?** — It must run once per (question, chunk) pair at query time — too slow for large collections; use it on the top ~20 only.
8. **The right document is ranked 2nd for one question and 1st for another. What is the MRR?** — (0.5 + 1) / 2 = 0.75.
9. **What is faithfulness, and one cheap way to check it?** — Every claim is supported by the retrieved sources; check content-word overlap and that cited ids are real (then spot-check / LLM-judge).
10. **A company already runs PostgreSQL and has 200,000 chunks. Which store would you suggest first?** — pgvector: vectors next to existing data, SQL filters, no new service.

## 5. Adapting the sessions

**Faster groups**
- Exercises 10–12 (sentence-window chunker, citation checker, LLM-judge evaluation).
- Swap MiniLM for a larger or multilingual embedding model and re-run the evaluation.
- Try `faiss.IndexHNSWFlat` and compare speed and results with the flat index.
- Run the pipeline with an API key or a local Ollama model and compare faithfulness with the tiny generator.
- Install Qdrant or Chroma locally and port `rag_pipeline.py` to use it.

**Slower groups**
- Spend session 1 entirely on chunking and embeddings; do BM25/RRF/rerank as a demo only.
- Use paper cards for RRF: give each pair two ranked lists and let them compute scores by hand.
- In session 2, skip running the evaluation loop; use the numbers already in `excel/rag-tracker.xlsx` and focus on interpreting them.
- Pair weaker students with stronger ones for exercises 6–9.
