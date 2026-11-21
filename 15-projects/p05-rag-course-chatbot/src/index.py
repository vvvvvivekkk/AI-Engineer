"""
index.py - turn chunks into embeddings and store them in a FAISS index.

  * embedding  - a list of 384 numbers that captures a chunk's meaning (all-MiniLM-L6-v2).
                 Similar meaning -> vectors pointing in similar directions.
  * FAISS      - a library from Meta for fast "find the nearest vectors" search.
                 IndexFlatIP compares the question with every chunk using the inner product;
                 because we normalise vectors to length 1, that equals cosine similarity.
  * Chroma     - an alternative "vector database" that stores text + metadata too. Optional:
                 see the README for the 6-line swap.
Analogy: every chunk gets a pin on a huge map of meanings; a question gets a pin too, and we
look up the closest pins.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

import faiss
import numpy as np

from . import config
from .ingest import Chunk, load_chunks


@lru_cache(maxsize=2)
def embedder(name: str | None = None):
    """Load the sentence-transformers model once (first call downloads ~90 MB from Hugging Face)."""
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(int(os.getenv("TORCH_THREADS", "2")))
    return SentenceTransformer(name or config.EMBED_MODEL, device="cpu")


def embed(texts: list[str]) -> np.ndarray:
    vecs = embedder().encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vecs, dtype="float32")


class VectorIndex:
    """Chunks + their FAISS index, with save/load so we only embed once."""

    def __init__(self, chunks: list[Chunk], index: faiss.Index):
        self.chunks, self.index = chunks, index

    @classmethod
    def build(cls, chunks: list[Chunk]) -> "VectorIndex":
        # Embed the heading together with the text: the heading often names the topic
        vecs = embed([f"{c.heading}\n{c.text}" for c in chunks])
        index = faiss.IndexFlatIP(vecs.shape[1])
        index.add(vecs)
        return cls(chunks, index)

    def search(self, query: str, k: int) -> list[tuple[Chunk, float]]:
        scores, ids = self.index.search(embed([query]), min(k, len(self.chunks)))
        return [(self.chunks[i], float(s)) for i, s in zip(ids[0], scores[0]) if i != -1]

    def save(self, folder: Path) -> None:
        folder.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(folder / "faiss.index"))
        (folder / "chunks.json").write_text(json.dumps([c.to_dict() for c in self.chunks]), encoding="utf-8")

    @classmethod
    def load(cls, folder: Path) -> "VectorIndex":
        chunks = [Chunk(**d) for d in json.loads((folder / "chunks.json").read_text(encoding="utf-8"))]
        return cls(chunks, faiss.read_index(str(folder / "faiss.index")))


def get_index(rebuild: bool = False, docs: str | None = None, folder: Path | None = None) -> VectorIndex:
    """Load the saved index, or build (and save) it if missing or rebuild=True."""
    folder = folder or config.INDEX_DIR
    if not rebuild and (folder / "faiss.index").exists():
        return VectorIndex.load(folder)
    vi = VectorIndex.build(load_chunks(docs))
    vi.save(folder)
    return vi
