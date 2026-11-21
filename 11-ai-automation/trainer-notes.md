# Module 11 — Trainer notes

Read `concepts.md` once and run the four notebooks (about 1 minute in total). If you can, install n8n with Docker the day before and import workflow 01 — a live n8n canvas is the most engaging part of this session. If you cannot, the notebooks and diagrams carry the session on their own.

## 1. What students should be able to do after the session

- Explain the difference between a workflow and an agent, and why "an LLM step inside a workflow" is not an agent.
- Name n8n's core parts (node, trigger, item, expression, credential, execution) and import a workflow file.
- Explain each node of workflow 01 and what the IF node's two outputs mean.
- State the four rules of a reliable webhook (verify, validate, de-duplicate, reply fast).
- Write a retry loop with backoff and a timeout.
- Explain how browser agents and computer-use agents work, and three safety rules for them.
- Use the decision guide and the ROI calculator to argue for automation or an agent.

## 2. Teaching sequence (2-hour session; starred rows can be cut for 1 hour)

| Time | Activity | Materials | Notes |
|---|---|---|---|
| 0:00–0:10 | Hook: "train vs taxi"; ask for repetitive tasks from students' lives | Slides 1–3 | Write 5 student examples on the board; reuse them at the end with the decision tree. |
| 0:10–0:20 | Part 1 of notebook 01: workflow vs agent call counts | Notebook 01 part 1 | The "4× the calls, same answer" moment is the key insight. |
| 0:20–0:45 | n8n from zero: vocabulary, running it, importing workflow 01 | Slides 4–9, n8n (Docker) or diagrams | Show an execution and click into each node's input/output. Show the credential warnings. |
| 0:45–0:55 | Read the JSON: notebook 03 steps 2–5 | Notebook 03 | Connect what they saw on the canvas to `nodes` and `connections`. |
| 0:55–1:05 | Break | | |
| 1:05–1:25 | Webhooks: doorbell analogy, four rules, TestClient demo | Slides 10–11, notebook 02 | Run the "good / duplicate / bad signature / bad data" cell and ask students to predict each status code first. |
| 1:25–1:35 ★ | Python automation: retries with a flaky mock server, schedule, cron | Slide 12, notebook 01 parts 2–4 | |
| 1:35–1:50 | Browser and computer-use agents: how they see, safety, cost | Slides 13–14, notebook 04 | Optional live demo: `python code/playwright_basics.py` if Playwright is installed. |
| 1:50–1:57 | When automation beats agents + ROI | Slides 15–16, Excel | Run the board examples through the decision tree. Change one Excel number live. |
| 1:57–2:00 | Recap, set exercises | Slides 17–18 | 1–4 in class / tonight, 5–12 homework. |

**One-hour version:** hook (5) → notebook 01 part 1 (10) → n8n + workflow 01 walkthrough (20) → webhook four rules with notebook 02 (15) → decision tree + recap (10). Assign notebooks 03–04 as homework.

## 3. Common student mistakes and how to fix them

| Mistake | Symptom | Fix |
|---|---|---|
| Reaching for an agent first | Slow, expensive, unpredictable solution to a simple task | Walk the decision tree: API? steps known? Only then consider an agent. |
| Pasting API keys into node parameters or workflow JSON | Key leaks when the file is shared or committed | Use n8n **Credentials**; files then contain only `{id, name}` references. Run `validate_workflows.py`. |
| Using the n8n **Test URL** in production | Webhook works while the editor is open, then stops | Activate the workflow and use the **Production URL**. |
| Expression typos / wrong node name in `$('...')` | `ERROR: Referenced node doesn't exist` or empty values | Node names are case-sensitive; rename nodes in the editor (it updates references) rather than by hand. |
| LLM node before Limit/Filter | Large bill, slow runs | Filter and limit first; send only what the model needs. |
| `localhost` from inside Docker | n8n cannot reach the FastAPI server | Inside the container, `localhost` is the container. Use `host.docker.internal` (add `--add-host=host.docker.internal:host-gateway` on Linux). |
| Webhook without signature check | Anyone can trigger the workflow | HMAC with a shared secret; `compare_digest`; reject with 401. |
| No de-duplication | Customers get two emails after a retry | Store event ids; return 200 for duplicates. |
| No timeout on HTTP calls | Script hangs forever | `httpx.get(url, timeout=10)`; enable "Retry on fail" in n8n. |
| Relying on `schedule` for a daily job on a laptop | Job silently stops when the laptop sleeps or the script ends | cron / Task Scheduler / cloud scheduler / n8n Schedule Trigger on a server. |
| Running computer use on their own computer | Risk of real clicks, purchases, deletions | Only in a sandbox VM/container with no personal accounts; step limits; human watching. |
| Brittle Playwright selectors (`div:nth-child(3)`) | Script breaks after a small site change | Prefer `get_by_role`, `get_by_label`, `get_by_text`. |

## 4. Questions to check understanding (with answers)

1. **What makes a workflow different from an agent?** In a workflow the designer fixed the steps in advance; in an agent the LLM chooses the next step at run time.
2. **Is "classify with an LLM, then route with an IF node" an agent?** No — the LLM does one step; the path is fixed. It's a workflow with an AI step.
3. **What is an n8n item, and why does it matter?** One record of data; most nodes run once per item, so 50 items means 50 LLM calls unless you limit them.
4. **Where are credentials stored and what does the workflow file contain?** Encrypted in n8n's credential store; the file only references them by id and name.
5. **What are output 0 and output 1 of an IF node?** True and false branches.
6. **Why must a webhook receiver be idempotent?** Senders retry on slow or failed responses, so the same event can arrive more than once.
7. **Why reply fast and do the work in the background?** Slow replies cause sender timeouts and retries (duplicates); background tasks keep the reply quick.
8. **What is exponential backoff?** Waiting longer after each failure (1s, 2s, 4s…) before retrying.
9. **Playwright script or browser agent for a stable, daily price check?** Playwright — deterministic, fast, cheap. Agent only if the pages change often or the task varies.
10. **Name three safety rules for computer-use agents.** Sandbox VM/container; no personal accounts or secrets inside; step limits and human confirmation for irreversible actions (also: treat screen text as untrusted).

## 5. Adapting the session

**Faster groups**
- Get a real LLM credential into n8n and run workflow 01 end to end with `send_test_webhook.py` pointed at the n8n Test URL.
- Rebuild workflow 01's LLM step with n8n's built-in AI nodes and compare.
- Exercises 6 (Switch node) and 12 (design review) in class; discuss replay attacks (exercise 4).
- Install Playwright and run `code/playwright_basics.py`; then try `browser_use_agent.py` in a separate environment with a key.

**Slower groups**
- Skip the JSON internals (notebook 03 steps 4–6); stay on the canvas or the workflow diagrams.
- Do the webhook rules as a role-play: one student is the sender, one the receiver holding the "secret word".
- Show computer use only through the simulated loop in notebook 04; skip the cost table.
- Focus on exercises 1–3 and 9 (ROI), which need no code.

## Before the session checklist

- [ ] `python 11-ai-automation/build.py` ran; `python 11-ai-automation/code/validate_workflows.py` shows three OK lines.
- [ ] (Optional) n8n running in Docker at `http://localhost:5678`; workflow 01 imported.
- [ ] (Optional) `uvicorn webhook_receiver:app --port 8000` starts in `11-ai-automation/code/`.
- [ ] Excel ROI file opens and formulas calculate (enable editing if Excel opens it in Protected View).
