"""
build_notebooks.py - cell-by-cell content of the Module 09 notebooks (imported by build.py).
"""

DOC_NAMES = ["01-returns-policy.md", "02-exchanges.md", "03-shipping-and-delivery.md", "04-warranty.md",
             "05-repairs-service.md", "06-payments-and-billing.md", "07-price-match.md", "08-gold-membership.md",
             "09-gear-rental.md", "10-account-and-privacy.md", "11-sustainability.md", "12-stores-and-hours.md",
             "13-customer-support.md", "14-gift-cards.md", "15-safety-recalls.md"]

FIND_DATA_MD = """## Find the data (works locally and in Colab)

The documents live in the module's `data/docs/` folder. Locally the notebook finds them next door. In Colab the cell downloads them (and the helper code) from the course's GitHub repository."""

FIND_DATA_CODE = r'''import sys, urllib.request
from pathlib import Path
RAW = "https://raw.githubusercontent.com/vvvvvivekkk/AI-Engineer/main/09-rag/"
DOC_NAMES = %s
EXTRA = ["data/eval_questions.json", "code/rag_pipeline.py"]

BASE = next((p for p in [Path(".."), Path("09-rag"), Path(".")] if (p / "data" / "docs").exists()), None)
if BASE is None:                                   # not found locally -> download (Colab)
    BASE = Path("09-rag")
    for rel in [f"data/docs/{n}" for n in DOC_NAMES] + EXTRA:
        dest = BASE / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(RAW + rel, dest)
DOCS_DIR = BASE / "data" / "docs"
sys.path.insert(0, str(BASE / "code"))             # so "import rag_pipeline" works
print("documents folder:", DOCS_DIR.resolve(), "|", len(list(DOCS_DIR.glob("*.md"))), "files")''' % repr(DOC_NAMES)

