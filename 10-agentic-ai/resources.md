# Module 10 — Resources

Hand-picked links, each with one line on why it is worth your time. Most come from the course's source catalogue (source repos are credited by number; see the root `SOURCES.md` — source 7 is Eric-LLMs/awesome-ai-engineering, CC-BY-4.0; source 9 is dave-nachman/awesome-ai-engineering, CC0; source 1 is openbestof/awesome-ai). Descriptions are our own. Fast-moving tools change often: check dates on anything you read.

## Start here (concepts)

| Resource | Level | Why |
|---|---|---|
| [LLM Powered Autonomous Agents — Lilian Weng](https://lilianweng.github.io/posts/2023-06-23-agent/) | Intermediate | The classic map of the field: planning, memory and tool use in one long, clear article. (source 9) |
| [Agents — Chip Huyen](https://huyenchip.com/2025/01/07/agents.html) | Intermediate | Practical view of tool selection, planning and why agents fail. (source 9) |
| [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) | Intermediate | Engineering principles for reliable agents: own your control flow, keep agents small, put humans in the loop. (source 9) |
| [The Brief History of AI Agents (talk)](https://www.youtube.com/watch?v=f9YleTc8AwE) | Beginner | Short video on how agent ideas evolved; good context before teaching. (source 9) |
| [A Minimal ReAct Agent — LLMs-Lab](https://github.com/Eric-LLMs/LLMs-Lab/tree/main/Agent/Agent_Project) | Intermediate | Another small readable ReAct loop to compare with our notebook 02. (source 7) |

## Tool use / function calling (official docs)

| Resource | Why |
|---|---|
| [Anthropic — tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) | The official Claude tool format (`input_schema`, `tool_use`, `tool_result`). |
| [OpenAI — function calling guide](https://platform.openai.com/docs/guides/function-calling) | The OpenAI format, for side-by-side comparison. |
| [JSON Schema — getting started](https://json-schema.org/learn/getting-started-step-by-step) | Learn the schema language every tool definition uses. |

## Frameworks

| Resource | Why |
|---|---|
| [LangGraph docs](https://langchain-ai.github.io/langgraph/) | Graphs, checkpointers, `interrupt` and streaming — the reference for notebook 03. (official) |
| [CrewAI docs](https://docs.crewai.com) | Agents, tasks, crews and flows; read alongside `code/crewai_example.py`. (official) |
| [CrewAI repo](https://github.com/joaomdmoura/crewAI) | Source and examples (the link redirects to the current repo location). (source 1) |
| [AutoGen](https://github.com/microsoft/autogen) | Microsoft's conversational multi-agent framework, for comparison. (source 1) |
| [MetaGPT](https://github.com/geekan/MetaGPT) | A multi-agent "software company" — a vivid example of role decomposition. (source 1) |
| [GPT Researcher](https://github.com/assafelovic/gpt-researcher) | A complete research agent (plan → search → summarise → report) to read and dissect. (source 1) |

## Model Context Protocol

| Resource | Why |
|---|---|
| [modelcontextprotocol.io](https://modelcontextprotocol.io) | Official docs: concepts, guides, and the list of client apps. (official) |
| [Connect Claude Desktop to local servers](https://modelcontextprotocol.io/docs/develop/connect-local-servers) | Step-by-step config file locations, restart and log-reading tips. |
| [MCP specification repo](https://github.com/modelcontextprotocol/modelcontextprotocol) | The exact protocol: primitives and transports. For when you need the details. (source 7) |
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | The `mcp` package used in `code/mcp_server.py`; its README shows the current API (note the 2.x `MCPServer` rename). (source 7) |
| [MCP reference servers](https://github.com/modelcontextprotocol/servers) | Filesystem, fetch, git and memory servers to read and reuse. (source 7) |
| [FastMCP](https://github.com/jlowin/fastmcp) | A popular decorator-style framework for MCP servers with extra features. (source 7) |
| [VS Code — MCP configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration) | Current file formats and commands for using MCP servers in VS Code. |
| [A2A (Agent2Agent protocol)](https://github.com/a2aproject/A2A) | An emerging standard for agents talking to other agents — the "next layer" after MCP. (source 7) |

## Memory

| Resource | Why |
|---|---|
| [Mem0](https://github.com/mem0ai/mem0) | A ready-made long-term memory layer for agents. (source 7) |
| [LangMem](https://github.com/langchain-ai/langmem) | Semantic, episodic and procedural memory for LangGraph agents. (source 7) |
| [Agent-Memory-Paper-List](https://github.com/Shichun-Liu/Agent-Memory-Paper-List) | Research index if you want to go deep on memory designs. (source 7) |

## Reference agents to study

| Resource | Why |
|---|---|
| [Claude Code](https://github.com/anthropics/claude-code) | A production coding agent; see how a real product handles tools, permissions and MCP. (source 7) |
| [OpenAI Codex CLI](https://github.com/openai/codex) | Open-source terminal coding agent with sandboxed execution — readable source. (source 7) |
| [AgentOps](https://github.com/AgentOps-AI/agentops) | Session replay and cost tracking for debugging agent runs. (source 7) |

## Also in this module
- `excel/agent-framework-comparison.xlsx` — a side-by-side table of frameworks with links to their docs.
