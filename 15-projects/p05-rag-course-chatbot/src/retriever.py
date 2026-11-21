"""
retriever.py - get the best chunks for a question, optionally improved by a reranker.

A reranker (cross-encoder) reads the question and ONE chunk together and scores how well the chunk
answers it. More accurate than comparing two separate embeddings, but slower - so we first fetch
~4x more candidates with FAISS, then let the reranker choose the best few.
Analogy: FAISS is a quick scan of book titles; the reranker actually opens each shortlisted book.
"""
from __future__ import annotations

from functools import lru_cache

from . import config
from .index import VectorIndex


@lru_cache(maxsize=1)
def reranker():
    from sentence_transformers import CrossEncoder
    return CrossEncoder(config.RERANK_MODEL, device="cpu")


def retrieve(vi: VectorIndex, question: str, k: int | None = None, rerank: bool | None = None):
    """Return a list of (chunk, similarity) for the top-k chunks. Similarity is always the cosine
    score from the embedding search (used for the 'not found' threshold), even after reranking."""
    k = k or config.TOP_K
    rerank = config.USE_RERANKER if rerank is None else rerank
    hits = vi.search(question, k * 4 if rerank else k)
    if rerank and hits:
        scores = reranker().predict([(question, f"{c.heading}\n{c.text}") for c, _ in hits])
        order = sorted(range(len(hits)), key=lambda i: -scores[i])
        hits = [hits[i] for i in order]
    return hits[:k]
