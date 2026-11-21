"""
solutions.py - runnable solutions for Module 09 exercises 2-12 (exercise 1 is a drawing).

Run from the module folder:   python solutions/solutions.py          (all, several minutes on CPU)
or pick some:                 python solutions/solutions.py 4 5 9
No API key needed (exercise 12 uses a rule-based judge offline).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "code"))
import rag_pipeline as rp  # noqa: E402

QUESTIONS = json.loads((HERE / "data" / "eval_questions.json").read_text(encoding="utf-8"))
DOCS = rp.load_documents(HERE / "data" / "docs")


def evaluate_ranker(search_fn, questions=QUESTIONS):
    """search_fn(question) -> list of doc_ids in rank order. Returns hit@1, hit@5, MRR."""
    h1 = h5 = rr = 0
    for q in questions:
        ids = search_fn(q["question"])
        h1 += rp.hit_at_k(ids, q["source"], 1); h5 += rp.hit_at_k(ids, q["source"], 5)
        rr += rp.reciprocal_rank(ids, q["source"])
    n = len(questions)
    return {"hit@1": round(h1 / n, 3), "hit@5": round(h5 / n, 3), "MRR": round(rr / n, 3)}


# ---------------------------------------------------------------- 2
def exercise_2():
    for name in rp.CHUNKERS:
        cs = rp.chunk_all(DOCS, name)
        lengths = [len(c.text.split()) for c in cs]
        shortest = cs[int(np.argmin(lengths))]
        print(f"{name:<22} {len(cs):>3} chunks, {min(lengths)}-{max(lengths)} words; shortest = {shortest.chunk_id}")
        print("    ", shortest.text.replace("\n", " | ")[:160])


# ---------------------------------------------------------------- 3
def exercise_3():
    s = ["Can I bring my jacket back?", "Is it possible to return a coat?",
         "The parcel never arrived.", "My delivery is missing.", "Penguins live in Antarctica."]
    v = rp.Embedder().encode(s)
    sim = v @ v.T
    print("      " + "  ".join(f"S{i+1}  " for i in range(5)))
    for i, row in enumerate(sim):
        print(f"S{i+1}  " + "  ".join(f"{x:.2f}" for x in row), "|", s[i])


# ---------------------------------------------------------------- 4
def exercise_4():
    dense, bm25 = ["D3", "D1", "D7", "D2"], ["D1", "D9", "D3", "D4"]
    scores = {}
    for ranking in (dense, bm25):
        for rank, d in enumerate(ranking, 1):
            scores[d] = scores.get(d, 0) + 1 / (60 + rank)
    for d, sc in sorted(scores.items(), key=lambda x: -x[1]):
        print(d, round(sc, 5))
    # D1 = 1/62 + 1/61 = 0.03252 wins: ranked well by BOTH methods. D3 = 1/61 + 1/63 = 0.03227 is a close second.


# ---------------------------------------------------------------- 5
def metrics_from_ranks(ranks, ks=(1, 3, 5)):
    """ranks: list of int rank (1 = first) or None if not found."""
    n = len(ranks)
    out = {f"hit@{k}": sum(r is not None and r <= k for r in ranks) / n for k in ks}
    out["MRR"] = sum(1 / r for r in ranks if r) / n
    return out


def exercise_5():
    print(metrics_from_ranks([1, 3, None, 2]))   # hit@1 .25, hit@3 .75, hit@5 .75, MRR (1+1/3+0+1/2)/4 = 0.458


# ---------------------------------------------------------------- 6
def exercise_6():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    emb, sizes, mrrs = rp.Embedder(), [30, 60, 120, 250], []
    for size in sizes:
        cs = [c for d in DOCS for c in rp.chunk_fixed(d, size, 0)]
        idx = rp.DenseIndex(cs, emb)
        m = evaluate_ranker(lambda q: [c.doc_id for c, _ in idx.search(q, 10)])
        mrrs.append(m["MRR"])
        print(f"size {size:>3}: {len(cs):>3} chunks {m}")
    plt.plot(sizes, mrrs, marker="o"); plt.xlabel("chunk size (words)"); plt.ylabel("MRR")
    plt.title("Chunk size sweep (dense retrieval)"); plt.savefig(HERE / "solutions" / "ex6_chunk_size.png", dpi=120)
    print("saved solutions/ex6_chunk_size.png")


# ---------------------------------------------------------------- 7
CATEGORY = {"01": "orders", "02": "orders", "03": "orders", "06": "orders", "07": "orders",
            "08": "membership", "09": "membership", "14": "membership"}


def category_of(doc_id):
    return CATEGORY.get(doc_id[:2], "company")


def exercise_7():
    chunks = rp.chunk_all(DOCS, "headings")
    emb = rp.Embedder()
    vecs = emb.encode([c.text for c in chunks])

    def search(question, category=None, k=4):
        q = emb.encode([question])[0]
        allowed = [i for i, c in enumerate(chunks) if category is None or category_of(c.doc_id) == category]
        scores = vecs[allowed] @ q                                  # only compare with allowed chunks
        return [chunks[allowed[i]] for i in np.argsort(-scores)[:k]]

    q = "Is there a refund if I cancel?"                              # ambiguous: cancel what?
    print("no filter          :", [c.doc_id for c in search(q)])
    print("category=orders    :", [c.doc_id for c in search(q, "orders")])       # user is on an order page
    print("category=membership:", [c.doc_id for c in search(q, "membership")])   # user is on the Gold page
    print("The app knows WHERE the user is asking from; a metadata filter turns that into better retrieval,")
    print("and each search compares the question with fewer vectors.")


# ---------------------------------------------------------------- 8
NEW_DOC = """# Kayak Rentals

