"""
workflow.py - the steps after extraction: find a help article, draft a reply, decide the route.

Words used here:
  **retrieval** - finding the most relevant document for a query. We use BM25
      (a keyword-scoring formula) over the 15 help articles. Project P5 has a
      fuller retriever (embeddings + FAISS) that could be swapped in here.
  **routing** - deciding where each email goes next, like a post-room clerk
      sorting letters into trays:
        human_review - a person must approve the draft before anything is sent
        auto         - routine; the draft is filed automatically
        discard      - spam; filed away, no reply
  **human-in-the-loop** - risky actions wait for a person's approval. One of the
      "12-factor agents" principles: automate the boring part, keep people in
      charge of the risky part.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from rank_bm25 import BM25Okapi

from .schema import Email, Ticket

DATA = Path(__file__).resolve().parents[1] / "data"
INTENT_HINTS = {  # extra words added to the query so the right article wins
    "refund": "refund return", "delivery_status": "delivery tracking parcel", "damaged_item": "damaged photo replacement",
    "cancel_order": "cancel dispatched", "billing_issue": "charged twice authorisation", "technical_support": "setup pairing wifi",
    "account_access": "log in password locked", "feedback": "feedback thank", "other": "contact support",
}


def _tok(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


@lru_cache(maxsize=1)
def _kb():
    """Load the help articles once and build a BM25 index."""
    docs = sorted((DATA / "help_articles").glob("*.md"))
    texts = [d.read_text(encoding="utf-8") for d in docs]
    return docs, texts, BM25Okapi([_tok(t) for t in texts])


def find_article(ticket: Ticket, email: Email) -> dict | None:
    if ticket.intents == ["spam"]:
        return None
    docs, texts, bm25 = _kb()
    query = " ".join([INTENT_HINTS.get(i, "") for i in ticket.intents] + [ticket.product or "", email.subject])
    if any(w in email.body.lower() for w in ["smoking", "sparks", "fire"]):
        query = "safety smokes sparks unplug hot"          # safety beats everything else
    scores = bm25.get_scores(_tok(query))
    best = int(scores.argmax())
    title = texts[best].splitlines()[0].lstrip("# ").strip()
    return {"slug": docs[best].stem, "title": title, "text": texts[best].split("\n", 2)[-1].strip(),
            "score": round(float(scores[best]), 2)}


def draft_reply(ticket: Ticket, article: dict | None, use_llm: bool = False) -> str:
    """A polite reply built from a template (or written by the LLM if use_llm=True)."""
    if ticket.intents == ["spam"]:
        return ""
    if use_llm:
        from .llm import generate
        return generate(f"Write a short, polite support reply (max 80 words) to {ticket.customer_name or 'the customer'}. "
                        f"Issue: {ticket.summary}. Use this help article: {article['text'] if article else 'none'}. "
                        "Do not promise anything the article does not say.", max_new_tokens=150)
    hello = f"Hi {ticket.customer_name.split()[0]}," if ticket.customer_name else "Hello,"
    sorry = "We're really sorry about this experience. " if ticket.sentiment in ("angry", "negative") else ""
    order = f"I've found your order {ticket.order_id}. " if ticket.order_id else \
        ("Could you reply with your order number (it looks like ORD-12345)? " if "feedback" not in ticket.intents else "")
    help_text = f"{article['text']} " if article else ""
    return f"{hello}\n\nThanks for contacting GadgetCo. {sorry}{order}{help_text}\n\nBest wishes,\nGadgetCo Support"


def route(ticket: Ticket, email: Email) -> tuple[str, list[str]]:
    """Return (route, reasons). The reasons are stored so reviewers see WHY it was flagged."""
    if ticket.intents == ["spam"]:
        return "discard", ["spam"]
    reasons = []
    low = email.body.lower()
    if ticket.urgency == "high":
        reasons.append("high urgency")
    if ticket.sentiment == "angry":
        reasons.append("angry customer")
    if any(w in low for w in ["lawyer", "chargeback", "legal"]):
        reasons.append("legal / chargeback threat")
    if any(w in low for w in ["smoking", "sparks", "fire"]):
        reasons.append("possible safety issue")
    if len(ticket.intents) > 1:
        reasons.append("multiple intents")
    if set(ticket.intents) & {"refund", "billing_issue"}:
        reasons.append("money involved")
    if ticket.order_id is None and not set(ticket.intents) <= {"feedback", "technical_support", "account_access"}:
        reasons.append("order id missing")
    return ("human_review" if reasons else "auto"), reasons
