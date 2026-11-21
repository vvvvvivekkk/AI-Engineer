"""
prompt_eval.py - test a prompt against a small, fixed set of examples and report a score.

Analogy: a driving test route. Same streets for every candidate (prompt
version), same checklist, so you can compare candidates fairly. Change the
prompt -> rerun the route -> did the score go up or down?

Run it:  python code/prompt_eval.py            (uses the offline local model unless an API key is set)
"""
import csv                                     # write results to a CSV file you can open in Excel
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # let Python find our sibling files
from llm_client import call_llm, backend_name   # noqa: E402  (our one-function model wrapper)
from prompt_templates import REGISTRY           # noqa: E402  (versioned prompt cards)

# Each test case: an input, the answer we expect, and how to check it.
TEST_CASES = [
    {"id": "T01", "ticket": "I was charged twice for the same order", "expected": "billing"},
    {"id": "T02", "ticket": "My parcel has not arrived after 10 days", "expected": "delivery"},
    {"id": "T03", "ticket": "The zip on the jacket broke on day one", "expected": "product"},
    {"id": "T04", "ticket": "I cannot log in, password reset email never comes", "expected": "account"},
    {"id": "T05", "ticket": "Please refund the extra fee on my card", "expected": "billing"},
    {"id": "T06", "ticket": "Courier left the box at the wrong house", "expected": "delivery"},
    {"id": "T07", "ticket": "How do I change the email on my profile?", "expected": "account"},
    {"id": "T08", "ticket": "The tent poles are shorter than described", "expected": "product"},
]
ALLOWED = {"billing", "delivery", "product", "account"}


def grade(reply: str, expected: str) -> dict:
    """Three simple checks. Each returns True/False so we can count them."""
    first_word = reply.strip().split()[0].strip(".,:;!\"'").lower() if reply.strip() else ""
    return {
        "format_ok": first_word in ALLOWED and len(reply.split()) <= 3,   # did it obey "one word only"?
        "correct": first_word == expected,                               # is the label right?
    }


def run(version: str) -> list[dict]:
    tpl = REGISTRY.get("classify_ticket", version)
    rows = []
    for case in TEST_CASES:
        system, user = tpl.render(ticket=case["ticket"])
        start = time.time()
        reply = call_llm(system, user, max_tokens=8, examples=list(tpl.examples))                 # short answers only
        rows.append({"version": version, "fingerprint": tpl.fingerprint(), "id": case["id"],
                     "input": case["ticket"], "expected": case["expected"], "reply": reply,
                     **grade(reply, case["expected"]), "seconds": round(time.time() - start, 2)})
    return rows


if __name__ == "__main__":
    print("Backend:", backend_name())
    all_rows = []
    for v in ["v1", "v2", "v3"]:
        rows = run(v)
        all_rows += rows
        acc = sum(r["correct"] for r in rows) / len(rows)
        fmt = sum(r["format_ok"] for r in rows) / len(rows)
        print(f"{v}: accuracy {acc:.0%}, format obeyed {fmt:.0%}")
    out = Path(__file__).parent / "prompt_eval_results.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader(); writer.writerows(all_rows)
    print("Saved", out)
