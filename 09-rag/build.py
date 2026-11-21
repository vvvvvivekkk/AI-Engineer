"""
build.py - regenerate Module 09's images, notebooks, slides, Excel tracker and PDF handout.

    python 09-rag/build.py

The evaluation numbers in the Excel tracker come from data/eval_results.csv,
produced by `python 09-rag/code/evaluate_rag.py` (run it again after changing the pipeline).
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "code"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook  # noqa: E402

import csv  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

IMG = HERE / "images"
NAME = HERE.name

MERMAID = {
    "rag_pipeline": """
flowchart LR
  subgraph Indexing [Indexing - offline]
    D[Documents] --> L[Load + metadata] --> C[Chunk] --> E[Embed] --> I[(Vector index + BM25)]
  end
  subgraph Query [Answering - every question]
    Q[Question] --> R[Retrieve top 20] --> RR[Rerank to top 4] --> P[Prompt with sources] --> G[LLM answer with citations]
  end
  I --> R
""",
    "hybrid_rerank": """
flowchart LR
  Q[Question] --> V[Vector search: meaning]
  Q --> B[BM25: keywords]
  V --> F[Reciprocal rank fusion]
  B --> F
  F --> X[Cross-encoder reranker]
  X --> T[Top 3-5 chunks]
""",
    "vector_db_choice": """
flowchart TD
  S{Learning or prototyping?} -- yes --> F[FAISS or Chroma]
  S -- no --> P{Already run PostgreSQL?}
  P -- yes --> PG[pgvector]
  P -- no --> O{Want zero ops, OK with cloud?}
  O -- yes --> PC[Managed service e.g. Pinecone]
  O -- no --> Q[Self-host Qdrant / Weaviate / Milvus]
""",
    "rag_evaluation": """
flowchart LR
  T[Test set: question + source doc] --> R[Retrieval]
  R --> M1[hit rate at k, MRR]
  R --> G[Generation]
  G --> M2[Faithfulness: supported by sources?]
  G --> M3[Correctness: key facts, relevance]
  G --> M4[Citations valid?]
