import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook

sys.path.insert(0, str(HERE))
from notebook_sources import NOTEBOOKS  # noqa: E402

IMG = HERE / "images"
MOD = "14-deployment-and-llmops"

# ---------------------------------------------------------------------------
# 1. Diagrams (Mermaid -> PNG). The .mmd source is saved next to each PNG.
# ---------------------------------------------------------------------------
DIAGRAMS = {
    "big_picture": """
flowchart LR
    U[User] --> UI[Web UI<br/>Streamlit / Gradio]
    UI -->|HTTP JSON| API[FastAPI service]
    subgraph Docker container
    API --> G[Guardrails]
    G --> L[LLM client]
    end
    L --> P[Hosted LLM API]
    L --> V[vLLM server<br/>open model on GPU]
    API -.traces, cost.-> LF[Langfuse]
    API -.metrics.-> M[Dashboard + alerts]
    GH[GitHub Actions CI/CD] -.builds and ships.-> API
""",
    "http_flow": """
flowchart LR
    C[Client<br/>browser, app, curl] -->|POST /chat<br/>JSON body| S[uvicorn server]
    S --> F[FastAPI routing]
    F --> V{pydantic<br/>validation}
    V -->|bad shape| E[422 error]
    V -->|ok| R[route function]
    R -->|raise HTTPException| E2[400 / 401 error]
    R -->|return dict| J[200 + JSON response]
    J --> C
    E --> C
    E2 --> C
""",
    "docker_flow": """
flowchart LR
    D[Dockerfile<br/>the recipe] -->|docker build| I[Image<br/>frozen package]
    I -->|docker run| C1[Container 1]
    I -->|docker run| C2[Container 2]
    I -->|docker push| R[(Registry<br/>Docker Hub / ghcr.io)]
    R -->|docker pull| S[Server]
    S -->|docker run| C3[Container on server]
    E[.env secrets] -.passed at run time.-> C1
""",
    "trace_tree": """
flowchart TD
    T[TRACE: answer-question<br/>user u42, 1.9 s, $0.0011]
    T --> S1[SPAN guardrails<br/>5 ms]
    T --> S2[RETRIEVER search docs<br/>120 ms, 4 chunks]
    T --> S3[GENERATION llm-call<br/>1.7 s, 410 in / 95 out tokens]
    T --> S4[SPAN output check<br/>3 ms]
    T --> SC[SCORE user_feedback = 1]
""",
    "guardrails_pipeline": """
flowchart LR
    IN[User input] --> V[Validate<br/>length, type]
    V --> INJ[Injection<br/>heuristics]
    INJ --> PII[Redact PII]
    PII --> LLM[LLM]
    LLM --> SCH[Schema check<br/>pydantic]
    SCH --> OUT2[Redact output]
    OUT2 --> OUT[Reply]
    V -.reject.-> B[400 + log]
    INJ -.block.-> B
    SCH -.retry or fallback.-> LLM
""",
    "cicd_pipeline": """
flowchart LR
    DEV[Developer pushes<br/>or opens PR] --> CO[Checkout code]
    CO --> LINT[Lint<br/>ruff]
    LINT --> TEST[Unit tests<br/>pytest]
    TEST --> EV[Small eval set]
    EV -->|main branch only| BUILD[docker build]
    BUILD --> PUSH[Push image<br/>to registry]
    PUSH --> DEP[Deploy]
    TEST -.fail.-> STOP[Block merge]
    EV -.score too low.-> STOP
""",
}


def build_diagrams():
    for name, src in DIAGRAMS.items():
        mermaid(src, IMG / f"{name}.png")


