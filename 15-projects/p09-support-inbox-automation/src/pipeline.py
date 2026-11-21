"""
pipeline.py - the plain-Python version of the whole workflow.

For each email:  extract -> find help article -> draft reply -> route -> save in the queue.

Run:
  python -m src.pipeline                       # all 200 emails in data/emails.jsonl (rules extractor)
  python -m src.pipeline --inbox data/inbox    # "watch" a folder of .eml / .json files (one pass)
  python -m src.pipeline --method llm --limit 5    # try the LLM extractor on 5 emails
  python -m src.pipeline --fresh               # delete the queue first

When the input has true labels (our synthetic emails do), it also prints accuracy.
"""
from __future__ import annotations

import argparse
import json
from email import policy
from email.parser import BytesParser
from pathlib import Path

from .extract import extract
from .queue_db import DB_PATH, connect, save
from .schema import Email, Ticket
from .workflow import draft_reply, find_article, route

DATA = Path(__file__).resolve().parents[1] / "data"


def process(email_data: dict, con, method: str = "rules", use_llm_draft: bool = False) -> dict:
    """Run every step for one email and store the result. Returns a JSON-friendly dict."""
    email = Email.model_validate(email_data)
    ticket, used = extract(email, method)
    article = find_article(ticket, email)
    draft = draft_reply(ticket, article, use_llm=use_llm_draft)
    where, reasons = route(ticket, email)
    email_id = email.id or f"anon-{abs(hash((email.sender, email.subject, email.body))) % 10**10}"
    row_id = save(con, email_id, email.received_at, email.sender, email.subject, ticket, article, where, reasons,
                  draft, used)
    return {"ticket_id": row_id, "email_id": email_id, "ticket": ticket.model_dump(), "route": where,
            "reasons": reasons, "article": article["slug"] if article else None, "draft": draft,
            "extract_method": used}


def read_inbox(folder: Path) -> list[dict]:
    """Read .json and .eml files from a folder into email dicts."""
    out = []
    for f in sorted(folder.iterdir()):
        if f.suffix == ".json":
            out.append(json.loads(f.read_text(encoding="utf-8")))
        elif f.suffix == ".eml":
            msg = BytesParser(policy=policy.default).parse(f.open("rb"))
            body = msg.get_body(preferencelist=("plain",))
            out.append({"id": f.stem, "from": str(msg["From"]), "subject": str(msg["Subject"] or ""),
                        "body": body.get_content() if body else "", "received_at": str(msg["Date"] or "")})
    return out


def evaluate(emails: list[dict], results: list[dict]) -> dict:
    """Compare extracted fields and routes with the true labels."""
    n = len(results)
    score = {"intents_exact": 0, "urgency": 0, "order_id": 0, "product": 0, "route": 0}
    for e, r in zip(emails, results):
        lab, t = e["labels"], r["ticket"]
        score["intents_exact"] += set(t["intents"]) == set(lab["intents"])
        score["urgency"] += t["urgency"] == lab["urgency"]
        score["order_id"] += t["order_id"] == lab["order_id"]
        score["product"] += t["product"] == lab["product"]
        truth = Ticket(customer_name=lab["customer_name"], customer_email=lab["customer_email"],
                       order_id=lab["order_id"], product=lab["product"], intents=lab["intents"],
                       urgency=lab["urgency"], sentiment=lab["sentiment"], summary="-")
        score["route"] += route(truth, Email.model_validate(e))[0] == r["route"]
    return {k: round(v / n, 3) for k, v in score.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", type=Path, help="folder of .eml/.json files instead of data/emails.jsonl")
    ap.add_argument("--method", choices=["rules", "llm"], default="rules")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--fresh", action="store_true", help="delete the queue database first")
    args = ap.parse_args()
    if args.fresh and DB_PATH.exists():
        DB_PATH.unlink()
    emails = read_inbox(args.inbox) if args.inbox else \
        [json.loads(line) for line in (DATA / "emails.jsonl").read_text(encoding="utf-8").splitlines()]
    if args.limit:
        emails = emails[:args.limit]
    con = connect()
    results = [process(e, con, args.method) for e in emails]
    routes: dict[str, int] = {}
    for r in results:
        routes[r["route"]] = routes.get(r["route"], 0) + 1
    methods: dict[str, int] = {}
    for r in results:
        methods[r["extract_method"]] = methods.get(r["extract_method"], 0) + 1
    print(f"processed {len(results)} emails | routes {routes} | extract methods {methods}")
    if all("labels" in e for e in emails):
        print("accuracy vs true labels:", evaluate(emails, results))
    ex = next((r for r in results if r["route"] == "human_review"), results[0])
    print(f"\nexample -> route={ex['route']} reasons={ex['reasons']}\n{json.dumps(ex['ticket'], indent=1)}\n{ex['draft']}")


if __name__ == "__main__":
    main()
