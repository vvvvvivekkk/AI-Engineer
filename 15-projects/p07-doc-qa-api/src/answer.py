"""
answer.py - from a question to an answer with citations (or an honest "not found").

Steps:
  1. hybrid search returns the top-k chunks
  2. a **confidence score** checks whether the best chunk really talks about the
     question (meaning similarity + how many question words it contains). Below a
     threshold we answer "Not found in the documents" instead of guessing. This
     is the main defence against **hallucination** (a model inventing facts).
  3. build the answer:
       extractive (default) - pick the sentences from the retrieved chunks that
                              best match the question and quote them. Fast,
                              never invents facts, works with no model.
       llm                  - give the chunks to the LLM (src/llm.py) and ask for a
                              short answer that cites [doc p.N]. The default local
                              135M model writes weak answers; use ollama/anthropic/
                              openai for good ones.
  4. every answer carries citations: document name + page number.
"""
from __future__ import annotations

import os
import re

from .retrieval import HybridIndex, tokenize

NOT_FOUND = "Not found in the documents."
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.33"))
GENERIC = {"northwind", "labs", "company", "employee", "employees", "policy"}   # appear everywhere, prove nothing


def _stems(text: str) -> list[str]:
    """Very light stemming: drop a final 's' and keep 5 letters ('meals' -> 'meal', 'travelling' -> 'trave')."""
    return [w.rstrip("s")[:5] for w in tokenize(text) if w not in GENERIC]


def coverage(question: str, text: str) -> float:
    """Share of the question's content words that also appear in the text (0..1)."""
    q, t = _stems(question), set(_stems(text))
    return sum(w in t for w in q) / max(1, len(q))


def confidence(question: str, top_hit: dict) -> float:
    """Blend meaning similarity and word coverage into one 0..1 confidence number."""
    return 0.5 * top_hit["cosine"] + 0.5 * coverage(question, top_hit["text"])


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 3]


def extractive_answer(question: str, hits: list[dict], max_sentences: int = 2) -> tuple[str, list[dict]]:
    """Quote the best-matching sentences and remember which chunk each came from."""
    scored = []
    for h in hits:
        for s in split_sentences(h["text"]):
            if len(s.split()) <= 5:                          # skip headings such as "Annual leave."
                continue
            scored.append((coverage(question, s) + 0.1 * h["rrf"] * 60, s, h))   # word match + small rank bonus
    scored.sort(key=lambda x: -x[0])
    picked, cites = [], []
    best = scored[0][0] if scored else 0
    for score, s, h in scored[:max_sentences]:
        if s not in picked and score >= 0.6 * best:      # a 2nd sentence only if it is nearly as relevant
            picked.append(s)
            cites.append(h)
    text = " ".join(f"{s} [{h['doc']} p.{h['page']}]" for s, h in zip(picked, cites))
    return text, cites


def llm_answer(question: str, hits: list[dict]) -> tuple[str, list[dict]]:
    """Ask the configured LLM to answer only from the retrieved context."""
    from .llm import generate
    context = "\n\n".join(f"[{h['doc']} p.{h['page']}] {h['text']}" for h in hits)
    prompt = (f"Answer the question using ONLY the context. Cite sources like [file.pdf p.2]. "
              f"If the answer is not in the context, say '{NOT_FOUND}'\n\nContext:\n{context}\n\n"
              f"Question: {question}\nAnswer:")
    return generate(prompt, max_new_tokens=120), hits


def answer(index: HybridIndex, question: str, k: int = 3, mode: str | None = None) -> dict:
    """Full pipeline. Returns a dict that the API sends back as JSON."""
    mode = mode or os.getenv("ANSWER_MODE", "extractive")
    hits = index.search(question, k=k)
    if not hits:
        return {"answer": NOT_FOUND, "found": False, "confidence": 0.0, "citations": []}
    conf = confidence(question, hits[0])
    if conf < CONF_THRESHOLD:
        return {"answer": NOT_FOUND, "found": False, "confidence": round(conf, 3), "citations": []}
    text, used = llm_answer(question, hits) if mode == "llm" else extractive_answer(question, hits)
    cites, seen = [], set()
    for h in used:                                   # unique (doc, page) citations, best first
        if (h["doc"], h["page"]) not in seen:
            seen.add((h["doc"], h["page"]))
            cites.append({"doc": h["doc"], "page": h["page"], "snippet": h["text"][:160], "rrf": h["rrf"]})
    return {"answer": text, "found": True, "confidence": round(conf, 3), "citations": cites}
