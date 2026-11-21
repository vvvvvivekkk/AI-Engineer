"""
hitl_guard.py - safety rails and human-in-the-loop (HITL) approval for agent tool calls.

Ideas shown:
  * allow-list   : the agent may only use tools we listed.
  * risk levels  : "read" tools run automatically, "write"/"money" tools need a human yes.
  * budgets      : stop after N tool calls (protects your wallet and stops runaway loops).
  * audit log    : every decision is recorded so a human can review it later.

Run interactively:   python hitl_guard.py
Run without typing:  python hitl_guard.py --auto-deny
"""
import sys
import time

TOOL_RISK = {                       # allow-list + risk level for each tool
    "search_docs": "read",
    "send_email": "write",
    "issue_refund": "money",
}
AUDIT_LOG: list[dict] = []          # in production write this to a file or database


def ask_human(tool: str, args: dict, auto_answer: str | None = None) -> bool:
    """Ask a person to approve. auto_answer lets tests/notebooks run without typing."""
    question = f"Agent wants to run {tool}({args}). Approve? [y/N] "
    answer = auto_answer if auto_answer is not None else input(question)
    print(question + (answer if auto_answer is not None else ""))
    return answer.strip().lower() in {"y", "yes"}


def guarded_call(tool: str, args: dict, run_fn, auto_answer: str | None = None) -> str:
    risk = TOOL_RISK.get(tool)
    if risk is None:                                         # not on the allow-list
        decision, result = "blocked", f"Tool '{tool}' is not allowed."
    elif risk == "read":                                     # harmless: run directly
        decision, result = "auto", run_fn(**args)
    elif ask_human(tool, args, auto_answer):                 # risky: ask first
        decision, result = "approved", run_fn(**args)
    else:
        decision, result = "denied", "A human declined this action."
    AUDIT_LOG.append({"time": time.strftime("%H:%M:%S"), "tool": tool, "args": args, "decision": decision})
    return result


class Budget:
    """Stop the agent after max_calls tool calls."""

    def __init__(self, max_calls: int):
        self.left = max_calls

    def spend(self) -> None:
        if self.left <= 0:
            raise RuntimeError("Tool-call budget exhausted - stopping the agent.")
        self.left -= 1


if __name__ == "__main__":
    auto = "n" if "--auto-deny" in sys.argv else None
    fake_tools = {
        "search_docs": lambda query: f"3 documents found for '{query}'",
        "send_email": lambda to, body: f"email sent to {to}",
        "issue_refund": lambda order_id, amount: f"refunded {amount} on {order_id}",
    }
    budget = Budget(max_calls=3)
    plan = [("search_docs", {"query": "refund policy"}),
            ("issue_refund", {"order_id": "A17", "amount": 499}),
            ("delete_database", {}),
            ("send_email", {"to": "asha@example.com", "body": "Done"})]
    for tool, args in plan:
        try:
            budget.spend()
        except RuntimeError as e:
            print(e)
            break
        fn = fake_tools.get(tool, lambda **k: "")
        print("->", guarded_call(tool, args, fn, auto_answer=auto))
    print("\nAudit log:")
    for row in AUDIT_LOG:
        print(row)
