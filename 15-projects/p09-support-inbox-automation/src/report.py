"""
report.py - the daily summary report (Markdown) built from the queue database.

Managers do not read 200 emails; they read one page: how many came in, what
people wanted, how urgent, what is still waiting for approval.

Run:  python -m src.report                  # latest day in the queue
      python -m src.report --date 2026-11-18
Writes reports/daily_summary_<date>.md and prints it.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from .queue_db import connect

REPORTS = Path(__file__).resolve().parents[1] / "reports"


def build_report(day: str | None = None, con=None) -> tuple[str, str]:
    """Return (date, markdown text) for one day."""
    con = con or connect()
    if day is None:
        last = con.execute("SELECT MAX(substr(received_at, 1, 10)) AS d FROM tickets").fetchone()["d"]
        day = last or "no-data"
    rows = [dict(r) for r in con.execute("SELECT * FROM tickets WHERE substr(received_at, 1, 10) = ?", (day,))]
    tickets = [json.loads(r["ticket_json"]) for r in rows]
    intents = Counter(i for t in tickets for i in t["intents"])
    urgency = Counter(t["urgency"] for t in tickets)
    status = Counter(r["status"] for r in rows)
    products = Counter(t["product"] for t in tickets if t["product"])
    reasons = Counter(x for r in rows for x in json.loads(r["reasons"] or "[]"))
    all_pending = con.execute("SELECT COUNT(*) AS n FROM tickets WHERE status = 'pending_review'").fetchone()["n"]

    def table(counter: Counter, header: str) -> str:
        lines = [f"| {header} | count |", "|---|---|"] + [f"| {k} | {v} |" for k, v in counter.most_common()]
        return "\n".join(lines)

    urgent = [r for r, t in zip(rows, tickets) if t["urgency"] == "high" and r["status"] == "pending_review"][:5]
    md = "\n".join([
        f"# Support inbox - daily summary for {day}",
        "",
        f"- Emails received: **{len(rows)}**",
        f"- Waiting for human approval (this day): **{status.get('pending_review', 0)}** "
        f"(all days: {all_pending})",
        f"- Auto-filed: **{status.get('auto_filed', 0)}** · Spam discarded: **{status.get('discarded', 0)}** · "
        f"Approved: **{status.get('approved', 0)}** · Rejected: **{status.get('rejected', 0)}**",
        "",
        "## What customers wanted", table(intents, "intent"), "",
        "## Urgency", table(urgency, "urgency"), "",
        "## Products mentioned", table(products, "product"), "",
        "## Why emails were sent to a human", table(reasons, "reason"), "",
        "## Top urgent items waiting for approval",
        *([f"- #{r['id']} {r['sender']} - {r['subject']} ({', '.join(json.loads(r['reasons']))})" for r in urgent]
          or ["- none"]),
        "",
    ])
    return day, md


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD (default: latest day)")
    args = ap.parse_args()
    day, md = build_report(args.date)
    REPORTS.mkdir(exist_ok=True)
    out = REPORTS / f"daily_summary_{day}.md"
    out.write_text(md, encoding="utf-8")
    print(md)
    print(f"saved -> reports/{out.name}")


if __name__ == "__main__":
    main()