# ==========================================================================
NB01 = [
("md", """# 09.01 — Loading documents and chunking strategies

**RAG** (Retrieval-Augmented Generation) = *find the relevant passages in your documents, then give them to the model with the question.* Before we can find passages, we need to **load** documents and cut them into **chunks** (small passages).

**What you will learn**
- How to load Markdown files with their **metadata** (facts about each file such as its name and title).
- Three chunking strategies: **fixed-size**, **fixed-size with overlap**, and **recursive by headings**.
- How to *see* where each strategy cuts, and compare chunk counts and sizes.

**Our data:** 15 short policy documents for **Brightleaf Outdoor Gear**, a made-up outdoor shop (returns, shipping, warranty, payments ...). Runs offline in under a minute."""),
("md", FIND_DATA_MD),
("code", FIND_DATA_CODE),
("md", """## 1. Load the documents

Each file becomes a small record: its id (file name), its title (the first `# ` heading) and its full text. Keeping the id matters: later it becomes the **citation** that tells users where an answer came from."""),
("code", r'''from dataclasses import dataclass

@dataclass
class Document:
    doc_id: str
    title: str
    text: str

def load_documents(folder):
    docs = []
    for path in sorted(Path(folder).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), path.stem)
        docs.append(Document(path.name, title, text))
    return docs

docs = load_documents(DOCS_DIR)
for d in docs:
    print(f"{d.doc_id:<30} {len(d.text.split()):>4} words | {d.title}")'''),
("md", """Let's read one document in full, so we know what we are cutting up. Notice the `##` section headings — they are the document's natural boundaries."""),
("code", r'''print(docs[3].text)'''),
("md", """## 2. Strategy A — fixed-size chunks

Cut every *N* words, no matter what. Like cutting a sausage into equal slices: easy and predictable, but the knife lands wherever it lands — sometimes in the middle of a sentence or a list."""),
("code", r'''@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    section: str
    text: str

def chunk_fixed(doc, size=80, overlap=0):
    words = doc.text.split()
    step = max(1, size - overlap)              # how far the window moves each time
    chunks = []
    for i, start in enumerate(range(0, len(words), step)):
        piece = words[start:start + size]
        chunks.append(Chunk(f"{doc.doc_id}#{i}", doc.doc_id, doc.title, " ".join(piece)))
        if start + size >= len(words):
            break
    return chunks

fixed = chunk_fixed(docs[3], size=80)
for c in fixed:
    print(c.chunk_id, "|", c.text[:90], "...", c.text[-50:], "\n")'''),
("md", """Look at where chunks start and end: mid-sentence, and the list of warranty periods may be split from its heading. A question like *"how long is the tent warranty?"* might match a chunk that contains "5 years" but not the word "Tents".

## 3. Strategy B — fixed-size with overlap

Each chunk repeats the last 20 words of the previous one. A fact that straddles a boundary now appears whole in at least one chunk. The price: more chunks and some duplicated text."""),
("code", r'''overlap = chunk_fixed(docs[3], size=80, overlap=20)
print(len(fixed), "chunks without overlap ->", len(overlap), "chunks with 20-word overlap\n")
a, b = overlap[0].text.split(), overlap[1].text.split()
print("end of chunk 0  :", " ".join(a[-20:]))
print("start of chunk 1:", " ".join(b[:20]))'''),
("md", """The end of chunk 0 and the start of chunk 1 are the same 20 words — that is the overlap.

## 4. Strategy C — recursive chunking by headings

Respect the document's structure, like cutting a cake along the lines of its slices:
1. Split at `##` headings (one section = one idea).
2. If a section is still too long, split it at blank lines (paragraphs).
3. If a paragraph is still too long, fall back to fixed-size pieces.

Each chunk also gets a **prefix** with the document title and section heading (`Warranty > Warranty periods`), so it makes sense on its own and matches questions that mention its topic."""),
("code", r'''def chunk_by_headings(doc, max_words=120):
    sections, heading, lines = [], doc.title, []
    for line in doc.text.splitlines():
        if line.startswith("## "):
            if lines:
                sections.append((heading, "\n".join(lines).strip()))
            heading, lines = line[3:].strip(), []
        elif not line.startswith("# "):
            lines.append(line)
    if lines:
        sections.append((heading, "\n".join(lines).strip()))
    chunks = []
    for heading, body in sections:
        if not body:
            continue
        pieces = [body] if len(body.split()) <= max_words else [p for p in body.split("\n\n") if p.strip()]
        for piece in pieces:
            words = piece.split()
            subs = [piece] if len(words) <= max_words else [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
            for s in subs:
                chunks.append(Chunk(f"{doc.doc_id}#{len(chunks)}", doc.doc_id, heading, f"{doc.title} > {heading}\n{s.strip()}"))
    return chunks

for c in chunk_by_headings(docs[3]):
    print(f"--- {c.chunk_id}  ({len(c.text.split())} words)\n{c.text}\n")'''),
("md", """Every chunk is now one complete idea with a label. This usually retrieves better — but always check with real questions (notebook 03 does exactly that).

## 5. See the cuts

A picture makes the difference obvious. Each row is one strategy applied to the warranty document. Each coloured block is a chunk (position measured in words). Dashed lines mark where the `##` headings are. Fixed-size chunks ignore the headings; heading chunks line up with them; overlapping chunks are drawn as staggered bars."""),
("code", r'''import matplotlib.pyplot as plt

def heading_positions(doc):
    pos, count = [], 0
    for line in doc.text.splitlines():
        if line.startswith("## "):
            pos.append(count)
        count += len(line.split())
    return pos

def spans_fixed(doc, size, overlap):
    n, step = len(doc.text.split()), size - overlap
    return [(s, min(s + size, n)) for s in range(0, n, step) if s < n and (s == 0 or s + overlap < n)]

def spans_headings(doc):
    words = doc.text.split(); n = len(words)
    bounds = heading_positions(doc) + [n]
    return [(a, b) for a, b in zip([0] + bounds[:-1], bounds) if b > a]

def plot_cuts(doc, ax_title=None):
    rows = [("fixed 80", spans_fixed(doc, 80, 0)), ("fixed 80 + overlap 20", spans_fixed(doc, 80, 20)),
            ("by headings", spans_headings(doc))]
    colors = ["#0F9D9A", "#1B263B", "#E0A458", "#7FB7BE", "#C84C09", "#5A6370"]
    fig, ax = plt.subplots(figsize=(10, 3))
    for r, (name, spans) in enumerate(rows):
        for j, (a, b) in enumerate(spans):
            dy = (j % 2) * 0.18 if "overlap" in name else 0
            ax.barh(r + dy, b - a, left=a, height=0.32, color=colors[j % len(colors)], edgecolor="white")
    for h in heading_positions(doc):
        ax.axvline(h, color="grey", ls="--", lw=1)
    ax.set_yticks(range(len(rows)), [n for n, _ in rows]); ax.invert_yaxis()
    ax.set_xlabel("position in document (words); dashed lines = ## headings")
    ax.set_title(ax_title or f"Where each strategy cuts: {doc.title}")
    plt.tight_layout(); plt.show()

plot_cuts(docs[3])'''),
("md", """## 6. Compare the strategies across all 15 documents

Count chunks and look at their sizes. Many tiny chunks lack context; a few huge chunks give blurry search results."""),
("code", r'''import pandas as pd
strategies = {"fixed-80": lambda d: chunk_fixed(d, 80, 0),
              "fixed-80-overlap-20": lambda d: chunk_fixed(d, 80, 20),
              "headings": lambda d: chunk_by_headings(d, 120)}
all_chunks = {name: [c for d in docs for c in fn(d)] for name, fn in strategies.items()}
stats = pd.DataFrame([{"strategy": n, "chunks": len(cs),
                       "mean words": round(sum(len(c.text.split()) for c in cs) / len(cs), 1),
                       "min words": min(len(c.text.split()) for c in cs),
                       "max words": max(len(c.text.split()) for c in cs),
                       "total words stored": sum(len(c.text.split()) for c in cs)} for n, cs in all_chunks.items()])
stats'''),
("md", """Notice: overlap stores more words in total (duplication); heading chunks vary in size because sections vary. A histogram shows the spread."""),
("code", r'''fig, ax = plt.subplots(figsize=(8, 3.5))
for (name, cs), color in zip(all_chunks.items(), ["#0F9D9A", "#1B263B", "#E0A458"]):
    ax.hist([len(c.text.split()) for c in cs], bins=range(0, 130, 8), alpha=0.6, label=name, color=color)
ax.set_xlabel("words per chunk"); ax.set_ylabel("number of chunks"); ax.legend()
ax.set_title("Chunk size distribution by strategy"); plt.tight_layout(); plt.show()'''),
("md", """## 7. The same code, packaged

These functions live in `code/rag_pipeline.py` so the next notebooks can reuse them. Let's check the packaged version gives the same counts."""),
("code", r'''import rag_pipeline as rp
for name in rp.CHUNKERS:
    print(f"{name:<22}", len(rp.chunk_all(rp.load_documents(DOCS_DIR), name)), "chunks")'''),
("md", """## Recap
- **Load** documents with metadata (id, title) — the id becomes the citation.
- **Fixed-size** chunking is simple but cuts blindly; **overlap** protects facts on boundaries at the cost of duplication; **heading-based (recursive)** chunking keeps one idea per chunk and adds a helpful title prefix.
- There is no universal best chunk size: **measure** with your own questions (notebook 03).

**Try it:** change `size=80` to `size=40` and `size=200`. How do the chunk counts and the cut picture change? Which would you expect to retrieve better, and why?"""),
]

