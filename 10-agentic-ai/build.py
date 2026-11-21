"""
build.py - regenerates images/, notebooks/, slides/, pdf/ and excel/ for module 10.

    python 10-agentic-ai/build.py

Markdown files (README, concepts, exercises, ...) are written by hand; this script
only builds the generated artefacts. Safe to run again and again.
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook  # noqa: E402

IMG = HERE / "images"
NB = HERE / "notebooks"

# =============================================================================
# 1. DIAGRAMS
# =============================================================================
DIAGRAMS = {
    "agent_loop": """
flowchart LR
    U([User goal]) --> L[LLM decides next step]
    L -->|tool call| C[Your code runs the tool]
    C -->|tool result| L
    L -->|final answer| A([Answer to user])
""",
    "react_loop": """
flowchart TD
    Q([Question]) --> T[Thought: what do I need?]
    T --> A[Action: tool and input]
    A --> O[Observation: tool result]
    O --> D{Enough to answer?}
    D -->|no| T
    D -->|yes| F([Final Answer])
""",
    "langgraph_agent": """
flowchart LR
    S([START]) --> L[llm node]
    L --> C{tools_condition}
    C -->|has tool calls| T[tools node]
    T --> L
    C -->|no tool calls| E([END])
    L -.-> K[(checkpointer saves state)]
""",
    "multi_agent_patterns": """
flowchart TB
    subgraph S1[1 Supervisor]
      direction LR
      R[Request] --> B{Boss agent}
      B --> W1[Billing]
      B --> W2[Tech]
    end
    subgraph S2[2 Handoff]
      direction LR
      I[Intake] --> T2[Tech] --> F[Follow-up]
    end
    subgraph S3[3 Debate]
      direction LR
      P1[Agent A] --> J{Judge}
      P2[Agent B] --> J
    end
    S1 ~~~ S2 ~~~ S3
""",
    "mcp_architecture": """
flowchart LR
    subgraph Host app e.g. Claude Desktop
      M[LLM] --- C1[MCP client 1]
      M --- C2[MCP client 2]
    end
    C1 <-->|stdio| S1[Server: study notes]
    C2 <-->|HTTP| S2[Server: GitHub]
    S1 --> P[Tools / Resources / Prompts]
""",
    "hitl_flow": """
flowchart TD
    A[Model requests tool] --> B{On allow-list?}
    B -->|no| X[Block + log]
    B -->|yes| R{Risk level}
    R -->|read| RUN[Run tool]
    R -->|write or money| H{Human approves?}
    H -->|yes| RUN
    H -->|no| D[Decline + tell model]
    RUN --> LOG[(Audit log)]
""",
}

# =============================================================================
# 2. NOTEBOOKS
# =============================================================================
NB01 = [
("md", """# Notebook 01 — Tools and function calling

**Goal:** understand exactly what "tool use" (also called **function calling**) is, by building every piece by hand:

1. a normal Python function (the **tool**),
2. a **JSON Schema** that describes its inputs,
3. the **OpenAI** and **Anthropic** wrappers around that schema, side by side,
4. the code that reads a model's **tool call**, checks it, runs the function and sends the **tool result** back.

Everything runs **offline** with no API key. Where a real API call is shown, it only runs if you have set a key.

*Jargon:* **JSON** is a text format for data that looks like Python dicts and lists. **JSON Schema** is a standard way to say what shape a piece of JSON must have."""),
("md", """## Step 1 — A normal Python function

A tool is just a function. The model will never run it. It can only *ask* us to run it."""),
("code", """def get_weather(city: str, unit: str = "celsius") -> dict:
    \"\"\"Pretend weather service (a real one would call a weather API).\"\"\"
    fake_data = {"taipei": 24, "hyderabad": 31, "london": 9}
    temp_c = fake_data.get(city.lower(), 20)
    temp = temp_c if unit == "celsius" else round(temp_c * 9 / 5 + 32)
    return {"city": city, "temperature": temp, "unit": unit}

print(get_weather("Taipei"))
print(get_weather("London", unit="fahrenheit"))"""),
("md", """## Step 2 — Describe the inputs with JSON Schema

