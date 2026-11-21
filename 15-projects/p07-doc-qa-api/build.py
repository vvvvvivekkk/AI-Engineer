"""
build.py - regenerate this project's diagrams (images/) and Colab notebook.

Run from anywhere:  python 15-projects/p07-doc-qa-api/build.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from build_kit import mermaid, notebook  # noqa: E402

PROJECT = HERE.name

ARCH = """
flowchart LR
  M[make_pdfs.py<br/>10 policy PDFs] --> P[(data/pdfs)]
  P --> I[ingest.py<br/>pypdf -> page-aware chunks]
  I --> B[BM25<br/>keyword index]
  I --> V[MiniLM embeddings<br/>FAISS index]
  Q[POST /ask] --> B
  Q --> V
  B --> F[RRF fusion]
  V --> F
  F --> C{confidence<br/>>= threshold?}
  C -- no --> NF[Not found in the documents]
  C -- yes --> A[answer + citations<br/>doc + page]
  A --> L[(logs/requests.jsonl)]
"""

DEPLOY = """
flowchart LR
  U[client / curl / browser] -->|HTTP :8000| API[FastAPI container<br/>uvicorn src.api:app]
  API --> PDF[(volume: data/pdfs)]
  API --> LOG[(volume: logs)]
  API -. ANSWER_MODE=llm .-> O[Ollama container<br/>optional profile]
  API -. or .-> H[Hosted API<br/>Anthropic / OpenAI]
"""

# Shared first cells: get the code (skip clone if we are already inside the repo) and install.
SETUP = [
    ("md", "## 1. Get the code\nIn Colab this clones the course repo. If you are already inside the project "
           "folder (running locally), the clone is skipped."),
    ("code", f"""import os, pathlib, subprocess, sys
PROJECT = "{PROJECT}"
if pathlib.Path("src").is_dir() and pathlib.Path("README.md").exists():
    print("Project folder found - using the local copy, no clone needed.")
else:
    if not pathlib.Path("AI-Engineer").exists():
        subprocess.run(["git", "clone", "--depth", "1", "https://github.com/vvvvvivekkk/AI-Engineer.git"], check=True)
    os.chdir(f"AI-Engineer/15-projects/{{PROJECT}}")
print("working in", os.getcwd())"""),
    ("md", "## 2. Install the pinned packages (Colab only)\nColab already has PyTorch with GPU support, so we skip "
           "the `torch` line to avoid replacing it. Locally you install with `pip install -r requirements.txt` in a venv."),
    ("code", """IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    reqs = [l for l in open("requirements.txt") if l.strip() and not l.startswith(("torch==", "#"))]
    open("/tmp/req.txt", "w").writelines(reqs)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "/tmp/req.txt"], check=True)
print("ready")"""),
]




def build():
    mermaid(ARCH, HERE / "images" / "architecture.png")
    mermaid(DEPLOY, HERE / "images" / "deployment.png")
    cells = [
        ("md", "# P7 - Policy document Q&A API: quick start\nAsk questions about 10 fictional policy PDFs. "
               "Hybrid search (BM25 + vectors, fused with RRF) finds the right page; answers cite document and page. "
               "CPU runtime is fine; no API key needed."),
        *SETUP,
        ("md", "## 3. Generate the PDFs and the golden question set"),
        ("code", "!python -m src.make_pdfs"),
        ("md", "## 4. Evaluate retrieval and answers\nCompares BM25-only, vector-only and hybrid search on the "
               "golden set (Recall@k, MRR), then checks refusals, citations and a faithfulness proxy."),
        ("code", "!python -m src.evaluate"),
        ("md", "## 5. Start the API and ask a real HTTP question\nWe start `uvicorn` in the background, wait for "
               "`/health`, then POST to `/ask`."),
        ("code", """import socket, time, httpx
sock = socket.socket(); sock.bind(("127.0.0.1", 0)); PORT = sock.getsockname()[1]; sock.close()   # a free port
server = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.api:app", "--port", str(PORT)],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(120):                      # wait up to ~2 minutes for the index to build
    try:
        print(httpx.get(f"http://127.0.0.1:{PORT}/health").json()); break
    except httpx.HTTPError:
        time.sleep(1)"""),
        ("md", "Ask an answerable question, then one that is not in any document."),
        ("code", """for q in ["How many days of paid annual leave do full-time employees get?",
          "What is the Wi-Fi password for guests?",
          "How quickly must a suspected data breach be reported?"]:
    r = httpx.post(f"http://127.0.0.1:{PORT}/ask", json={"question": q}, timeout=60).json()
    print(q, "->", r["answer"], "| confidence", r["confidence"])"""),
        ("md", "Stop the server."),
        ("code", "server.terminate(); server.wait(); print('stopped')"),
        ("md", "## 6. Run the tests\nThe tests use FastAPI's `TestClient`, which calls the app in-process."),
        ("code", "!python -m pytest -q tests"),
        ("md", "## 7. Docker (on your own machine)\nColab cannot run Docker. On a machine with Docker installed:\n\n"
               "```bash\ndocker compose up --build\ncurl -X POST localhost:8000/ask -H 'Content-Type: application/json' "
               "-d '{\"question\": \"How long is the probation period?\"}'\n```"),
    ]
    notebook(cells, HERE / "colab_quickstart.ipynb")


if __name__ == "__main__":
    build()
