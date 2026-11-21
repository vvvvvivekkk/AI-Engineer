"""
api.py - a small FastAPI service so other tools (like n8n) can use the workflow over HTTP.

Endpoints:
  GET  /health                     is it up?
  POST /triage                     one email in -> extracted ticket, route, draft out (and saved in the queue)
  GET  /queue                      tickets waiting for human approval
  POST /queue/{id}/approve         {"reviewer": "...", "note": "...", "edited_draft": "..."}
  POST /queue/{id}/reject          {"reviewer": "...", "note": "..."}
  GET  /report/daily?date=YYYY-MM-DD   the daily summary as Markdown (n8n emails it every evening)

Run:  uvicorn src.api:app --port 8000   then open http://localhost:8000/docs
"""
from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from .pipeline import process
from .queue_db import connect, decide, pending
from .report import build_report
from .schema import Email

app = FastAPI(title="Support inbox triage", version="1.0")
METHOD = os.getenv("EXTRACT_METHOD", "rules")       # rules | llm


class Decision(BaseModel):
    reviewer: str
    note: str = ""
    edited_draft: str | None = None


@app.get("/health")
def health():
    return {"status": "ok", "extract_method": METHOD}


@app.post("/triage")
def triage(email: Email):
    """n8n's HTTP Request node posts {"from", "subject", "body", "id"?, "received_at"?} here."""
    with connect() as con:
        return process(email.model_dump(by_alias=True), con, METHOD)


@app.get("/queue")
def queue():
    with connect() as con:
        return {"pending": pending(con)}


def _decide(ticket_id: int, d: Decision, approve: bool):
    with connect() as con:
        try:
            return decide(con, ticket_id, approve, d.reviewer, d.note, d.edited_draft)
        except KeyError as e:
            raise HTTPException(404, str(e)) from e
        except ValueError as e:
            raise HTTPException(409, str(e)) from e      # 409 Conflict: already decided


@app.post("/queue/{ticket_id}/approve")
def approve(ticket_id: int, d: Decision):
    return _decide(ticket_id, d, True)


@app.post("/queue/{ticket_id}/reject")
def reject(ticket_id: int, d: Decision):
    return _decide(ticket_id, d, False)


@app.get("/report/daily", response_class=PlainTextResponse)
def daily_report(date: str | None = None):
    with connect() as con:
        return build_report(date, con)[1]