The model cannot read our Python code. We describe the function's inputs in JSON Schema. Read it as: *"an object with a text field `city` (required) and a field `unit` that must be one of two words."*"""),
("code", """import json

WEATHER_PARAMS = {
    "type": "object",
    "properties": {
        "city": {"type": "string", "description": "City name, e.g. Taipei"},
        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "Temperature unit"},
    },
    "required": ["city"],
}
print(json.dumps(WEATHER_PARAMS, indent=2))"""),
("md", """## Step 3 — The same tool, wrapped for OpenAI and for Anthropic

Both companies accept the same schema. Only the wrapper differs:

* **OpenAI** puts it under `function.parameters`.
* **Anthropic** puts it under `input_schema`."""),
("code", """OPENAI_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current temperature for a city. Use when the user asks about weather.",
        "parameters": WEATHER_PARAMS,
    },
}
ANTHROPIC_TOOL = {
    "name": "get_weather",
    "description": "Get the current temperature for a city. Use when the user asks about weather.",
    "input_schema": WEATHER_PARAMS,
}
print("OpenAI:\\n", json.dumps(OPENAI_TOOL, indent=2))
print("\\nAnthropic:\\n", json.dumps(ANTHROPIC_TOOL, indent=2))"""),
("md", """Because the formats are so close, converting between them is a three-line function. Frameworks such as LangChain do this for you."""),
("code", """def openai_to_anthropic(tool: dict) -> dict:
    f = tool["function"]
    return {"name": f["name"], "description": f["description"], "input_schema": f["parameters"]}

print(openai_to_anthropic(OPENAI_TOOL) == ANTHROPIC_TOOL)"""),
("md", """## Step 4 — Let Python write the schema for you

Writing schemas by hand is boring and error-prone. Libraries read the function's **type hints** (the `: str` parts) and **docstring** and build the schema automatically. Here is a tiny home-made version using Python's `inspect` module, so you can see there is no magic."""),
("code", """import inspect

PY_TO_JSON = {str: "string", int: "integer", float: "number", bool: "boolean", list: "array", dict: "object"}

def schema_from_function(fn) -> dict:
    sig = inspect.signature(fn)                      # the function's parameters
    props, required = {}, []
    for name, p in sig.parameters.items():
        props[name] = {"type": PY_TO_JSON.get(p.annotation, "string")}
        if p.default is inspect.Parameter.empty:     # no default value -> required
            required.append(name)
    return {"name": fn.__name__,
            "description": (fn.__doc__ or "").strip(),
            "input_schema": {"type": "object", "properties": props, "required": required}}

print(json.dumps(schema_from_function(get_weather), indent=2))"""),
("md", """The real libraries do the same with more care. LangChain's `@tool` decorator (installed here) is one example:"""),
("code", """from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool

@tool
def get_weather_lc(city: str, unit: str = "celsius") -> str:
    \"\"\"Get the current temperature for a city.\"\"\"
    return json.dumps(get_weather(city, unit))

print(json.dumps(convert_to_openai_tool(get_weather_lc), indent=2))"""),
("md", """## Step 5 — What the model sends back (offline simulation)

When a model decides to use a tool, it does **not** run it. It replies with a structured request. The two providers shape that reply differently:

* OpenAI: `tool_calls[i].function.arguments` is a JSON **string** — you must `json.loads` it.
* Anthropic: a content block of `type == "tool_use"` whose `input` is already a **dict**.

Below we write those replies by hand (exactly the shape the real APIs return, simplified)."""),
("code", """openai_reply = {"role": "assistant", "content": None, "tool_calls": [
    {"id": "call_abc", "type": "function",
     "function": {"name": "get_weather", "arguments": '{"city": "Taipei"}'}}]}

anthropic_reply = {"role": "assistant", "stop_reason": "tool_use", "content": [
    {"type": "text", "text": "Let me check."},
    {"type": "tool_use", "id": "toolu_123", "name": "get_weather", "input": {"city": "Taipei"}}]}

print(type(openai_reply["tool_calls"][0]["function"]["arguments"]))   # str
print(type(anthropic_reply["content"][1]["input"]))                    # dict"""),
("md", """## Step 6 — Validate before you run

The model can make mistakes: a missing field, a wrong type, a value not in the `enum`. **Never trust tool arguments blindly.** The `jsonschema` library checks a dict against a schema."""),
("code", """from jsonschema import validate, ValidationError

def check_args(args: dict, schema: dict) -> str | None:
    try:
        validate(instance=args, schema=schema)
        return None                         # None = no problem
    except ValidationError as e:
        return f"Invalid arguments: {e.message}"

print(check_args({"city": "Taipei"}, WEATHER_PARAMS))
print(check_args({"unit": "kelvin"}, WEATHER_PARAMS))"""),
("md", """## Step 7 — Dispatch: from tool call to tool result

A **registry** maps tool names to Python functions. The **dispatcher** looks up the name, validates, runs, and wraps the result in the format the provider expects. Errors are *returned to the model as text* so it can try again — a crash would end the conversation."""),
("code", """TOOLS = {"get_weather": (get_weather, WEATHER_PARAMS)}

def run_tool(name: str, args: dict) -> str:
    if name not in TOOLS:
        return f"Error: unknown tool '{name}'. Available: {list(TOOLS)}"
    fn, schema = TOOLS[name]
    problem = check_args(args, schema)
    if problem:
        return problem
    return json.dumps(fn(**args))

# OpenAI style result message
tc = openai_reply["tool_calls"][0]
openai_result = {"role": "tool", "tool_call_id": tc["id"],
                 "content": run_tool(tc["function"]["name"], json.loads(tc["function"]["arguments"]))}
# Anthropic style result message (goes in a *user* turn)
block = anthropic_reply["content"][1]
anthropic_result = {"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": block["id"], "content": run_tool(block["name"], block["input"])}]}

print(openai_result)
print(anthropic_result)
print(run_tool("get_stock_price", {"ticker": "TSM"}))"""),
("md", """## Step 8 — The real calls (only run with a key)

This is the real code for both providers. Without a key it prints a message and moves on, so the notebook always runs. To try it, set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (in Colab: the key icon → Secrets) and `pip install openai anthropic`.

Model names change often — as of late 2026, check the official model pages and set `OPENAI_MODEL` / `ANTHROPIC_MODEL`."""),
("code", """import os

question = "What's the weather in Taipei?"

if os.getenv("OPENAI_API_KEY"):
    from openai import OpenAI
    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    msgs = [{"role": "user", "content": question}]
    r = client.chat.completions.create(model=model, messages=msgs, tools=[OPENAI_TOOL])
    m = r.choices[0].message
    if m.tool_calls:
        msgs.append(m)
        for t in m.tool_calls:
            msgs.append({"role": "tool", "tool_call_id": t.id,
                         "content": run_tool(t.function.name, json.loads(t.function.arguments))})
        r = client.chat.completions.create(model=model, messages=msgs, tools=[OPENAI_TOOL])
    print("OpenAI:", r.choices[0].message.content)
else:
    print("No OPENAI_API_KEY - skipping the real OpenAI call (offline simulation above shows the shapes).")

if os.getenv("ANTHROPIC_API_KEY"):
    import anthropic
    client = anthropic.Anthropic()
    model = os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")
    msgs = [{"role": "user", "content": question}]
    r = client.messages.create(model=model, max_tokens=400, tools=[ANTHROPIC_TOOL], messages=msgs)
    if r.stop_reason == "tool_use":
        msgs.append({"role": "assistant", "content": r.content})
        msgs.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": b.id, "content": run_tool(b.name, b.input)}
            for b in r.content if b.type == "tool_use"]})
        r = client.messages.create(model=model, max_tokens=400, tools=[ANTHROPIC_TOOL], messages=msgs)
    print("Claude:", r.content[0].text)
else:
    print("No ANTHROPIC_API_KEY - skipping the real Anthropic call.")"""),
("md", """## Recap

* A tool = **name + description + JSON Schema** for the inputs.
* OpenAI wraps it as `function.parameters`; Anthropic as `input_schema`.
* The model only **requests** a call. Your code validates, runs, and returns the result.
* Return errors as text so the model can recover.

**Try it:** add a second tool `convert_currency(amount: float, from_code: str, to_code: str)` with its schema, add it to `TOOLS`, and test `run_tool` with good and bad arguments."""),
]

