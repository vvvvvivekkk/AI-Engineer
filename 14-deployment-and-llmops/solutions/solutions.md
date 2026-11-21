# Module 14 — Solutions

Runnable solution scripts in this folder: `ex05_summarize.py`, `ex06_pii.py`, `ex10_retry.py`, `ex11_rate_limit.py`, `ex12_eval_gate.py`. Each one runs on its own from this folder (`python ex10_retry.py`) and needs no API key.

---

## 1. Name that status code

| Situation | Code | Whose fault |
|---|---|---|
| a) `message` field missing | **422** Unprocessable Entity (pydantic validation) | client |
| b) message empty | **400** Bad Request (our `HTTPException`) | client |
| c) no API key header | **401** Unauthorized (use 403 Forbidden when the key is valid but not allowed) | client |
| d) `/chta` typo | **404** Not Found | client |
| e) provider timed out | **502** Bad Gateway or **504** Gateway Timeout (an upstream service failed) | server side (ours or the provider's) |
| f) over your rate limit | **429** Too Many Requests, ideally with a `Retry-After` header | client |

Memory trick: 4xx = "you made a mistake", 5xx = "we made a mistake".

## 2. A token-counting route

```python
@app.get("/tokens")
def tokens(text: str):                       # required query parameter
    return {"text_length": len(text), "approx_tokens": max(1, len(text) // 4)}

def test_tokens_ok():
    r = client.get("/tokens", params={"text": "hello world!"})
    assert r.json() == {"text_length": 12, "approx_tokens": 3}

def test_tokens_missing():
    assert client.get("/tokens").status_code == 422   # required parameter missing -> validation error
```

## 3. Docker vocabulary and commands

a) *Dockerfile*: a recipe listing the steps to set up the app. *Image*: the sealed box produced by following the recipe — the app plus everything it needs, frozen. *Container*: one running copy made from that box; you can run many at once. *Registry*: an online shelf where images are stored and downloaded from (Docker Hub, ghcr.io).

b) `docker run --rm -p 9000:8000 --env-file .env llm-chat-api` — ports read `HOST:CONTAINER`, so laptop 9000 → container 8000.

c) Inside a container `127.0.0.1` means "this container only", so connections arriving from your laptop through the port mapping would be refused. `0.0.0.0` means "listen on every network interface", which lets the mapped traffic in.

## 4. Fix the broken Dockerfile

Problems:
1. `python:latest` — not pinned; a future Python release can break your build. Use `python:3.13-slim` (pinned and small).
2. `COPY . .` before installing — every code edit invalidates the cache and reinstalls packages; it also copies `.env`, `.git` and data unless `.dockerignore` exists.
3. `ENV ANTHROPIC_API_KEY=...` — a secret baked into the image forever; anyone who pulls it can read it with `docker history` or `docker inspect`. Pass it at run time.
4. `pip install fastapi uvicorn anthropic` — unpinned versions; use a pinned `requirements.txt`.
5. No `--host 0.0.0.0` — the app is unreachable from outside the container.
6. Runs as root, no `WORKDIR`, no health check.