# ---------------------------------------------------------------------------
# 2. Matplotlib figures
# ---------------------------------------------------------------------------
def build_figures():
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # (a) static vs continuous batching
    rng = np.random.default_rng(7)
    lengths = list(rng.integers(5, 60, size=12))
    slots = 4

    def static(lengths):
        tl, t = [], 0
        for b in range(0, len(lengths), slots):
            batch = lengths[b:b + slots]
            for j, L in enumerate(batch):
                tl.append((j, t, L, b + j))
            t += max(batch)
        return tl, t

    def continuous(lengths):
        free = [0] * slots
        tl = []
        for rid, L in enumerate(lengths):
            j = int(np.argmin(free))
            tl.append((j, free[j], L, rid))
            free[j] += L
        return tl, max(free)

    s_tl, s_T = static(lengths)
    c_tl, c_T = continuous(lengths)
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.4), sharey=True)
    cmap = plt.get_cmap("tab20")
    for ax, (tl, T, title) in zip(axes, [(s_tl, s_T, "Static batching"), (c_tl, c_T, "Continuous batching")]):
        ax.add_patch(plt.Rectangle((0, -0.5), T, slots, color="#e5e7eb"))
        for slot, start, L, rid in tl:
            ax.barh(slot, L, left=start, color=cmap(rid % 20), edgecolor="white")
        used = sum(lengths) / (T * slots)
        ax.set_title(f"{title}: {T} steps, {used:.0%} of slot time busy")
        ax.set_xlabel("token steps (grey = idle GPU slot)")
        ax.set_xlim(0, max(s_T, c_T))
    axes[0].set_ylabel("GPU slot")
    axes[0].set_yticks(range(slots))
    fig.tight_layout()
    fig.savefig(IMG / "continuous_batching.png", dpi=120)
    plt.close(fig)

    # (b) monitoring dashboard: reuse the script in code/monitoring
    sys.path.insert(0, str(HERE / "code" / "monitoring"))
    import metrics_dashboard
    metrics_dashboard.draw(metrics_dashboard.simulate(), IMG / "monitoring_dashboard.png")


# ---------------------------------------------------------------------------
# 3. Notebooks
# ---------------------------------------------------------------------------
def build_notebooks():
    for name, cells in NOTEBOOKS.items():
        notebook(cells, HERE / "notebooks" / name)


