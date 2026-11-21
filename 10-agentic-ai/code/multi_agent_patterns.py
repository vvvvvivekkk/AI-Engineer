"""
multi_agent_patterns.py - three multi-agent patterns in plain Python, no API key needed.

  1. Supervisor : a boss agent reads the request and routes it to a specialist.
  2. Handoff    : an agent finishes its part and passes control (plus context) to the next.
  3. Debate     : two agents argue, a judge picks the better answer.

Each "agent" here is a small Python function standing in for an LLM call with its
own system prompt. Swap the function bodies for real model calls to go live.

Run: python multi_agent_patterns.py
"""

# ----------------------------------------------------------------------------
# Specialist agents (stand-ins). Each takes a request string, returns a reply string.
# ----------------------------------------------------------------------------
def billing_agent(request: str) -> str:
    return "Billing: I have issued a refund for the duplicate charge."


def tech_agent(request: str) -> str:
    return "Tech support: please clear your cache and log in again."


def general_agent(request: str) -> str:
    return "General: thanks for reaching out, a human will follow up."


SPECIALISTS = {"billing": billing_agent, "tech": tech_agent, "general": general_agent}


# ----------------------------------------------------------------------------
# 1. SUPERVISOR - one agent decides who should do the work.
# ----------------------------------------------------------------------------
def supervisor(request: str) -> str:
    """A real supervisor is an LLM asked: 'Which worker should handle this? Reply with one word.'"""
    text = request.lower()
    if any(w in text for w in ["refund", "charge", "invoice"]):   # keyword rules stand in for the LLM
        choice = "billing"
    elif any(w in text for w in ["error", "login", "crash"]):
        choice = "tech"
    else:
        choice = "general"
    print(f"[supervisor] routing to -> {choice}")
    return SPECIALISTS[choice](request)                           # call the chosen specialist


# ----------------------------------------------------------------------------
# 2. HANDOFF - agents pass a shared "context" dict along a chain.
# ----------------------------------------------------------------------------
def intake_agent(ctx: dict) -> tuple[dict, str | None]:
    ctx["customer"] = "Asha"                                       # collect details
    ctx["issue"] = "app crashes on login"
    print("[intake] collected details, handing off to tech")
    return ctx, "tech"                                             # (updated context, next agent)


def tech_handoff_agent(ctx: dict) -> tuple[dict, str | None]:
    ctx["fix"] = "update to version 2.1"
    print(f"[tech] fixed '{ctx['issue']}', handing off to followup")
    return ctx, "followup"


def followup_agent(ctx: dict) -> tuple[dict, str | None]:
    ctx["message"] = f"Hi {ctx['customer']}, please {ctx['fix']}. Reply if it still crashes."
    print("[followup] wrote the customer message. Done.")
    return ctx, None                                               # None = no more handoffs


HANDOFF_AGENTS = {"intake": intake_agent, "tech": tech_handoff_agent, "followup": followup_agent}


def run_handoffs(start: str = "intake", max_hops: int = 5) -> dict:
    ctx, current = {}, start
    for _ in range(max_hops):                                      # guard against ping-pong loops
        if current is None:
            break
        ctx, current = HANDOFF_AGENTS[current](ctx)
    return ctx


# ----------------------------------------------------------------------------
# 3. DEBATE - two agents propose, a judge decides.
# ----------------------------------------------------------------------------
def optimist(question: str, rival: str = "") -> str:
    return "Use an agent: it can adapt when the website layout changes."


def skeptic(question: str, rival: str = "") -> str:
    return "Use a fixed script: it is cheaper, faster and gives the same result every time."


def judge(question: str, answers: dict) -> str:
    """A real judge is an LLM given a rubric. Here: prefer the answer mentioning cost AND reliability."""
    scores = {name: sum(w in a.lower() for w in ["cheaper", "same result", "faster"])
              for name, a in answers.items()}
    winner = max(scores, key=scores.get)
    print(f"[judge] scores={scores} -> winner: {winner}")
    return answers[winner]


def run_debate(question: str, rounds: int = 2) -> str:
    a, b = optimist(question), skeptic(question)
    for r in range(rounds - 1):                                    # each side sees the other's last answer
        a, b = optimist(question, rival=b), skeptic(question, rival=a)
    return judge(question, {"optimist": a, "skeptic": b})


if __name__ == "__main__":
    print(supervisor("I was charged twice, I want a refund"))
    print()
    print(run_handoffs())
    print()
    print(run_debate("Should we scrape a stable government form with an agent or a script?"))
