"""
api.py - the FastAPI web service.

**API** (application programming interface) - a way for other programs to use
ours over HTTP, like a restaurant's order window: you hand in a request in an
agreed format and get a response back. **FastAPI** is a Python library for
building such services; it checks request data with **Pydantic** models (classes
that describe the expected fields and types) and writes interactive docs at /docs.

Endpoints:
  GET  /health   is the service up, and how many chunks are indexed?
  POST /ingest   re-read the PDF folder (optionally upload one new PDF first)
  POST /ask      {"question": "...", "k": 3} -> answer + citations

**Tracing** - every /ask request gets an id, and one JSON line (question,
latency, pages cited, found or not) is appended to logs/requests.jsonl. That is
a tiny, dependency-free version of what tools like Langfuse do.

Run locally:  uvicorn src.api:app --reload --port 8000   then open http://localhost:8000/docs
"""
from __future__ import annotations

import json
import os
import shutil
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from .answer import answer
from .ingest import ingest_folder
from .retrieval import HybridIndex

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = Path(os.getenv("DOCS_DIR", ROOT / "data" / "pdfs"))
LOG_FILE = Path(os.getenv("LOG_FILE", ROOT / "logs" / "requests.jsonl"))

STATE: dict = {"index": None}          # the search index lives here while the server runs


def build_index() -> int:
    """(Re)build the hybrid index from every PDF in DOCS_DIR. Returns the chunk count."""
    chunks = ingest_folder(DOCS_DIR)
    STATE["index"] = HybridIndex(chunks) if chunks else None
    return len(chunks)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once at start-up: build the index so the first question is fast."""
    build_index()
    yield


app = FastAPI(title="Policy Doc Q&A", version="1.0", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500, examples=["How many days of annual leave do I get?"])
    k: int = Field(3, ge=1, le=10, description="how many chunks to retrieve")


class Citation(BaseModel):
    doc: str
    page: int
    snippet: str
    rrf: float


class AskResponse(BaseModel):
    trace_id: str
    answer: str
    found: bool
    confidence: float
    citations: list[Citation]
    latency_ms: float


def log_trace(record: dict) -> None:
    """Append one JSON line per request (our minimal tracing)."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


@app.get("/health")
def health() -> dict:
    idx = STATE["index"]
    return {"status": "ok", "chunks": len(idx.chunks) if idx else 0, "docs_dir": str(DOCS_DIR)}


@app.post("/ingest")
def ingest(file: UploadFile | None = File(default=None)) -> dict:
    """Optionally save an uploaded PDF, then rebuild the index from the whole folder."""
    if file is not None:
        if not (file.filename or "").lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only .pdf files are accepted.")
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        with (DOCS_DIR / Path(file.filename).name).open("wb") as out:   # .name blocks "../" tricks
            shutil.copyfileobj(file.file, out)
    n = build_index()
    return {"status": "indexed", "chunks": n, "files": sorted(p.name for p in DOCS_DIR.glob("*.pdf"))}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    if STATE["index"] is None:
        raise HTTPException(status_code=503, detail="No documents indexed yet. Call /ingest first.")
    trace_id, start = uuid.uuid4().hex[:12], time.perf_counter()
    result = answer(STATE["index"], req.question, k=req.k)
    latency = round((time.perf_counter() - start) * 1000, 1)
    log_trace({"trace_id": trace_id, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "question": req.question,
               "found": result["found"], "confidence": result["confidence"], "latency_ms": latency,
               "cited": [f"{c['doc']}#p{c['page']}" for c in result["citations"]]})
    return AskResponse(trace_id=trace_id, latency_ms=latency, **result)