# ==========================================================================
NB02 = [
("md", """# 09.02 — Embeddings, FAISS, BM25, hybrid search and reranking

**What you will learn**
- **Embeddings**: turning text into a **vector** (list of numbers) that captures meaning, and **cosine similarity** to compare them.
- **FAISS**: a library for fast vector search.
- **BM25**: classic keyword search, and where it beats embeddings.
- **Hybrid search** with **Reciprocal Rank Fusion (RRF)**: merging two ranked lists.
- **Reranking** with a **cross-encoder**: a slower, more careful second opinion.

Runs offline in about 2–3 minutes (downloads two small models, ~90 MB each)."""),
("md", FIND_DATA_MD),
("code", FIND_DATA_CODE),
("md", """Load and chunk the documents with the heading strategy from notebook 01 (now imported from `rag_pipeline.py`)."""),
("code", r'''import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import rag_pipeline as rp
docs = rp.load_documents(DOCS_DIR)
chunks = rp.chunk_all(docs, "headings")
print(len(docs), "documents ->", len(chunks), "chunks")
print(chunks[10].chunk_id, "\n" + chunks[10].text)'''),
("md", """## 1. Embeddings: meaning as numbers

`all-MiniLM-L6-v2` turns any text into **384 numbers**. Texts with similar meaning get vectors pointing in similar directions. We **normalise** them (scale to length 1), so the **dot product** (multiply matching numbers, add them up) equals the **cosine similarity**: 1 = same meaning, about 0 = unrelated.

Let's embed five sentences and look at the similarity of every pair."""),
("code", r'''from sentence_transformers import SentenceTransformer
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
sentences = ["How long is the warranty on a tent?",
             "What guarantee do tents come with?",
             "Tents have a five-year warranty.",
             "When is the Hillcrest store open?",
             "Can I pay with PayPal?"]
vecs = embedder.encode(sentences, normalize_embeddings=True)
print("one vector has", vecs.shape[1], "numbers; first five:", np.round(vecs[0][:5], 3))
sim = vecs @ vecs.T                          # all pairwise dot products at once
pd.DataFrame(np.round(sim, 2), index=[s[:32] for s in sentences], columns=range(1, 6))'''),
("md", """Sentences 1–3 score high with each other even though sentence 2 shares almost no words with sentence 1 ("guarantee" vs "warranty"). The store-hours and payment sentences score low. A heatmap makes this easy to see."""),
("code", r'''import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6, 4.5))
im = ax.imshow(sim, cmap="GnBu", vmin=0, vmax=1)
ax.set_xticks(range(5), range(1, 6)); ax.set_yticks(range(5), [s[:34] for s in sentences])
for i in range(5):
    for j in range(5):
        ax.text(j, i, f"{sim[i, j]:.2f}", ha="center", va="center", fontsize=8)
fig.colorbar(im, label="cosine similarity"); ax.set_title("Similar meaning -> similar vectors")
plt.tight_layout(); plt.show()'''),
("md", """## 2. A FAISS index over all chunks

**FAISS** stores vectors and finds the ones closest to a query vector. `IndexFlatIP` compares the query with every vector by inner (dot) product — exact, and plenty fast for thousands of chunks. (For millions you would use an approximate index such as HNSW.) FAISS stores only vectors, so we keep the chunk list alongside to map result positions back to text."""),
("code", r'''import faiss
chunk_vecs = embedder.encode([c.text for c in chunks], normalize_embeddings=True).astype("float32")
index = faiss.IndexFlatIP(chunk_vecs.shape[1])
index.add(chunk_vecs)
print("vectors in index:", index.ntotal)

def dense_search(query, k=5):
    q = embedder.encode([query], normalize_embeddings=True).astype("float32")
    scores, ids = index.search(q, k)
    return [(chunks[i], float(s)) for i, s in zip(ids[0], scores[0])]

for c, s in dense_search("What guarantee do tents come with?", 3):
    print(f"{s:.3f}  {c.chunk_id:<28} {c.section}")'''),
("md", """The warranty chunk comes first even though the question says "guarantee". That is the power of embeddings.

## 3. BM25 keyword search

**BM25** scores chunks by shared words, giving more weight to **rare** words and less to common ones. First we **tokenize** (split text into lowercase words and drop very common "stop words" like *the*, *is*)."""),
("code", r'''from rank_bm25 import BM25Okapi
print(rp.tokenize("My headlamp serial starts with TG3-26A, what should I do?"))
bm25 = BM25Okapi([rp.tokenize(c.text) for c in chunks])

def bm25_search(query, k=5):
    scores = bm25.get_scores(rp.tokenize(query))
    top = np.argsort(-scores)[:k]
    return [(chunks[i], float(scores[i])) for i in top]

for c, s in bm25_search("What guarantee do tents come with?", 3):
    print(f"{s:6.2f}  {c.chunk_id:<28} {c.section}")'''),
("md", """## 4. Where each one wins

Let's compare the top result of each method on three kinds of question:
- a **paraphrase** (different words, same meaning) — embeddings should win;
- an **exact code** (`TG3-26A`) — BM25 should be strong;
- a question that shares a **misleading keyword** with the wrong document."""),
("code", r'''queries = ["What guarantee do tents come with?",
           "My headlamp serial starts with TG3-26A, what should I do?",
           "How long until my money comes back after I send something back?"]
rows = []
for q in queries:
    d = dense_search(q, 3); b = bm25_search(q, 3)
    rows.append({"question": q[:45], "dense top-3": [c.doc_id[:14] for c, _ in d],
                 "bm25 top-3": [c.doc_id[:14] for c, _ in b]})
pd.DataFrame(rows)'''),
("md", """Read the table: which method found the right document first for each question? On real corpora each method has blind spots — which is why we combine them.

## 5. Hybrid search with Reciprocal Rank Fusion (RRF)

BM25 scores (like 7.3) and cosine scores (like 0.62) are on different scales, so we cannot add them. **RRF** uses only **ranks**: each chunk gets `1 / (k + rank)` from each list, and we add them up. `k = 60` is the standard value.

First a tiny worked example with letters instead of chunks."""),
("code", r'''def rrf(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0) + 1 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])

dense_list = ["A", "B", "C", "D"]
bm25_list = ["C", "A", "E", "B"]
for item, score in rrf([dense_list, bm25_list]):
    print(item, round(score, 4))'''),
("md", """A (ranked 1st and 2nd) wins; C (3rd and 1st) is close behind; E and D, found by only one method, come last. Now on real chunks:"""),
("code", r'''def hybrid_search(query, k=5, candidates=20):
    d = [c.chunk_id for c, _ in dense_search(query, candidates)]
    b = [c.chunk_id for c, _ in bm25_search(query, candidates)]
    by_id = {c.chunk_id: c for c in chunks}
    return [(by_id[cid], s) for cid, s in rrf([d, b])[:k]]

for q in queries:
    print("Q:", q)
    for c, s in hybrid_search(q, 3):
        print(f"   {s:.4f}  {c.chunk_id:<28} {c.section}")'''),
("md", """## 6. Reranking with a cross-encoder

The embedding model compares two *separate* vectors (a **bi-encoder**). A **cross-encoder** reads the question and a chunk *together* and outputs one relevance score — more accurate, but slower, so we only use it on the top ~20 candidates. Analogy: HR skims 500 CVs, the manager interviews 20."""),
("code", r'''from sentence_transformers import CrossEncoder
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query, candidates, k=5):
    scores = reranker.predict([(query, c.text) for c in candidates])
    order = np.argsort(-scores)[:k]
    return [(candidates[i], float(scores[i])) for i in order]

q = "How long until my money comes back after I send something back?"
cands = [c for c, _ in hybrid_search(q, k=20)]
print("BEFORE reranking (hybrid order):")
for c in cands[:5]:
    print("   ", c.chunk_id, "|", c.section)
print("AFTER reranking (cross-encoder):")
for c, s in rerank(q, cands, 5):
    print(f"   {s:6.2f}", c.chunk_id, "|", c.section)'''),
("md", """Cross-encoder scores are not probabilities (they can be negative); only their **order** matters. The chunk that actually answers the question ("Refund timing") should now be at or near the top.

## 7. Timing: why two stages?

Embedding search over all chunks is very fast; the cross-encoder is slower per chunk. Measure both."""),
("code", r'''import time
t = time.time(); [dense_search(q, 20) for _ in range(20)]; dense_ms = (time.time() - t) / 20 * 1000
t = time.time(); rerank(q, cands, 5); rerank_ms = (time.time() - t) * 1000
print(f"dense search over {len(chunks)} chunks: {dense_ms:.1f} ms per query")
print(f"cross-encoder on 20 candidates:      {rerank_ms:.1f} ms per query")
print("Running the cross-encoder on EVERY chunk of a million-chunk index would be far too slow - hence two stages.")'''),
("md", """## Recap
- **Embeddings** capture meaning; compare with **cosine similarity** (dot product of normalised vectors).
- **FAISS** finds nearest vectors fast; it stores only vectors, you keep the text.
- **BM25** matches words and loves rare terms like product codes; it misses synonyms.
- **RRF** merges ranked lists using ranks only.
- A **cross-encoder** reranks the top candidates more accurately.

**Try it:** write two questions of your own — one that should favour BM25, one that should favour embeddings — and check with the table in section 4."""),
]

