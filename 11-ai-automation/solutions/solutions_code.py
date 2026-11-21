"""
solutions_code.py - runnable solutions for module 11's coding exercises (4, 5, 6, 7, 8, 11).

Run all:  python solutions_code.py      (offline; writes solutions/01b-ticket-triage-with-billing.json)
"""
import copy
import hashlib
import hmac
import json
import sys
import time
import uuid
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
WF_DIR = HERE.parent / "workflows"
sys.path.insert(0, str(HERE.parent / "code"))


# ----------------------------------------------------------------------------- 4
def ex4():
    from fastapi import FastAPI, Header, HTTPException, Request
    from fastapi.testclient import TestClient

    SECRET = "dev-secret"
    app = FastAPI()

    def sign(ts: str, body: bytes) -> str:
        return hmac.new(SECRET.encode(), ts.encode() + b"." + body, hashlib.sha256).hexdigest()

    @app.post("/hook")
    async def hook(request: Request, x_signature: str = Header(""), x_timestamp: str = Header("0")):
        body = await request.body()
        if not hmac.compare_digest(sign(x_timestamp, body), x_signature):
            raise HTTPException(401, "bad signature")
        if abs(time.time() - int(x_timestamp)) > 300:          # older than 5 minutes -> replay?
            raise HTTPException(401, "stale request")
        return {"ok": True}

    c = TestClient(app)
    body = b'{"event": "paid"}'
    for label, ts in [("fresh", str(int(time.time()))), ("stale", str(int(time.time()) - 3600))]:
        r = c.post("/hook", content=body, headers={"X-Timestamp": ts, "X-Signature": sign(ts, body)})
        print(f"ex4 {label}: {r.status_code} {r.json()}")


# ----------------------------------------------------------------------------- 5
def fetch_with_retry(client: httpx.Client, url: str, attempts: int = 3, backoff: float = 0.01):
    for i in range(attempts):
        try:
            r = client.get(url)
            r.raise_for_status()
            return r.text
        except httpx.HTTPError as e:
            time.sleep(backoff * 2 ** i)
            last = e
    print(f"WARNING: giving up on {url} after {attempts} attempts ({type(last).__name__})", file=sys.stderr)
    return None


def ex5():
    always_down = httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(503)))
    print("ex5 always 503 ->", fetch_with_retry(always_down, "https://x.test"))
    state = {"n": 0}

    def once_then_ok(req):
        state["n"] += 1
        return httpx.Response(503) if state["n"] == 1 else httpx.Response(200, text="hello")
    print("ex5 fail once ->", fetch_with_retry(httpx.Client(transport=httpx.MockTransport(once_then_ok)), "https://x.test"))


# ----------------------------------------------------------------------------- 6
def ex6() -> Path:
    wf = json.loads((WF_DIR / "01-webhook-ticket-triage.json").read_text(encoding="utf-8"))
    wf = copy.deepcopy(wf)
    wf["name"] = "01b Support ticket triage with billing branch"
    # A Switch node (rules mode) with three outputs: urgent, billing, everything else (fallback).
    def rule(value):
        return {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose"},
                               "conditions": [{"id": str(uuid.uuid4()), "leftValue": "={{ $json.category }}",
                                               "rightValue": value, "operator": {"type": "string", "operation": "equals"}}],
                               "combinator": "and"}}
    switch = {"parameters": {"rules": {"values": [rule("urgent"), rule("billing")]},
                             "options": {"fallbackOutput": "extra"}},
              "id": str(uuid.uuid4()), "name": "Route by category", "type": "n8n-nodes-base.switch",
              "typeVersion": 3.2, "position": [720, 300]}
    billing = copy.deepcopy(next(n for n in wf["nodes"] if n["name"] == "Email support team"))
    billing.update({"id": str(uuid.uuid4()), "name": "Email billing team", "position": [960, 560]})
    billing["parameters"]["toEmail"] = "billing@example.com"
    wf["nodes"] = [n for n in wf["nodes"] if n["name"] != "Is urgent?"] + [switch, billing]
    wf["connections"].pop("Is urgent?")
    wf["connections"]["Parse category"] = {"main": [[{"node": "Route by category", "type": "main", "index": 0}]]}
    wf["connections"]["Route by category"] = {"main": [
        [{"node": "Alert Slack", "type": "main", "index": 0}],          # output 0: urgent
        [{"node": "Email billing team", "type": "main", "index": 0}],   # output 1: billing
        [{"node": "Email support team", "type": "main", "index": 0}],   # output 2: fallback (general)
    ]}
    out = HERE / "01b-ticket-triage-with-billing.json"
    out.write_text(json.dumps(wf, indent=2), encoding="utf-8")
    from validate_workflows import validate
    print("ex6 wrote", out.name, "->", validate(wf) or "valid")
    return out


