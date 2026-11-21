"""
extract.py - turn an email into a validated Ticket.

Two extractors:
  rules (default) - regular expressions and keyword lists. Fast, free,
                    predictable, and good on these templated emails.
  llm             - ask the LLM for JSON matching the schema, validate it with
                    Pydantic, and if it fails, send the error back and ask once
                    more ("retry with feedback"). If it still fails we fall back
                    to the rules. With the default 135M local model the JSON is
                    often invalid, so you will see many fallbacks - honest note.

**Regular expression (regex)** - a tiny pattern language for finding text,
e.g. ORD-\\d{5} means "ORD-" followed by exactly five digits.
"""
from __future__ import annotations

import json
import re

from pydantic import ValidationError

from .schema import PRODUCTS, Email, Ticket

INTENT_KEYWORDS = {
    "refund": ["refund", "money back", "return it"],
    "delivery_status": ["where is my", "hasn't arrived", "not arrived", "delivery status", "nahi aaya", "still waiting"],
    "damaged_item": ["damaged", "cracked", "broken", "crushed", "does not turn on", "smoking", "sparks"],
    "cancel_order": ["cancel"],
    "billing_issue": ["charged twice", "wrong amount", "overcharged", "invoice"],
    "technical_support": ["how do i", "pairing", "disconnecting", "connect my", "set up", "setup"],
    "account_access": ["log in", "login", "locked", "reset email", "password"],
    "feedback": ["thank you", "love my", "is great", "great service"],
}
SPAM_WORDS = ["click here", "you won", "unsubscribe", "limited offer", "seo"]
ANGRY_WORDS = ["unacceptable", "worst", "extremely angry", "furious", "!!", "lawyer", "chargeback"]
NEGATIVE_WORDS = ["not happy", "disappointed", "nahi aaya", "??"]
HIGH_URGENCY = ["lawyer", "chargeback", "smoking", "sparks", "locked", "can't log in"]


def strip_quoted(body: str) -> str:
    """Remove quoted earlier messages (lines starting with '>') - they describe OLD issues."""
    return "\n".join(line for line in body.splitlines() if not line.lstrip().startswith(">"))


def parse_sender(sender: str) -> tuple[str | None, str]:
    """'Asha Rao <asha@x.com>' -> ('Asha Rao', 'asha@x.com')."""
    m = re.match(r"\s*(.*?)\s*<([^>]+)>", sender)
    if m:
        return (m.group(1) or None), m.group(2).strip()
    return None, sender.strip()


def rule_extract(email: Email) -> Ticket:
    text = strip_quoted(email.body)
    low = (email.subject + " " + text).lower()
    name, addr = parse_sender(email.sender)

    if any(w in low for w in SPAM_WORDS):
        return Ticket(customer_name=None, customer_email=addr, intents=["spam"], urgency="low",
                      sentiment="neutral", summary="Marketing / spam email - no support request.")

    order = re.search(r"\bORD-\d{5}\b", text)                       # only in the new (unquoted) text
    product = next((p for p in PRODUCTS if p.lower() in low), None)
    intents = [i for i, words in INTENT_KEYWORDS.items() if any(w in low for w in words)]
    # 'thank you' in a complaint is politeness, not feedback; 'cancel' etc. outrank generic words
    if len(intents) > 1 and "feedback" in intents:
        intents.remove("feedback")
    if "damaged_item" in intents and "technical_support" in intents:
        intents.remove("technical_support")
    if "account_access" in intents and "technical_support" in intents:
        intents.remove("technical_support")
    intents = intents or ["other"]

    angry = any(w in low for w in ANGRY_WORDS) or sum(c.isupper() for c in text) > 0.3 * max(1, sum(c.isalpha() for c in text))
    days = [int(d) for d in re.findall(r"(\d+)\s*(?:days|din)", low)]
    if angry:
        sentiment = "angry"
    elif intents == ["feedback"]:
        sentiment = "positive"
    elif any(w in low for w in NEGATIVE_WORDS):
        sentiment = "negative"
    else:
        sentiment = "neutral"

    if angry or any(w in low for w in HIGH_URGENCY) or (days and max(days) > 10):
        urgency = "high"
    elif set(intents) & {"feedback", "technical_support", "other"} == set(intents):
        urgency = "low"
    else:
        urgency = "medium"

    summary = f"{', '.join(intents).replace('_', ' ')} about {product or 'an unspecified product'}" + \
              (f" (order {order.group(0)})" if order else " (no order id)")
    return Ticket(customer_name=name, customer_email=addr, order_id=order.group(0) if order else None,
                  product=product, intents=intents, urgency=urgency, sentiment=sentiment, summary=summary[:300])


SYSTEM = "You extract structured data from customer-support emails. Reply with JSON only."


def llm_extract(email: Email, retries: int = 1) -> tuple[Ticket, str]:
    """Return (ticket, method) where method is 'llm', 'llm_retry' or 'rules_fallback'."""
    from .llm import generate
    schema = json.dumps(Ticket.model_json_schema()["properties"])
    prompt = (f"Schema (fields and allowed values): {schema}\n\nEmail from: {email.sender}\nSubject: {email.subject}\n"
              f"{strip_quoted(email.body)}\n\nReturn one JSON object with exactly these fields.")
    for attempt in range(retries + 1):
        reply = generate(prompt, system=SYSTEM, max_new_tokens=220)
        m = re.search(r"\{.*\}", reply, re.S)
        try:
            ticket = Ticket.model_validate_json(m.group(0) if m else reply)
            return ticket, "llm" if attempt == 0 else "llm_retry"
        except (ValidationError, ValueError) as e:
            # retry with feedback: show the model exactly what was wrong
            prompt += f"\n\nYour previous answer was invalid: {str(e)[:400]}\nReturn corrected JSON only."
    return rule_extract(email), "rules_fallback"


def extract(email: Email, method: str = "rules") -> tuple[Ticket, str]:
    if method == "llm":
        return llm_extract(email)
    return rule_extract(email), "rules"
