"""Tests: schema validation, extraction edge cases, routing, the approval queue, the API and the n8n JSON."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from src.api import app
from src.extract import rule_extract
from src.schema import Email, Ticket
from src.workflow import route

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def mail(body, subject="Help", sender="Asha Rao <asha@x.com>"):
    return Email.model_validate({"from": sender, "subject": subject, "body": body})


def test_schema_rejects_bad_values():
    with pytest.raises(ValidationError):
        Ticket(customer_email="a@b.c", order_id="12345", intents=["refund"], urgency="low",
               sentiment="neutral", summary="x")                                 # bad order id format
    with pytest.raises(ValidationError):
        Ticket(customer_email="a@b.c", product="iPhone", intents=["refund"], urgency="low",
               sentiment="neutral", summary="x")                                 # unknown product
    with pytest.raises(ValidationError):
        Ticket(customer_email="a@b.c", intents=[], urgency="low", sentiment="neutral", summary="x")


def test_two_intents_and_quoted_old_order_ignored():
    t = rule_extract(mail("My FitBand Pro (order ORD-11111) came with a cracked case. I would like a refund.\n"
                          "> On Monday I wrote:\n> My previous order ORD-99999 was fine."))
    assert set(t.intents) == {"damaged_item", "refund"}
    assert t.order_id == "ORD-11111" and t.product == "FitBand Pro"


def test_missing_order_angry_and_legal_go_to_human():
    e = mail("WHERE IS MY PARCEL. This is UNACCEPTABLE. I am talking to my lawyer about this.")
    t = rule_extract(e)
    assert t.order_id is None and t.sentiment == "angry" and t.urgency == "high"
    where, reasons = route(t, e)
    assert where == "human_review" and "legal / chargeback threat" in reasons


def test_spam_is_discarded_and_phone_is_not_an_order_id():
    spam = mail("Click here, you WON a cruise. Unsubscribe anytime.", sender="deals@promo.example")
    assert route(rule_extract(spam), spam)[0] == "discard"
    t = rule_extract(mail("How do I connect my SoundBuds X to the app?\nThanks\nPhone: +91 98123-45678"))
    assert t.order_id is None and t.intents == ["technical_support"] and t.urgency == "low"


def test_routine_email_is_auto_filed():
    e = mail("How do I connect my HomeCam 360 to the app? The pairing keeps failing.")
    assert route(rule_extract(e), e) == ("auto", [])


def test_rule_extractor_accuracy_on_dataset():
    emails = [json.loads(l) for l in (ROOT / "data" / "emails.jsonl").read_text().splitlines()]
    hits = sum(set(rule_extract(Email.model_validate(e)).intents) == set(e["labels"]["intents"]) for e in emails)
    assert hits / len(emails) >= 0.95


def test_api_triage_queue_approve_and_report():
    r = client.post("/triage", json={"id": "t1", "from": "Ben <ben@x.com>", "subject": "Damaged",
                                     "body": "My SmartKettle 2 (order ORD-12345) arrived damaged and started smoking!",
                                     "received_at": "2026-11-20T10:00:00"})
    body = r.json()
    assert r.status_code == 200 and body["route"] == "human_review" and body["article"] == "safety-issues"
    again = client.post("/triage", json={"id": "t1", "from": "Ben <ben@x.com>", "subject": "Damaged",
                                         "body": "duplicate delivery of the same email"}).json()
    assert again["ticket_id"] == body["ticket_id"]                       # idempotent: same email id, same row
    ids = [p["id"] for p in client.get("/queue").json()["pending"]]
    assert body["ticket_id"] in ids
    ok = client.post(f"/queue/{body['ticket_id']}/approve", json={"reviewer": "maya", "note": "fine"})
    assert ok.status_code == 200 and ok.json()["status"] == "approved"
    twice = client.post(f"/queue/{body['ticket_id']}/approve", json={"reviewer": "maya"})
    assert twice.status_code == 409                                      # cannot decide twice
    assert client.post("/queue/99999/reject", json={"reviewer": "maya"}).status_code == 404
    report = client.get("/report/daily", params={"date": "2026-11-20"}).text
    assert "daily summary for 2026-11-20" in report and "Approved: **1**" in report


def test_n8n_workflow_is_consistent_with_the_api():
    wf = json.loads((ROOT / "n8n" / "support_triage_workflow.json").read_text())
    names = [n["name"] for n in wf["nodes"]]
    assert len(names) == len(set(names))                                 # unique node names
    for n in wf["nodes"]:
        assert n["type"].startswith("n8n-nodes-base.") and {"id", "typeVersion", "position", "parameters"} <= set(n)
        for cred in n.get("credentials", {}).values():
            assert cred["id"] == "REPLACE_WITH_YOUR_CREDENTIAL_ID"       # placeholders only
    for src, conn in wf["connections"].items():
        assert src in names
        for output in conn["main"]:
            for target in output:
                assert target["node"] in names
    routes = {r.path for r in app.routes}
    http = [n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.httpRequest"]
    for n in http:
        assert n["parameters"]["url"].split("8000", 1)[1] in routes      # every URL exists in our API
    triage = next(n for n in http if n["parameters"]["url"].endswith("/triage"))
    sent = {"from", "subject", "body", "received_at"}
    assert all(f"{k}:" in triage["parameters"]["jsonBody"] for k in sent)
    assert sent <= {f.alias or k for k, f in Email.model_fields.items()}  # fields match the Pydantic model
