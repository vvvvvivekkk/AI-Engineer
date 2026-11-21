"""
make_emails.py - generate ~200 fake customer-support emails WITH the correct answers.

Each email is written from templates, and at the same time we record its true
labels (customer, order id, product, intents, urgency, sentiment). Because the
labels are known exactly, we can measure how good our extractor is.

Deliberate edge cases (the messy stuff real inboxes contain):
  * two intents in one email ("it arrived broken AND I want a refund")
  * missing order id
  * angry tone (capitals, "unacceptable", "worst")
  * legal / chargeback threats (must go to a human)
  * a forwarded thread whose quoted part mentions an OLD order id
  * a signature with a phone number that looks a bit like an id
  * spam / marketing mail that is not a support request at all
  * very short emails and Hinglish (Hindi + English) emails

Run:  python -m src.make_emails   -> data/emails.jsonl (+ 12 .eml samples in data/inbox/)
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import format_datetime
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
SEED = 11

PRODUCTS = ["AquaPure Filter", "SmartKettle 2", "FitBand Pro", "SoundBuds X", "HomeCam 360"]
NAMES = ["Asha Rao", "Ben Carter", "Chen Wei", "Divya Nair", "Emma Brown", "Farhan Ali", "Grace Kim", "Hiro Sato",
         "Isha Patel", "Jack Wilson", "Kavya Reddy", "Liam Murphy", "Meera Iyer", "Noah Smith", "Olivia Jones",
         "Priya Sharma", "Ravi Kumar", "Sara Lopez", "Tom Baker", "Uma Das"]

# intent -> list of sentence templates ({p} product, {o} order phrase, {d} days)
INTENT_TEXT = {
    "refund": ["I would like a refund for my {p}{o}.", "Please refund the money for the {p}{o}, it is not what I expected."],
    "delivery_status": ["Where is my {p}{o}? It has been {d} days since I ordered.",
                        "My {p}{o} still hasn't arrived after {d} days. Can you check the delivery status?"],
    "damaged_item": ["The {p}{o} arrived damaged - the box was crushed and it does not turn on.",
                     "My {p}{o} came with a cracked case."],
    "cancel_order": ["Please cancel my order for the {p}{o} before it ships.", "I need to cancel the {p}{o}, I ordered by mistake."],
    "billing_issue": ["I was charged twice for the {p}{o}.", "My card shows a wrong amount for the {p}{o}."],
    "technical_support": ["How do I connect my {p} to the app? The pairing keeps failing.",
                          "My {p} keeps disconnecting from Wi-Fi. Any tips?"],
    "account_access": ["I can't log in to my account - the reset email never comes.",
                       "My account is locked after a password reset and I can't see my orders."],
    "feedback": ["Just wanted to say the {p} is great, thank you!", "Love my new {p}, delivery was quick too."],
}
ANGRY = ["This is UNACCEPTABLE.", "Worst service I have ever had!!", "I am extremely angry and frustrated."]
LEGAL = ["If this is not fixed in 48 hours I will file a chargeback with my bank.",
         "I am talking to my lawyer about this."]
SAFETY = ["It started smoking when I plugged it in!", "There were sparks from the charger."]


def order_phrase(oid: str | None) -> str:
    return f" (order {oid})" if oid else ""


def make_one(i: int, rng: random.Random, start: datetime) -> dict:
    name = rng.choice(NAMES)
    addr = name.lower().replace(" ", ".") + rng.choice(["@gmail.com", "@outlook.com", "@example.org"])
    received = start + timedelta(hours=rng.randint(0, 24 * 5 - 1), minutes=rng.randint(0, 59))
    kind = rng.random()

    if kind < 0.06:                                                    # spam / marketing
        return {"id": f"e{i:03d}", "from": "deals@promo-blast.example", "received_at": received.isoformat(),
                "subject": rng.choice(["You WON a free cruise!!!", "Boost your SEO 300% today"]),
                "body": "Click here to claim your prize now. Limited offer. Unsubscribe anytime.",
                "labels": {"customer_name": None, "customer_email": "deals@promo-blast.example", "order_id": None,
                           "product": None, "intents": ["spam"], "urgency": "low", "sentiment": "neutral",
                           "edge_cases": ["spam"]}}

    product = rng.choice(PRODUCTS)
    oid = f"ORD-{rng.randint(10000, 99999)}" if rng.random() > 0.2 else None      # 20% missing order id
    edge = [] if oid else ["missing_order_id"]
    intents = [rng.choice(list(INTENT_TEXT))]
    if rng.random() < 0.15:                                            # two intents in one email
        second = {"damaged_item": "refund", "delivery_status": "cancel_order", "billing_issue": "refund"}.get(
            intents[0], rng.choice(["refund", "billing_issue"]))
        if second not in intents:
            intents.append(second)
            edge.append("two_intents")
    days = rng.randint(2, 15)
    lines = [rng.choice(INTENT_TEXT[it]).format(p=product, o=order_phrase(oid) if j == 0 else "", d=days)
             for j, it in enumerate(intents)]
    sentiment = "positive" if intents == ["feedback"] else "neutral"
    urgency = "low" if all(it in ("feedback", "technical_support") for it in intents) else "medium"
    if any(it in ("account_access",) for it in intents) or (intents[0] == "delivery_status" and days > 10):
        urgency = "high"
    if "feedback" not in intents and rng.random() < 0.18:              # angry tone
        lines.append(rng.choice(ANGRY))
        sentiment, urgency = "angry", "high"
        edge.append("angry")
    if "feedback" not in intents and rng.random() < 0.06:              # legal threat
        lines.append(rng.choice(LEGAL))
        sentiment, urgency = "angry", "high"
        edge.append("legal_threat")
    if "damaged_item" in intents and rng.random() < 0.3:               # safety issue
        lines.append(rng.choice(SAFETY))
        urgency = "high"
        edge.append("safety")
    if sentiment == "neutral" and urgency != "high" and rng.random() < 0.3:
        sentiment = "negative" if intents[0] not in ("technical_support",) else "neutral"
        if sentiment == "negative":
            lines.append("Not happy about this.")

    greeting = rng.choice(["Hi,", "Hello support,", "Dear team,", ""])
    signoff = f"Thanks,\n{name}"
    if rng.random() < 0.15:                                            # signature with a phone number
        signoff += f"\nPhone: +91 98{rng.randint(100, 999)}-{rng.randint(10000, 99999)}"
        edge.append("phone_in_signature")
    body = "\n".join(x for x in [greeting, " ".join(lines), "", signoff] if x is not None)
    if rng.random() < 0.08:                                            # forwarded thread with an old order id
        old = f"ORD-{rng.randint(10000, 99999)}"
        body += f"\n\n> On an earlier date, {name} wrote:\n> My previous order {old} was fine."
        edge.append("quoted_thread")
    if rng.random() < 0.05:                                            # very short email
        body = (f"where is my order {oid}??" if oid else "where is my order??")
        intents, urgency, sentiment = ["delivery_status"], "medium", "negative"
        product = None
        edge = ["very_short"] + ([] if oid else ["missing_order_id"])
    elif rng.random() < 0.04:                                          # Hinglish
        body = (f"Hello, mera {product} order{order_phrase(oid)} abhi tak nahi aaya, {days} din ho gaye. "
                f"Please check karo.\n{name}")
        intents, sentiment = ["delivery_status"], "negative"
        urgency = "high" if days > 10 else "medium"
        edge = ["hinglish"] + ([] if oid else ["missing_order_id"])

    # Labels must describe what is really IN the text: some templates never mention the order or product.
    if oid and oid not in body:
        oid = None
        edge.append("missing_order_id")
    if product and product not in body:
        product = None
    subject = {"refund": "Refund request", "delivery_status": "Where is my order?", "damaged_item": "Damaged item",
               "cancel_order": "Cancel order", "billing_issue": "Billing problem", "technical_support": "Help with setup",
               "account_access": "Can't log in", "feedback": "Thank you!"}[intents[0]]
    if "angry" in edge:
        subject = subject.upper() + "!!!"
    return {"id": f"e{i:03d}", "from": f"{name} <{addr}>", "received_at": received.isoformat(), "subject": subject,
            "body": body, "labels": {"customer_name": name, "customer_email": addr, "order_id": oid,
                                     "product": product, "intents": intents, "urgency": urgency,
                                     "sentiment": sentiment, "edge_cases": edge}}


def build(n: int = 200, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed)
    start = datetime(2026, 11, 16, 0, 0)                              # five days: Mon 16 - Fri 20 Nov 2026
    return sorted((make_one(i + 1, rng, start) for i in range(n)), key=lambda e: e["received_at"])


def write_eml(email: dict, folder: Path) -> None:
    """Save one email as a standard .eml file (what most mail programs export)."""
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = email["from"], "support@gadgetco.example", email["subject"]
    msg["Date"] = format_datetime(datetime.fromisoformat(email["received_at"]))
    msg["Message-ID"] = f"<{email['id']}@gadgetco.example>"
    msg.set_content(email["body"])
    (folder / f"{email['id']}.eml").write_bytes(bytes(msg))


def main():
    emails = build()
    DATA.mkdir(exist_ok=True)
    with (DATA / "emails.jsonl").open("w", encoding="utf-8") as fh:
        for e in emails:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    inbox = DATA / "inbox"
    inbox.mkdir(exist_ok=True)
    for old in inbox.glob("*.eml"):
        old.unlink()
    for e in emails[:12]:
        write_eml(e, inbox)
    counts: dict[str, int] = {}
    for e in emails:
        for tag in e["labels"]["edge_cases"]:
            counts[tag] = counts.get(tag, 0) + 1
    print(f"wrote {len(emails)} emails -> data/emails.jsonl, 12 .eml files -> data/inbox/")
    print("edge cases:", counts)


if __name__ == "__main__":
    main()