```dockerfile
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Plus a `.dockerignore` containing `.env`, `.git/`, `__pycache__/`, and run with `docker run --env-file .env ...`.

## 5. A `/summarize` endpoint

See `ex05_summarize.py`. Key points:
- `Field(..., min_length=20, max_length=20_000)` gives the 422 for short text with no extra code.
- The same guardrail order as `/chat`: injection check → PII redaction → model → metrics.
- `max_tokens=req.max_words * 2` caps cost: English averages a bit more than one token per word, so twice the word limit is a safe ceiling.
- Three tests: happy path (200), too short (422), injection (400).

## 6. More PII patterns

See `ex06_pii.py`.

```python
"PAN": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
"AADHAAR": re.compile(r"\b\d{4}[ -]\d{4}[ -]\d{4}\b"),
```

Ordering: patterns run one after another on the text that earlier patterns already changed. If PHONE ran before AADHAAR, the phone pattern (10 digits with optional spaces) would grab the first ten digits of `1234 5678 9012` and leave `[PHONE]12` — a half-redacted number. Run the most specific, longest patterns first: CARD (13–16 digits), then AADHAAR (12), then PHONE (10).

False positives found: `Train 1234 5678 9012 ...` (any 4-4-4 code) and `Product code HELLO2024X` (any 5-letters-4-digits-1-letter code). Real systems reduce these with **checksums** (Aadhaar numbers have a check digit; cards use the Luhn check) and context words ("PAN", "Aadhaar") — or ML-based detectors such as Presidio.

## 7. Make the alert less noisy

a) Requiring ≥ 50 requests in a single hour removes **every** alert — including the real outage, because the outage happened between 4 a.m. and 10 a.m. when traffic was only 17–51 requests per hour. Too strict: you would miss a real incident.

b)
```python
h = df.set_index("time").resample("h").agg(requests=("error", "size"), errors=("error", "sum"))
w = h.rolling(3).sum()                       # last 3 hours, added up
w["rate"] = w.errors / w.requests
fired = w[(w.rate > 0.06) & (w.requests >= 50)]
print(fired)
```
It fires for **6 hours: Nov 5, 05:00 to 10:00** — all during the outage, or (10:00) a window that still contains outage hours. No night-time false alarms. (With a 5% threshold one extra false alarm appears at Nov 6 02:00, which is why thresholds are tuned on past data.)

c) A longer window is calmer (fewer false alarms) but slower to notice a real problem; a shorter window reacts fast but is noisy.

## 8. Add a vector database to Compose

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: [.env]
    environment:
      QDRANT_URL: http://qdrant:6333
    depends_on: [qdrant]
  qdrant:
    image: qdrant/qdrant
    ports: ["6333:6333"]
    volumes:
      - qdrant_data:/qdrant/storage      # data lives in a named volume, not inside the container
volumes:
  qdrant_data:                           # declare the named volume
```

Compose puts all services on one private network and registers each **service name** as a hostname, so from inside the `api` container the database is reachable at `qdrant:6333`. `localhost` would point at the api container itself. A **named volume** is storage managed by Docker that survives `docker compose down` / container re-creation (it is removed only with `docker compose down -v`). For production, pin the image to a specific version tag instead of the implicit `latest`.

## 9. Percentiles by hand

a) Mean = 23,330 / 20 = **1,166.5 ms**. Sorted, the 10th and 11th values are 440 and 445, so the median (p50) = **442.5 ms**.

b) `numpy.percentile(x, 95)` = **6,625 ms** (numpy interpolates between the 19th and 20th sorted values, 6,500 and 9,000).

c) Show **p50 ≈ 0.44 s and p95 ≈ 6.6 s** together. The mean (1.17 s) describes nobody: 18 of 20 requests took under 0.52 s, while two took 6.5–9 s. Those two slow requests are the real problem to investigate (timeouts? retries? huge prompts?).

## 10. Retries with exponential backoff

See `ex10_retry.py`. Why each part matters:
- Only **temporary** errors (429, 5xx, timeouts) are retried; a 400 will fail the same way every time, and retrying it wastes money.
- Exponential delays (0.1, 0.2, 0.4 s …) give an overloaded provider time to recover.
- **Jitter** (a small random extra) stops thousands of clients from retrying at exactly the same moment.
- A maximum number of retries keeps a user from waiting forever; then fail clearly or switch to a fallback model.
- Many SDKs (Anthropic, OpenAI) already retry some errors; check their `max_retries` setting so you do not retry twice over.

## 11. A per-user rate limiter

See `ex11_rate_limit.py`. The dependency keeps a `deque` of timestamps per `X-User-Id`, drops timestamps older than 10 seconds, and raises 429 (with a `Retry-After` header) when 5 remain.

Why it breaks with 3 containers: each container has its **own memory**, so each keeps its own counters. A load balancer spreads a user's requests across all three, so the user actually gets 3 × 5 = 15 requests per window, and a restart wipes the counters. Fix: keep counters in a **shared store** all copies can see — usually **Redis** (an in-memory database) — or enforce limits at an **API gateway** or load balancer in front of the app.

## 12. An eval gate in CI

See `ex12_eval_gate.py`. It returns exit code 0 when `mean ≥ EVAL_THRESHOLD`, otherwise 1; CI treats any non-zero exit code as a failed step and blocks the merge.

Workflow step, added after "Run tests" in the `test` job:

```yaml
      - name: Eval gate
        run: python eval_gate.py
        env:
          EVAL_THRESHOLD: "0.7"
```

Why offline/cheap and small: CI runs on **every push**, often dozens of times a day. A real-model eval over hundreds of cases would be slow, cost money each run, and give slightly different scores each time (models are not fully deterministic), making builds flaky. Keep a small, fixed, fast set in CI; run the large real-model eval nightly or before a release, and store its scores in Langfuse to watch the trend.
