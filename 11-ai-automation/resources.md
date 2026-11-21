# Module 11 — Resources

Curated links with one line on why each is useful. The course's nine source repos have little on workflow automation, so this module leans on official documentation. Where a link came from the source catalogue, the source number is given (see root `SOURCES.md`: 1 = openbestof/awesome-ai, 6 = ashishpatel26 project list, 7 = Eric-LLMs/awesome-ai-engineering, 8 = dipakkr/awesome-ai-engineering, 9 = dave-nachman/awesome-ai-engineering). Descriptions are our own. Tools in this space change quickly — check dates.

## Workflow automation (n8n and friends)

| Resource | Level | Why |
|---|---|---|
| [n8n](https://n8n.io) | Beginner | The tool used in this module: visual workflows, many integrations, AI nodes, self-hostable. (official) |
| [n8n documentation](https://docs.n8n.io) | Beginner–intermediate | Nodes, triggers, credentials, expressions, Docker hosting and the AI Agent node — the reference for everything in section 3–4 of concepts.md. (official) |
| [Flowise](https://github.com/FlowiseAI/Flowise) | Beginner | Drag-and-drop builder focused on LLM chains and agents — an alternative to compare with n8n. (source 1) |
| [Dify](https://github.com/langgenius/dify) | Beginner–intermediate | Self-hostable LLM app platform with workflows and RAG built in. (source 1) |
| [CrewAI docs (Flows)](https://docs.crewai.com) | Intermediate | Event-driven "flows" that mix fixed steps with agent steps in code. (official) |
| [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) | Intermediate | Strong argument for owning your control flow with deterministic code — the heart of "when automation beats agents". (source 9) |

## Python automation and webhooks

| Resource | Level | Why |
|---|---|---|
| [Automate the Boring Stuff with Python](https://automatetheboringstuff.com/) | Beginner | Free book covering files, spreadsheets, email and web scripting — the fundamentals under every automation. (source 8) |
| [FastAPI](https://fastapi.tiangolo.com) | Intermediate | The framework used for our webhook receiver; excellent tutorial, including testing with `TestClient`. (official) |
| [HTTPX](https://www.python-httpx.org) | Intermediate | Docs for the HTTP client used here, including timeouts and `MockTransport` for offline tests. (official) |
| [schedule (PyPI)](https://pypi.org/project/schedule/) | Beginner | The tiny in-process scheduler used in `python_automation.py`. (official) |
| [5 web scraping projects with Python](https://amankharwal.medium.com/5-web-scraping-projects-with-python-4bcc25ff039) | Intermediate | Project ideas for the "collect data" step of a pipeline (Medium may limit free reads). (source 6) |

## Browser and computer-use agents

| Resource | Level | Why |
|---|---|---|
| [Playwright for Python](https://playwright.dev/python/) | Intermediate | Official docs: installation, locators (`get_by_role` etc.), auto-waiting, screenshots. (official) |
| [browser-use](https://github.com/browser-use/browser-use) | Intermediate | The open-source browser-agent library shown in `code/browser_use_agent.py`; check its README for the current API. (official repo) |
| [Anthropic computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) | Advanced | Current tool versions, supported actions, the Docker reference implementation and safety guidance. (official) |
| [Open Interpreter](https://github.com/KillianLucas/open-interpreter/) | Intermediate | Lets an LLM run code on your machine — powerful, and a clear lesson in why sandboxing matters. (source 1) |
| [MCP reference servers](https://github.com/modelcontextprotocol/servers) | Intermediate | Ready connectors (filesystem, git, fetch) that automations and agents can call — links back to module 10. (source 7) |

## Handing automations to non-coders

| Resource | Level | Why |
|---|---|---|
| [Gradio](https://www.gradio.app/) | Beginner | Wrap a Python function in a shareable web UI in a few lines. (source 9) |
| [Streamlit](https://streamlit.io/) | Beginner | Quick dashboards to trigger and monitor automations. (source 9) |

## Going further (optional)

| Resource | Why |
|---|---|
| [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | An early autonomous-agent project that later added a workflow builder — a useful historical contrast. (source 1) |
| [LLM App (Pathway)](https://github.com/pathwaycom/llm-app) | Real-time data pipelines feeding LLM apps, for "always fresh" automations. (source 1) |
| [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) | Fast local speech-to-text, for voice-note → task automations. (source 1) |
| [Adala](https://github.com/HumanSignal/Adala) | Agents specialised in data-labelling automation; connects to module 12. (source 1) |

## Also in this module
- `excel/automation-ideas-roi.xlsx` — ROI calculator with live formulas and a list of automation ideas with the least-agentic approach for each.