## Where and when
Kayaks can be rented at the Harbour Market store from April to October, every day from 9:00 to 17:00.

## Prices
A single kayak costs $35 for half a day and $55 for a full day. A life jacket is always included free.

## Safety rules
Renters must be at least 16 years old and pass a 10-minute safety briefing before the first rental.
"""


def exercise_8():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    shutil.copytree(HERE / "data" / "docs", tmp / "docs")
    (tmp / "docs" / "16-kayak-rentals.md").write_text(NEW_DOC, encoding="utf-8")
    docs = rp.load_documents(tmp / "docs")
    chunks = rp.chunk_all(docs, "headings")                          # must re-chunk ...
    retriever = rp.HybridRetriever(chunks)                           # ... and re-embed / re-index everything new
    for q in ["How much is a full day in a kayak?", "How old do you need to be to rent a kayak?"]:
        top = [c.doc_id for c, _ in retriever.search(q, 3)]
        print(q, "->", top)
    print("Rebuilt: chunks, embeddings, FAISS index and BM25 statistics (BM25's word rarity changes with every new document).")


# ---------------------------------------------------------------- 9
def exercise_9():
    chunks = rp.chunk_all(DOCS, "headings")
    retriever, reranker = rp.HybridRetriever(chunks), rp.Reranker()
    unanswerable = ["Do you sell kayaks?", "What is the CEO's name?", "Do you have a store in Paris?",
                    "Can I bring my dog into the store?", "What is your stock price?"]

    def best_score(q):
        cands = [c for c, _ in retriever.search(q, k=20)]
        return reranker.rerank(q, cands, 1)[0][1]

    ans = [best_score(q["question"]) for q in QUESTIONS]
    una = [best_score(q) for q in unanswerable]
    print("answerable   scores: min %.2f, median %.2f" % (min(ans), float(np.median(ans))))
    print("unanswerable scores:", [round(s, 2) for s in una])
    best = max(np.linspace(-11, 8, 77), key=lambda t: sum(s >= t for s in ans) + sum(s < t for s in una))
    print(f"chosen threshold {best:.2f}: answerable kept {sum(s >= best for s in ans)}/{len(ans)}, "
          f"unanswerable rejected {sum(s < best for s in una)}/{len(una)}")
    for t in [-10, -8, -6, -4, 0]:                                  # the trade-off, threshold by threshold
        print(f"   threshold {t:>4}: answerable kept {sum(s >= t for s in ans):>2}/{len(ans)}, "
              f"unanswerable rejected {sum(s < t for s in una)}/{len(una)}")
    print("In production, choose the threshold on one question set and confirm it on a different one.")


# ---------------------------------------------------------------- 10
def chunk_sentence_window(doc, window=1):
    chunks, section = [], doc.title
    sents = []
    for line in doc.text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        elif line.strip() and not line.startswith("# "):
            for s in re.split(r"(?<=[.!?])\s+", line.strip()):
                if s:
                    sents.append((section, s))
    for i, (sec, _) in enumerate(sents):
        text = " ".join(s for _, s in sents[max(0, i - window): i + window + 1])
        chunks.append(rp.Chunk(f"{doc.doc_id}#{i}", doc.doc_id, sec, f"{doc.title} > {sec}\n{text}"))
    return chunks


def exercise_10():
    rp.CHUNKERS["sentence-window"] = chunk_sentence_window
    emb, reranker = rp.Embedder(), rp.Reranker()
    for name in ["fixed-80", "headings", "sentence-window"]:
        cs = rp.chunk_all(DOCS, name)
        hyb = rp.HybridRetriever(cs, emb)
        dense = evaluate_ranker(lambda q: [c.doc_id for c, _ in hyb.dense.search(q, 10)])
        rerank = evaluate_ranker(lambda q: [c.doc_id for c, _ in reranker.rerank(q, [c for c, _ in hyb.search(q, k=20)], 10)])
        print(f"{name:<16} {len(cs):>4} chunks | dense {dense} | hybrid+rerank {rerank}")


# ---------------------------------------------------------------- 11
def check_citations(answer, chunks):
    by_id = {c.chunk_id: c for c in chunks}
    report = []
    # split into sentences, but keep a citation like "[04-warranty.md#1]" attached to the sentence before it
    for sent in [s for s in re.split(r"(?<=[.!?\]])\s+(?=[A-Z])", answer.strip()) if s]:
        cited = rp.citations_in(sent)
        words = rp.tokenize(re.sub(r"\[[^\]]*\]", "", sent))
        rows = []
        for cid in cited:
            exists = cid in by_id
            overlap = (sum(w in set(rp.tokenize(by_id[cid].text)) for w in words) / len(words)) if exists and words else 0
            rows.append({"id": cid, "exists": exists, "supported": exists and overlap >= 0.5})
        report.append({"sentence": sent[:60], "citations": rows or "NONE"})
    return report


def exercise_11():
    chunks = [c for c in rp.chunk_all(DOCS, "headings") if c.doc_id == "04-warranty.md"]
    period = next(c.chunk_id for c in chunks if c.section == "Warranty periods")
    answers = [f"Tents, backpacks and sleeping bags have a 5 years warranty. [{period}]",
               "Tents have a 5 years warranty. [04-warranty.md#99]",
               f"Brightleaf ships worldwide with free express delivery. [{period}]"]
    for a in answers:
        print(a, "\n   ", check_citations(a, chunks))


# ---------------------------------------------------------------- 12
JUDGE_SYSTEM = ("You grade whether an ANSWER is supported by SOURCES. Score 1-5: 5 = every claim supported, "
                "1 = mostly unsupported. Reply with the number only.")


def judge(answer, chunks):
    import os
    if os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"):
        reply = rp.generate(f"SOURCES:\n{rp.build_prompt('', chunks)}\n\nANSWER:\n{answer}", system=JUDGE_SYSTEM, max_tokens=5)
        m = re.search(r"[1-5]", reply)
        return int(m.group(0)) if m else None, "llm"
    support = rp.faithfulness_report(answer, chunks)["support"]       # offline: rule-based stand-in
    return 1 + round(support * 4), "rule-based (no API key)"


def exercise_12(n=8):
    import pandas as pd
    pipe = rp.RAGPipeline()
    rows = []
    for q in QUESTIONS[:n]:
        chunks = pipe.retrieve(q["question"], 4)
        ans = rp.generate(rp.build_prompt(q["question"], chunks), max_tokens=80)
        rep = rp.faithfulness_report(ans, chunks, q["key_facts"])
        score, kind = judge(ans, chunks)
        rows.append({"id": q["id"], "retrieved_gold": q["source"] in [c.doc_id for c in chunks],
                     "answer": ans[:70], **rep, "judge": score, "judge_type": kind})
    df = pd.DataFrame(rows)
    print(df.to_string())
    print("\nRetrieval found the gold document for", int(df.retrieved_gold.sum()), "of", n,
          "questions; key facts appeared in", round(df.key_facts_found.mean(), 2), "of answers on average.")
    print("If retrieval is near-perfect but answers miss facts, improve GENERATION first (stronger model, clearer prompt).")


if __name__ == "__main__":
    for n in sys.argv[1:] or ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]:
        print(f"\n===== Exercise {n} =====")
        globals()[f"exercise_{n}"]()
