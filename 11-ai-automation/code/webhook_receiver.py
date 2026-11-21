"""
webhook_receiver.py - a small FastAPI app that RECEIVES webhooks and does work.

A webhook is an HTTP request that another system sends to YOUR URL when something
happens ("a form was submitted", "a payment succeeded"). Think of it as a doorbell:
you don't keep checking the door (polling) - the visitor rings when they arrive.

Endpoints
---------
GET  /health              -> {"status": "ok"} (used by monitors and n8n to check we are alive)
POST /webhook/ticket      -> receives a support ticket, checks its signature, classifies it, routes it
POST /search              -> tiny keyword (BM25) search over FAQ text; workflow 03 (RAG) calls this

Run
---
    pip install fastapi uvicorn rank_bm25
    export WEBHOOK_SECRET=change-me          # shared secret, same value in the sender
    uvicorn webhook_receiver:app --reload --port 8000
Then in another terminal:  python send_test_webhook.py

Security notes
--------------
* Anyone on the internet can call a public URL. We verify an HMAC signature
  (a fingerprint made from the body + a shared secret) so only senders who know
  the secret are accepted.
* Respond fast (under a few seconds). Senders retry if you are slow, which can
  cause duplicates - so we also de-duplicate by event id (idempotency).
"""
import hashlib   # hash functions (SHA-256) for the signature
import hmac      # HMAC = keyed hash; compare_digest avoids timing attacks
import os
import time

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request  # web framework pieces
from pydantic import BaseModel, Field, ValidationError                         # data validation

app = FastAPI(title="Automation webhook receiver")

SECRET = os.getenv("WEBHOOK_SECRET", "dev-secret-change-me")   # never hard-code real secrets
SEEN_EVENT_IDS: set[str] = set()      # remembers processed events (use a database in production)
OUTBOX: list[dict] = []               # where "sent" notifications go in this demo


class Ticket(BaseModel):
    """The JSON body we expect. Anything that doesn't match is rejected with HTTP 422."""
    event_id: str = Field(..., description="Unique id from the sender, used to skip duplicates")
    email: str
    subject: str
    message: str


def sign(body: bytes, secret: str = SECRET) -> str:
    """Compute the signature the sender should put in the X-Signature header."""
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def classify(ticket: Ticket) -> str:
    """Rule-based classifier. In n8n workflow 01 this step is an LLM call instead."""
    text = f"{ticket.subject} {ticket.message}".lower()
    if any(w in text for w in ["refund", "charged", "invoice", "payment"]):
        return "billing"
    if any(w in text for w in ["down", "error", "crash", "urgent", "outage"]):
        return "urgent"
    return "general"


def notify(category: str, ticket: Ticket) -> None:
    """Runs AFTER we have replied (background task) so the sender isn't kept waiting."""
    time.sleep(0.1)                                           # pretend to call Slack / email
    OUTBOX.append({"to": "#support-urgent" if category == "urgent" else "support@example.com",
                   "text": f"[{category}] {ticket.subject} from {ticket.email}"})


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/webhook/ticket")
async def receive_ticket(request: Request, background: BackgroundTasks,
                         x_signature: str = Header(default="")) -> dict:
    body = await request.body()                               # raw bytes: the signature is over these exact bytes
    if not hmac.compare_digest(sign(body), x_signature):      # wrong or missing signature -> reject
        raise HTTPException(status_code=401, detail="bad signature")
    try:
        ticket = Ticket.model_validate_json(body)             # parse + validate JSON into a Ticket
    except ValidationError as e:                              # missing/wrong fields -> 422
        raise HTTPException(status_code=422, detail=[{"loc": err["loc"], "msg": err["msg"]} for err in e.errors()])
    if ticket.event_id in SEEN_EVENT_IDS:                     # duplicate delivery -> do nothing again
        return {"status": "duplicate", "event_id": ticket.event_id}
    SEEN_EVENT_IDS.add(ticket.event_id)
    category = classify(ticket)
    background.add_task(notify, category, ticket)             # slow work happens after the reply
    return {"status": "accepted", "category": category}


# ------------------------------------------------------------------ tiny search API
FAQ = [
    "Refunds are processed within 5 working days to the original payment method.",
    "You can reset your password from the login page using 'Forgot password'.",
    "Our support team is available Monday to Friday, 9am to 6pm IST.",
    "Invoices can be downloaded from Settings > Billing > Invoices.",
]


class Query(BaseModel):
    question: str
    k: int = 2


@app.post("/search")
def search(q: Query) -> dict:
    from rank_bm25 import BM25Okapi                           # keyword ranking from module 09
    bm25 = BM25Okapi([doc.lower().split() for doc in FAQ])
    scores = bm25.get_scores(q.question.lower().split())
    best = sorted(range(len(FAQ)), key=lambda i: -scores[i])[: q.k]
    return {"question": q.question, "context": [FAQ[i] for i in best if scores[i] > 0]}  # drop non-matches
