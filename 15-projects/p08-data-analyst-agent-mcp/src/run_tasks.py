"""
run_tasks.py - run the 5 test tasks and check each agent run.

For every task in data/tasks.json we check two things:
  1. the **tool sequence** - did the agent call the expected tools in the expected
     order? (For an LLM planner we report it but only require the key tools to
     appear, because a good model may take a different, still-valid path.)
  2. the **answer** - does it contain the key facts (e.g. "North", "Kettle")?

This is a tiny version of **trajectory evaluation**, which real agent teams run in
CI to catch regressions when they change prompts or models.

Run:  python -m src.run_tasks            (planner chosen by PLANNER / LLM_PROVIDER in .env)
      python -m src.run_tasks --planner scripted
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import run_agent
from .planners import get_planner

DATA = Path(__file__).resolve().parents[1] / "data"


def check(task: dict, record: dict, strict: bool) -> dict:
    tools = record["tools"]
    if strict:
        seq_ok = tools == task["expected_tools"]
    else:                                   # every expected tool appears at least once
        seq_ok = set(task["expected_tools"]) <= set(tools)
    ans_ok = all(s.lower() in str(record["answer"]).lower() for s in task["answer_must_contain"])
    return {"id": task["id"], "tools_ok": seq_ok, "answer_ok": ans_ok, "tools": tools}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--planner", default=None, help="scripted | llm | auto")
    args = ap.parse_args()
    planner = get_planner(args.planner)
    tasks = json.loads((DATA / "tasks.json").read_text(encoding="utf-8"))
    results = []
    for t in tasks:
        rec = run_agent(t["question"], planner)
        res = check(t, rec, strict=planner.name == "scripted")
        results.append(res)
        flag = "PASS" if res["tools_ok"] and res["answer_ok"] else "FAIL"
        print(f"[{flag}] {t['id']} tools={res['tools']}\n       answer: {str(rec['answer'])[:150]}")
    passed = sum(r["tools_ok"] and r["answer_ok"] for r in results)
    print(f"\n{passed}/{len(tasks)} tasks passed with the {planner.name} planner")
    return passed


if __name__ == "__main__":
    main()
