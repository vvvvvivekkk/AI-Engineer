# Module 09 — Solutions

Runnable code for exercises 2–12 is in [solutions.py](solutions.py). Run from the module folder: `python solutions/solutions.py 4 5` (or no numbers for all; several minutes on a CPU). Numbers below come from our runs; small differences on your machine are normal.

---

## Exercise 1 — Draw the pipeline
**Indexing (offline):** Documents (files) → Load (text + metadata) → Chunk (passages) → Embed (one vector per chunk) → Index (FAISS vectors + BM25 word statistics, with chunk ids).
**Answering (online):** Question (text) → Embed question (vector) → Retrieve (top ~20 chunks from vector + keyword search, merged with RRF) → Rerank (top 3–5 by cross-encoder) → Assemble prompt (rules + sources with ids + question) → Generate (answer with citations) → Check (faithfulness, citations valid) → Show to user with source links.

## Exercise 2 — Count and inspect chunks
| Strategy | Chunks | Words (min–max) | Shortest chunk |
|---|---|---|---|
| fixed-80 | 36 | 1–80 | the 1-word tail of the rental document ("price.") |
| fixed-80-overlap-20 | 42 | 22–80 | the tail of the Gold membership document |
| headings | 73 | 13–66 | "Stores and Opening Hours > ... Brightleaf has three stores." |

The 1-word fixed chunk is useless on its own — a classic fixed-size artefact. Overlap avoids tiny tails because each window starts 60 words after the previous one. The shortest heading chunk is short but still meaningful thanks to its title prefix. A common fix for tiny tails: merge any final chunk under ~20 words into the previous one.

## Exercise 3 — Similarity table
Our run: the two "return" sentences scored 0.71, the two "delivery" sentences 0.42, and every pair with the penguin sentence scored about 0.1 or less. Paraphrase pairs score highest with each other even with almost no shared words. Note that 0.42 is "related", not "identical" — similarity is a scale, not a yes/no.

## Exercise 4 — RRF by hand
k = 60.
- D1: 1/(60+2) + 1/(60+1) = 0.01613 + 0.01639 = **0.03252**
- D3: 1/(60+1) + 1/(60+3) = 0.01639 + 0.01587 = **0.03227**
- D9: 1/62 = 0.01613 · D7: 1/63 = 0.01587 · D2: 1/64 = 0.01563 · D4: 1/64 = 0.01563

D1 wins because both methods rank it near the top; D3 is a close second. Documents found by only one method trail behind.

## Exercise 5 — Hit@k and MRR by hand
Ranks: 1, 3, none, 2.
- hit@1 = 1/4 = 0.25 · hit@3 = 3/4 = 0.75 · hit@5 = 3/4 = 0.75
- MRR = (1/1 + 1/3 + 0 + 1/2) / 4 = 1.833 / 4 = **0.458**

See `metrics_from_ranks()` for the general function.

## Exercise 6 — Chunk size sweep (dense retrieval, fixed-size, no overlap)
| Size (words) | Chunks | hit@1 | MRR |
|---|---|---|---|
| 30 | 83 | 0.885 | 0.933 |
| 60 | 44 | 0.885 | 0.933 |
| 120 | 27 | 0.923 | 0.962 |
| 250 | 15 | 0.962 | 0.981 |

**Surprise — and an important lesson about metrics.** Bigger chunks scored *better* here. Why? Our documents are only 100–200 words long, so a 250-word chunk is the *whole document*, and our metric only checks whether the right **document** was found. It does not check whether the retrieved text is focused. In real use, whole-document chunks fill the prompt with irrelevant text, cost more tokens and bury the answer. To see the downside, measure at the **passage** level (did we retrieve the exact section with the answer?) or measure **answer quality**. Very small chunks hurt in a different way: they lose context ("It lasts 5 years" — what does?). Always ask what your metric can and cannot see.

## Exercise 7 — Metadata filtering
Question: *"Is there a refund if I cancel?"* (ambiguous: cancel what?)
- No filter → top result: Gold membership (membership fee refund).
- `category="orders"` (user is on an order page) → price match and returns policy.
- `category="membership"` (user is on the Gold page) → Gold membership.

The application knows *where* the user is asking from; a metadata filter turns that knowledge into better retrieval, and each search compares the question with fewer vectors. Real vector databases (Chroma, Qdrant, pgvector, Pinecone) all support filters like this.

## Exercise 8 — Add a new document
Both new questions retrieved `16-kayak-rentals.md` at ranks 1–3. You must rebuild **chunks, embeddings, the FAISS index and BM25**. BM25 needs rebuilding even for documents you did not change, because word rarity (how many chunks contain each word) changes when the collection changes. In production, vector databases let you add or update single documents without rebuilding everything; BM25-style indexes in search engines update their statistics automatically.

## Exercise 9 — Relevance threshold
Cross-encoder scores (best chunk per question): answerable questions had a minimum of about −9.2 and a median of about +3.2; our five unanswerable questions scored −11.2, −11.0, −10.2, −7.3 and −6.4.
- A threshold of **−10** keeps all 26 answerable questions and rejects 3 of 5 unanswerable ones.
- Raising it towards **−6** rejects all 5 unanswerable questions but starts rejecting real questions with low scores.

That is the classic **precision/recall trade-off**: decide which mistake is worse for your users (a wrong answer vs an unnecessary "I don't know"), choose the threshold on one question set, and confirm it on a different one. `solutions.py` prints the full trade-off table.

## Exercise 10 — Sentence-window chunking
`chunk_sentence_window()` makes one chunk per sentence plus one neighbour on each side, prefixed with `title > section`. It produces many more, smaller, overlapping chunks. In our run it retrieved about as well as heading chunks with hybrid + rerank, and a little worse with dense search alone (very small chunks carry less context). Its real advantage is **precision**: the text you pass to the model is tightly focused. A popular variant searches small windows but sends the larger parent section to the model ("small-to-big" retrieval). Run `python solutions/solutions.py 10` to see the numbers on your machine.

## Exercise 11 — Citation checker
`check_citations()` keeps citations attached to their sentence, then checks (a) the id exists among the provided chunks and (b) at least half of the sentence's content words appear in the cited chunk. Results on the three test answers:
1. Correct answer citing the warranty-periods chunk → exists ✔, supported ✔.
2. Citing `04-warranty.md#99` → exists ✘ (invented id).
3. "Brightleaf ships worldwide with free express delivery" citing the warranty chunk → exists ✔, **supported ✘** — a real citation attached to a claim it does not support. This is the case students most often miss.

## Exercise 12 — End-to-end evaluation with a judge
`exercise_12()` builds a DataFrame with, per question: whether retrieval found the gold document, the answer, support score, citation flags, key-fact match and a judge score (LLM if an API key is set, otherwise a clearly-labelled rule-based stand-in). Our offline run: retrieval found the gold document for **8 of 8** questions, but key facts appeared in only **25%** of the tiny generator's answers, none had citations, and one invented a "3 months" answer. Notice also that the rule-based judge gave high scores to answers that simply echoed source text — a cheap judge can be fooled, which is why real projects use a strong LLM judge plus human spot checks. **Conclusion to write:** retrieval is already good, so improve **generation** first — a stronger model (API or a 3–8B model via Ollama), a clearer prompt with a citation example, or fall back to the extractive answer when the faithfulness check fails. With an API key, rerun and compare: the judge scores and key-fact rate rise sharply while the retrieval column stays the same — proof that the bottleneck was the generator.
