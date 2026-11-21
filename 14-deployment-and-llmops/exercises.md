# Module 14 — Exercises

Twelve exercises, from easy to hard. Work in the notebooks or in `code/` (copy the folder first so you keep a clean version). Full solutions are in `solutions/`.

Difficulty: ⭐ easy · ⭐⭐ medium · ⭐⭐⭐ hard

---

### 1. Name that status code ⭐
For each situation, give the HTTP status code FastAPI (or your code) should return and say whose fault it is (client or server):

a) The request body is missing the required `message` field.
b) The message is present but empty.
c) No `X-API-Key` header was sent to a protected route.
d) The URL `/chta` (typo) was called.
e) The LLM provider timed out.
f) The user sent 200 requests in one minute and hit your rate limit.

### 2. A token-counting route ⭐
In notebook 01 (or `code/app/main.py`) add `GET /tokens?text=...` that returns `{"text_length": ..., "approx_tokens": ...}` using the 4-characters-per-token rule. Write two tests with `TestClient`: one normal call, and one call without `text` (what status code do you expect?).

### 3. Docker vocabulary and commands ⭐
a) In one sentence each, explain *Dockerfile*, *image*, *container* and *registry* to a friend who has never coded.
b) Write the command to run the image `llm-chat-api` so that it is reachable on **your laptop's port 9000**, reads settings from `.env`, and is deleted when it stops.
c) Why does the app inside the container listen on `0.0.0.0` and not `127.0.0.1`?

### 4. Fix the broken Dockerfile ⭐⭐
Find at least **five** problems in this Dockerfile and rewrite it correctly:

```dockerfile
FROM python:latest
COPY . .
ENV ANTHROPIC_API_KEY=sk-ant-REPLACE-ME
RUN pip install fastapi uvicorn anthropic
CMD ["uvicorn", "app.main:app", "--port", "8000"]
```

### 5. A `/summarize` endpoint ⭐⭐
Add `POST /summarize` to `code/app/main.py`:
- Request model: `text` (string, 20–20,000 characters) and `max_words` (integer, 10–200, default 50).
- Run the same guardrails as `/chat` (validation, injection check, PII redaction).
- Use `generate()` with a prompt that asks for a summary in at most `max_words` words.
- Response model: `summary`, `input_tokens`, `output_tokens`, `cost_usd`.
- Record metrics. Write at least three tests (happy path, too-short text → 422, injection → 400).

### 6. More PII patterns ⭐⭐
Extend `redact_pii()` with:
- an Indian **PAN** pattern (5 capital letters, 4 digits, 1 capital letter, e.g. `ABCDE1234F`) labelled `PAN`;
- a 12-digit **Aadhaar-like** number written as three groups of four digits (`1234 5678 9012`) labelled `AADHAAR`.
Write tests that show both are redacted. Then find one *innocent* sentence your new patterns wrongly redact, and explain why ordering of patterns matters (hint: the CARD and PHONE patterns).

### 7. Make the alert less noisy ⭐⭐
In notebook 03 the error-rate alert fires at night on normal days because traffic is low (one error in 15 requests is already 6.7%).
a) First try the obvious fix: fire only when **error rate > 5% AND requests in that hour ≥ 50**. How many hours fire now? Is that good?
b) Better: compute the error rate over a **rolling 3-hour window** (sum of errors ÷ sum of requests in the last 3 hours) and fire when it is **above 6% and the window has at least 50 requests**. Which hours fire now, and are they all linked to the outage (Nov 5, 04:00–09:59)?
c) In one sentence: what is the trade-off between a long window and a short window?

### 8. Add a vector database to Compose ⭐⭐
Extend `code/docker-compose.yml` with a third service, `qdrant`, using the official image `qdrant/qdrant`, exposing port 6333, and storing its data in a **named volume** so it survives restarts. Give the `api` service an environment variable `QDRANT_URL` pointing at it, and make `api` depend on it. Explain why the URL uses `qdrant` as the hostname.

### 9. Percentiles by hand ⭐⭐
Twenty request latencies in milliseconds:
`420, 380, 510, 450, 9000, 470, 390, 430, 460, 400, 480, 410, 440, 6500, 395, 455, 405, 465, 425, 445`
a) Compute the mean and the median (p50) by hand or with Python.
b) Compute p95 with `numpy.percentile`.
c) Which number would you show your manager to describe the user experience, and why is the mean misleading here?

### 10. Retries with exponential backoff ⭐⭐⭐
Write `call_with_retries(fn, max_retries=3, base_delay=0.1)` that calls `fn()` and, if it raises a `RateLimitError` or `ServerError` (define these two exception classes yourself), waits `base_delay × 2^attempt` seconds plus a little random **jitter**, then tries again. Any other exception must be raised immediately (do not retry a bad request!). After the last retry, raise the error. Test it with a fake function that fails twice with `ServerError` then succeeds, and with one that raises `ValueError`.

### 11. A per-user rate limiter ⭐⭐⭐
Write a FastAPI **dependency** that allows each `X-User-Id` at most **5 requests per 10 seconds** (a sliding window kept in memory) and otherwise raises `HTTPException(429)`. Attach it to `/chat`. Test: 5 quick requests succeed, the 6th returns 429, and a different user is not affected. Then explain why an in-memory limiter breaks when you run 3 copies of the container behind a load balancer, and what you would use instead.

### 12. An eval gate in CI ⭐⭐⭐
Write `eval_gate.py` that:
1. loads a small list of `(question, required_keywords)` test cases,
2. sends each question to the app via `TestClient` (offline model),
3. scores each answer as the share of required keywords present,
4. prints a table and the mean score,
5. **exits with code 1** if the mean is below a threshold given by the environment variable `EVAL_THRESHOLD` (default 0.7).

Then add a step to `code/ci/github-actions-ci.yml` that runs it after the unit tests. Explain why CI evals should use an offline or cheap model and a small fixed set.