NB02 = [
("md", """# Notebook 02 — A ReAct agent loop from scratch

**Goal:** build the agent loop yourself in plain Python and watch every step.

**ReAct** = **Re**ason + **Act**. The model repeats *Thought → Action → Observation* until it writes *Final Answer*.

So the notebook runs with no internet and gives the same result every time, the "LLM" is a **scripted fake LLM**: an object that hands back pre-written replies one by one. The **loop is real** — swapping in a real model changes one line."""),
("md", """## Step 1 — Tools

Two small tools: a calculator (which refuses anything that is not arithmetic — a first taste of safety) and a tiny search over fake notes."""),
("code", """import re

def calculator(expression: str) -> str:
    if not re.fullmatch(r"[0-9+\\-*/(). ]+", expression):
        return "Error: only arithmetic is allowed"
    return str(eval(expression))

KB = {"taipei 101 height": "Taipei 101 is 508 metres tall.",
      "eiffel tower height": "The Eiffel Tower is about 330 metres tall.",
      "burj khalifa height": "The Burj Khalifa is 828 metres tall."}

def search_notes(query: str) -> str:
    for key, value in KB.items():
        if all(w in key for w in query.lower().split()):
            return value
    return "No result found."

TOOLS = {"calculator": calculator, "search_notes": search_notes}
print(calculator("508 - 330"), "|", calculator("__import__('os')"), "|", search_notes("eiffel height"))"""),
("md", """## Step 2 — The prompt format and the fake LLM

The **system prompt** teaches the model the format. A real model reads the whole **transcript** (everything so far) and writes the next step. Our `ScriptedLLM` ignores the transcript and returns the next scripted line — but it has the *same interface*: text in, text out."""),
("code", """SYSTEM_PROMPT = \"\"\"You are a helpful agent. Use this format:
Thought: <reasoning>
Action: <tool>[<input>]
You will then get: Observation: <result>
When done: Final Answer: <answer>
Tools: calculator[expression], search_notes[query]\"\"\"

class ScriptedLLM:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0
    def __call__(self, transcript: str) -> str:
        self.calls += 1
        return self.replies.pop(0) if self.replies else "Final Answer: I am out of ideas."

print(SYSTEM_PROMPT)"""),
("md", """## Step 3 — The loop

Read this cell slowly; it is the whole idea of an agent:

1. ask the LLM for the next step,
2. stop if it gave a Final Answer,
3. otherwise find the `Action: tool[input]`,
4. run the tool,
5. append `Observation: ...` and go round again — but never more than `max_steps` times."""),
("code", """ACTION_RE = re.compile(r"Action:\\s*(\\w+)\\[(.*)\\]")

def run_agent(question, llm, max_steps=6, verbose=True):
    transcript = f"{SYSTEM_PROMPT}\\n\\nQuestion: {question}\\n"
    for step in range(1, max_steps + 1):
        reply = llm(transcript)
        transcript += reply + "\\n"
        if verbose:
            print(f"--- step {step} ---\\n{reply}")
        if "Final Answer:" in reply:
            return reply.split("Final Answer:", 1)[1].strip()
        m = ACTION_RE.search(reply)
        if not m:
            obs = "Error: no Action found. Use Action: tool[input]."
        else:
            name, arg = m.group(1), m.group(2)
            obs = TOOLS[name](arg) if name in TOOLS else f"Error: unknown tool '{name}'. Use one of {list(TOOLS)}"
        transcript += f"Observation: {obs}\\n"
        if verbose:
            print(f"Observation: {obs}")
    return "Stopped: max_steps reached."
print("loop defined")"""),
("md", """## Step 4 — Run it

The question needs **two lookups and one calculation**. Watch the Thought → Action → Observation rhythm."""),
("code", """script = [
    "Thought: I need Taipei 101's height.\\nAction: search_notes[taipei 101 height]",
    "Thought: 508 m. Now the Eiffel Tower.\\nAction: search_notes[eiffel tower height]",
    "Thought: Subtract.\\nAction: calculator[508 - 330]",
    "Thought: 178 m.\\nFinal Answer: Taipei 101 is about 178 metres taller than the Eiffel Tower.",
]
answer = run_agent("How much taller is Taipei 101 than the Eiffel Tower?", ScriptedLLM(script))
print("\\nANSWER:", answer)"""),
("md", """## Step 5 — What goes wrong (and how the loop protects us)

Real models make mistakes. Here the fake LLM (a) asks for a tool that does not exist, (b) forgets the format, then (c) recovers. The loop returns **error observations** instead of crashing, so the model can correct itself."""),
("code", """messy = [
    "Thought: I'll use the internet.\\nAction: google[burj khalifa]",
    "I think it's tall.",
    "Thought: Use the right tool.\\nAction: search_notes[burj khalifa height]",
    "Final Answer: The Burj Khalifa is 828 metres tall.",
]
print("ANSWER:", run_agent("How tall is the Burj Khalifa?", ScriptedLLM(messy)))"""),
("md", """And if the model never finishes (it keeps calling the same tool), `max_steps` stops the loop. Without this limit an agent can burn money forever."""),
("code", """stuck = ["Thought: check again.\\nAction: calculator[1+1]"] * 10
print("ANSWER:", run_agent("What is 1+1?", ScriptedLLM(stuck), max_steps=3))"""),
("md", """## Step 6 — The same loop with native tool calls

Modern APIs return **structured tool calls** instead of text to parse (see notebook 01). The loop is the same — only the parsing step disappears. Here the fake LLM returns dicts shaped like an Anthropic reply. The `messages` list is the transcript."""),
("code", """import json

class ScriptedToolLLM:
    \"\"\"Returns Anthropic-shaped replies: a list of content blocks + a stop_reason.\"\"\"
    def __init__(self, replies): self.replies = list(replies)
    def __call__(self, messages, tools): return self.replies.pop(0)

def native_agent(question, llm, max_steps=5):
    messages = [{"role": "user", "content": question}]
    for step in range(max_steps):
        reply = llm(messages, tools=list(TOOLS))
        messages.append({"role": "assistant", "content": reply["content"]})
        if reply["stop_reason"] != "tool_use":
            return reply["content"][0]["text"], messages
        results = []
        for b in reply["content"]:
            if b["type"] == "tool_use":
                out = TOOLS[b["name"]](**b["input"])
                print(f"step {step+1}: {b['name']}({b['input']}) -> {out}")
                results.append({"type": "tool_result", "tool_use_id": b["id"], "content": out})
        messages.append({"role": "user", "content": results})
    return "Stopped", messages

fake = ScriptedToolLLM([
    {"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "t1", "name": "search_notes", "input": {"query": "burj khalifa height"}},
                                             {"type": "tool_use", "id": "t2", "name": "search_notes", "input": {"query": "taipei 101 height"}}]},
    {"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "t3", "name": "calculator", "input": {"expression": "828 / 508"}}]},
    {"stop_reason": "end_turn", "content": [{"type": "text", "text": "The Burj Khalifa is about 1.63 times as tall as Taipei 101."}]},
])
ans, history = native_agent("How many times taller is the Burj Khalifa than Taipei 101?", fake)
print("\\nANSWER:", ans)
print("messages in history:", len(history))"""),
("md", """Notice the model asked for **two tool calls in one turn** (parallel tool calls). Your loop must run all of them and send all results back together.

## Step 7 — Plug in a real model (optional)

`real_llm` below has the same shape as `ScriptedToolLLM`. With a key, the same `native_agent` drives Claude. Without one, it is skipped."""),
("code", """import os

def make_real_llm():
    import anthropic
    client = anthropic.Anthropic()
    schemas = [
        {"name": "calculator", "description": "Evaluate arithmetic.", "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}},
        {"name": "search_notes", "description": "Look up facts about building heights.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    ]
    def llm(messages, tools):
        r = client.messages.create(model=os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5"), max_tokens=500, tools=schemas, messages=messages)
        return {"stop_reason": r.stop_reason, "content": [b.model_dump() for b in r.content]}
    return llm

if os.getenv("ANTHROPIC_API_KEY"):
    print(native_agent("How much taller is the Burj Khalifa than the Eiffel Tower?", make_real_llm())[0])
else:
    print("No ANTHROPIC_API_KEY - real model skipped. The scripted run above used the identical loop.")"""),
("md", """## Recap

* An agent is a **loop**: ask → (answer? stop) → run tool → feed back.
* Always have **max_steps**, **unknown-tool errors** and **argument validation**.
* Text ReAct and native tool calling share the same loop; native calling is more reliable.

**Try it:** add a `max_same_call` rule that stops the agent if it makes the exact same tool call twice in a row."""),
]

