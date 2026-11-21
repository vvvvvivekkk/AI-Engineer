<!-- nav:start -->
> [🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 09 RAG (Retrieval-Augmented Generation)](../09-rag/README.md) · [11 AI Automation ➡️](../11-ai-automation/README.md)  
> **🦾 Module 10 · Agentic AI**  
> [📖 Lesson](concepts.md) · [📄 PDF handout](pdf/10-agentic-ai-handout.pdf) · [🎞️ Slides](slides/10-agentic-ai.pptx) · [📓 Notebooks](notebooks/) · [✍️ Exercises](exercises.md) · [✅ Solutions](solutions/) · [🧑‍🏫 Trainer notes](trainer-notes.md) · [🔗 Resources](resources.md)
<!-- nav:end -->

# Module 10 — Agentic AI

**Weeks 17–18 · about 8–10 hours of learner time · one 1–2 hour live session**

Until now our LLMs could only *answer*. In this module they learn to *act*: call tools, loop until a goal is reached, remember things, work in teams, plug into apps through the Model Context Protocol, and do all this safely with a human in charge of risky steps.

## Learning goals

After this module you can:

1. Explain what an **agent** is (LLM + tools + loop) and when a plain workflow is better.
2. Describe a tool with **JSON Schema** and write it in both the **OpenAI** and **Anthropic** formats.
3. Build a **ReAct** agent loop from scratch and protect it with step limits and error handling.
4. Build a **LangGraph** agent with nodes, edges, conditional edges, a checkpointer (memory) and a human-approval `interrupt`.
5. Explain **CrewAI**'s agents/tasks/crews and the **supervisor**, **handoff** and **debate** patterns.
6. Add **short-term** and **long-term** (vector) memory to an agent.
7. Build a minimal **MCP server** in Python and connect it to Claude Desktop or VS Code.
8. Apply **safety** rules: least privilege, allow-lists, risk levels, budgets, audit logs, human-in-the-loop.

## Prerequisites

- Module 01 (Python functions, dicts, classes), module 07 (calling LLM APIs, messages and roles), module 08 (prompts, prompt injection), module 09 (embeddings and vector search — used for long-term memory).

## Which tool to use, and why

| Task | Tool | Why |
|---|---|---|
| Notebooks 01–04 | **Jupyter in VS Code** or **Google Colab** | Everything runs on CPU with no API keys. Colab needs no install; the notebooks `pip install` `langgraph` / `mcp` if missing. |
| `code/mcp_server.py` with Claude Desktop / VS Code | **VS Code + local Python** | An MCP server must run on your own computer so the host app can start it. Colab cannot do this. |
| `code/crewai_example.py` | **A separate virtual environment** on your computer | CrewAI is large; keep it out of your main environment. |

API keys are optional. Copy `.env.example` to `.env` and fill in a key only if you want the real-model cells to run.

## File map

| Path | What it is |
|---|---|
| `concepts.md` | The main lesson: agents, tool use, ReAct, LangGraph, CrewAI, multi-agent patterns, memory, MCP, safety |
| `notebooks/01-tools-and-function-calling.ipynb` | JSON Schema, OpenAI vs Anthropic formats, validation, dispatch, guarded real calls |
| `notebooks/02-react-loop-from-scratch.ipynb` | A visible ReAct loop with a scripted fake LLM; failure cases; native tool-call loop |
| `notebooks/03-langgraph-agents.ipynb` | State, reducers, conditional edges, streaming, ToolNode agent, checkpointer memory, `interrupt` |
| `notebooks/04-multi-agent-memory-mcp.ipynb` | Plain-Python crew, supervisor/handoff/debate, memory, a real MCP server + client |
| `code/tool_formats.py` | Same tool in both provider formats, offline round trip, real calls behind key checks |
| `code/react_agent.py` | The ReAct loop as a script |
| `code/langgraph_agent.py` | A LangGraph tool agent (offline stand-in, real model if a key is set) |
| `code/crewai_example.py` | Real CrewAI code, heavily commented (not installed here) |
| `code/multi_agent_patterns.py` | Supervisor, handoff and debate in plain Python |
| `code/agent_memory.py` | Short-term buffer + long-term vector memory |
| `code/mcp_server.py` / `code/mcp_client.py` | Minimal MCP server (tools, resources, prompts) and a test client |
| `code/hitl_guard.py` | Allow-list, risk levels, approval, budget, audit log |
| `excel/agent-framework-comparison.xlsx` | Comparison of agent frameworks + "which one?" chooser |
| `slides/10-agentic-ai.pptx` | 18-slide teaching deck with speaker notes |
| `pdf/10-agentic-ai-handout.pdf` | Handout generated from concepts.md |
| `exercises.md` / `solutions/` | 12 exercises (easy → hard) with full solutions |
| `trainer-notes.md` | Session plan, common mistakes, check questions |
| `resources.md` | Curated links |
| `build.py` | Rebuilds images, notebooks, slides, PDF and Excel |

## Rebuild

```bash
python 10-agentic-ai/build.py
python tools/check_module.py 10-agentic-ai --run
```

Versions checked while writing (late 2026): `langgraph` 1.2, `langchain-core` 1.8, `mcp` 2.3 (in `mcp` 1.x the server class is called `FastMCP` — the code handles both).

<!-- nav:start -->
---
[🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 09 RAG (Retrieval-Augmented Generation)](../09-rag/README.md) · [11 AI Automation ➡️](../11-ai-automation/README.md)
<!-- nav:end -->
