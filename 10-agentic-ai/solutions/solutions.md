# Module 10 — Solutions

Runnable code for every coding exercise is in [`solutions_code.py`](solutions_code.py) (`python solutions_code.py` runs them all offline) and [`mcp_server_solution.py`](mcp_server_solution.py) (exercise 9). This file explains the answers.

---

### 1. Agent or workflow?
a) **Fixed workflow.** The steps never change (download → summarise → email). A scheduled script or n8n workflow is cheaper and predictable.
b) **Router.** One LLM decision (billing or tech), then a fixed path. No loop needed.
c) **Agent.** The steps depend on what is discovered (read logs, open files, run tests, edit, re-run). Nobody can write the steps in advance.
d) **Fixed workflow.** Trigger on new post → translate → save. The LLM is one step, not the controller.

### 2. JSON Schema
```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "date": {"type": "string", "description": "ISO date, e.g. 2026-12-01"},
    "duration_minutes": {"type": "integer", "enum": [15, 30, 60]},
    "attendees": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["title", "date"]
}
```
Validation fails with `45 is not one of [15, 30, 60]`: the `enum` keyword lists the only allowed values. In an agent, you would send that message back to the model as the tool result so it can pick a valid duration. See `ex2()`.

### 3. Reverse conversion
```python
def anthropic_to_openai(tool):
    return {"type": "function", "function": {
        "name": tool["name"], "description": tool.get("description", ""),
        "parameters": tool["input_schema"]}}
```
The schema itself is unchanged; only the wrapper keys move (`input_schema` → `function.parameters`).

### 4. Unit-convert tool
Register a new function in the `TOOLS` dict; the loop does not change at all. That is the point: tools are plug-ins. The tool parses `"508 m ft"`, multiplies by 3.28084 and returns `"1667 ft"`. See `ex4()`.

### 5. Stop repeated calls
Keep `last_action` and a `repeats` counter. On the second identical action, return a warning observation (the model gets a chance to change course). On the third, stop the loop. See `run_agent_no_repeats()`. In production you might also compare *arguments*, not only the text, and count repeats across the whole run, not just in a row.

### 6. Errors as text
```python
def safe_run(fn, args):
    try:
        return json.dumps(fn(**args))
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"
```
The model sees `Error: ZeroDivisionError: division by zero` and can apologise or try another approach. A raised exception would end the whole conversation.

### 7. LangGraph router
The key line is
`g.add_conditional_edges("classify", lambda s: s["category"], {"math": "math", "chat": "chat"})`.
The router returns a key; the dict maps that key to a node name. Output: `12 * 7 → 84`, `hello → Hello! How can I help?`. Note that the `math` node still validates the expression before `eval`.

### 8. Separate threads
Each `thread_id` is its own save slot. Thread A (two questions) ends with 8 messages; thread B (one question) has 4. The number of checkpoints is higher than the number of messages because LangGraph saves after the input and after every node. See `ex8()`.

### 9. MCP tool + resource
```python
@mcp.tool()
def word_count(text: str) -> int:
    """Count the words in a piece of text."""
    return len(text.split())

@mcp.resource("notes://count")
def notes_count() -> str:
    return str(len(NOTES))
```
Client calls: `await c.call_tool("word_count", {"text": "..."})` and `await c.read_resource("notes://count")`.
Claude Desktop entry (example paths — use your own absolute paths):
```json
{"mcpServers": {"study-helper": {
  "command": "/Users/you/.venv/bin/python",
  "args": ["/Users/you/AI-Engineer/10-agentic-ai/solutions/mcp_server_solution.py"]}}}
```

### 10. Approval with edits
`interrupt()` returns whatever the human sent with `Command(resume=...)`. Check it: `"yes"` → approve; digits → approve and **return a new `amount`** in the update; anything else → reject. The `execute` node reads the (possibly edited) amount. All three paths are printed by `ex10()`. This "approve / reject / edit" trio is the standard HITL design.

### 11. Supervisor as a graph
The supervisor node writes `route`; `add_conditional_edges("supervisor", lambda s: s["route"], ["billing", "tech", "general"])` sends control to the matching worker (a list works when the returned value equals a node name). `stream(stream_mode="updates")` yields one dict per node, so the path is `supervisor -> billing` etc. A real supervisor would be an LLM node with a "reply with one word" prompt or a structured-output schema.

### 12. Guarded agent
Every tool call passes through `guarded_call`. Result: `search_docs → auto`, `send_email → denied` (human said no), `delete_all → blocked` (not on the allow-list). The model receives the refusal text as the tool result and can explain it to the user.

**Replacing `auto_answer` with `interrupt`:** put the tool-running code in a LangGraph node compiled with a checkpointer. When a risky call is found, call `interrupt({"tool": name, "args": args})`; the graph pauses and the web app shows an Approve/Reject button. When the person clicks, the app calls `app.invoke(Command(resume="y"), config)` with the same `thread_id`, and the node continues by running (or skipping) the tool. Because the state is checkpointed, the approval can come minutes or days later.