# ---------------------------------------------------------------------------
# 4. Slides
# ---------------------------------------------------------------------------
def build_slides():
    I = lambda n: str(IMG / f"{n}.png")  # noqa: E731
    deck = {
        "title": "Module 14 - Deployment and LLMOps",
        "subtitle": "From notebook to a safe, observable product",
        "slides": [
            {"title": "Why this module matters",
             "bullets": ["A notebook is your kitchen; deployment is opening a restaurant",
                         "Other people and programs must use your AI reliably",
                         "LLMOps = deploy, trace, monitor, evaluate, protect, ship",
                         "Extra LLM worries: free-text answers, per-token cost, users who try tricks"],
             "notes": "Open with the restaurant analogy. In a notebook you can taste as you go and nobody waits. Once real users arrive you need a menu, the same kitchen in every branch, someone watching order times, a doorman, and a locked safe. Each of those maps to one section of today's session: API, Docker, monitoring, guardrails and secrets."},
            {"title": "The system we build today", "image": I("big_picture"),
             "bullets": ["UI talks only to our API", "API runs guardrails, calls a model, records traces",
                         "Docker wraps the API", "CI/CD builds and ships it"],
             "notes": "Walk the diagram left to right. Point out that the web page never holds an API key: everything sensitive lives in the FastAPI service. The dotted lines are observability: traces and metrics flow out to Langfuse and a dashboard. Students will build or read every box today."},
            {"title": "APIs and HTTP in one slide", "image": I("http_flow"),
             "bullets": ["Request = method + path + headers + body", "GET reads, POST sends data",
                         "Status: 2xx ok, 4xx caller's mistake, 5xx our mistake",
                         "JSON looks like a Python dict"],
             "notes": "An API is a menu: you cannot walk into the kitchen, but you can order from a fixed list. Teach the status code memory trick: 2xx here you go, 4xx you made a mistake, 5xx we made a mistake. Ask students what 404 and 422 mean before revealing."},
            {"title": "FastAPI: the smallest app",
             "bullets": ["FastAPI = web framework; uvicorn = the server", "@app.get is a decorator that registers a route",
                         "Return a dict -> JSON", "Free interactive docs at /docs"],
             "code": 'from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/health")\ndef health():\n    return {"status": "ok"}\n\n# terminal:\n# uvicorn main:app --reload',
             "notes": "Live-code this in the notebook. Emphasise that FastAPI itself does not listen on the network: uvicorn does. Then show /docs in a browser if you can run locally; the Try it out button impresses every group."},
            {"title": "pydantic: validation for free",
             "bullets": ["A model class = a form with labelled boxes", "Wrong type or out of range -> 422 before your code runs",
                         "response_model checks and documents output", "HTTPException for 'right shape, still not ok'"],
             "code": "class ChatRequest(BaseModel):\n    message: str\n    max_tokens: int = Field(256, ge=1, le=1024)\n\n@app.post('/chat')\ndef chat(req: ChatRequest):\n    if not req.message.strip():\n        raise HTTPException(400, 'empty input')\n    ...",
             "notes": "Run notebook 01 step 5: three bad requests, three precise 422 messages. Stress that validation is the first and cheapest guardrail. ge means greater or equal, le means less or equal."},
            {"title": "Async: the waiter analogy",
             "bullets": ["Blocking waiter stands at the kitchen door", "Async waiter serves other tables meanwhile",
                         "LLM calls are mostly waiting -> async helps", "Never call time.sleep or blocking libs inside async def",
                         "  blocking library? use plain def"],
             "notes": "Show the measurement from notebook 01 step 8: async-good about 0.5 s, async-bad about 2.5 s, sync-def about 0.5 s. Let students predict first. This is the single most common performance bug in FastAPI LLM services."},
            {"title": "Testing with TestClient",
             "bullets": ["Calls the app in-process: no server, no network", "Tests are functions starting with test_ using assert",
                         "pytest runs them; CI runs pytest on every push", "Use the offline model so tests are free and repeatable"],
             "code": "client = TestClient(app)\n\ndef test_chat_rejects_empty():\n    r = client.post('/chat', json={'message': ' '})\n    assert r.status_code == 400",
             "notes": "Open code/tests/test_main.py and run python -m pytest -q from the code folder. Seven tests pass in under a second. Explain why tests force the offline model: no cost and the same answer every time."},
            {"title": "Docker: the kitchen in a box", "image": I("docker_flow"),
             "bullets": ["Dockerfile = recipe", "Image = sealed cake mix", "Container = a cake baked from it",
                         "Registry = supermarket shelf"],
             "notes": "Shipping-container analogy first, then the four words. A container is not a virtual machine: it shares the host kernel, so it starts in about a second. Secrets are passed at run time with --env-file, shown by the dotted line."},
            {"title": "Reading our Dockerfile",
             "bullets": ["Rarely-changing steps first, code last (layer cache)", "--host 0.0.0.0 so the outside can connect",
                         "Non-root user, health check", ".dockerignore keeps .env out"],
             "code": "FROM python:3.13-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY app/ ./app/\nUSER appuser\nCMD [\"uvicorn\", \"app.main:app\",\n     \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]",
             "notes": "Notebook 02 simulates the cache: good order rebuilds in 2 seconds after a code edit, bad order reinstalls everything. Then show docker build, docker run -p 8000:8000 --env-file .env, docker ps, docker logs. Port mapping reads HOST:CONTAINER."},
            {"title": "Docker Compose and quick UIs",
             "bullets": ["Compose: several containers, one command", "Service names are hostnames: http://api:8000",
                         "Streamlit: script that re-runs on every click", "Gradio: function -> page, used by HF Spaces",
                         "UIs call the API; they never hold keys"],
             "notes": "Show code/docker-compose.yml and the two UI files. Streamlit keeps memory in st.session_state because the whole script re-runs. Gradio's ChatInterface needs one function. Warn about share=True links spending your API credit."},
            {"title": "vLLM: serving open models fast", "image": I("continuous_batching"),
             "bullets": ["Inference server for open-weight models on GPUs", "Continuous batching: refill slots every token step",
                         "PagedAttention: KV cache in small blocks on demand", "OpenAI-compatible API: change only base_url"],
             "notes": "Lift analogy for static batching: nobody gets in until everyone inside has reached their floor. Continuous batching lets people in at every floor. PagedAttention is like not reserving a 12-seat table for every booking. vLLM needs an NVIDIA GPU, so we show code only and simulate in notebook 02."},
            {"title": "Observability: traces and spans", "image": I("trace_tree"),
             "bullets": ["Monitoring: is something wrong?", "Observability: why?",
                         "Trace = one request; span = one step; generation = LLM call with tokens and cost",
                         "Langfuse: open source, cloud or self-hosted"],
             "notes": "Dashboard light versus mechanic's log. Show the home-made tracer in notebook 03 so students see a trace is just nested timed records. Then show code/observability/langfuse_tracing.py and explain the three environment variables and the cloud versus self-host table."},
            {"title": "Monitoring: four numbers", "image": I("monitoring_dashboard"),
             "bullets": ["Latency p50 / p95 (not the average)", "Error rate by cause (4xx, 429, 5xx)",
                         "Token cost per request, feature, day", "Drift: inputs or outputs changing"],
             "notes": "Ask students to find the outage and the drift in this simulated week before you point them out. Day 5 has an error spike and slow p95; day 6 prompt length jumps because users paste long documents, and cost rises with it. Introduce SLO and alert thresholds."},
            {"title": "Guardrails: doorman and head chef", "image": I("guardrails_pipeline"),
             "bullets": ["Validate input", "Prompt-injection heuristics", "Redact PII with regex",
                         "Validate output with pydantic; retry or fall back", "Defence in depth: no single layer is enough"],
             "notes": "Run notebook 04: regex finds emails and phones but misses names and addresses; the injection heuristic misses rephrased attacks. Measure precision and recall so students learn never to trust an unmeasured guardrail."},
            {"title": "CI/CD with GitHub Actions", "image": I("cicd_pipeline"),
             "bullets": ["CI: every push is linted and tested", "CD: passing main builds and ships the image",
                         "Workflow YAML lives in .github/workflows/", "Add a small, cheap eval step for LLM quality"],
             "notes": "Open code/ci/github-actions-ci.yml and read the two jobs. Point out needs: test, which makes the docker job wait for tests, and that secrets come from repository settings, used as secrets.NAME, never written in the file."},
            {"title": "Secrets management",
             "bullets": ["Never in code, git, notebooks or Docker images", "Local: .env + python-dotenv; commit .env.example only",
                         "CI: GitHub Actions secrets; prod: a secret manager", "Least privilege, spend limits, separate dev/prod keys",
                         "Leaked? Revoke first, then rotate, then clean up"],
             "notes": "Bots scan public GitHub for keys within minutes. Deleting the commit is not enough because history keeps it. Show the tiny secret scanner in notebook 04 step 11."},
            {"title": "Common mistakes",
             "bullets": ["Blocking call inside async def", "Forgetting --host 0.0.0.0 in Docker",
                         "COPY . . before pip install", "Key in the Dockerfile or the front-end",
                         "Watching the average latency only", "Trusting model JSON without validation"],
             "notes": "Go through each mistake and ask the group how to fix it. Fixes: plain def or an async client; add the host flag; copy requirements first; env-file and keep keys in the API; use p95; validate with pydantic and retry."},
            {"title": "Recap and exercise",
             "bullets": ["FastAPI + pydantic = typed, validated, documented API", "Docker = same app everywhere",
                         "Langfuse + dashboards = see what happens and what it costs", "Guardrails + CI + secrets = safe to ship",
                         "Exercise: add a /summarize endpoint with tests, guardrails and metrics"],
             "notes": "Recap one line per section. Then set exercises 1 to 6 from exercises.md for practice, with 7 to 12 as stretch or homework. The deployment checklist workbook is the take-home reference."},
        ],
    }
    slides(deck, HERE / "slides" / f"{MOD}.pptx")