""",
}


def chunking_figure():
    """Where three chunking strategies cut the warranty document (real data from data/docs)."""
    import rag_pipeline as rp
    doc = [d for d in rp.load_documents(HERE / "data" / "docs") if d.doc_id.startswith("04")][0]
    n = len(doc.text.split())
    heads, count = [], 0
    for line in doc.text.splitlines():
        if line.startswith("## "):
            heads.append(count)
        count += len(line.split())
    rows = [("fixed 80 words", [(s, min(s + 80, n)) for s in range(0, n, 80)]),
            ("fixed 80 + 20 overlap", [(s, min(s + 80, n)) for s in range(0, n, 60) if s == 0 or s + 20 < n]),
            ("recursive by headings", [(a, b) for a, b in zip([0] + heads, heads + [n]) if b > a])]
    colors = ["#0F9D9A", "#1B263B", "#E0A458", "#7FB7BE", "#C84C09", "#5A6370"]
    fig, ax = plt.subplots(figsize=(10, 3))
    for r, (name, spans) in enumerate(rows):
        for j, (a, b) in enumerate(spans):
            dy = (j % 2) * 0.18 if "overlap" in name else 0
            ax.barh(r + dy, b - a, left=a, height=0.32, color=colors[j % len(colors)], edgecolor="white")
    for h in heads:
        ax.axvline(h, color="grey", ls="--", lw=1)
    ax.set_yticks(range(3), [r[0] for r in rows]); ax.invert_yaxis()
    ax.set_xlabel("position in the Warranty document (words); dashed lines = ## section headings")
    ax.set_title("Fixed-size chunks ignore structure; heading chunks follow it")
    plt.tight_layout(); fig.savefig(IMG / "chunking_strategies.png", dpi=150); plt.close(fig)


def eval_figure(rows):
    if not rows:
        return
    import numpy as np
    methods = ["bm25", "dense", "hybrid", "hybrid+rerank"]
    strategies = list(dict.fromkeys(r["chunking"] for r in rows))
    fig, ax = plt.subplots(figsize=(9, 3.5))
    w = 0.25
    for i, s in enumerate(strategies):
        vals = [float(next(r["MRR"] for r in rows if r["chunking"] == s and r["retriever"] == m)) for m in methods]
        ax.bar(np.arange(4) + i * w, vals, w, label=s, color=["#0F9D9A", "#1B263B", "#E0A458"][i])
    ax.set_xticks(np.arange(4) + w, methods); ax.set_ylim(0.6, 1.02); ax.set_ylabel("MRR")
    ax.set_title("Our measured retrieval quality (26 questions)"); ax.legend(fontsize=8)
    plt.tight_layout(); fig.savefig(IMG / "eval_results.png", dpi=150); plt.close(fig)


def deck():
    I = lambda n: str(IMG / f"{n}.png")
    return {
        "title": "Module 09 - Retrieval-Augmented Generation (RAG)",
        "subtitle": "Python to Pro AI Engineer curriculum",
        "slides": [
            {"title": "The problem RAG solves",
             "bullets": ["LLMs don't know your private documents", "Their knowledge is frozen at training time",
                         "They hallucinate confidently", "Pasting everything in is slow, costly, distracting",
                         "RAG: find the right passages, then answer from them with citations"],
             "notes": "Ask the class: could ChatGPT answer 'what is Brightleaf's returns window?' No - it has never seen the document. RAG fetches the passage and puts it into the prompt."},
            {"title": "Analogy: the open-book exam",
             "bullets": ["Closed book = plain LLM (memory only)", "Open book = RAG (look it up)",
                         "Librarian = retriever (finds the pages)", "Student = generator (writes the answer)",
                         "Page numbers = citations"],
             "notes": "Most of the engineering effort in RAG goes into the librarian: finding the right page quickly. Keep coming back to this analogy."},
            {"title": "The pipeline", "image": I("rag_pipeline"),
             "bullets": ["Indexing (offline): load, chunk, embed, store", "Answering (online): retrieve, rerank, prompt, generate"],
             "notes": "Walk through both halves. Indexing happens once and whenever documents change. Answering happens for every question."},
            {"title": "Loading documents",
             "bullets": ["Turn PDFs, web pages, docs into clean text", "Keep metadata: source, title, date, access rights",
                         "Preserve structure (headings, lists, tables)", "Our corpus: 15 Markdown policy docs"],
             "notes": "Metadata is what lets you cite sources, prefer fresh documents and enforce who may see what. Show the data/docs folder."},
            {"title": "Chunking strategies", "image": I("chunking_strategies"),
             "bullets": ["Fixed-size: simple, cuts blindly", "Overlap: protects facts on boundaries",
                         "Recursive by headings: one idea per chunk", "Prefix chunks with title > section"],
             "notes": "Index-card analogy: one card per idea. Point at the picture: fixed chunks cross the dashed heading lines, heading chunks follow them."},
            {"title": "Embeddings",
             "bullets": ["Text -> 384 numbers (MiniLM)", "Similar meaning -> similar direction",
                         "Cosine similarity: 1 = same meaning", "Same model for chunks and questions"],
             "code": 'from sentence_transformers import SentenceTransformer\nm = SentenceTransformer(\n  "sentence-transformers/all-MiniLM-L6-v2")\nv = m.encode(["What guarantee do tents have?"],\n             normalize_embeddings=True)\nprint(v.shape)   # (1, 384)',
             "notes": "Map-of-meaning analogy: guarantee and warranty land near each other. Show the similarity heatmap from notebook 02."},
            {"title": "Vector search and FAISS",
             "bullets": ["Nearest-neighbour search over vectors", "Exact (flat) for thousands of chunks",
                         "Approximate (HNSW, IVF) for millions", "FAISS stores vectors only - you keep the text"],
             "code": "import faiss\nindex = faiss.IndexFlatIP(384)\nindex.add(chunk_vecs)\nscores, ids = index.search(q_vec, 5)",
             "notes": "IndexFlatIP compares the question with every chunk by dot product. HNSW is like taking motorways then local roads to skip most comparisons."},
            {"title": "Vector databases: which one?", "image": I("vector_db_choice"),
             "bullets": ["FAISS / Chroma: learning, prototypes", "pgvector: you already use Postgres",
                         "Qdrant / Weaviate / Milvus: self-hosted scale", "Pinecone: managed cloud, zero ops"],
             "notes": "Open the comparison sheet in excel/rag-tracker.xlsx. Stress that features and prices change, so check official pages. Start simple."},
            {"title": "BM25 keyword search",
             "bullets": ["Ranks by shared words, rare words count more", "Great for codes, names, numbers (TG3-26A)",
                         "Misses synonyms (guarantee vs warranty)", "No model needed, easy to explain"],
             "notes": "Book-index analogy: exact and fast, but only finds the words you look up."},
            {"title": "Hybrid search + reranking", "image": I("hybrid_rerank"),
             "bullets": ["Run both searches", "RRF: score = sum of 1/(60 + rank)", "Cross-encoder reranks the top 20",
                         "Keep 3-5 chunks for the prompt"],
             "notes": "Two-judges analogy for RRF: compare placings, not raw scores. Hiring analogy for reranking: HR skims, the manager interviews the shortlist."},
            {"title": "Prompt assembly with citations",
             "bullets": ["System: answer only from sources, cite ids, fallback sentence", "Sources are data, not instructions",
                         "Most relevant first, question last", "Your code can verify every citation"],
             "code": '<sources>\n<source id="04-warranty.md#1">\nWarranty > Warranty periods\n- Tents ...: 5 years\n</source>\n</sources>\n\nQuestion: How long is the\nguarantee on a tent?',
             "notes": "This is module 08 in action. The exact fallback sentence lets your code detect 'I don't know'. Citations make answers checkable."},
            {"title": "Generation - and honest failure",
             "bullets": ["Real API if a key is set", "Offline: tiny SmolLM2-135M (weak on purpose)",
                         "It once said '3 months' when the source said 5 years", "Faithfulness check caught it",
                         "Extractive baseline: quote the best sentence"],
             "notes": "Show the hallucination example live if it happens. The lesson: never trust generation without checks; a stronger model reduces but does not remove the risk."},
            {"title": "Evaluating RAG", "image": I("rag_evaluation"),
             "bullets": ["Retrieval: hit rate@k, MRR", "Generation: faithfulness, correctness, citations",
                         "LLM-as-judge + human spot checks", "Test set: 26 hand-written questions"],
             "notes": "Define hit@k and MRR with a quick example on the board: right document 2nd -> reciprocal rank 0.5."},
            {"title": "Our results", "image": I("eval_results"),
             "bullets": ["Dense alone already strong on paraphrased questions", "Plain hybrid slightly worse at rank 1 here",
                         "Heading chunks + hybrid + rerank: best", "Small test set: 1 question = 4 points"],
             "notes": "Be honest with students: hybrid is not automatically better. It helps with exact codes and jargon. Measure on your own questions."},
            {"title": "Common failures and fixes",
             "bullets": ["Right doc never retrieved -> better chunks, hybrid", "Answer invents facts -> faithfulness check, refuse",
                         "Codes not found -> add BM25", "Stale answers -> re-index, use dates",
                         "Retrieval always returns something -> relevance threshold"],
             "notes": "Go through the table from concepts.md section 12. Ask students which failure they think is most common in real projects (usually retrieval)."},
            {"title": "Recap and exercises",
             "bullets": ["Load -> chunk -> embed -> index -> retrieve -> rerank -> prompt -> generate -> evaluate",
                         "Measure, don't assume", "Exercises 1-12 in exercises.md", "Next: agents that use retrieval as a tool"],
             "notes": "Assign exercises 1-4 in class. Exercises 9-12 build a relevance threshold, a new chunker and an LLM-judge."},
        ],
    }


def tracker(rows):
    eval_sheet = [["chunking", "retriever", "num_chunks", "avg_chunk_words", "hit@1", "hit@3", "hit@5", "MRR",
                   "questions", "notes"]]
    for r in rows:
        eval_sheet.append([r["chunking"], r["retriever"], int(r["num_chunks"]), float(r["avg_chunk_words"]),
                           float(r["hit@1"]), float(r["hit@3"]), float(r["hit@5"]), float(r["MRR"]),
                           int(r["questions"]), "measured by code/evaluate_rag.py"])
    n = len(eval_sheet)
    eval_sheet.append(["BEST MRR", "", "", "", "", "", "", f"=MAX(H2:H{n})", "", ""])
    log = [["date", "experiment", "chunker", "chunk_size", "overlap", "embedding_model", "retriever", "k",
            "reranker", "hit@1", "hit@5", "MRR", "faithfulness (0-1)", "what changed / conclusion"],
           ["2026-11-21", "baseline", "headings", 120, 0, "all-MiniLM-L6-v2", "hybrid (RRF k=60)", 4,
            "ms-marco-MiniLM-L-6-v2", "", "", "", "", "copy numbers from the Eval results sheet"]]
    log += [["", "", "", "", "", "", "", "", "", "", "", "", "", ""] for _ in range(8)]
    vdb = [["store", "type", "hosting", "metadata filtering", "hybrid (keyword+vector)", "scale", "best for", "watch out", "official link"],
           ["FAISS", "library", "in your process", "no (do it yourself)", "no (combine with BM25 yourself)", "millions in RAM; billions with care",
            "prototypes, notebooks, research, batch jobs", "not a database: persistence, updates and filters are on you",
            "https://github.com/facebookresearch/faiss"],
           ["Chroma", "embedded / server DB", "in process or server, open source", "yes", "check current docs", "small to medium",
            "first real vector DB, demos, small apps", "built for modest scale", "https://github.com/chroma-core/chroma"],
           ["Qdrant", "vector DB server", "Docker / self-host / cloud, open source", "yes (rich payload filters)", "yes", "large",
            "production apps needing filters and scale", "one more service to run", "https://github.com/qdrant/qdrant"],
           ["pgvector", "PostgreSQL extension", "wherever your Postgres runs", "yes (plain SQL WHERE)", "yes (with Postgres full-text search)", "medium to large",
            "teams already on Postgres; vectors next to business data", "index tuning at very large scale", "https://github.com/pgvector/pgvector"],
           ["Pinecone", "managed cloud DB", "SaaS (paid tiers)", "yes", "yes", "very large",
            "zero-ops production", "cost, lock-in, data leaves your servers", "https://www.pinecone.io/"],
           ["Weaviate", "vector DB server", "self-host / cloud, open source", "yes", "yes", "large",
            "hybrid search out of the box", "more concepts to learn", "https://weaviate.io/"],
           ["Milvus", "distributed vector DB", "self-host / cloud, open source", "yes", "yes", "very large (billions)",
            "massive scale", "heavier to operate", "https://github.com/milvus-io/milvus"],
           ["Note", "", "", "", "", "", "Features and prices change: check each official page (as of late 2026).", "", ""]]
    guide = [["sheet", "how to use it"],
             ["Eval results", "Numbers measured by code/evaluate_rag.py on data/eval_questions.json (26 questions). Rerun after changes."],
             ["Experiment log", "One row per experiment. Change ONE thing (chunk size, overlap, model, k...) and record the metrics."],
             ["Vector DB comparison", "Use with concepts.md section 5 to choose a store."],
             ["Metrics", "hit@k = share of questions whose correct document is in the top k. MRR = average of 1/rank of the first correct result."]]
    workbook({"Eval results": eval_sheet, "Experiment log": log, "Vector DB comparison": vdb, "How to use": guide},
             HERE / "excel" / "rag-tracker.xlsx",
             col_widths={"Vector DB comparison": [11, 18, 26, 22, 26, 22, 36, 36, 40], "How to use": [20, 100]})


def main():
    for name, src in MERMAID.items():
        mermaid(src, IMG / f"{name}.png")
    chunking_figure()
    res = HERE / "data" / "eval_results.csv"
    rows = list(csv.DictReader(open(res, encoding="utf-8"))) if res.exists() else []
    eval_figure(rows)
    from build_notebooks import NB01, NB02, NB03
    nbdir = HERE / "notebooks"
    notebook(NB01, nbdir / "01-loading-and-chunking.ipynb")
    notebook(NB02, nbdir / "02-embeddings-search-hybrid-rerank.ipynb")
    notebook(NB03, nbdir / "03-generation-and-evaluation.ipynb")
    slides(deck(), HERE / "slides" / f"{NAME}.pptx")
    tracker(rows)
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / f"{NAME}-handout.pdf",
                      title="Module 09 - Retrieval-Augmented Generation (RAG)")
    print("built", NAME)


if __name__ == "__main__":
    main()
