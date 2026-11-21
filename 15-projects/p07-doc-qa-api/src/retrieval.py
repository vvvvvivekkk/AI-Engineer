"""
retrieval.py - hybrid search: keyword search (BM25) + meaning search (vectors), fused with RRF.

Words used here:
  **BM25** - a classic keyword-scoring formula used by search engines. A chunk
      scores high if it contains the question's words, especially rare words.
      Great for exact terms like "VPN" or "extension 4444".
  **embedding / vector** - a list of numbers that represents the meaning of a
      text. Texts with similar meaning get similar vectors, even with different
      words ("time off" ~ "leave"). We use the small all-MiniLM-L6-v2 model.
  **FAISS** - a library that finds the nearest vectors quickly.
  **cosine similarity** - how closely two vectors point the same way (1 = same meaning).
  **RRF (reciprocal rank fusion)** - a simple way to merge two ranked lists.
      Each chunk gets 1/(60 + rank) from each list and the scores are added.
      A chunk ranked well by both methods wins. Like combining two judges'
      rankings without having to compare their very different raw scores.
"""
from __future__ import annotations

import os
import re
from functools import lru_cache

import numpy as np
from rank_bm25 import BM25Okapi

from .ingest import Chunk

EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
RRF_K = 60   # the usual constant from the original RRF paper; dampens the effect of rank 1 vs rank 2

STOPWORDS = set("a an the of to in on for and or is are be by with at from as it this that do does how what "
                "when where which who whom why can i my we our you your must should may per".split())


def tokenize(text: str) -> list[str]:
    """Lower-case words without punctuation or very common filler words."""
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]


@lru_cache(maxsize=1)
def embedder():
    """Load the sentence-embedding model once (about 90 MB, downloaded the first time)."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBED_MODEL, device="cpu")


def embed(texts: list[str]) -> np.ndarray:
    """Vectors of length 384, normalised so a dot product equals cosine similarity."""
    return np.asarray(embedder().encode(texts, normalize_embeddings=True, batch_size=32), dtype="float32")


class HybridIndex:
    """Holds the chunks, a BM25 index and a FAISS vector index side by side."""

    def __init__(self, chunks: list[Chunk]):
        import faiss
        if not chunks:
            raise ValueError("No chunks to index - did you put PDFs in the folder?")
        self.chunks = chunks
        self.bm25 = BM25Okapi([tokenize(c.text) for c in chunks])
        vecs = embed([c.text for c in chunks])
        self.faiss = faiss.IndexFlatIP(vecs.shape[1])     # "IP" = inner product = cosine on normalised vectors
        self.faiss.add(vecs)

    # -- the two separate searches -------------------------------------------------
    def bm25_search(self, query: str, k: int) -> list[tuple[int, float]]:
        scores = self.bm25.get_scores(tokenize(query))
        order = np.argsort(-scores)[:k]
        return [(int(i), float(scores[i])) for i in order if scores[i] > 0]

    def vector_search(self, query: str, k: int) -> list[tuple[int, float]]:
        sims, idx = self.faiss.search(embed([query]), min(k, len(self.chunks)))
        return [(int(i), float(s)) for i, s in zip(idx[0], sims[0]) if i >= 0]

    # -- fusion ------------------------------------------------------------------------
    def search(self, query: str, k: int = 5, mode: str = "hybrid", pool: int = 20) -> list[dict]:
        """Return the top-k chunks with their scores. mode = hybrid | bm25 | vector."""
        bm = self.bm25_search(query, pool) if mode in ("hybrid", "bm25") else []
        vec = self.vector_search(query, pool) if mode in ("hybrid", "vector") else []
        fused: dict[int, float] = {}
        for ranked in (bm, vec):
            for rank, (i, _) in enumerate(ranked, start=1):
                fused[i] = fused.get(i, 0.0) + 1.0 / (RRF_K + rank)
        bm_score, vec_score = dict(bm), dict(vec)
        best = sorted(fused, key=lambda i: -fused[i])[:k]
        return [{**self.chunks[i].to_dict(), "rrf": round(fused[i], 5),
                 "bm25": round(bm_score.get(i, 0.0), 3), "cosine": round(vec_score.get(i, 0.0), 3)}
                for i in best]

    def best_cosine(self, query: str) -> float:
        """Similarity of the single closest chunk - used to decide 'not found'."""
        hits = self.vector_search(query, 1)
        return hits[0][1] if hits else 0.0
