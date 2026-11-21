"""
config.py - every setting in one place, read from environment variables / the .env file.

Change behaviour without touching code: edit .env (copy it from .env.example).
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROJECT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_DIR.parents[1]                  # the AI-Engineer repo (two levels up)
SAMPLE_DOCS = PROJECT_DIR / "data" / "sample_docs"  # small fixed docs used by tests and eval


def _get(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


# Which markdown files to index. "repo" = every *.md in the whole curriculum (default),
# "sample" = only data/sample_docs, or any folder path you like.
DOCS = _get("DOCS", "repo")
DOCS_GLOB = _get("DOCS_GLOB", "**/*.md")

CHUNK_WORDS = int(_get("CHUNK_WORDS", "180"))      # target chunk size, in words
CHUNK_OVERLAP = int(_get("CHUNK_OVERLAP", "30"))   # words repeated between neighbouring chunks
EMBED_MODEL = _get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
RERANK_MODEL = _get("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
USE_RERANKER = _get("USE_RERANKER", "false").lower() == "true"
TOP_K = int(_get("TOP_K", "4"))
MIN_SCORE = float(_get("MIN_SCORE", "0.25"))       # below this cosine similarity -> "not found"
RELEVANCE_GAP = float(_get("RELEVANCE_GAP", "0.15"))  # drop chunks scoring this far below the best

# How answers are written: "llm" (LLM_PROVIDER decides which model) or "extractive"
# (no LLM: quote the best-matching sentences - deterministic, instant, always faithful).
ANSWER_MODE = _get("ANSWER_MODE", "llm")
# How follow-up questions are rewritten: "rules" (default, deterministic) or "llm".
REWRITE_MODE = _get("REWRITE_MODE", "rules")
MEMORY_TURNS = int(_get("MEMORY_TURNS", "3"))      # how many past turns the chatbot remembers

INDEX_DIR = Path(_get("INDEX_DIR", str(PROJECT_DIR / "index")))
