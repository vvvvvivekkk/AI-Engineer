"""
evaluate.py - score the system on the golden question set.

Metrics (all between 0 and 1, higher is better):
  **Recall@k** - for answerable questions, did the correct (document, page)
      appear in the top k search results? "Did the right index card make the shortlist?"
  **MRR** (mean reciprocal rank) - 1 if the right page is ranked 1st, 1/2 if 2nd,
      1/3 if 3rd... averaged. Rewards putting the right page near the top.
  **not-found accuracy** - for questions with no answer in the documents, did we
      say "not found"? And for answerable ones, did we wrongly refuse?
  **faithfulness (proxy)** - is the answer text supported by what it cites? Here:
      share of answer words found in the cited chunks. A real project would use an
      LLM grader (e.g. DeepEval / RAGAS); this cheap proxy needs no model.
  **citation accuracy** - the first citation points at the expected page.

Compares three retrieval modes: BM25 only, vectors only, hybrid (RRF).
Run:  python -m src.evaluate      -> prints a table, writes data/eval_report.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .answer import NOT_FOUND, answer
from .ingest import ingest_folder
from .retrieval import HybridIndex

DATA = Path(__file__).resolve().parents[1] / "data"


def retrieval_metrics(index: HybridIndex, golden: list[dict], mode: str, k: int = 3) -> dict:
    answerable = [g for g in golden if g["doc"]]
    hits, rr = 0, 0.0
    for g in answerable:
        results = index.search(g["question"], k=k, mode=mode)
        ranks = [i for i, r in enumerate(results, 1) if (r["doc"], r["page"]) == (g["doc"], g["page"])]
        hits += bool(ranks)
        rr += 1 / ranks[0] if ranks else 0
    return {f"recall@{k}": round(hits / len(answerable), 3), "mrr": round(rr / len(answerable), 3)}


def faithfulness(answer_text: str, citations: list[dict], index: HybridIndex) -> float:
    """Share of answer words that occur in the full text of the cited chunks."""
    clean = re.sub(r"\[[^\]]+\]", "", answer_text).lower()      # drop the [doc p.N] tags
    words = re.findall(r"[a-z0-9]+", clean)
    cited = " ".join(c.text.lower() for c in index.chunks
                     if any((c.doc, c.page) == (x["doc"], x["page"]) for x in citations))
    return sum(w in cited for w in words) / max(1, len(words))


def main():
    golden = json.loads((DATA / "golden.json").read_text(encoding="utf-8"))
    index = HybridIndex(ingest_folder(DATA / "pdfs"))
    report = {"chunks": len(index.chunks), "questions": len(golden), "retrieval": {}}
    for mode in ("bm25", "vector", "hybrid"):
        report["retrieval"][mode] = retrieval_metrics(index, golden, mode, k=1) | \
            retrieval_metrics(index, golden, mode, k=3)

    tp = fn = tn = fp = 0
    faith, cite_ok, examples = [], 0, []
    for g in golden:
        res = answer(index, g["question"])
        if g["doc"]:
            if res["found"]:
                tp += 1
                faith.append(faithfulness(res["answer"], res["citations"], index))
                cite_ok += (res["citations"][0]["doc"], res["citations"][0]["page"]) == (g["doc"], g["page"])
            else:
                fn += 1                                    # wrongly refused
        else:
            tn += res["answer"] == NOT_FOUND               # correctly refused
            fp += res["answer"] != NOT_FOUND               # answered something that is not there
        if len(examples) < 5 or not g["doc"]:
            examples.append({"q": g["question"], "a": res["answer"], "confidence": res["confidence"]})
    n_ans = tp + fn
    report["answers"] = {
        "answered_when_answerable": round(tp / n_ans, 3),
        "refused_when_unanswerable": round(tn / max(1, tn + fp), 3),
        "citation_accuracy": round(cite_ok / max(1, tp), 3),
        "faithfulness_proxy": round(sum(faith) / max(1, len(faith)), 3),
    }
    report["examples"] = examples

    print(f"{'mode':8s} {'R@1':>6s} {'R@3':>6s} {'MRR@3':>6s}")
    for mode, m in report["retrieval"].items():
        print(f"{mode:8s} {m['recall@1']:6.3f} {m['recall@3']:6.3f} {m['mrr']:6.3f}")
    for key, v in report["answers"].items():
        print(f"{key:28s} {v:.3f}")
    (DATA / "eval_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("saved -> data/eval_report.json")


if __name__ == "__main__":
    main()
