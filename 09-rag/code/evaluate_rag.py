"""
evaluate_rag.py - compare chunking strategies and retrieval methods on the hand-written question set.

For every (chunking strategy x retriever) pair it measures, over all questions in
data/eval_questions.json:
  hit@1, hit@3, hit@5 - how often the correct document is in the top 1 / 3 / 5 chunks
  MRR                 - mean reciprocal rank: 1.0 if the right document is always first,
                        0.5 if it is usually second, and so on
Results go to data/eval_results.csv (build.py copies them into the Excel tracker).

Run it:  python code/evaluate_rag.py      (about 1-3 minutes on a CPU, no API key needed)
"""
import csv
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rag_pipeline import (CHUNKERS, BM25Index, DenseIndex, Embedder, HybridRetriever, Reranker,  # noqa: E402
                          chunk_all, hit_at_k, load_documents, reciprocal_rank)

QUESTIONS = json.loads((HERE.parent / "data" / "eval_questions.json").read_text(encoding="utf-8"))


def evaluate(strategy: str, method: str, chunks, indexes, reranker) -> dict:
    hits = {1: 0, 3: 0, 5: 0}
    rr_total = 0.0
    for q in QUESTIONS:
        if method == "bm25":
            ranked = [c for c, _ in indexes["bm25"].search(q["question"], 10)]
        elif method == "dense":
            ranked = [c for c, _ in indexes["dense"].search(q["question"], 10)]
        elif method == "hybrid":
            ranked = [c for c, _ in indexes["hybrid"].search(q["question"], k=10)]
        else:  # hybrid + rerank
            cands = [c for c, _ in indexes["hybrid"].search(q["question"], k=20)]
            ranked = [c for c, _ in reranker.rerank(q["question"], cands, k=10)]
        doc_ids = [c.doc_id for c in ranked]
        for k in hits:
            hits[k] += hit_at_k(doc_ids, q["source"], k)
        rr_total += reciprocal_rank(doc_ids, q["source"])
    n = len(QUESTIONS)
    return {"chunking": strategy, "retriever": method, "num_chunks": len(chunks),
            "avg_chunk_words": round(sum(len(c.text.split()) for c in chunks) / len(chunks), 1),
            "hit@1": round(hits[1] / n, 3), "hit@3": round(hits[3] / n, 3), "hit@5": round(hits[5] / n, 3),
            "MRR": round(rr_total / n, 3), "questions": n}


def main():
    docs = load_documents()
    embedder, reranker = Embedder(), Reranker()
    rows = []
    for strategy in CHUNKERS:
        start = time.time()
        chunks = chunk_all(docs, strategy)
        hybrid = HybridRetriever(chunks, embedder)                     # builds its own dense + BM25 indexes
        indexes = {"bm25": hybrid.sparse, "dense": hybrid.dense, "hybrid": hybrid}
        for method in ["bm25", "dense", "hybrid", "hybrid+rerank"]:
            row = evaluate(strategy, method, chunks, indexes, reranker)
            rows.append(row)
            print(f"{strategy:<22}{method:<15} hit@1={row['hit@1']:.2f} hit@3={row['hit@3']:.2f} "
                  f"hit@5={row['hit@5']:.2f} MRR={row['MRR']:.2f}")
        print(f"   ({time.time() - start:.0f}s)")
    out = HERE.parent / "data" / "eval_results.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("saved", out)


if __name__ == "__main__":
    main()
