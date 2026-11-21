"""
agent.py - the hand-written tool-calling loop (the "ReAct" pattern).

**Agent** - a program where a model decides, step by step, which tool to use
next, sees the result, and decides again, until it can answer. **ReAct** =
"reason + act": think, call a tool, observe, repeat. Analogy: a detective who
asks one question at a time and changes the next question based on the answer.

The loop below is deliberately small so every line can be read:
  * max_steps   - a hard stop so a confused model cannot loop forever (and burn money)
  * errors      - a failing tool does not crash the agent; the error text goes back
                  to the planner as the observation so it can fix its next call
  * invalid     - if the model's reply cannot be understood, we record it and retry
                  (twice in a row -> give up)
  * trajectory  - every step is logged to logs/trajectories.jsonl for debugging and tests

Run:  python -m src.agent "Which region's revenue fell most last quarter, and why?"
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from .planners import get_planner
from .tools import call_tool

LOG = Path(__file__).resolve().parents[1] / "logs" / "trajectories.jsonl"


def run_agent(question: str, planner=None, max_steps: int = 8, log: bool = True) -> dict:
    planner = planner or get_planner()
    history: list[dict] = []          # each item: {"tool", "args", "result"}
    invalid_in_a_row, answer = 0, None
    start = time.perf_counter()
    for _ in range(max_steps):
        try:
            action = planner.next_action(question, history)
        except Exception as e:                                   # e.g. missing API key, no Ollama
            answer = f"Planner error: {e}"
            break
        if "invalid" in action:                                  # the model's reply was not valid JSON
            invalid_in_a_row += 1
            history.append({"tool": "_invalid_reply", "args": {}, "result": {"error": action["invalid"]}})
            if invalid_in_a_row >= 2:
                answer = "Stopped: the model did not return a valid action twice in a row."
                break
            continue
        invalid_in_a_row = 0
        if "final" in action:
            answer = action["final"]
            break
        result = call_tool(action["tool"], action.get("args", {}))   # errors come back as {"error": ...}
        history.append({"tool": action["tool"], "args": action.get("args", {}), "result": result})
    else:
        answer = f"Stopped after {max_steps} steps without a final answer."
    record = {"question": question, "planner": planner.name, "answer": answer,
              "tools": [h["tool"] for h in history], "steps": history,
              "seconds": round(time.perf_counter() - start, 2)}
    if log:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")
    return record


def main():
    q = " ".join(sys.argv[1:]) or "Which region's revenue fell most last quarter, and why?"
    rec = run_agent(q)
    for i, s in enumerate(rec["steps"], 1):
        print(f"[{i}] {s['tool']}({json.dumps(s['args'])[:120]})\n     -> {json.dumps(s['result'], default=str)[:200]}")
    print(f"\nANSWER ({rec['planner']} planner): {rec['answer']}")


if __name__ == "__main__":
    main()