# ---------------------------------------------------------------------------
# 5. Excel: deployment checklist + monitoring metrics
# ---------------------------------------------------------------------------
def build_excel():
    checklist = [["Area", "Check", "Why it matters", "How to verify", "Done? (Y/N)"]]
    items = [
        ("API", "GET /health endpoint returns 200 quickly", "Load balancers and Docker use it to restart broken instances", "curl http://host/health"),
        ("API", "Request and response pydantic models on every route", "Bad input rejected with 422 before your code runs", "Look at /docs; send a wrong type"),
        ("API", "Clear 4xx/5xx errors, no raw stack traces to users", "Users get a useful message; internals stay private", "Send empty input; expect 400 with detail"),
        ("API", "Timeout on every model call", "A hung provider must not hang your whole service", "Search code for timeout="),
        ("API", "Retries with backoff for 429 and 5xx (max 2-3)", "Providers have short hiccups and rate limits", "Unit test with a fake failing client"),
        ("API", "Rate limit per user or API key", "Stops one user (or bot) burning your budget", "Fire 100 quick requests; expect 429"),
        ("Container", "Small base image (e.g. python:3.13-slim)", "Faster pulls, fewer vulnerabilities", "docker images (check size)"),
        ("Container", "Pinned requirements.txt, copied before code", "Reproducible builds and fast layer caching", "Edit main.py, rebuild: pip step is CACHED"),
        ("Container", "Runs as non-root user", "Limits damage if the app is compromised", "docker exec <id> whoami"),
        ("Container", ".dockerignore excludes .env, .git, data", "No secrets or junk inside the image", "docker run --rm img ls -a"),
        ("Container", "HEALTHCHECK defined", "Orchestrator knows when to restart", "docker ps shows (healthy)"),
        ("UI", "No API keys in the front-end", "Anything in the browser can be read by users", "Search UI code for key names"),
        ("UI", "Front-end calls the API, not the model provider", "Guardrails, logging and secrets stay in one place", "Read UI code"),
        ("Observability", "Every request traced (spans for retrieval, model, tools)", "You can explain any bad answer later", "Open a trace in Langfuse"),
        ("Observability", "Token usage and cost recorded per request", "Find what is expensive before the bill does", "Cost dashboard per feature/day"),
        ("Observability", "User feedback (thumbs up/down) stored as scores", "Real-world quality signal", "Score visible on traces"),
        ("Observability", "Logs contain no secrets and redacted PII", "Logs are widely readable and kept long", "grep logs for @ and key prefixes"),
        ("Monitoring", "Dashboard: p50/p95 latency, error rate, cost/day, drift signal", "See problems at a glance", "Open the dashboard"),
        ("Monitoring", "Alerts with thresholds and owners", "Someone is told when things break", "Trigger a test alert"),
        ("Monitoring", "Weekly re-run of a fixed eval set", "Catches quality drift and silent model changes", "Eval score history chart"),
        ("Guardrails", "Input length and type limits", "Cost control and attack surface", "Send 10,000-char input"),
        ("Guardrails", "PII redaction before logging and before third-party models", "Privacy law and user trust", "Send an email address; check trace"),
        ("Guardrails", "Prompt-injection checks + least-privilege tools", "Stop instruction hijacking from doing damage", "Run an injection test set"),
        ("Guardrails", "Model output validated against a schema", "Downstream code never receives broken data", "Feed malformed JSON in a test"),
        ("CI/CD", "Lint + unit tests on every pull request", "Bugs caught before merge", "PR shows green checks"),
        ("CI/CD", "Small, cheap eval in CI with a pass threshold", "Prompt changes cannot silently reduce quality", "Lower a prompt's quality; CI fails"),
        ("CI/CD", "Image built and pushed only from main after tests pass", "Only tested code is shipped", "Workflow uses needs: test"),
        ("CI/CD", "Rollback plan (previous image tag kept)", "Fast recovery from a bad release", "Deploy previous tag in staging"),
        ("Secrets", "No secrets in git, notebooks, images or front-end", "Leaked keys are abused within minutes", "Secret scanner in CI (e.g. gitleaks)"),
        ("Secrets", ".env.example committed with placeholders only", "Teammates know which variables exist", "Open .env.example"),
        ("Secrets", "Secret manager / platform secrets in production", "Encrypted storage, rotation, audit log", "Check deployment config"),
        ("Secrets", "Separate dev and prod keys with spend limits", "A dev mistake cannot drain prod budget", "Provider console"),
        ("Secrets", "Written 'key leaked' procedure: revoke, rotate, review", "Minutes matter in an incident", "Read the runbook"),
    ]
    for a, c, w, h in items:
        checklist.append([a, c, w, h, ""])

    metrics = [["Metric", "Plain-English definition", "How to compute", "Starting threshold (tune for your app)", "If it fires, check..."]]
    metrics += [
        ["Request rate", "How many requests per minute/hour", "count(requests) per time bucket", "Alert on sudden drop of >50% vs same hour last week", "Is the app reachable? DNS, deploy, front-end errors"],
        ["Latency p50", "Typical request time (median)", "50th percentile of request durations", "Depends on the model; track the trend", "Model choice, prompt size, network"],
        ["Latency p95", "What the slowest 5% of users feel", "95th percentile of request durations", "e.g. > 3 s for 10 minutes (an example SLO)", "Provider status, long prompts, retries, cold starts"],
        ["Time to first token (TTFT)", "How fast the first word appears when streaming", "time from request to first streamed token", "e.g. > 1.5 s", "Queueing, prompt length, provider load"],
        ["Error rate", "Share of requests that failed", "failed / total, split by 4xx, 429, 5xx, timeout", "e.g. > 5% for 5 minutes", "Provider outage, bad deploy, expired key"],
        ["429 rate", "How often the provider says 'too many requests'", "count(status==429) / total", "> 1%", "Rate limits, need for backoff, quota increase"],
        ["Guardrail block rate", "Share of inputs blocked by guardrails", "blocked / total", "Sudden change of 2x in either direction", "Attack wave, or a too-strict new rule"],
        ["Tokens per request", "Average input and output tokens", "mean(input_tokens), mean(output_tokens)", "+25% vs baseline", "Prompt template change, users pasting documents, RAG returning too much"],
        ["Cost per day", "Money spent on model calls", "sum(in_tokens*in_price + out_tokens*out_price)", "Above daily budget", "Expensive feature, loops, abuse, wrong model"],
        ["Cost per user / feature", "Who or what is expensive", "group cost by user_id / feature", "Top user > 10x median", "Abuse, missing rate limit, bad agent loop"],
        ["Input drift (PSI)", "Are inputs changing vs the baseline period?", "Population Stability Index on prompt length/topic/language", "< 0.1 stable, 0.1-0.25 watch, > 0.25 act", "New user group, product change, new language"],
        ["Refusal rate", "Share of answers where the model declines", "count(answers matching refusal patterns) / total", "Sudden change of 2x", "Provider model update, system prompt change"],
        ["Eval score", "Quality on a fixed test set", "mean score of weekly eval run (LLM-as-judge or rules)", "Drop of > 5 points vs last release", "Prompt/model change, retrieval index stale"],
        ["User feedback", "Thumbs up share", "up / (up + down)", "Drop of > 10 points week over week", "Read the down-voted traces"],
        ["Schema failure rate", "Model output that failed validation", "failed validations / structured calls", "> 2%", "Prompt format drift, model change, need for retries"],
    ]
    workbook({"Deployment checklist": checklist, "Monitoring metrics": metrics},
             HERE / "excel" / "deployment-checklist.xlsx",
             col_widths={"Deployment checklist": [14, 50, 45, 38, 12],
                         "Monitoring metrics": [24, 38, 42, 38, 45]})


if __name__ == "__main__":
    build_diagrams()
    build_figures()
    build_notebooks()
    build_slides()
    build_excel()
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / f"{MOD}-handout.pdf",
                      title="Module 14 - Deployment and LLMOps")
    print("built", MOD)