# ==========================================================================
NB03 = [
("md", """# 09.03 — Prompt assembly, generation and evaluation

**What you will learn**
- How to **assemble a RAG prompt** with numbered sources and ask for **citations**.
- How to **generate** an answer (tiny local model offline; real API if you set a key) and compare with an **extractive baseline** (no LLM, just quote the best sentence).
- How to check **faithfulness** (is every claim supported by the sources?).
- How to **evaluate retrieval** with **hit rate@k** and **MRR** on a hand-written question set, and compare chunking strategies and retrievers.

Runs offline in about 4–8 minutes."""),
("md", FIND_DATA_MD),
("code", FIND_DATA_CODE),
("md", """Build the full pipeline from `rag_pipeline.py`: heading chunks, hybrid retrieval (FAISS + BM25 + RRF) and cross-encoder reranking."""),
("code", r'''import warnings, json; warnings.filterwarnings("ignore")
import pandas as pd
import rag_pipeline as rp
rp.DATA_DIR = DOCS_DIR
docs = rp.load_documents(DOCS_DIR)
chunks = rp.chunk_all(docs, "headings")
retriever = rp.HybridRetriever(chunks)
reranker = rp.Reranker()

def retrieve(question, k=4):
    candidates = [c for c, _ in retriever.search(question, k=20)]
    return [c for c, _ in reranker.rerank(question, candidates, k)]

for c in retrieve("Can I bring back boots I wore on a hike?"):
    print(c.chunk_id, "|", c.section)'''),
("md", """## 1. Assemble the prompt

The system prompt tells the model to answer **only** from the sources, cite source ids in brackets, treat sources as data (not instructions), and use an exact fallback sentence when the answer is missing. The user message lists the sources — most relevant first — and puts the question **last**."""),
("code", r'''print("SYSTEM PROMPT:\n" + rp.RAG_SYSTEM + "\n")
question = "How long is the guarantee on a tent?"
top = retrieve(question)
prompt = rp.build_prompt(question, top)
print("USER MESSAGE:\n" + prompt)'''),
("md", """## 2. Generate an answer

Without an API key this uses **SmolLM2-135M-Instruct** — a deliberately tiny model. Expect weak or partly wrong answers: watching the faithfulness check catch them is part of the lesson. With `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` set, a real model answers instead.

We also show the **extractive baseline**: pick the single sentence from the retrieved chunks most similar to the question and quote it with its citation. It cannot hallucinate, but it is not fluent."""),
("code", r'''import os
print("Generator:", "real API" if (os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")) else "tiny local model (offline)")
answer = rp.generate(prompt)
print("\nLLM answer:        ", answer)
print("Extractive answer: ", rp.extractive_answer(question, top))'''),
("md", """## 3. Check faithfulness

Our simple, explainable checks:
- **support** — share of the answer's content words that appear in the retrieved text (low = probably invented);
- **has_citation** / **citations_valid** — did it cite, and are the cited ids chunks we actually provided?
- **key_facts_found** — does the answer contain the fact we expect (from the question set)?

These are cheap smoke tests, not proof. Real projects add an **LLM-as-judge** (a strong model grading with a rubric) and human spot checks."""),
("code", r'''print("LLM answer       :", rp.faithfulness_report(answer, top, key_facts=["5 years"]))
ext = rp.extractive_answer(question, top)
print("Extractive answer:", rp.faithfulness_report(ext, top, key_facts=["5 years"]))'''),
("md", """Now a few more questions, including one the documents **cannot** answer. A good RAG system should say "I don't know" rather than invent something."""),
("code", r'''tests = [("Can I pay with Bitcoin?", ["cryptocurrency"]),
         ("What deposit do you take when I rent a tent?", ["100"]),
         ("Do you sell kayaks?", ["don't know"])]          # not in any document
rows = []
for q, facts in tests:
    ctx = retrieve(q)
    llm = rp.generate(rp.build_prompt(q, ctx))
    ext = rp.extractive_answer(q, ctx)
    rows.append({"question": q, "llm_answer": llm[:120], **{f"llm_{k}": v for k, v in rp.faithfulness_report(llm, ctx, facts).items()},
                 "extractive": ext[:90]})
pd.DataFrame(rows)'''),
("md", """**Read the table.** Where does the tiny model invent things or skip citations? Notice the extractive baseline happily quotes *something* for the kayak question — retrieval always returns chunks, even when none is relevant. Real systems add a **relevance threshold** (if the best reranker score is too low, answer "I don't know") — exercise 9 asks you to build one.

## 4. Evaluate retrieval on the question set

`data/eval_questions.json` holds 26 hand-written questions, each with the document that answers it. They are phrased the way customers talk ("guarantee", "send back"), not copied from the documents."""),
("code", r'''questions = json.loads((BASE / "data" / "eval_questions.json").read_text(encoding="utf-8"))
print(len(questions), "questions, e.g.:")
pd.DataFrame(questions)[["id", "question", "source"]].head(6)'''),
("md", """Two metrics:
- **hit@k** — 1 if the correct document is in the top *k* retrieved chunks, else 0; averaged over questions.
- **MRR** (mean reciprocal rank) — 1/rank of the first correct result (1.0 if first, 0.5 if second ...), averaged.

We compare **3 chunking strategies × 4 retrievers**. This is the slowest cell (a couple of minutes)."""),
("code", r'''import time
def ranked_doc_ids(method, idx, q):
    if method == "bm25":
        return [c.doc_id for c, _ in idx.sparse.search(q, 10)]
    if method == "dense":
        return [c.doc_id for c, _ in idx.dense.search(q, 10)]
    if method == "hybrid":
        return [c.doc_id for c, _ in idx.search(q, k=10)]
    cands = [c for c, _ in idx.search(q, k=20)]
    return [c.doc_id for c, _ in reranker.rerank(q, cands, 10)]

embedder = rp.Embedder()
results, per_question = [], []
start = time.time()
for strategy in rp.CHUNKERS:
    cs = rp.chunk_all(docs, strategy)
    idx = rp.HybridRetriever(cs, embedder)
    for method in ["bm25", "dense", "hybrid", "hybrid+rerank"]:
        h1 = h3 = h5 = rr = 0
        for q in questions:
            ids = ranked_doc_ids(method, idx, q["question"])
            h1 += rp.hit_at_k(ids, q["source"], 1); h3 += rp.hit_at_k(ids, q["source"], 3)
            h5 += rp.hit_at_k(ids, q["source"], 5); rr += rp.reciprocal_rank(ids, q["source"])
            per_question.append({"chunking": strategy, "retriever": method, "id": q["id"],
                                 "question": q["question"], "gold": q["source"], "top1": ids[0]})
        n = len(questions)
        results.append({"chunking": strategy, "retriever": method, "chunks": len(cs),
                        "hit@1": round(h1 / n, 3), "hit@3": round(h3 / n, 3), "hit@5": round(h5 / n, 3), "MRR": round(rr / n, 3)})
print(f"done in {time.time() - start:.0f}s")
res = pd.DataFrame(results)
res'''),
("md", """Charts make the comparison easier to discuss. Because our corpus is small, almost everything scores well at hit@5 — the interesting differences are at **hit@1** and **MRR**."""),
("code", r'''import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
for ax, metric in zip(axes, ["hit@1", "MRR"]):
    res.pivot(index="retriever", columns="chunking", values=metric).loc[["bm25", "dense", "hybrid", "hybrid+rerank"]] \
       .plot.bar(ax=ax, rot=0, color=["#0F9D9A", "#1B263B", "#E0A458"])
    ax.set_title(metric); ax.set_ylim(0.5, 1.02); ax.legend(fontsize=8, loc="lower right")
plt.suptitle("Retrieval quality on 26 hand-written questions"); plt.tight_layout(); plt.show()'''),
("md", """**How to read it (and be honest about it):**
- With 26 questions, one question = about 4 percentage points. Small differences may be noise.
- If dense beats hybrid on your data, believe your data — hybrid helps most when users type exact codes, names or jargon.
- The reranker usually lifts hit@1 and MRR: it reorders candidates the fast retrievers already found.

## 5. Read the failures

Numbers tell you *how often*; failures tell you *why*. List questions where the best configuration still put the wrong document first."""),
("code", r'''pq = pd.DataFrame(per_question)
best = res.sort_values(["MRR", "hit@1"], ascending=False).iloc[0]
print("best configuration:", best["chunking"], "+", best["retriever"])
fails = pq[(pq.chunking == best["chunking"]) & (pq.retriever == best["retriever"]) & (pq.top1 != pq.gold)]
fails[["id", "question", "gold", "top1"]] if len(fails) else "No rank-1 failures for the best configuration."'''),
("md", """## 6. Save the results

Write the table to CSV — the module's `excel/rag-tracker.xlsx` has a sheet with the same columns so you can log every experiment (chunk size, overlap, model, k) over time."""),
("code", r'''res.to_csv("rag_eval_results.csv", index=False)
print("saved rag_eval_results.csv")'''),
("md", """## Recap
- A RAG prompt = system rules (only from sources, cite ids, fallback) + numbered sources + question last.
- Tiny generators hallucinate; **faithfulness checks** and an **extractive baseline** keep you honest.
- Evaluate retrieval separately with **hit@k** and **MRR** on a hand-written question set; compare chunkers and retrievers; **read the failures**.
- Retrieval always returns *something* — add a **relevance threshold** so the system can say "I don't know".

**Try it:** add five questions of your own to the question set (including one with an exact code or number) and rerun section 4. Does the ranking of methods change?"""),
]
