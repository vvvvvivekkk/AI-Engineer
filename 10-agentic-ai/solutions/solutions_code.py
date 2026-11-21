"""
solutions_code.py - runnable solutions for the coding exercises of module 10.

Run all:            python solutions_code.py
Each exercise is a function ex2(), ex3(), ... so you can run one at a time in a notebook.
Offline - no API keys needed.
"""
import json
import operator
import re
import sys
from pathlib import Path
from typing import Annotated, TypedDict

# Let us import the module's code/ folder (react_agent, hitl_guard).
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


# ----------------------------------------------------------------------------- 2
def ex2():
    from jsonschema import ValidationError, validate
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "date": {"type": "string", "description": "ISO date, e.g. 2026-12-01"},
            "duration_minutes": {"type": "integer", "enum": [15, 30, 60]},
            "attendees": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["title", "date"],
    }
    try:
        validate({"title": "Sync", "date": "2026-12-01", "duration_minutes": 45}, schema)
    except ValidationError as e:
        print("ex2 error:", e.message)   # 45 is not one of [15, 30, 60]


# ----------------------------------------------------------------------------- 3
def anthropic_to_openai(tool: dict) -> dict:
    return {"type": "function", "function": {
        "name": tool["name"], "description": tool.get("description", ""), "parameters": tool["input_schema"]}}


def ex3():
    a = {"name": "get_weather", "description": "Weather", "input_schema": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}
    print("ex3:", json.dumps(anthropic_to_openai(a)))


# ----------------------------------------------------------------------------- 4
def ex4():
    import react_agent as ra

    def unit_convert(arg: str) -> str:
        value, frm, to = arg.split()                 # e.g. "508 m ft"
        v = float(value)
        if (frm, to) == ("m", "ft"):
            return f"{v * 3.28084:.0f} ft"
        if (frm, to) == ("ft", "m"):
            return f"{v / 3.28084:.1f} m"
        return "Error: use 'm ft' or 'ft m'"

    ra.TOOLS["unit_convert"] = unit_convert
    script = ["Thought: find the height.\nAction: search_notes[taipei 101 height]",
              "Thought: 508 m, convert.\nAction: unit_convert[508 m ft]",
              "Final Answer: Taipei 101 is about 1667 feet tall."]
    print("ex4:", ra.run_agent("How tall is Taipei 101 in feet?", ra.ScriptedLLM(script), verbose=False))


# ----------------------------------------------------------------------------- 5
def run_agent_no_repeats(question, llm, tools, max_steps=8):
    import react_agent as ra
    transcript, last_action, repeats = f"Question: {question}\n", None, 0
    for _ in range(max_steps):
        reply = llm(transcript)
        transcript += reply + "\n"
        if "Final Answer:" in reply:
            return reply.split("Final Answer:", 1)[1].strip()
        m = ra.ACTION_RE.search(reply)
        action = m.group(0) if m else None
        repeats = repeats + 1 if action and action == last_action else 0
        last_action = action
        if repeats >= 2:                                # third identical call in a row
            return "Stopped: the agent kept repeating the same action."
        if repeats == 1:                                # second identical call
            obs = "Error: you already called this. Try something else or give a Final Answer."
        elif not m:
            obs = "Error: no Action found."
        else:
            fn = tools.get(m.group(1))
            obs = fn(m.group(2)) if fn else "Error: unknown tool"
        transcript += f"Observation: {obs}\n"
    return "Stopped: max_steps"


def ex5():
    import react_agent as ra
    stuck = ra.ScriptedLLM(["Action: calculator[1+1]"] * 5)
    print("ex5:", run_agent_no_repeats("1+1?", stuck, ra.TOOLS))


# ----------------------------------------------------------------------------- 6
def safe_run(fn, args: dict) -> str:
    try:
        return json.dumps(fn(**args))
    except Exception as e:                              # any error becomes text for the model
        return f"Error: {type(e).__name__}: {e}"


def ex6():
    def broken(x: int):
        return x / 0
    print("ex6:", safe_run(broken, {"x": 1}))


# ----------------------------------------------------------------------------- 7
def ex7():
    from langgraph.graph import END, START, StateGraph

    class S(TypedDict):
        question: str
        category: str
        answer: str

    def classify(s):
        return {"category": "math" if any(ch.isdigit() for ch in s["question"]) else "chat"}

    def math(s):
        expr = s["question"]
        ok = re.fullmatch(r"[0-9+\-*/(). ]+", expr)
        return {"answer": str(eval(expr)) if ok else "I can only do arithmetic."}

    def chat(s):
        return {"answer": "Hello! How can I help?"}

    g = StateGraph(S)
    g.add_node("classify", classify); g.add_node("math", math); g.add_node("chat", chat)
    g.add_edge(START, "classify")
    g.add_conditional_edges("classify", lambda s: s["category"], {"math": "math", "chat": "chat"})
    g.add_edge("math", END); g.add_edge("chat", END)
    app = g.compile()
    for q in ["12 * 7", "hello"]:
        print("ex7:", app.invoke({"question": q, "category": "", "answer": ""}))


