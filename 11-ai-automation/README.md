# Module 11 — AI Automation

**Week 19 · about 8 hours of learner time · one 1–2 hour live session**

Module 10 taught you to build agents. This module asks the business question: **when do you actually need one?** Most real-world value comes from **workflows** with a small AI step — classify, summarise, extract — wired to triggers like webhooks and schedules. You will learn n8n (a visual workflow tool) from zero, import three ready-made workflows, build a secure webhook receiver in FastAPI, write robust Python automations, and see how browser agents and computer-use agents work and when they are worth their cost.

## Learning goals

After this module you can:

1. Explain the difference between automation (fixed workflows) and agents, and place a task on the "automation spectrum".
2. Explain n8n's nodes, triggers, items, expressions, credentials and executions, and run n8n with Docker, npx or n8n Cloud.
3. Import, configure and explain the three workflows in `workflows/`, node by node.
4. Build a webhook receiver that verifies signatures, validates data, ignores duplicates and replies fast.
5. Write a Python automation with timeouts, retries with backoff and a schedule (and know when to use cron instead).
6. Describe how Playwright, browser agents (browser-use) and computer-use agents (Anthropic computer use) work, and the safety rules for them.
7. Decide when automation beats an agent, and estimate ROI with the Excel calculator.

## Prerequisites

Module 07 (calling LLM APIs), module 09 (RAG — used by workflow 03), module 10 (agents, tool use, safety). Basic HTTP ideas (GET/POST, JSON) are explained in `concepts.md`.

## Which tool to use, and why

| Task | Tool | Why |
|---|---|---|
| Notebooks 01–04 | **Jupyter in VS Code** or **Google Colab** | All offline: mock network, `TestClient`, simulated browser. No keys needed. |
| n8n workflows | **n8n in Docker** (or `npx n8n`, or n8n Cloud) | n8n is a separate app with its own web UI at `http://localhost:5678`. |
| `code/webhook_receiver.py`, `code/python_automation.py` | **VS Code + terminal** | They run as servers / long-running scripts, which notebooks are not designed for. |
| `code/playwright_basics.py` | **Local Python** with `playwright install chromium` | Needs a real browser binary. |
| `code/browser_use_agent.py`, `code/computer_use_agent.py --real` | **Separate virtual environment / sandbox VM**, API key | Large dependencies; computer use must be isolated for safety. |

## File map

| Path | What it is |
|---|---|
| `concepts.md` | The main lesson |
| `workflows/01-webhook-ticket-triage.json` | n8n: webhook → LLM classify → IF urgent → Slack / email |
| `workflows/02-rss-digest-to-sheets.json` | n8n: schedule → RSS → limit → LLM summary → Google Sheet |
| `workflows/03-rag-answer-webhook.json` | n8n: question webhook → search API → IF found → LLM answer → respond |
| `notebooks/01-automation-vs-agents-python.ipynb` | Workflow vs agent call counts; retries with a mock server; parse/filter/save; schedule and cron |
| `notebooks/02-webhooks-fastapi-offline.ipynb` | Signed webhooks, validation, idempotency, background tasks, `/search` endpoint — tested with `TestClient` |
| `notebooks/03-n8n-workflow-json.ipynb` | Read, tabulate, validate and simulate the n8n workflow files |
| `notebooks/04-browser-and-computer-use-offline.ipynb` | How agents see pages, a simulated browser agent, a simulated computer-use loop with safety, cost comparison |
| `code/webhook_receiver.py` / `code/send_test_webhook.py` | FastAPI receiver (+ `/search` for workflow 03) and a signed test sender |
| `code/python_automation.py` | Scheduled RSS digest in plain Python (httpx + schedule) |
| `code/validate_workflows.py` | Structure checker for the workflow JSON files |
| `code/playwright_basics.py` | Scripted browser automation on a local demo page |
| `code/browser_use_agent.py` | LLM browser agent with browser-use (not installed here) |
| `code/computer_use_agent.py` | Simulated computer-use loop; `--real` prints (never executes) requested actions |
| `excel/automation-ideas-roi.xlsx` | ROI calculator with live formulas + automation ideas list |
| `slides/11-ai-automation.pptx` | 18-slide deck with speaker notes |
| `pdf/11-ai-automation-handout.pdf` | Handout generated from concepts.md |
| `exercises.md` / `solutions/` | 12 exercises (easy → hard) with solutions |
| `trainer-notes.md` | Session plan, mistakes, check questions |
| `resources.md` | Curated links |
| `build.py` | Rebuilds images, notebooks, slides, PDF, Excel |

## Rebuild and check

```bash
python 11-ai-automation/build.py
python 11-ai-automation/code/validate_workflows.py
python tools/check_module.py 11-ai-automation --run
```

The workflow files contain **no secrets** — only `REPLACE_WITH_YOUR_CREDENTIAL_ID` placeholders. Create your own credentials inside n8n after importing.
