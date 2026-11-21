# Module 09 — Exercises

Graded from easy (1) to hard (12). Solutions: [solutions/solutions.md](solutions/solutions.md) and runnable code in [solutions/solutions.py](solutions/solutions.py). Everything runs offline. Import the pipeline with `sys.path.insert(0, "code"); import rag_pipeline as rp` from the module folder.

---

### Exercise 1 — Draw the pipeline (easy, 10 min)
Without looking, draw the RAG pipeline in two halves (indexing and answering) with at least 8 boxes. Then write one sentence for each box saying what goes in and what comes out.

### Exercise 2 — Count and inspect chunks (easy, 15 min)
Using `rp.load_documents()` and `rp.chunk_all()`, print for each of the three strategies: number of chunks, shortest and longest chunk (in words), and the full text of the shortest chunk. Is the shortest chunk useful on its own?

### Exercise 3 — Your own similarity table (easy, 20 min)
Write five sentences: two pairs that mean the same thing with different words, and one unrelated sentence. Embed them with MiniLM and print the cosine similarity matrix. Do the pairs score highest with each other?

### Exercise 4 — RRF by hand (easy–medium, 15 min)
Dense ranking: `[D3, D1, D7, D2]`. BM25 ranking: `[D1, D9, D3, D4]`. With k = 60, compute the RRF score of every document by hand (show the fractions), then check with code. Which document wins and why?

### Exercise 5 — Hit@k and MRR by hand (medium, 20 min)
Four questions; the rank of the correct document was: 1, 3, not found (in top 5), 2. Compute hit@1, hit@3, hit@5 and MRR by hand. Then write a function that does it for any list of ranks.

### Exercise 6 — Chunk size sweep (medium, 40 min)
Using `rp.chunk_fixed`, try chunk sizes 30, 60, 120 and 250 words (no overlap). For each, build a `rp.DenseIndex` and measure hit@1 and MRR on `data/eval_questions.json`. Plot MRR against chunk size. Which size is best here, and why might very small and very large chunks both hurt?

### Exercise 7 — Metadata filtering (medium, 40 min)
Add a `category` to each document (e.g. "orders" for returns/exchanges/shipping/payments, "membership" for gold/rental/gift cards, "company" for the rest). Write `search(question, category=None, k=4)` that retrieves only chunks from documents in that category. Show one question where filtering fixes a wrong result or makes the search faster.

### Exercise 8 — Add a new document (medium, 30 min)
Write a new policy document `16-kayak-rentals.md` (your own made-up facts, with `##` sections). Add it to `data/docs/` (or a copy of the folder), rebuild the pipeline, and add two questions about it to a copy of the question set. Do the new questions retrieve the new document at rank 1? What did you have to rebuild, and why?

### Exercise 9 — "I don't know" with a relevance threshold (medium–hard, 45 min)
Retrieval always returns something. Using the cross-encoder scores from `rp.Reranker().rerank()`, find a threshold so that answerable questions from the question set pass, and at least 4 unanswerable questions you write ("Do you sell kayaks?", "What is the CEO's name?") are rejected. Report how many of each are classified correctly at your chosen threshold.

### Exercise 10 — Sentence-window chunking (hard, 60 min)
Implement a new chunker: split each document into sentences; each chunk is one sentence plus one sentence before and after it (a "window"), prefixed with `title > section`. Add it to `rp.CHUNKERS` and compare it with the three existing strategies using the evaluation loop from notebook 03 (dense and hybrid+rerank are enough). Report hit@1 and MRR.

### Exercise 11 — Citation checker (hard, 45 min)
Write `check_citations(answer, chunks)` that returns, for each sentence of an answer: the citations it contains, whether each cited id exists in the provided chunks, and whether at least half of the sentence's content words appear in the cited chunk's text. Test it on three hand-written answers: one fully correct, one citing a non-existent id, one citing a real id for a claim that is not in that chunk.

### Exercise 12 — End-to-end evaluation with a judge (hard, 90 min)
Build `evaluate_answers(questions)` that, for each question: retrieves 4 chunks, generates an answer (local model or API), and scores it with (a) key-fact match, (b) `rp.faithfulness_report`, and (c) an **LLM-as-judge** prompt that grades faithfulness 1–5 (use `rp.generate` with your own judge system prompt; when no API key is set, fall back to a rule-based judge and say so). Run it on 8 questions, put the results in a DataFrame, and write five lines on what you would improve first: retrieval or generation? Why?
