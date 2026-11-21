"""
agent_memory.py - short-term and long-term memory for an agent.

Short-term memory : the recent conversation, kept in a fixed-size buffer
                    (like a notepad that only has room for the last N lines).
Long-term memory  : facts stored as vectors (lists of numbers that capture meaning)
                    and found again by similarity search (like a library index).

Embeddings come from sentence-transformers/all-MiniLM-L6-v2 if it can be loaded,
otherwise a tiny "hashing" embedder is used so the script still runs offline.

Run: python agent_memory.py
"""
from collections import deque   # a list with a maximum length: old items fall off the front

import numpy as np              # fast maths on arrays of numbers


class ShortTermMemory:
    """Keep only the last `max_turns` messages."""

    def __init__(self, max_turns: int = 4):
        self.buffer = deque(maxlen=max_turns)       # deque drops the oldest item automatically

    def add(self, role: str, text: str) -> None:
        self.buffer.append({"role": role, "content": text})

    def as_messages(self) -> list[dict]:
        return list(self.buffer)                    # ready to send to a chat model


def get_embedder():
    """Return a function text-list -> 2-D numpy array of unit-length vectors."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return lambda texts: model.encode(texts, normalize_embeddings=True)
    except Exception:                               # no internet / not installed -> fallback
        def hashing(texts, dim=256):
            out = np.zeros((len(texts), dim))
            for i, t in enumerate(texts):
                for word in t.lower().split():      # each word bumps one "bucket"
                    out[i, hash(word.strip(".,?!")) % dim] += 1
            norms = np.linalg.norm(out, axis=1, keepdims=True) + 1e-9
            return out / norms                      # unit length so dot product = cosine similarity
        return hashing


class LongTermMemory:
    """A minimal vector store: remember(text) and recall(query, k)."""

    def __init__(self, embed):
        self.embed = embed
        self.texts: list[str] = []
        self.vectors = None                         # 2-D array, one row per memory

    def remember(self, text: str) -> None:
        vec = self.embed([text])
        self.texts.append(text)
        self.vectors = vec if self.vectors is None else np.vstack([self.vectors, vec])

    def recall(self, query: str, k: int = 2) -> list[tuple[float, str]]:
        if self.vectors is None:
            return []
        q = self.embed([query])[0]
        scores = self.vectors @ q                   # cosine similarity with every memory at once
        best = np.argsort(-scores)[:k]              # indices of the k highest scores
        return [(float(scores[i]), self.texts[i]) for i in best]


if __name__ == "__main__":
    stm = ShortTermMemory(max_turns=3)
    for i in range(5):
        stm.add("user", f"message {i}")
    print("Short-term buffer keeps only the last 3:", stm.as_messages())

    ltm = LongTermMemory(get_embedder())
    for fact in ["The user's name is Priya.", "Priya prefers answers in Telugu.",
                 "Priya's project deadline is 5 December.", "Priya is allergic to peanuts."]:
        ltm.remember(fact)
    for q in ["What language should I reply in?", "When is the deadline?"]:
        print(q, "->", ltm.recall(q, k=1))
