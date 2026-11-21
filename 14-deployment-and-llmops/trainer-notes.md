# Module 14 — Trainer notes

## 1. What students should be able to do after the session

- Explain what an API, an endpoint and a status code are, and build and test a FastAPI route with a pydantic request model.
- Explain the difference between blocking and async code, and spot a blocking call inside `async def`.
- Read a Dockerfile line by line and explain image vs container vs registry, port mapping and layer caching.
- Say when to use Streamlit vs Gradio, and why the UI should call the API instead of the model.
- Explain continuous batching and PagedAttention in one sentence each.
- Name the four core monitoring numbers (p95 latency, error rate, cost, drift) and read a dashboard.
- List the guardrail layers and say what regex PII redaction and injection heuristics miss.
- Describe a CI/CD pipeline and the rules for handling secrets, including what to do when a key leaks.

## Before you teach

- Read `concepts.md` fully and run all four notebooks once (each takes under a minute).
- On your own laptop: run the API (`uvicorn app.main:app --reload` in `code/`), open `/docs`, run `python -m pytest -q`, and if possible `docker build` + `docker run` and `docker compose up`. **The build machine for this course had no Docker engine, so do this dry run yourself** — fix anything before class.
- Optional: create a free Langfuse Cloud project and put the three keys in `code/.env` so you can show a real trace. Never show your keys on the projector.
- Open the slides (`slides/14-deployment-and-llmops.pptx`); speaker notes are written to be read aloud.

## 2. Teaching sequence (2-hour session)

| Time | Segment | What you do | Materials |
|---|---|---|---|
| 0:00–0:08 | Hook | Restaurant analogy: kitchen (notebook) vs restaurant (deployment). Show the big-picture diagram. | Slides 1–2 |
| 0:08–0:20 | HTTP and APIs | Request/response parts, status code trick, quick quiz (exercise 1 aloud). | Slide 3 |
| 0:20–0:45 | FastAPI live | Notebook 01 steps 1–7 and 11: routes, params, pydantic, 422s, HTTPException, tests. Then show `/docs` in a browser. | Notebook 01, slides 4–5, 7 |
| 0:45–0:55 | Async | Ask students to predict timings, then run notebook 01 step 8. Waiter analogy. | Slide 6 |
| 0:55–1:05 | Break / catch-up | Students finish notebook 01 steps they missed. | — |
| 1:05–1:25 | Docker + UIs | Diagram, then read the Dockerfile; run the cache simulation (notebook 02 steps 1–3); show compose file and the two UI files; demo `docker compose up` if you have Docker. | Slides 8–10, notebook 02, `code/` |
| 1:25–1:35 | vLLM | Lift analogy, batching chart (notebook 02 steps 7–9). Stress: GPU needed, code only. | Slide 11 |
| 1:35–1:50 | Observability + monitoring | Home-made tracer, then the dashboard: students find the outage and drift. Show the Langfuse code (and a real trace if set up). | Slides 12–13, notebook 03 |
| 1:50–2:00 | Guardrails, CI, secrets, wrap-up | Notebook 04 steps 3–6 (regex and the precision/recall surprise), CI yaml tour, the "key leaked" rule. Set exercises. | Slides 14–18, notebook 04 |

For a **1-hour** version: hook (5), HTTP + FastAPI (20), Docker (12), monitoring dashboard (10), guardrails + secrets (10), wrap-up (3). Assign notebooks 02–04 as homework.

## 3. Common student mistakes and how to fix them

