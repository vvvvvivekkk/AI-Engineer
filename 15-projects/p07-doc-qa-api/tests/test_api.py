"""API tests with FastAPI's TestClient (it calls the app in-process - no real server needed)."""
import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    """Copy the sample PDFs to a temp folder so /ingest uploads never touch data/."""
    import os
    docs = tmp_path_factory.mktemp("pdfs")
    for pdf in (ROOT / "data" / "pdfs").glob("*.pdf"):
        shutil.copy(pdf, docs)
    os.environ["DOCS_DIR"] = str(docs)
    os.environ["LOG_FILE"] = str(docs / "requests.jsonl")
    import importlib
    import src.api as api
    importlib.reload(api)                     # re-read DOCS_DIR / LOG_FILE from the environment
    with TestClient(api.app) as c:            # "with" runs the start-up code (builds the index)
        c.log_file = docs / "requests.jsonl"
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok" and r.json()["chunks"] > 10


def test_ask_answers_with_page_citation(client):
    r = client.post("/ask", json={"question": "How many days of paid annual leave do full-time employees get?"})
    body = r.json()
    assert r.status_code == 200 and body["found"]
    assert "24 days" in body["answer"]
    assert body["citations"][0]["doc"] == "leave-policy.pdf" and body["citations"][0]["page"] == 1


def test_ask_says_not_found(client):
    body = client.post("/ask", json={"question": "Who won the company football tournament last year?"}).json()
    assert body["found"] is False and body["citations"] == []


def test_validation_error(client):
    assert client.post("/ask", json={"question": "hi"}).status_code == 422     # too short


def test_trace_log_written(client):
    client.post("/ask", json={"question": "What is the minimum password length?"})
    lines = client.log_file.read_text().splitlines()
    assert lines and "trace_id" in json.loads(lines[-1])


def test_ingest_upload_and_reject_non_pdf(client):
    bad = client.post("/ingest", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert bad.status_code == 400
    pdf = (ROOT / "data" / "pdfs" / "travel-policy.pdf").read_bytes()
    ok = client.post("/ingest", files={"file": ("travel-copy.pdf", pdf, "application/pdf")})
    assert ok.status_code == 200 and "travel-copy.pdf" in ok.json()["files"]


def test_chunker_overlap():
    from src.ingest import chunk_text
    words = " ".join(str(i) for i in range(100))
    chunks = chunk_text(words, size=40, overlap=10)
    assert chunks[0].split()[-10:] == chunks[1].split()[:10]       # 10 shared words
    assert chunks[-1].split()[-1] == "99"                           # nothing lost at the end
