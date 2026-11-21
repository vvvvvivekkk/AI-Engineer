"""
queue_db.py - the approval queue, stored in SQLite.

**SQLite** - a full SQL database in a single file (data/queue.db by default).
Every processed email becomes one row in the `tickets` table with a status:

  pending_review  waiting for a person (route = human_review)
  approved        a person approved (optionally edited) the draft -> ready to send
  rejected        a person rejected it (with a note)
  auto_filed      routine email; draft filed automatically
  discarded       spam

Analogy: an in-tray on a manager's desk. Nothing risky leaves the building
until someone signs it.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(os.getenv("QUEUE_DB", Path(__file__).resolve().parents[1] / "data" / "queue.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id TEXT UNIQUE,            -- the same email is never queued twice
    received_at TEXT,
    sender TEXT,
    subject TEXT,
    ticket_json TEXT,                -- the extracted fields as JSON
    article TEXT,
    route TEXT,
    reasons TEXT,
    draft TEXT,
    status TEXT,
    reviewer TEXT,
    review_note TEXT,
    decided_at TEXT,
    extract_method TEXT
);
"""


def connect(path: Path | None = None) -> sqlite3.Connection:
    con = sqlite3.connect(path or DB_PATH)
    con.row_factory = sqlite3.Row            # rows behave like dictionaries
    con.executescript(SCHEMA)
    return con


def save(con, email_id, received_at, sender, subject, ticket, article, route, reasons, draft, method) -> int:
    """Insert one processed email (or return the existing row id if it was already processed)."""
    status = {"human_review": "pending_review", "auto": "auto_filed", "discard": "discarded"}[route]
    cur = con.execute(
        "INSERT OR IGNORE INTO tickets(email_id, received_at, sender, subject, ticket_json, article, route, reasons, "
        "draft, status, extract_method) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (email_id, received_at, sender, subject, ticket.model_dump_json(), article["slug"] if article else None,
         route, json.dumps(reasons), draft, status, method))
    con.commit()
    if cur.rowcount == 0:                    # already there -> idempotent
        return con.execute("SELECT id FROM tickets WHERE email_id = ?", (email_id,)).fetchone()["id"]
    return cur.lastrowid


def pending(con) -> list[dict]:
    rows = con.execute("SELECT * FROM tickets WHERE status = 'pending_review' ORDER BY received_at").fetchall()
    return [dict(r) for r in rows]


def decide(con, ticket_id: int, approve: bool, reviewer: str, note: str = "", edited_draft: str | None = None) -> dict:
    """Approve or reject a pending ticket. Only pending tickets can be decided."""
    row = con.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    if row is None:
        raise KeyError(f"ticket {ticket_id} not found")
    if row["status"] != "pending_review":
        raise ValueError(f"ticket {ticket_id} is '{row['status']}', not pending_review")
    con.execute("UPDATE tickets SET status = ?, reviewer = ?, review_note = ?, decided_at = ?, draft = ? WHERE id = ?",
                ("approved" if approve else "rejected", reviewer, note, time.strftime("%Y-%m-%dT%H:%M:%S"),
                 edited_draft if edited_draft is not None else row["draft"], ticket_id))
    con.commit()
    return dict(con.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone())