| Mistake | What they see | Fix |
|---|---|---|
| Running `uvicorn main:app` from the wrong folder | `Error loading ASGI app. Could not import module "main"` | `cd` into the folder that contains the module; for our layout run `uvicorn app.main:app` from `code/`. |
| Forgetting `-p` or `--host 0.0.0.0` with Docker | Container runs but browser says "connection refused" | Run with `-p 8000:8000` and make sure the CMD has `--host 0.0.0.0`. |
| `time.sleep()` or `requests.get()` inside `async def` | Server becomes slow under load; one request blocks the rest | Use plain `def` for blocking code, or an async library (`httpx.AsyncClient`, `asyncio.sleep`). Show notebook 01 step 8. |
| Sending form data or a Python string instead of JSON | 422 with "Input should be a valid dictionary" | Use `json={...}` in httpx/TestClient (not `data=`), and set `Content-Type: application/json` in other tools. |
| Reading 422 as "server broken" | Panic, random code changes | Read `detail[0]["loc"]` and `msg` — it says exactly which field is wrong. |
| Putting the API key in the Dockerfile, notebook or Streamlit file | Key leaks into git or the image | Environment variables, `.env` + `.dockerignore`/`.gitignore`, `--env-file`. If it leaked: revoke first. |
| `COPY . .` before `pip install` | Every rebuild takes minutes | Copy `requirements.txt` first, install, then copy code (notebook 02 step 2–3). |
| Judging speed by the average latency | "Average is 1 s, all fine" while users complain | Show p50 vs p95 vs p99 (notebook 03 step 5, exercise 9). |
| Trusting regex guardrails as complete | "We redact PII, we're compliant" | Run notebook 04 step 4: names and addresses slip through. Regex is one layer only. |
| Forgetting that Streamlit re-runs the script | Chat history disappears after each message | Store state in `st.session_state`. |
| Expecting the CI workflow to run from `code/ci/` | Nothing happens on GitHub | Workflows must be in `.github/workflows/` at the repository root. |

## 4. Questions to check understanding (with answers)

1. **What is the difference between a 400 and a 422 in our app?** — 422 is raised automatically by FastAPI when the body doesn't match the pydantic model (wrong type, missing field, out of range). 400 is raised by our own code when the shape is right but the content is unacceptable (empty message, injection).
2. **Why do we copy `requirements.txt` before the code in the Dockerfile?** — Docker caches layers; if requirements are unchanged, the slow install layer is reused and only the cheap code layer rebuilds.
3. **Image vs container?** — An image is a frozen package (the recipe's result); a container is a running copy of it. One image can run many containers.
4. **Why should the Streamlit UI call our API instead of calling the model provider directly?** — Keys stay on the server, guardrails/logging/metrics live in one place, and the UI can be swapped freely.
5. **In one sentence, what does continuous batching do?** — After every generation step it removes finished requests from the GPU batch and adds waiting ones immediately, so slots never sit idle waiting for the longest request.
6. **What is a span?** — One timed step inside a trace, e.g. "retrieve documents, 120 ms, 4 chunks". A generation is a span for an LLM call with tokens and cost.
7. **p50 is 0.8 s and p95 is 6 s. What does that mean?** — Half of requests finish within 0.8 s, but 1 in 20 takes 6 s or more — a real problem for regular users.
8. **Give two drift signals you can compute cheaply.** — Average prompt length; share of each language/topic; refusal rate; average answer length; weekly eval score; PSI on any of those.
9. **Why is the injection heuristic not enough on its own?** — Attackers rephrase; it also produces false alarms. Combine with least-privilege tools, separating instructions from data, output checks, classifiers and human approval.
10. **A teammate committed a key to GitHub and deleted the commit. Are we safe?** — No. The key is in history and may already be scraped. Revoke it in the provider console immediately, issue a new one, then clean history and add secret scanning.

## 5. Adapting for faster or slower groups

**Slower groups**
- Spend most of the time on FastAPI and Docker concepts; treat vLLM and Langfuse as "know the words" topics with the analogies only.
- Do notebook 01 together cell by cell; give notebook 04 steps 1–3 and 9 only.
- Use exercises 1, 2, 3, 9 in class; 4 and 5 as homework with pairs.

**Faster groups**
- Have them run the real API, UIs and `docker compose up` on their laptops during the session.
- Set exercises 10–12 (retries, rate limiter, eval gate) and ask them to wire `ex12_eval_gate.py` into a real GitHub repo's Actions.
- Stretch: deploy the container to a free/cheap host (e.g. a Hugging Face Space with the Gradio UI, or a cloud container service), add Langfuse Cloud tracing, and present the trace and dashboard to the class.
- Discussion: when is self-hosting with vLLM worth it versus a hosted API? (data rules, volume, latency, team skills, GPU cost).
