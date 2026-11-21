# Module 10 — Exercises

Graded from easy (⭐) to hard (⭐⭐⭐). Everything can be done offline. Full solutions are in [`solutions/solutions.md`](solutions/solutions.md) and the `.py` files in `solutions/`.

---

### 1. ⭐ Agent or workflow?
For each task, say whether you would build a **fixed workflow**, a **router**, or an **agent**, and give one reason.
a) Every night, download yesterday's sales CSV and email a summary.
b) Read a support email and send it to either the billing or the tech team.
c) "Find out why our test suite fails and fix it."
d) Translate every new blog post into Hindi.

### 2. ⭐ Write a JSON Schema
Write the JSON Schema for a tool `book_meeting(title: str, date: str, duration_minutes: int, attendees: list of str)`. `title` and `date` are required. `duration_minutes` must be one of 15, 30 or 60. Then validate `{"title": "Sync", "date": "2026-12-01", "duration_minutes": 45}` with `jsonschema` and explain the error.

### 3. ⭐ Convert formats
Write `anthropic_to_openai(tool: dict) -> dict` (the reverse of the function in notebook 01) and test it on the `ANTHROPIC_TOOL` from the notebook.

### 4. ⭐⭐ Add a tool to the ReAct agent
Add a `unit_convert[value from to]` tool (metres ↔ feet) to `code/react_agent.py`. Write a script for the `ScriptedLLM` that answers "How tall is Taipei 101 in feet?" using `search_notes` and then `unit_convert`.

### 5. ⭐⭐ Stop repeated calls
Change `run_agent` so that if the model makes the **exact same Action twice in a row**, the loop returns the observation `"Error: you already called this. Try something else or give a Final Answer."` and, on the third identical call, stops completely.

### 6. ⭐⭐ Return errors, not crashes
In notebook 01's `run_tool`, the tool itself might raise an exception (e.g. a network error). Wrap the call so any exception becomes the text `"Error: <ExceptionType>: <message>"`. Test with a tool that does `1/0`.

### 7. ⭐⭐ LangGraph router
Build a LangGraph graph with state `{"question": str, "category": str, "answer": str}`. A `classify` node sets category to `"math"` if the question contains a digit, else `"chat"`. A conditional edge sends math questions to a `math` node (which evaluates the arithmetic) and others to a `chat` node (which returns a polite reply). Run it on `"12 * 7"` and `"hello"`.

### 8. ⭐⭐ Memory across threads
Using the tool agent from notebook 03, show with code that two different `thread_id`s keep separate histories, and print the number of checkpoints saved for each thread.

### 9. ⭐⭐ A new MCP tool and resource
Add to `code/mcp_server.py`:
- a tool `word_count(text: str) -> int`,
- a resource `notes://count` that returns how many notes exist.
Then extend `code/mcp_client.py` to call both. Bonus: write the `claude_desktop_config.json` entry for your server with absolute paths for your computer.

### 10. ⭐⭐⭐ Human approval with edits
Extend the refund graph from notebook 03 so the human can answer `"yes"`, `"no"` or a **number** (a new, edited amount). If a number is given, the refund is sent for that amount instead. Show all three paths.

### 11. ⭐⭐⭐ Supervisor as a LangGraph
Rebuild the supervisor pattern as a LangGraph graph: a `supervisor` node chooses `billing`, `tech` or `general` (keyword rules are fine), each worker is a node that writes `answer`, and every worker goes to `END`. Print the path taken for three requests using `stream`.

### 12. ⭐⭐⭐ Guarded agent end to end
Combine notebook 02's `native_agent` with `code/hitl_guard.py`: every tool call must go through `guarded_call`. Give the agent tools `search_docs` (read), `send_email` (write) and a scripted LLM that tries to call `search_docs`, then `send_email`, then a forbidden `delete_all`. Use `auto_answer="n"` and print the audit log. Explain in 3–4 sentences how you would replace `auto_answer` with a LangGraph `interrupt` in a real app.
