"""
rewrite.py - turn a follow-up question into a standalone question before searching.

Problem: after "What is RAG?", the user asks "how do I evaluate it?". Searching for
"how do I evaluate it" finds nothing about RAG, because "it" carries the meaning.
Fix: rewrite it to "how do I evaluate RAG?" using the conversation so far.

Two modes (REWRITE_MODE in .env):
  * rules (default) - if the question looks like a follow-up (pronouns such as it/this/they, or
    starts with "and"/"what about"/"how about", or is very short), append the topic of the last
    standalone question. Deterministic and testable, but crude.
  * llm             - ask the LLM to rewrite. Better with a capable model; the tiny local model
                      often changes the meaning, which is why rules is the default.
"""
from __future__ import annotations

import re

from . import config

FOLLOW_UP_WORDS = {"it", "its", "this", "that", "these", "those", "they", "them", "their", "one", "ones"}
FOLLOW_UP_STARTS = ("and ", "what about", "how about", "also ", "why is that", "so ")
STOP = {"what", "is", "are", "the", "a", "an", "how", "do", "does", "i", "to", "of", "in", "for", "and",
        "why", "when", "should", "can", "you", "me", "my", "with", "on", "use", "explain", "tell", "about"}


def looks_like_follow_up(question: str) -> bool:
    words = re.findall(r"[a-z']+", question.lower())
    return (bool(set(words) & FOLLOW_UP_WORDS) or question.lower().startswith(FOLLOW_UP_STARTS)
            or len(words) <= 3)


def topic_of(question: str) -> str:
    """The content words of a question: 'What is overfitting?' -> 'overfitting'."""
    words = re.findall(r"[A-Za-z0-9'+-]+", question)
    return " ".join(w for w in words if w.lower() not in STOP and w.lower() not in FOLLOW_UP_WORDS)


def rewrite_rules(question: str, history: list[tuple[str, str]]) -> str:
    if not history or not looks_like_follow_up(question):
        return question
    # history holds (standalone question, answer); use the most recent topic
    topic = topic_of(history[-1][0])
    return f"{question.rstrip('?')} ({topic})?" if topic else question


def rewrite_llm(question: str, history: list[tuple[str, str]]) -> str:
    from .llm import generate
    convo = "\n".join(f"User: {q}\nAssistant: {a[:300]}" for q, a in history)
    prompt = (f"Conversation so far:\n{convo}\n\nFollow-up question: {question}\n\n"
              "Rewrite the follow-up as one standalone question that makes sense without the "
              "conversation. Reply with the question only.")
    out = generate(prompt, max_new_tokens=60).strip().splitlines()
    return out[0].strip() if out and out[0].strip() else question


def rewrite(question: str, history: list[tuple[str, str]], mode: str | None = None) -> str:
    mode = mode or config.REWRITE_MODE
    if not history:
        return question
    if mode == "llm":
        try:
            return rewrite_llm(question, history)
        except Exception as e:  # noqa: BLE001 - never let rewriting break the chat
            print(f"[rewrite] LLM rewrite failed ({e}); using rules")
    return rewrite_rules(question, history)