NB03 = [
("md", """# Notebook 03 — LangGraph: state, nodes, edges, memory and human approval

**Goal:** learn LangGraph's building blocks by running small graphs, then build a tool-calling agent with memory and a human-approval step. Checked against **langgraph 1.2.x**.

Vocabulary (also in concepts.md):

* **State** — a dictionary passed through the graph.
* **Node** — a function: takes state, returns an *update* (only the keys it changes).
* **Edge** — a fixed arrow. **Conditional edge** — an arrow chosen at run time.
* **Reducer** — how an update merges into state (replace, or e.g. append).
* **Checkpointer** — saves state after every step; **thread_id** names one saved conversation.

All offline: the "LLM" node is a stand-in function."""),
("md", """## Step 0 — Check the installed version

In Colab you may need `pip install langgraph` first. The cell does that only if the import fails."""),
("code", """try:
    import langgraph
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "langgraph"], check=True)
from importlib.metadata import version
print("langgraph", version("langgraph"), "| langchain-core", version("langchain-core"))"""),
("md", """## Step 1 — The smallest graph: two nodes in a line

State has two fields. Each node returns only the field it changes. `START` and `END` are the entry and exit."""),
("code", """from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    text: str
    word_count: int

def clean(state: State) -> dict:
    return {"text": state["text"].strip().lower()}

def count(state: State) -> dict:
    return {"word_count": len(state["text"].split())}

g = StateGraph(State)
g.add_node("clean", clean)
g.add_node("count", count)
g.add_edge(START, "clean")
g.add_edge("clean", "count")
g.add_edge("count", END)
app = g.compile()
print(app.invoke({"text": "   Agents Are LLMs In A Loop  ", "word_count": 0}))"""),
("md", """## Step 2 — Reducers: append instead of replace

By default a node's update **replaces** the old value. With `Annotated[list, operator.add]` the update is **added** (appended) to the list instead. This is how chat history grows."""),
("code", """import operator
from typing import Annotated

class LogState(TypedDict):
    log: Annotated[list, operator.add]     # reducer = list addition (append)

def a(state): return {"log": ["a ran"]}
def b(state): return {"log": ["b ran"]}

g = StateGraph(LogState)
g.add_node("a", a); g.add_node("b", b)
g.add_edge(START, "a"); g.add_edge("a", "b"); g.add_edge("b", END)
print(g.compile().invoke({"log": ["start"]}))"""),
("md", """## Step 3 — Conditional edges and loops

A **router function** looks at the state and returns the name of the next node. Here a "draft" node keeps improving a draft until a quality score is high enough — a loop, with a safety limit."""),
("code", """class DraftState(TypedDict):
    draft: str
    score: int
    rounds: int

def write(state):
    return {"draft": state["draft"] + " +detail", "score": state["score"] + 30, "rounds": state["rounds"] + 1}

def route(state) -> str:
    if state["score"] >= 80 or state["rounds"] >= 5:   # good enough, or safety stop
        return "publish"
    return "write"

def publish(state):
    return {"draft": state["draft"] + " [PUBLISHED]"}

g = StateGraph(DraftState)
g.add_node("write", write); g.add_node("publish", publish)
g.add_edge(START, "write")
g.add_conditional_edges("write", route, {"write": "write", "publish": "publish"})
g.add_edge("publish", END)
loop_app = g.compile()
print(loop_app.invoke({"draft": "Intro", "score": 0, "rounds": 0}))"""),
("md", """`stream` shows each node's update as it happens — this is how UIs show progress."""),
("code", """for update in loop_app.stream({"draft": "Intro", "score": 0, "rounds": 0}, stream_mode="updates"):
    print(update)"""),
("md", """LangGraph can describe its own graph as Mermaid text (the same diagram language used in this course's images)."""),
("code", """print(loop_app.get_graph().draw_mermaid())"""),
("md", """## Step 4 — A tool-calling agent with prebuilt pieces

* `MessagesState` = state with a `messages` list that **appends** automatically.
* `ToolNode(tools)` runs every tool call found in the last AI message.
* `tools_condition` routes to `"tools"` if there are tool calls, otherwise to `END`.

The `llm` node is an offline stand-in that emits a tool call for new questions and answers once it sees a tool result."""),
("code", """from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    \"\"\"Get the current weather for a city.\"\"\"
    return {"taipei": "Sunny, 24C", "london": "Rainy, 9C"}.get(city.lower(), "Cloudy, 20C")

TOOLS = [get_weather]

def fake_llm(state: MessagesState):
    last = state["messages"][-1]
    if isinstance(last, HumanMessage):
        q = last.content.lower()
        if "weather" in q:
            city = "Taipei" if "taipei" in q else "London"
            return {"messages": [AIMessage(content="", tool_calls=[{"name": "get_weather", "args": {"city": city}, "id": f"call_{len(state['messages'])}"}])]}
        # questions about earlier conversation: look back through history (memory!)
        earlier = [m.content for m in state["messages"] if isinstance(m, ToolMessage)]
        return {"messages": [AIMessage(content=f"Earlier tool results I remember: {earlier}")]}
    return {"messages": [AIMessage(content=f"The weather is: {last.content}")]}

g = StateGraph(MessagesState)
g.add_node("llm", fake_llm)
g.add_node("tools", ToolNode(TOOLS))
g.add_edge(START, "llm")
g.add_conditional_edges("llm", tools_condition)
g.add_edge("tools", "llm")
print("graph built:", list(g.nodes))"""),
("md", """## Step 5 — Memory with a checkpointer

Compile with `InMemorySaver()`. Each call with the same `thread_id` continues the same conversation, because the saved state (all messages) is loaded first. A different `thread_id` starts fresh."""),
("code", """from langgraph.checkpoint.memory import InMemorySaver

agent = g.compile(checkpointer=InMemorySaver())
cfg = {"configurable": {"thread_id": "student-1"}}

r1 = agent.invoke({"messages": [HumanMessage("What's the weather in Taipei?")]}, cfg)
for m in r1["messages"]:
    print(f"{type(m).__name__:12}", repr(m.content), getattr(m, "tool_calls", "") or "")"""),

("md", """Second turn, **same thread**: the agent can see the first turn."""),
("code", """r2 = agent.invoke({"messages": [HumanMessage("What did you find out before?")]}, cfg)
print(r2["messages"][-1].content)
print("messages saved in this thread:", len(r2["messages"]))"""),
("md", """A **different thread** has no memory of the first one."""),
("code", """r3 = agent.invoke({"messages": [HumanMessage("What did you find out before?")]}, {"configurable": {"thread_id": "student-2"}})
print(r3["messages"][-1].content)"""),
("md", """You can inspect the saved state and its history (one checkpoint per step) — very useful for debugging."""),
("code", """snap = agent.get_state(cfg)
print("next node to run:", snap.next)
print("number of checkpoints:", len(list(agent.get_state_history(cfg))))"""),
("md", """## Step 6 — Human-in-the-loop with `interrupt`

Calling `interrupt(payload)` inside a node **pauses** the graph and saves it. The caller sees the payload under `__interrupt__`. Later we resume with `Command(resume=answer)`; the node continues and `interrupt` returns that answer. A checkpointer is required (the paused state must be stored)."""),
("code", """from langgraph.types import interrupt, Command

class RefundState(TypedDict):
    order_id: str
    amount: int
    status: str

def propose(state):
    return {"status": f"proposed refund of {state['amount']} for {state['order_id']}"}

def human_gate(state):
    if state["amount"] <= 100:                       # small refunds: no approval needed
        return {"status": state["status"] + " | auto-approved"}
    answer = interrupt({"question": f"Approve {state['status']}?"})
    return {"status": state["status"] + (" | APPROVED" if answer == "yes" else " | REJECTED")}

def execute(state):
    done = "APPROVED" in state["status"] or "auto-approved" in state["status"]
    return {"status": state["status"] + (" | refund sent" if done else " | nothing sent")}

g = StateGraph(RefundState)
for name, fn in [("propose", propose), ("human_gate", human_gate), ("execute", execute)]:
    g.add_node(name, fn)
g.add_edge(START, "propose"); g.add_edge("propose", "human_gate"); g.add_edge("human_gate", "execute"); g.add_edge("execute", END)
refund_app = g.compile(checkpointer=InMemorySaver())

cfg = {"configurable": {"thread_id": "refund-42"}}
paused = refund_app.invoke({"order_id": "A42", "amount": 900, "status": ""}, cfg)
print("Paused with:", paused["__interrupt__"][0].value)
print("Waiting at node:", refund_app.get_state(cfg).next)"""),
("md", """A human (in a real app: a button in a web page) answers **yes**. We resume the same thread."""),
("code", """final = refund_app.invoke(Command(resume="yes"), cfg)
print(final["status"])

small = refund_app.invoke({"order_id": "B7", "amount": 40, "status": ""}, {"configurable": {"thread_id": "refund-7"}})
print(small["status"])"""),
("md", """## Step 7 — Optional: a real model

With `ANTHROPIC_API_KEY` set and `pip install langchain-anthropic`, the stand-in can be replaced by a real chat model with tools bound. The graph does not change."""),
("code", """import os
if os.getenv("ANTHROPIC_API_KEY"):
    try:
        from langchain_anthropic import ChatAnthropic
        model = ChatAnthropic(model=os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")).bind_tools(TOOLS)
        g2 = StateGraph(MessagesState)
        g2.add_node("llm", lambda s: {"messages": [model.invoke(s["messages"])]})
        g2.add_node("tools", ToolNode(TOOLS))
        g2.add_edge(START, "llm"); g2.add_conditional_edges("llm", tools_condition); g2.add_edge("tools", "llm")
        real = g2.compile(checkpointer=InMemorySaver())
        out = real.invoke({"messages": [HumanMessage("Weather in London?")]}, {"configurable": {"thread_id": "real"}})
        print(out["messages"][-1].content)
    except ImportError:
        print("pip install langchain-anthropic to try the real model")
else:
    print("No ANTHROPIC_API_KEY - real model skipped.")"""),
("md", """## Recap

| Piece | Code |
|---|---|
| State | `class State(TypedDict)` / `MessagesState` |
| Node | `g.add_node("name", fn)` |
| Edge | `g.add_edge("a", "b")` |
| Conditional edge | `g.add_conditional_edges("a", router, {...})` |
| Memory | `compile(checkpointer=InMemorySaver())` + `thread_id` |
| Human approval | `interrupt(...)` then `invoke(Command(resume=...))` |

**Try it:** add a `max_refund` check node that routes amounts over 5000 straight to a "reject" node without asking a human."""),
]

