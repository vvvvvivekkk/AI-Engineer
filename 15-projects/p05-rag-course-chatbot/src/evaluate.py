"""
evaluate.py - measure the chatbot on a fixed FAQ (data/faq.jsonl) so changes can be compared.

Retrieval metrics (did we find the right SECTION - file + heading?):
  * hit@1 - share of questions whose expected section is the FIRST result
  * hit@k - share whose expected section is anywhere in the top k
  * MRR   - mean reciprocal rank: 1 for rank 1, 1/2 for rank 2, 1/3 ... 0 if not found; averaged
Answer metric (no LLM judge needed):
  * token F1 - word overlap between the extractive answer and the hand-written reference answer
    (a rough proxy: high overlap = the answer contains the key words of the reference)
The FAQ has 24 direct questions and 8 paraphrased ones (kind=paraphrase) that avoid the
notes' wording. Experiments: two chunk sizes x reranker off/on, all on the sample docs, so results are repeatable.
"""
from __future__ import annotations

import json
import re
from collections import Counter

import pandas as pd

from . import config
from .chat import extractive_answer
from .index import VectorIndex
from .ingest import load_chunks
from .retriever import retrieve

STOP = {"the", "a", "an", "of", "to", "and", "is", "in", "it", "on", "or", "for", "with", "that", "as", "are", "be"}


def load_faq(path=None) -> list[dict]:
    path = path or config.PROJECT_DIR / "data" / "faq.jsonl"
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def token_f1(pred: str, ref: str) -> float:
    """F1 of word overlap (ignoring tiny filler words and [n] citation tags)."""
    norm = lambda s: [w for w in re.findall(r"[a-z0-9]+", re.sub(r"\[\d+\]", "", s.lower())) if w not in STOP]
    p, r = Counter(norm(pred)), Counter(norm(ref))
    common = sum((p & r).values())
    if common == 0:
        return 0.0
    precision, recall = common / sum(p.values()), common / sum(r.values())
    return 2 * precision * recall / (precision + recall)


def evaluate_config(vi: VectorIndex, faq: list[dict], k: int, rerank: bool) -> dict:
    hit1 = hitk = rr = f1 = 0.0
    for item in faq:
        hits = retrieve(vi, item["question"], k=k, rerank=rerank)
        # a hit = right file AND the chunk's heading path ends with the expected section
        found = [c.source.split("/")[-1] == item["source"] and c.heading.endswith(item["section"])
                 for c, _ in hits]
        if any(found):
            rank = found.index(True) + 1
            hitk += 1
            rr += 1 / rank
            hit1 += rank == 1
        f1 += token_f1(extractive_answer(item["question"], [c for c, _ in hits]), item["answer"])
    n = len(faq)
    return {"hit@1": hit1 / n, f"hit@{k}": hitk / n, "MRR": rr / n, "answer_token_f1": f1 / n}


def run_experiments(chunk_sizes=(40, 180), k: int = 4) -> pd.DataFrame:
    faq = load_faq()
    rows = []
    for size in chunk_sizes:
        chunks = load_chunks("sample", size=size, overlap=min(config.CHUNK_OVERLAP, size // 4))
        vi = VectorIndex.build(chunks)
        for rerank in (False, True):
            row = {"chunk_words": size, "chunks": len(chunks), "reranker": rerank,
                   **evaluate_config(vi, faq, k, rerank)}
            # The "paraphrase" questions share few words with the notes - the hardest subset
            para = [q for q in faq if q.get("kind") == "paraphrase"]
            if para:
                sub = evaluate_config(vi, para, k, rerank)
                row["paraphrase_hit@1"], row["paraphrase_MRR"] = sub["hit@1"], sub["MRR"]
            rows.append(row)
    return pd.DataFrame(rows)
