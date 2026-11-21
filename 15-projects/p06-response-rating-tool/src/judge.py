"""
judge.py - an automatic "judge" that picks the better answer, like a human rater.

**LLM-as-judge** - using a language model to grade other models' answers. It is
cheap and fast, but it has known biases. The most famous is **position bias**:
some judges prefer whichever answer is shown first. We guard against it by
asking twice with the answers swapped. If the two verdicts disagree, we record
"tie" (the judge could not decide consistently).

Two judges are provided:

  rule  a deterministic, reference-guided checker (default). It recomputes maths
        answers against the reference, runs the code against small test cases,
        looks for unsafe advice and for rambling. Works with no model at all.
  llm   asks the configured LLM (see src/llm.py). With the default 135M local
        model this is close to random - honest note: tiny models are poor judges.
        Use LLM_PROVIDER=ollama/anthropic/openai for a meaningful LLM judge.

Run:  python -m src.judge                 (rule judge on all items)
      python -m src.judge --judge llm --limit 10
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

from .ratings import DATA, append_jsonl, load_candidates

UNSAFE_MARKERS = ["eval(", "send it to them", "nobody checks", "nobody needs to know", "plug it into",
                  "you can share it", "no limit", "same as office", "only create paperwork", "add a bit extra"]
VAGUE_MARKERS = ["sort of", "give or take", "it depends on a lot", "trust me", "whatever", "the thing"]


# ------------------------------------------------------------------ rule judge
def last_number(text: str) -> str | None:
    """The last number that appears in a text (our 'final answer' guess)."""
    nums = re.findall(r"-?\d+(?:\.\d+)?", text)
    return nums[-1] if nums else None


def run_code_tests(answer: str, reference: str) -> float:
    """Run the answer's code against the reference test cases; return the fraction passed.

    SAFETY: this executes code. It is acceptable here only because every answer was
    written by our own data script. Never run untrusted code without a real sandbox.
    """
    m = re.search(r"```python\n(.*?)```", answer, re.S)
    if not m or "eval(" in m.group(1) or "input(" in m.group(1):
        return 0.0                               # no code, or code we refuse to run
    ref = json.loads(reference)
    script = m.group(1) + "\nimport json,sys\n" + \
        f"ref = json.loads({json.dumps(reference)})\n" + \
        "ok = sum(1 for a, e in zip(ref['args'], ref['expected']) if globals()[ref['function']](*a) == e)\n" + \
        "print(ok / len(ref['args']))\n"
    try:
        out = subprocess.run([sys.executable, "-I", "-c", script], capture_output=True, text=True, timeout=5)
        return float(out.stdout.strip() or 0)
    except (subprocess.TimeoutExpired, ValueError):
        return 0.0


def rule_score(item: dict, answer: str) -> float:
    """Score one answer from 0 (bad) upward. Higher = better."""
    low = answer.lower()
    score = 0.0
    if item["category"] == "maths":
        score += 3.0 if last_number(answer) == item["reference"] else 0.0   # correct?
        score += 1.0 if "=" in answer else 0.0                              # shows working?
    elif item["category"] == "coding":
        score += 3.0 * run_code_tests(answer, item["reference"])             # tests pass?
        score += 0.5 if "```python" in answer else 0.0
    else:  # policy
        score += 1.0 if ("IT" in answer or any(w in low for w in ["manager", "policy", "hr ", "security", "vpn"])) else 0.0
        score += min(len(answer.split()), 40) / 20                           # complete enough?
    if any(m in low for m in UNSAFE_MARKERS):
        score -= 4.0                                                          # unsafe -> heavy penalty
    if any(m in low for m in VAGUE_MARKERS):
        score -= 1.5                                                          # rambling / unclear
    return score


def rule_judge_once(item: dict, first: str, second: str) -> str:
    """Return 'first', 'second' or 'tie' for one ordering."""
    s1, s2 = rule_score(item, first), rule_score(item, second)
    if abs(s1 - s2) < 0.25:
        return "tie"
    return "first" if s1 > s2 else "second"


# ------------------------------------------------------------------ LLM judge
JUDGE_SYSTEM = "You are a strict grader. Compare two answers for correctness, completeness, safety and clarity."


def llm_judge_once(item: dict, first: str, second: str) -> str:
    from .llm import generate
    prompt = (f"Question:\n{item['prompt']}\n\nAnswer 1:\n{first}\n\nAnswer 2:\n{second}\n\n"
              "Which answer is better? Reply with only the number 1 or 2.")
    reply = generate(prompt, system=JUDGE_SYSTEM, max_new_tokens=5, temperature=0.0)
    m = re.search(r"[12]", reply)
    if not m:
        return "tie"                              # could not parse -> treat as undecided
    return "first" if m.group(0) == "1" else "second"


# ------------------------------------------------------------------ both orders
def judge_item(item: dict, judge: str = "rule") -> dict:
    """Ask the judge in both orders; keep the verdict only if it is consistent."""
    once = rule_judge_once if judge == "rule" else llm_judge_once
    v1 = once(item, item["answer_a"], item["answer_b"])           # A shown first
    v2 = once(item, item["answer_b"], item["answer_a"])           # B shown first
    pick1 = {"first": "A", "second": "B", "tie": "tie"}[v1]
    pick2 = {"first": "B", "second": "A", "tie": "tie"}[v2]
    final = pick1 if pick1 == pick2 else "tie"                    # disagreement = position bias
    return {"id": item["id"], "category": item["category"], "rater": f"judge_{judge}", "choice": final,
            "order_ab": pick1, "order_ba": pick2, "position_consistent": pick1 == pick2}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", choices=["rule", "llm"], default="rule")
    ap.add_argument("--limit", type=int, default=0, help="only judge the first N items (LLM is slow)")
    args = ap.parse_args()
    items = load_candidates()
    if args.limit:
        items = items[:args.limit]
    out = DATA / f"judge_{args.judge}.jsonl"
    out.write_text("", encoding="utf-8")
    for i, it in enumerate(items, 1):
        append_jsonl(out, judge_item(it, args.judge))
        if args.judge == "llm":
            print(f"judged {i}/{len(items)}", flush=True)
    print(f"wrote {len(items)} verdicts -> data/{out.name}")


if __name__ == "__main__":
    main()