NB04 = [
("md", """# Notebook 04 — Crews, multi-agent patterns, memory and MCP

**Goal:** see that "multi-agent" frameworks are built from simple parts, add memory to an agent, and run a real **MCP** server and client.

1. A plain-Python mimic of **CrewAI** (agents with roles, tasks, a crew).
2. **Supervisor**, **handoff** and **debate** patterns.
3. **Short-term** and **long-term** memory.
4. **MCP**: define a server with tools, resources and prompts; connect a client; call the tools.

CrewAI is not installed here (it is large). The real CrewAI code is in `code/crewai_example.py`."""),
("md", """## Part 1 — A mini "crew" in plain Python

In CrewAI an **Agent** has a role, goal and backstory; a **Task** has a description, expected output and an agent; a **Crew** runs tasks in order, passing earlier outputs forward as context.

Below, each agent's *system prompt* is built from its role/goal/backstory exactly as a framework would. The LLM is a fake function that returns a canned reply per role, and prints the prompt it received so you can see what the model would see."""),
("code", """from dataclasses import dataclass, field

def fake_llm(system: str, user: str) -> str:
    \"\"\"Stand-in for a chat model. Picks a canned answer based on the role in the system prompt.\"\"\"
    if "Research Analyst" in system:
        return "1. MCP is an open protocol. 2. Hosts contain clients. 3. Servers expose tools, resources, prompts."
    if "Technical Writer" in system:
        return "MCP is like a USB-C port for AI apps: one standard plug so any app can use any tool server."
    return "OK."

@dataclass
class Agent:
    role: str
    goal: str
    backstory: str
    def system_prompt(self) -> str:
        return f"You are a {self.role}. Your goal: {self.goal}. Background: {self.backstory}"
    def work(self, task_text: str) -> str:
        return fake_llm(self.system_prompt(), task_text)

@dataclass
class Task:
    description: str
    expected_output: str
    agent: Agent

@dataclass
class Crew:
    agents: list
    tasks: list
    log: list = field(default_factory=list)
    def kickoff(self, inputs: dict) -> str:
        context = ""
        for t in self.tasks:                                   # sequential process
            prompt = t.description.format(**inputs) + f"\\nExpected output: {t.expected_output}"
            if context:
                prompt += f"\\nContext from previous task:\\n{context}"
            print(f"\\n>>> {t.agent.role} receives:\\n{prompt}")
            context = t.agent.work(prompt)
            print(f"<<< {t.agent.role} returns:\\n{context}")
            self.log.append((t.agent.role, context))
        return context

researcher = Agent("Research Analyst", "collect facts about {topic}", "careful and precise")
writer = Agent("Technical Writer", "explain {topic} to beginners", "loves analogies")
crew = Crew([researcher, writer], [
    Task("List 3 key facts about {topic}.", "a numbered list", researcher),
    Task("Write a one-sentence beginner explanation of {topic}.", "one sentence", writer),
])
print("\\nFINAL:", crew.kickoff({"topic": "the Model Context Protocol"}))"""),
("md", """That is the core of a crew: **prompts built from roles + a loop over tasks + passing outputs forward**. Frameworks add tools, retries, delegation and logging on top.

## Part 2 — Supervisor, handoff and debate

**Supervisor:** a router decides which specialist handles a request. In real life the router is an LLM asked to reply with one word; here keyword rules stand in."""),
("code", """SPECIALISTS = {
    "billing": lambda r: "Billing agent: refund issued for the duplicate charge.",
    "tech":    lambda r: "Tech agent: clear the cache and log in again.",
    "general": lambda r: "General agent: a human will follow up.",
}

def supervisor(request: str) -> str:
    t = request.lower()
    choice = ("billing" if any(w in t for w in ["refund", "charge", "invoice"]) else
              "tech" if any(w in t for w in ["error", "login", "crash"]) else "general")
    print(f"[supervisor] '{request}' -> {choice}")
    return SPECIALISTS[choice](request)

for req in ["I was charged twice", "Login error 500", "Do you have stickers?"]:
    print("  ", supervisor(req))"""),
("md", """**Handoff:** each agent updates a shared context and names the next agent (or `None` to stop). A **hop limit** prevents agents passing the baton back and forth forever."""),
("code", """def intake(ctx):   ctx["issue"] = "app crashes on login"; return ctx, "tech"
def tech(ctx):     ctx["fix"] = "update to v2.1";         return ctx, "followup"
def followup(ctx): ctx["reply"] = f"Please {ctx['fix']} to fix: {ctx['issue']}."; return ctx, None
AGENTS = {"intake": intake, "tech": tech, "followup": followup}

ctx, current, hops = {}, "intake", 0
while current and hops < 5:
    print("handoff ->", current)
    ctx, current = AGENTS[current](ctx)
    hops += 1
print(ctx)"""),
("md", """**Debate:** two agents answer; a judge scores them against a **rubric** (a list of criteria). Real judges are LLMs given the rubric."""),
("code", """answers = {
    "agent_A": "Use an AI agent; it adapts if the page changes.",
    "agent_B": "Use a fixed script: cheaper, faster, and the same result every time; add an agent only if pages change often.",
}
rubric = ["cheaper", "faster", "same result", "only if"]
scores = {name: sum(word in text.lower() for word in rubric) for name, text in answers.items()}
print(scores, "-> winner:", max(scores, key=scores.get))"""),
("md", """## Part 3 — Memory

**Short-term memory** = the last few messages. A `deque` with `maxlen` drops old ones automatically. Real systems also *summarise* what falls off."""),
("code", """from collections import deque
short_term = deque(maxlen=3)
for i in range(1, 6):
    short_term.append(f"user message {i}")
print(list(short_term))"""),
("md", """**Long-term memory** = facts stored as **embeddings** (lists of numbers capturing meaning) and recalled by **cosine similarity** (how closely two vectors point the same way). We use the small `all-MiniLM-L6-v2` model; if it cannot be downloaded, a simple word-hashing embedder is used instead so the notebook still runs."""),
("code", """import numpy as np

def get_embedder():
    try:
        from sentence_transformers import SentenceTransformer
        m = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("using MiniLM embeddings")
        return lambda texts: m.encode(texts, normalize_embeddings=True)
    except Exception as e:
        print("MiniLM unavailable, using hashing fallback:", type(e).__name__)
        def h(texts, dim=256):
            out = np.zeros((len(texts), dim))
            for i, t in enumerate(texts):
                for w in t.lower().split():
                    out[i, hash(w.strip(".,?!")) % dim] += 1
            return out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-9)
        return h

embed = get_embedder()
facts = ["The user's name is Priya.", "Priya prefers answers in Telugu.",
         "Priya's project deadline is 5 December.", "Priya is allergic to peanuts."]
fact_vecs = embed(facts)

def recall(query, k=1):
    scores = fact_vecs @ embed([query])[0]
    return [(round(float(scores[i]), 3), facts[i]) for i in np.argsort(-scores)[:k]]

for q in ["Which language should I reply in?", "When is the project due?", "Can she eat satay sauce?"]:
    print(q, "->", recall(q))"""),
("md", """An agent uses long-term memory by recalling relevant facts and **putting them into the prompt** before calling the LLM:"""),
("code", """def build_prompt(user_msg):
    memories = [f for _, f in recall(user_msg, k=2)]
    history = "\\n".join(short_term)
    return f"Known facts: {memories}\\nRecent chat:\\n{history}\\nUser: {user_msg}"
print(build_prompt("Remind me when my deadline is"))"""),
("md", """## Part 4 — MCP: a real server and client

We define an MCP server with the official `mcp` package. In **mcp 2.x** the class is `MCPServer`; in **1.x** it was `FastMCP`. The cell installs `mcp` if missing (e.g. in Colab) and imports whichever exists.

* `@server.tool()` → a **tool** the model may call.
* `@server.resource("notes://...")` → a **resource**: read-only data addressed by a URI.
* `@server.prompt()` → a **prompt** template the user can pick."""),
("code", """try:
    import mcp
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "mcp"], check=True)
from importlib.metadata import version
print("mcp", version("mcp"))
try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as MCPServer

server = MCPServer("study-helper")
NOTES = {"agents": "An agent is an LLM in a loop with tools.",
         "mcp": "MCP connects AI apps to tool servers in one standard way.",
         "react": "ReAct = Reason + Act."}

@server.tool()
def add(a: float, b: float) -> float:
    \"\"\"Add two numbers.\"\"\"
    return a + b

@server.tool()
def search_notes(keyword: str) -> str:
    \"\"\"Return study notes containing the keyword.\"\"\"
    hits = [f"{k}: {v}" for k, v in NOTES.items() if keyword.lower() in (k + v).lower()]
    return "\\n".join(hits) or "no match"

@server.resource("notes://index")
def notes_index() -> str:
    \"\"\"All note topics.\"\"\"
    return ", ".join(NOTES)

@server.resource("notes://{topic}")
def note(topic: str) -> str:
    \"\"\"One note by topic.\"\"\"
    return NOTES.get(topic, "no such note")

@server.prompt()
def quiz_me(topic: str) -> str:
    \"\"\"Ask the model to quiz me.\"\"\"
    return f"Ask me 3 short quiz questions about {topic}, one at a time."
print("server defined:", server.name)"""),
("md", """Now connect a **client**, exactly as a host app (Claude Desktop, VS Code) would: list what the server offers, then call a tool, read a resource and fetch a prompt.

In mcp 2.x, `mcp.Client(server)` connects **in memory** (no subprocess) — perfect for testing. MCP is **asynchronous** (it waits on input/output), so we use `async`/`await`; Jupyter lets us `await` directly in a cell. If an older SDK without `Client` is installed, we call the server's own methods instead."""),
("code", """async def explore():
    try:
        from mcp import Client
    except ImportError:
        Client = None
    if Client is None:                                   # mcp 1.x fallback
        tools = await server.list_tools()
        print("Tools:", [t.name for t in tools])
        print(await server.call_tool("add", {"a": 2, "b": 40}))
        return
    async with Client(server) as client:
        tools = (await client.list_tools()).tools
        print("Tools:", [t.name for t in tools])
        print("Schema of add:", tools[0].input_schema)
        r = await client.call_tool("add", {"a": 2, "b": 40})
        print("add ->", r.content[0].text)
        r = await client.call_tool("search_notes", {"keyword": "loop"})
        print("search_notes ->", r.content[0].text)
        print("Resources:", [x.uri for x in (await client.list_resources()).resources])
        print("Templates:", [x.uri_template for x in (await client.list_resource_templates()).resource_templates])
        print("notes://react ->", (await client.read_resource("notes://react")).contents[0].text)
        p = await client.get_prompt("quiz_me", {"topic": "MCP"})
        print("prompt ->", p.messages[0].content.text)

await explore()"""),
("md", """### Connecting over stdio to the script in `code/`

Real hosts start the server as a separate process and talk over **stdio** (its standard input/output). If you are running inside the repo, this cell starts `../code/mcp_server.py` that way. In Colab the file is not there, so the cell skips."""),
("code", """import sys, pathlib
script = pathlib.Path("../code/mcp_server.py")
try:
    from mcp import Client, StdioServerParameters
    has_client = True
except ImportError:
    has_client = False

if script.exists() and has_client:
    async def over_stdio():
        params = StdioServerParameters(command=sys.executable, args=[str(script.resolve())])
        async with Client(params) as c:
            print("stdio tools:", [t.name for t in (await c.list_tools()).tools])
            print((await c.call_tool("search_notes", {"keyword": "protocol"})).content[0].text)
    await over_stdio()
else:
    print("code/mcp_server.py not found here (or old mcp) - skipping the stdio demo.")"""),
("md", """### From MCP tools to model tools

A host turns each MCP tool into a tool definition for its model. The MCP `input_schema` *is* JSON Schema, so it drops straight into the Anthropic format from notebook 01:"""),
("code", """async def mcp_tools_as_anthropic():
    from mcp import Client
    async with Client(server) as c:
        return [{"name": t.name, "description": t.description, "input_schema": t.input_schema}
                for t in (await c.list_tools()).tools]
try:
    import json
    print(json.dumps(await mcp_tools_as_anthropic(), indent=2))
except ImportError:
    print("needs mcp 2.x Client")"""),
("md", """## Recap

* A **crew** = role-based system prompts + a loop over tasks passing outputs forward.
* **Supervisor / handoff / debate** are small control-flow patterns around LLM calls.
* **Memory** = what you put back into the prompt: recent messages + recalled facts.
* **MCP** = one standard way for hosts to discover and call tools, read resources and use prompts from any server.

**Try it:** add a `word_count(text: str) -> int` tool to the MCP server, re-run the client cell, and check it appears with the right schema."""),
]

