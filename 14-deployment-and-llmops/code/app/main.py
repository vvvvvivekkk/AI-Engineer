"""
main.py - a small but realistic FastAPI service that wraps an LLM.

Run it locally (from the code/ folder):
    uvicorn app.main:app --reload --port 8000
Then open http://127.0.0.1:8000/docs for the automatic, clickable API docs.

Endpoints ("routes"):
    GET  /health   -> {"status": "ok"}  (used by Docker and load balancers to check the app is alive)
    POST /chat     -> send a message, get a reply (with guardrails + metrics)
    GET  /metrics  -> headline numbers: request count, error rate, latency, cost
"""
import os                                       # read settings from environment variables
import time                                     # stopwatch for latency
from fastapi import FastAPI, HTTPException      # FastAPI = the web framework; HTTPException = send an error response
from pydantic import BaseModel, Field           # pydantic models describe the JSON we accept and return

from app import guardrails, metrics             # our own helper modules (same folder)
from app.llm import generate

# Create the application object. uvicorn looks for this variable called "app".
app = FastAPI(title="LLM Chat Service", version="1.0.0",
              description="Teaching example for module 14: deployment and LLMOps")

APP_ENV = os.getenv("APP_ENV", "dev")           # e.g. dev / staging / prod, set in .env or docker-compose


# ---------------------------------------------------------------------------
# Request and response "schemas" (the shape of the JSON going in and out)
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., description="What the user typed", examples=["What is Docker?"])
    max_tokens: int = Field(256, ge=1, le=1024)  # must be between 1 and 1024 or FastAPI returns error 422


class ChatResponse(BaseModel):
    reply: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    pii_redacted: dict = {}                      # which kinds of PII we hid, e.g. {"EMAIL": 1}


# ---------------------------------------------------------------------------
# Routes: each function below handles one URL + HTTP method
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    """Liveness check. Cheap and fast on purpose."""
    return {"status": "ok", "env": APP_ENV}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Main endpoint: guardrails -> model -> metrics."""
    start = time.perf_counter()
    ok, reason = guardrails.validate_input(req.message)        # 1. basic input checks
    if not ok:
        metrics.record((time.perf_counter() - start) * 1000, ok=False)
        raise HTTPException(status_code=400, detail=reason)     # 400 = "bad request"
    if guardrails.looks_like_injection(req.message):            # 2. prompt-injection heuristic
        metrics.record((time.perf_counter() - start) * 1000, ok=False)
        raise HTTPException(status_code=400, detail="possible prompt injection")
    clean, pii = guardrails.redact_pii(req.message)             # 3. hide personal data before the model sees it
    try:
        result = generate(clean, max_tokens=req.max_tokens)     # 4. call the model (real or offline)
    except Exception as e:                                      # provider down, timeout, bad key ...
        metrics.record((time.perf_counter() - start) * 1000, ok=False)
        raise HTTPException(status_code=502, detail=f"model error: {type(e).__name__}")  # 502 = upstream failed
    total_ms = (time.perf_counter() - start) * 1000
    metrics.record(total_ms, ok=True, input_tokens=result["input_tokens"],
                   output_tokens=result["output_tokens"], cost_usd=result["cost_usd"])
    return ChatResponse(reply=result["text"], model=result["model"],
                        input_tokens=result["input_tokens"], output_tokens=result["output_tokens"],
                        cost_usd=result["cost_usd"], latency_ms=round(total_ms, 2), pii_redacted=pii)


@app.get("/metrics")
def get_metrics():
    """Headline monitoring numbers since the app started."""
    return metrics.summary()