# ----------------------------------------------------------------------------- 7
def extra_checks(wf: dict) -> list[str]:
    warnings = []
    for n in wf["nodes"]:
        if n["type"] == "n8n-nodes-base.httpRequest" and "timeout" not in n["parameters"].get("options", {}):
            warnings.append(f"{n['name']}: HTTP Request without a timeout")
        for cred_type, ref in n.get("credentials", {}).items():
            if set(ref) - {"id", "name"}:
                warnings.append(f"{n['name']}: credential '{cred_type}' has extra keys {set(ref) - {'id', 'name'}}")
    return warnings


def ex7():
    for p in sorted(WF_DIR.glob("*.json")):
        print("ex7", p.name, "->", extra_checks(json.loads(p.read_text())) or "no warnings")
    bad = {"nodes": [{"name": "X", "type": "n8n-nodes-base.httpRequest", "parameters": {},
                      "credentials": {"httpHeaderAuth": {"id": "1", "name": "k", "value": "Bearer secret"}}}]}
    print("ex7 bad example ->", extra_checks(bad))


# ----------------------------------------------------------------------------- 8
FAQ = ["Refunds are processed within 5 working days.", "Reset your password from the login page.",
       "Support is available Monday to Friday, 9am to 6pm IST."]


def ex8():
    wf = json.loads((WF_DIR / "03-rag-answer-webhook.json").read_text(encoding="utf-8"))
    nodes = {n["name"]: n for n in wf["nodes"]}

    def run(node, item, hist):
        t = node["type"].split(".")[-1]
        if t == "webhook":
            return item, 0
        if t == "httpRequest" and "search" in node["parameters"]["url"]:
            q = set(item["body"]["question"].lower().split())
            ctx = [d for d in FAQ if q & set(d.lower().strip(".").split())]
            return {"question": item["body"]["question"], "context": ctx}, 0
        if t == "if":
            return item, 0 if len(item["context"]) > 0 else 1
        if t == "httpRequest":                              # the LLM: answer from first context passage
            return {"choices": [{"message": {"content": "From our docs: " + item["context"][0]}}]}, 0
        if t == "respondToWebhook":
            if "choices" in item:
                return {"answer": item["choices"][0]["message"]["content"], "sources": hist["Search knowledge base"]["context"]}, 0
            return {"answer": "Sorry, I could not find that in our documents.", "sources": []}, 0
        raise ValueError(t)

    for question in ["how many days for refunds", "do you sell bicycles"]:
        cur, item, hist = "Question webhook", {"body": {"question": question}}, {}
        while cur:
            item, out = run(nodes[cur], item, hist)
            hist[cur] = item
            branches = wf["connections"].get(cur, {}).get("main", [])
            cur = branches[out][0]["node"] if out < len(branches) and branches[out] else None
        print(f"ex8 {question!r} -> {item}")


# ----------------------------------------------------------------------------- 11
SITE = {
    "/": ["/orders", "/help", "https://evil.example/promo"],
    "/orders": ["/orders/A17", "/"],
    "/orders/A17": ["/"],
    "/help": ["/"],
}


def guarded_browser(clicks, max_steps=10):
    url, visits, audit = "/", {"/": 1}, []
    for step, idx in enumerate(clicks[:max_steps], 1):
        target = SITE[url][idx]
        if not (target == "/" or target.startswith("/orders") or target == "/help"):
            audit.append((step, "BLOCKED", target)); continue          # (a) allow-list
        url = target
        visits[url] = visits.get(url, 0) + 1
        audit.append((step, "visit", url))                              # (c) audit log
        if visits[url] >= 3:
            audit.append((step, "STOP: loop detected", url)); break     # (b) loop detector
    return audit


def ex11():
    print("ex11 evil link:", guarded_browser([2, 0, 0]))
    print("ex11 looping:  ", guarded_browser([0, 1, 0, 1, 0, 1]))


if __name__ == "__main__":
    for fn in [ex4, ex5, ex6, ex7, ex8, ex11]:
        fn()
