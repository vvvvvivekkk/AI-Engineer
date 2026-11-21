"""
chat.py - the chatbot: remember -> rewrite -> retrieve -> answer with citations.

For every user message:
  1. rewrite  - make follow-ups standalone, using short conversation memory (src/rewrite.py)
  2. retrieve - top-k chunks from FAISS, optionally reranked (src/retriever.py)
  3. refuse   - if even the best chunk is a weak match, say "not in the notes" instead of guessing
  4. answer   - "llm": a language model writes the answer from the numbered sources only;
                "extractive": quote the sentences that best match the question (no LLM)
  5. cite     - list every source as  [n] file > heading
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np

from . import config
from .index import VectorIndex, embed, get_index
from .retriever import retrieve
from .rewrite import rewrite

SYSTEM = ("You are a teaching assistant for an AI engineering course. Answer ONLY from the numbered "
          "sources. Cite the sources you use like [1] or [2]. If the sources do not contain the "
          "answer, say: I could not find that in the course notes.")
NOT_FOUND = "I could not find that in the course notes. Try rephrasing, or ask about a topic the course covers."


@dataclass
class Answer:
    question: str
    standalone: str                       # the question after follow-up rewriting
    text: str
    sources: list[str] = field(default_factory=list)   # "file > heading" per [n]
    scores: list[float] = field(default_factory=list)
    found: bool = True
    mode: str = "extractive"

    def formatted(self) -> str:
        """Answer text + numbered source list, ready to print or show in the UI."""
        if not self.sources:
            return self.text
        refs = "\n".join(f"[{i}] {s}" for i, s in enumerate(self.sources, 1))
        return f"{self.text}\n\nSources:\n{refs}"


def split_sentences(text: str) -> list[str]:
    """Cut chunk text into clean sentences that read well when quoted."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)            # drop image links ![alt](file.png)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)         # [link text](url) -> link text
    out = []
    for s in re.split(r"(?<=[.!?])\s+", text):
        if s.count("|") >= 2 or "---" in s:                       # pieces of markdown tables
            continue
        s = re.sub(r"[*`#>|]", "", s).strip()                     # leftover markdown symbols
        # Skip very short bits and questions (a question repeated back is not an answer)
        if len(s.split()) >= 4 and not s.endswith("?"):
            out.append(s)
    return out


def extractive_answer(question: str, chunks, max_sentences: int = 3) -> str:
    """No LLM: pick the sentences most similar to the question and tag each with its source."""
    candidates = [(s, n) for n, c in enumerate(chunks, 1) for s in split_sentences(c.text)]
    if not candidates:
        return NOT_FOUND
    sims = embed([s for s, _ in candidates]) @ embed([question])[0]    # cosine similarity
    best = np.argsort(-sims)[:max_sentences]                          # most relevant first
    return " ".join(f"{candidates[i][0]} [{candidates[i][1]}]" for i in best)


def llm_answer(question: str, chunks) -> str:
    from .llm import generate
    context = "\n\n".join(f"[{n}] ({c.citation()})\n{c.text}" for n, c in enumerate(chunks, 1))
    prompt = f"Sources:\n{context}\n\nQuestion: {question}\nAnswer in 2-4 sentences with citations."
    return generate(prompt, system=SYSTEM, max_new_tokens=180)


class RAGChatbot:
    def __init__(self, index: VectorIndex | None = None, answer_mode: str | None = None,
                 rewrite_mode: str | None = None, k: int | None = None, rerank: bool | None = None):
        self.index = index or get_index()
        self.answer_mode = answer_mode or config.ANSWER_MODE
        self.rewrite_mode = rewrite_mode or config.REWRITE_MODE
        self.k, self.rerank = k, rerank
        self.history: list[tuple[str, str]] = []      # (standalone question, answer text)

    def reset(self) -> None:
        self.history.clear()

    def ask(self, question: str) -> Answer:
        standalone = rewrite(question, self.history[-config.MEMORY_TURNS:], self.rewrite_mode)
        hits = retrieve(self.index, standalone, self.k, self.rerank)
        if not hits or max(s for _, s in hits) < config.MIN_SCORE:
            ans = Answer(question, standalone, NOT_FOUND, found=False, mode=self.answer_mode)
        else:
            # Keep only chunks that are nearly as relevant as the best one; weak extras add noise
            top = max(s for _, s in hits)
            hits = [(c, s) for c, s in hits if s >= max(config.MIN_SCORE, top - config.RELEVANCE_GAP)]
            chunks = [c for c, _ in hits]
            mode = self.answer_mode
            try:
                text = llm_answer(standalone, chunks) if mode == "llm" else extractive_answer(standalone, chunks)
            except Exception as e:  # noqa: BLE001 - e.g. missing API key: still give a useful answer
                print(f"[chat] LLM answer failed ({e}); falling back to extractive")
                text, mode = extractive_answer(standalone, chunks), "extractive"
            if not text.strip():
                text, mode = extractive_answer(standalone, chunks), "extractive"
            ans = Answer(question, standalone, text, [c.citation() for c in chunks],
                         [round(s, 3) for _, s in hits], True, mode)
        self.history.append((standalone, ans.text))
        self.history = self.history[-config.MEMORY_TURNS:]   # short memory: last few turns only
        return ans