# =============================================================================
# 3. SLIDES
# =============================================================================
DECK = {
    "title": "Module 10 - Agentic AI",
    "subtitle": "Tools, loops, LangGraph, crews, memory, MCP and safety",
    "slides": [
        {"title": "What we will learn today",
         "bullets": ["What an agent is: LLM + tools + loop", "Tool use with JSON Schema (OpenAI vs Anthropic)",
                     "The ReAct loop, built from scratch", "LangGraph, CrewAI, multi-agent patterns",
                     "Memory and the Model Context Protocol (MCP)", "Safety and human-in-the-loop"],
         "notes": "Welcome everyone. Until now our LLMs could only talk. Today they learn to act. By the end you will have built an agent loop yourself, run a LangGraph agent with memory, and built a real MCP server that tools like Claude Desktop can use. We finish with safety, because agents that act can also make mistakes that cost money."},
        {"title": "Chatbot vs agent: the intern analogy",
         "bullets": ["Chatbot: you send one letter, you get one reply", "Agent: an intern at a desk with a phone and files",
                     "The intern decides the next step, again and again", "The intern only ASKS the receptionist (your code) to make calls"],
         "notes": "Use the intern analogy. A chatbot is an expert you can write one letter to. An agent is an intern with a phone, a calculator and a filing cabinet, who keeps working until the goal is done. Key point: the intern never touches the phone directly. They ask the receptionist, which is our code. That is why we stay in control."},
        {"title": "agent = LLM + tools + loop",
         "bullets": ["LLM decides what to do next", "Your code runs the requested tool", "The result goes back to the LLM", "Repeat until a final answer"],
         "image": str(IMG / "agent_loop.png"),
         "notes": "This is the single most important diagram of the module. Walk around the loop with your finger: the model decides, our code runs the tool, the result goes back, the model decides again. Ask the class: where could this go wrong? Lead them to infinite loops and wrong tools, which we fix later."},
        {"title": "Workflow or agent?",
         "bullets": ["Workflow: you fixed the steps - predictable, cheap", "Router: the LLM picks one branch",
                     "Agent: the LLM picks every next step - flexible, costly", "Use the least agentic design that works"],
         "notes": "Many problems do not need an agent. If the steps are always the same, write a workflow. Agents shine when the steps depend on what is discovered along the way, like debugging. Module 11 goes deeper on this choice."},
        {"title": "Tool use: the restaurant order slip",
         "bullets": ["Menu = tool definitions (name, description, schema)", "Order slip = tool call written by the model",
                     "Kitchen = your code runs the function", "Plate = tool result sent back"],
         "notes": "The model never runs code. It fills in an order slip that says which tool and which arguments. Our kitchen cooks it. Emphasise that the description is read by the model to decide when to use a tool, so it is effectively part of the prompt."},
        {"title": "Same schema, two wrappers",
         "bullets": ["OpenAI: function.parameters", "Anthropic: input_schema", "OpenAI arguments: a JSON string",
                     "Anthropic input: already a dict", "Results: role 'tool' vs a tool_result block"],
         "code": 'OPENAI = {"type": "function",\n  "function": {"name": "get_weather",\n    "description": "...",\n    "parameters": SCHEMA}}\n\nANTHROPIC = {"name": "get_weather",\n  "description": "...",\n  "input_schema": SCHEMA}',
         "notes": "Show both side by side. The JSON Schema in the middle is identical. The common bug: forgetting that OpenAI gives arguments as a string, so you must call json.loads. Notebook 01 shows both, with real calls guarded by an API-key check."},
        {"title": "ReAct: the detective's notebook",
         "bullets": ["Thought: what do I need?", "Action: tool[input]", "Observation: written by OUR code", "Repeat until Final Answer"],
         "image": str(IMG / "react_loop.png"),
         "notes": "ReAct means Reason plus Act. Like a detective writing down suspicions, checking, then writing what they found. Stress that the Observation line is written by our code, not the model. If the model writes its own observations, it is making things up."},
        {"title": "The loop in 8 lines",
         "code": "for step in range(max_steps):\n    reply = llm(transcript)\n    transcript += reply\n    if 'Final Answer:' in reply:\n        return answer\n    name, arg = parse(reply)\n    obs = TOOLS[name](arg)\n    transcript += 'Observation: ' + obs",
         "bullets": ["max_steps stops runaway loops", "Unknown tool -> error text, not a crash", "Scripted fake LLM = offline and repeatable"],
         "notes": "This is all an agent is. In notebook 02 the LLM is a scripted fake so it runs offline and the same way every time. Swap it for a real model and the loop does not change. Run the notebook live here."},
        {"title": "LangGraph: a board game for agents",
         "bullets": ["State = the board (a dict)", "Node = a square (a function)", "Edge / conditional edge = paths and forks",
                     "Checkpointer = save game; thread_id = save slot"],
         "image": str(IMG / "langgraph_agent.png"),
         "notes": "LangGraph draws the same loop as a graph. The llm node, a fork called tools_condition, a tools node, and back. Compiling with a checkpointer gives memory: the same thread_id continues the same conversation. Show notebook 03 step 5."},
        {"title": "Pausing for a human",
         "bullets": ["interrupt(payload) pauses and saves the graph", "Human answers in a UI", "invoke(Command(resume='yes')) continues",
                     "Needs a checkpointer"],
         "code": "def human_gate(state):\n    ans = interrupt({'question': 'Approve?'})\n    return {'approved': ans == 'yes'}\n\napp.invoke(Command(resume='yes'), cfg)",
         "notes": "This is how real products ask you before sending an email or spending money. The graph stops, its state is saved, and it continues later, even hours later, when the person clicks approve."},
        {"title": "CrewAI: a film crew",
         "bullets": ["Agent = role + goal + backstory", "Task = description + expected output + agent",
                     "Crew = agents + tasks + process", "Not installed here: plain-Python mimic in notebook 04"],
         "notes": "CrewAI models a team. Each agent's role, goal and backstory become its system prompt. Tasks run in order and each sees the earlier output. In notebook 04 we rebuild this in 40 lines, which proves there is no magic: prompts plus a loop."},
        {"title": "Multi-agent patterns",
         "bullets": ["Supervisor: a receptionist routes to specialists", "Handoff: a relay baton with context",
                     "Debate: two answers, a judge decides", "More agents = more cost: only when one agent struggles"],
         "image": str(IMG / "multi_agent_patterns.png"),
         "notes": "Three patterns to know by name. Warn about ping-pong in handoffs and the cost of debates. A single agent with good tools is often enough."},
        {"title": "Memory",
         "bullets": ["LLMs remember nothing between calls", "Short-term: recent messages, trimmed or summarised",
                     "Long-term: facts as embeddings in a vector store", "Memory = what you put back into the prompt"],
         "notes": "Sticky note versus filing cabinet. Short-term is the recent chat; long-term is RAG over the agent's own notes. Mention privacy: users should be able to see and delete what is remembered."},
        {"title": "MCP: USB-C for AI apps",
         "bullets": ["Host = the AI app (Claude Desktop, VS Code)", "Client = connector inside the host", "Server = offers capabilities",
                     "Tools (model), Resources (app), Prompts (user)", "Transports: stdio (local) or HTTP"],
         "image": str(IMG / "mcp_architecture.png"),
         "notes": "Without a standard, 10 apps and 10 tools need 100 connectors. With MCP they need 20. Explain who controls each primitive: the model calls tools, the app attaches resources, the user picks prompts."},
        {"title": "A minimal MCP server",
         "code": "from mcp.server.mcpserver import MCPServer\nmcp = MCPServer('study-helper')\n\n@mcp.tool()\ndef add(a: float, b: float) -> float:\n    '''Add two numbers.'''\n    return a + b\n\nif __name__ == '__main__':\n    mcp.run()   # stdio",
         "bullets": ["mcp 2.x: MCPServer; 1.x: FastMCP", "Type hints + docstring -> schema", "Never print() to stdout in stdio servers",
                     "Claude Desktop: claude_desktop_config.json", "VS Code: MCP: Add Server"],
         "notes": "Show code/mcp_server.py and run code/mcp_client.py. Then show the Claude Desktop config. If you have Claude Desktop, connect it live; it is the most memorable moment of the session."},
        {"title": "Safety: the two-signature rule",
         "bullets": ["Least privilege + allow-lists", "Risk levels: auto-run reads, approve writes and money",
                     "Budgets: max steps, max calls, timeouts", "Treat tool output as data (prompt injection)", "Audit logs for every action"],
         "image": str(IMG / "hitl_flow.png"),
         "notes": "A bank teller can check a balance alone but needs a manager to approve a big transfer. Agents get the same rule. Run code/hitl_guard.py with --auto-deny to show blocked, denied and auto-run decisions."},
        {"title": "Common mistakes",
         "bullets": ["No max_steps -> endless loops and big bills", "Vague tool descriptions -> wrong tool chosen",
                     "Not validating arguments", "Crashing on tool errors instead of returning text",
                     "Forgetting thread_id -> 'my agent has no memory'", "print() inside a stdio MCP server"],
         "notes": "Go through each and ask who has seen it already in the notebooks. Each has a fix listed in trainer-notes.md."},
        {"title": "Recap and exercises",
         "bullets": ["Agent = LLM + tools + loop", "Tools = name + description + JSON Schema", "LangGraph = graph + checkpointer + interrupt",
                     "MCP = one standard plug for tools", "Now: exercises.md 1-4 in class, 5+ at home"],
         "notes": "Summarise the four headline ideas. Students start exercises 1 to 4 in class; the harder ones are homework. Solutions are in solutions/."},
    ],
}