# ----------------------------------------------------------------------------- 8
def build_weather_agent():
    from langchain_core.messages import AIMessage, HumanMessage
    from langchain_core.tools import tool
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import START, MessagesState, StateGraph
    from langgraph.prebuilt import ToolNode, tools_condition

    @tool
    def get_weather(city: str) -> str:
        """Get weather."""
        return f"Sunny in {city}"

    def llm(state):
        last = state["messages"][-1]
        if isinstance(last, HumanMessage):
            return {"messages": [AIMessage(content="", tool_calls=[{"name": "get_weather", "args": {"city": last.content}, "id": f"c{len(state['messages'])}"}])]}
        return {"messages": [AIMessage(content=last.content)]}

    g = StateGraph(MessagesState)
    g.add_node("llm", llm); g.add_node("tools", ToolNode([get_weather]))
    g.add_edge(START, "llm"); g.add_conditional_edges("llm", tools_condition); g.add_edge("tools", "llm")
    return g.compile(checkpointer=InMemorySaver()), HumanMessage


def ex8():
    agent, Human = build_weather_agent()
    a, b = {"configurable": {"thread_id": "A"}}, {"configurable": {"thread_id": "B"}}
    agent.invoke({"messages": [Human("Taipei")]}, a)
    agent.invoke({"messages": [Human("Tainan")]}, a)
    agent.invoke({"messages": [Human("Paris")]}, b)
    for name, cfg in [("A", a), ("B", b)]:
        msgs = agent.get_state(cfg).values["messages"]
        print(f"ex8: thread {name}: {len(msgs)} messages, "
              f"{len(list(agent.get_state_history(cfg)))} checkpoints, last={msgs[-1].content!r}")


# ----------------------------------------------------------------------------- 10
def ex10():
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import END, START, StateGraph
    from langgraph.types import Command, interrupt

    class R(TypedDict):
        order_id: str
        amount: int
        status: str

    def gate(s):
        ans = str(interrupt({"question": f"Refund {s['amount']} for {s['order_id']}? yes / no / new amount"}))
        if ans == "yes":
            return {"status": "approved"}
        if ans.isdigit():
            return {"status": "approved (edited)", "amount": int(ans)}
        return {"status": "rejected"}

    def execute(s):
        if s["status"].startswith("approved"):
            return {"status": s["status"] + f" -> sent {s['amount']}"}
        return {"status": s["status"] + " -> nothing sent"}

    g = StateGraph(R)
    g.add_node("gate", gate); g.add_node("execute", execute)
    g.add_edge(START, "gate"); g.add_edge("gate", "execute"); g.add_edge("execute", END)
    app = g.compile(checkpointer=InMemorySaver())
    for i, answer in enumerate(["yes", "no", "250"]):
        cfg = {"configurable": {"thread_id": f"r{i}"}}
        app.invoke({"order_id": "A1", "amount": 900, "status": ""}, cfg)   # pauses at gate
        print(f"ex10: human says {answer!r}:", app.invoke(Command(resume=answer), cfg)["status"])


# ----------------------------------------------------------------------------- 11
def ex11():
    from langgraph.graph import END, START, StateGraph

    class S(TypedDict):
        request: str
        route: str
        answer: str

    def supervisor(s):
        t = s["request"].lower()
        r = "billing" if "refund" in t or "charge" in t else "tech" if "error" in t or "login" in t else "general"
        return {"route": r}

    g = StateGraph(S)
    g.add_node("supervisor", supervisor)
    for worker in ["billing", "tech", "general"]:
        g.add_node(worker, lambda s, w=worker: {"answer": f"{w} team handled: {s['request']}"})
        g.add_edge(worker, END)
    g.add_edge(START, "supervisor")
    g.add_conditional_edges("supervisor", lambda s: s["route"], ["billing", "tech", "general"])
    app = g.compile()
    for req in ["Refund please", "Login error", "Hi there"]:
        path = [list(u)[0] for u in app.stream({"request": req, "route": "", "answer": ""}, stream_mode="updates")]
        print("ex11:", req, "->", " -> ".join(path))


# ----------------------------------------------------------------------------- 12
def ex12():
    import hitl_guard as hg
    hg.TOOL_RISK.clear()
    hg.TOOL_RISK.update({"search_docs": "read", "send_email": "write"})
    hg.AUDIT_LOG.clear()
    impl = {"search_docs": lambda query: f"found 2 docs for {query}",
            "send_email": lambda to, body: f"sent to {to}"}
    script = [
        {"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "1", "name": "search_docs", "input": {"query": "policy"}}]},
        {"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "2", "name": "send_email", "input": {"to": "a@example.com", "body": "hi"}}]},
        {"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "3", "name": "delete_all", "input": {}}]},
        {"stop_reason": "end_turn", "content": [{"type": "text", "text": "Done."}]},
    ]
    messages = [{"role": "user", "content": "Handle the policy question"}]
    for reply in script:
        messages.append({"role": "assistant", "content": reply["content"]})
        if reply["stop_reason"] != "tool_use":
            break
        results = []
        for b in reply["content"]:
            out = hg.guarded_call(b["name"], b["input"], impl.get(b["name"], lambda **k: ""), auto_answer="n")
            results.append({"type": "tool_result", "tool_use_id": b["id"], "content": out})
        messages.append({"role": "user", "content": results})
    for row in hg.AUDIT_LOG:
        print("ex12:", row["tool"], "->", row["decision"])


if __name__ == "__main__":
    for fn in [ex2, ex3, ex4, ex5, ex6, ex7, ex8, ex10, ex11, ex12]:
        fn()
