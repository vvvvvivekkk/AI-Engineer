"""
make_n8n.py - write the importable n8n workflow (n8n/support_triage_workflow.json).

**n8n** - an open-source, visual workflow tool: you connect boxes ("nodes") such
as "when an email arrives" -> "call this web address" -> "post to Slack".
Here n8n does the plumbing (email in, alerts out, daily schedule) and calls our
FastAPI service for the thinking (extraction, routing, drafting).

We generate the JSON from Python so it is easy to read and to keep consistent
with the API. Import it in n8n with: Workflows -> Import from File.
All credentials are PLACEHOLDERS - you must create your own in n8n.

Run:  python -m src.make_n8n
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "n8n" / "support_triage_workflow.json"
API = "http://host.docker.internal:8000"     # how a Dockerised n8n reaches a FastAPI app on your computer


def nid(name: str) -> str:
    """Stable node ids (the same every time we regenerate)."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "p09/" + name))


def node(name, type_, version, position, parameters, credentials=None):
    n = {"parameters": parameters, "id": nid(name), "name": name, "type": type_, "typeVersion": version,
         "position": position}
    if credentials:
        n["credentials"] = credentials
    return n


def placeholder(kind: str, label: str) -> dict:
    return {kind: {"id": "REPLACE_WITH_YOUR_CREDENTIAL_ID", "name": f"{label} (placeholder - create your own)"}}


def build() -> dict:
    nodes = [
        node("IMAP Email Trigger", "n8n-nodes-base.emailReadImap", 2, [0, 0],
             {"mailbox": "INBOX", "postProcessAction": "read", "format": "simple", "options": {}},
             placeholder("imap", "Support mailbox IMAP")),
        node("Manual Trigger (test)", "n8n-nodes-base.manualTrigger", 1, [0, 220], {}),
        node("Sample email", "n8n-nodes-base.set", 3.4, [220, 220], {
            "assignments": {"assignments": [
                {"id": nid("s-from"), "name": "from", "value": "Asha Rao <asha.rao@gmail.com>", "type": "string"},
                {"id": nid("s-subj"), "name": "subject", "value": "DAMAGED ITEM!!!", "type": "string"},
                {"id": nid("s-body"), "name": "textPlain", "type": "string",
                 "value": "My SmartKettle 2 (order ORD-12345) arrived damaged and it started smoking! I want a refund."},
                {"id": nid("s-date"), "name": "date", "value": "2026-11-20T09:15:00", "type": "string"}]},
            "options": {}}),
        node("Map email fields", "n8n-nodes-base.set", 3.4, [440, 100], {
            "assignments": {"assignments": [
                {"id": nid("m-from"), "name": "from", "value": "={{ $json.from }}", "type": "string"},
                {"id": nid("m-subj"), "name": "subject", "value": "={{ $json.subject }}", "type": "string"},
                {"id": nid("m-body"), "name": "body", "value": "={{ $json.textPlain }}", "type": "string"},
                {"id": nid("m-date"), "name": "received_at", "value": "={{ $json.date }}", "type": "string"}]},
            "options": {}}),
        node("POST /triage", "n8n-nodes-base.httpRequest", 4.2, [660, 100], {
            "method": "POST", "url": f"{API}/triage", "sendBody": True, "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({ from: $json.from, subject: $json.subject, body: $json.body, "
                        "received_at: $json.received_at }) }}",
            "options": {"timeout": 60000}}),
        node("Needs human approval?", "n8n-nodes-base.if", 2, [880, 100], {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                           "conditions": [{"id": nid("cond-route"), "leftValue": "={{ $json.route }}",
                                           "rightValue": "human_review",
                                           "operator": {"type": "string", "operation": "equals"}}],
                           "combinator": "and"},
            "options": {}}),
        node("Alert reviewers (Slack)", "n8n-nodes-base.slack", 2.2, [1100, 0], {
            "select": "channel", "channelId": {"__rl": True, "value": "#support-approvals", "mode": "name"},
            "text": "=:rotating_light: Ticket #{{ $json.ticket_id }} needs approval\n"
                    "Reasons: {{ $json.reasons.join(', ') }}\nSummary: {{ $json.ticket.summary }}\n"
                    f"Review: {API.replace('host.docker.internal', 'localhost')}/docs (POST /queue/{{{{ $json.ticket_id }}}}/approve)",
            "otherOptions": {}},
            placeholder("slackApi", "Slack bot token")),
        node("Auto-filed (no action)", "n8n-nodes-base.noOp", 1, [1100, 200], {}),
        node("Every day at 18:00", "n8n-nodes-base.scheduleTrigger", 1.2, [0, 460],
             {"rule": {"interval": [{"field": "days", "triggerAtHour": 18}]}}),
        node("GET /report/daily", "n8n-nodes-base.httpRequest", 4.2, [220, 460], {
            "method": "GET", "url": f"{API}/report/daily",
            "options": {"response": {"response": {"responseFormat": "text"}}}}),
        node("Email report to manager", "n8n-nodes-base.emailSend", 2.1, [440, 460], {
            "fromEmail": "support-bot@gadgetco.example", "toEmail": "support-manager@gadgetco.example",
            "subject": "=Support inbox daily summary {{ $now.toFormat('yyyy-MM-dd') }}",
            "emailFormat": "text", "text": "={{ $json.data }}", "options": {}},
            placeholder("smtp", "Outgoing mail SMTP")),
    ]

    def link(*targets):
        return {"main": [[{"node": t, "type": "main", "index": 0} for t in targets]]}

    connections = {
        "IMAP Email Trigger": link("Map email fields"),
        "Manual Trigger (test)": link("Sample email"),
        "Sample email": link("Map email fields"),
        "Map email fields": link("POST /triage"),
        "POST /triage": link("Needs human approval?"),
        # an IF node has two outputs: index 0 = true, index 1 = false
        "Needs human approval?": {"main": [[{"node": "Alert reviewers (Slack)", "type": "main", "index": 0}],
                                           [{"node": "Auto-filed (no action)", "type": "main", "index": 0}]]},
        "Every day at 18:00": link("GET /report/daily"),
        "GET /report/daily": link("Email report to manager"),
    }
    return {"name": "P9 Support inbox triage (calls FastAPI)", "nodes": nodes, "connections": connections,
            "active": False, "settings": {"executionOrder": "v1"}, "pinData": {},
            "meta": {"templateCredsSetupCompleted": False}, "tags": []}


def main():
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(build(), indent=2), encoding="utf-8")
    print(f"wrote {OUT.relative_to(OUT.parents[1])}")


if __name__ == "__main__":
    main()