# =============================================================================
# 4. EXCEL: agent framework comparison
# =============================================================================
FRAMEWORKS = [
    ["Framework", "Style / mental model", "Best for", "Learning curve", "Memory / persistence", "Human-in-the-loop", "Multi-agent", "Language", "Licence (check repo)", "Docs"],
    ["Plain Python loop", "Your own while-loop around an LLM API", "Learning; tiny focused agents", "Low", "Whatever you build", "Whatever you build", "Manual", "Any", "n/a", "https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview"],
    ["LangGraph", "State graph: nodes, edges, checkpointer", "Production agents needing control, pausing, persistence", "Medium", "Built-in checkpointers (memory, SQLite, Postgres)", "interrupt() + Command(resume)", "Sub-graphs, supervisor/swarm helpers", "Python, JS", "MIT", "https://langchain-ai.github.io/langgraph/"],
    ["CrewAI", "Team of role-based agents with tasks", "Fast prototypes of role-based teams", "Low-Medium", "Built-in memory options", "human_input on tasks", "Core idea (sequential / hierarchical)", "Python", "MIT", "https://docs.crewai.com"],
    ["OpenAI Agents SDK", "Agents + handoffs + guardrails", "Teams already on OpenAI", "Low-Medium", "Sessions", "Via guardrails / app logic", "Handoffs", "Python, JS", "MIT", "https://openai.github.io/openai-agents-python/"],
    ["Claude Agent SDK", "The agent loop behind Claude Code as a library", "Coding / file / tool-heavy agents on Claude", "Medium", "Sessions", "Permission modes and hooks", "Subagents", "Python, TS", "See repo", "https://platform.claude.com/docs/en/agent-sdk/overview"],
    ["AutoGen / Microsoft Agent Framework", "Conversations between agents", "Research, multi-agent chat experiments", "Medium", "Varies by version", "Human proxy agent", "Core idea", "Python, .NET", "MIT", "https://github.com/microsoft/autogen"],
    ["LlamaIndex agents", "Agents on top of data/RAG tooling", "Data-heavy agents over documents", "Medium", "Memory modules", "Workflow events", "Workflows", "Python, TS", "MIT", "https://docs.llamaindex.ai"],
    ["Pydantic AI", "Type-safe agents with Pydantic models", "Python devs who want strict typed outputs", "Low-Medium", "Message history", "Deferred tools / app logic", "Agent delegation", "Python", "MIT", "https://ai.pydantic.dev"],
    ["n8n AI Agent node", "Visual workflow with an agent node", "Non-coders, business automations (module 11)", "Low", "Memory sub-nodes", "Wait / approval nodes", "Limited", "Visual (JS inside)", "Sustainable Use (fair-code)", "https://docs.n8n.io"],
]
CHOOSER = [
    ["If you need...", "Start with", "Why"],
    ["To understand how agents work", "Plain Python loop", "Nothing hidden; notebook 02"],
    ["Pause for approval and resume later", "LangGraph", "interrupt + checkpointer are built in"],
    ["A quick demo of a research + writing team", "CrewAI", "Roles/tasks map directly to the idea"],
    ["Your tools to work in Claude Desktop, VS Code and your app", "MCP server", "Write the tool once, use it in every host"],
    ["A business workflow owned by non-developers", "n8n", "Visual, many integrations (module 11)"],
    ["Strictly typed outputs", "Pydantic AI", "Validation built around Pydantic models"],
]

# =============================================================================
# BUILD
# =============================================================================
def main():
    for name, src in DIAGRAMS.items():
        mermaid(src, IMG / f"{name}.png")
        print("diagram", name)
    notebook(NB01, NB / "01-tools-and-function-calling.ipynb")
    notebook(NB02, NB / "02-react-loop-from-scratch.ipynb")
    notebook(NB03, NB / "03-langgraph-agents.ipynb")
    notebook(NB04, NB / "04-multi-agent-memory-mcp.ipynb")
    print("notebooks built")
    slides(DECK, HERE / "slides" / "10-agentic-ai.pptx")
    print("slides built")
    workbook({"Framework comparison": FRAMEWORKS, "Which one": CHOOSER},
             HERE / "excel" / "agent-framework-comparison.xlsx",
             col_widths={"Framework comparison": [22, 32, 32, 12, 28, 26, 24, 12, 18, 45],
                         "Which one": [45, 22, 45]})
    print("excel built")
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / "10-agentic-ai-handout.pdf",
                      title="Module 10 - Agentic AI")
    print("pdf built")


if __name__ == "__main__":
    main()
