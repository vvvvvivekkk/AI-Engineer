"""
build.py - regenerate this project's diagrams (images/), the n8n workflow JSON and the Colab notebook.

Run from anywhere:  python 15-projects/p09-support-inbox-automation/build.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
sys.path.insert(0, str(HERE))
from build_kit import mermaid, notebook  # noqa: E402

PROJECT = HERE.name

ARCH = """
flowchart LR
  IN[inbox/ .eml .json<br/>or n8n IMAP trigger] --> X[extract.py<br/>rules or LLM + Pydantic]
  X --> K[workflow.find_article<br/>BM25 over 15 help articles]
  K --> D[draft_reply]
  D --> R{route}
  R -- urgent / angry / money / legal --> H[(queue.db<br/>pending_review)]
  R -- routine --> A[(queue.db<br/>auto_filed)]
  R -- spam --> S[(discarded)]
  H --> HU[human approves / rejects<br/>POST /queue/id/approve]
  H --> REP[report.py<br/>daily summary]
  A --> REP
"""

N8N = """
flowchart LR
  T1[IMAP Email Trigger] --> M[Map email fields]
  T0[Manual Trigger + Sample email] --> M
  M --> P[HTTP POST /triage<br/>our FastAPI]
  P --> IF{route == human_review?}
  IF -- true --> SL[Slack alert to reviewers]
  IF -- false --> NO[Auto-filed]
  SC[Schedule 18:00] --> G[HTTP GET /report/daily] --> EM[Email report to manager]
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
    from src.make_n8n import main as make_n8n
    make_n8n()
    mermaid(ARCH, HERE / "images" / "architecture.png")
    mermaid(N8N, HERE / "images" / "n8n_workflow.png")
    cells = [
        ("md", "# P9 - Support-inbox automation: quick start\nTriage ~200 synthetic support emails: extract fields into a "
               "Pydantic schema, find a help article, draft a reply, route (human approval / auto / spam), store in an "
               "SQLite approval queue, and write a daily summary. CPU runtime, no API key."),
        *SETUP,
        ("md", "## 3. Generate emails and help articles\nThe emails include edge cases: two intents, missing order ids, "
               "angry or legal-threat tone, quoted old threads, spam, Hinglish."),
        ("code", "!python -m src.make_emails\n!python -m src.make_articles"),
        ("md", "## 4. Run the Python pipeline on all emails\nPrints the route counts and accuracy against the true labels."),
        ("code", "!python -m src.pipeline --fresh"),
        ("md", "## 5. Watch an inbox folder\nThe same pipeline reading `.eml` files (already-processed emails are skipped "
               "thanks to the unique email id)."),
        ("code", "!python -m src.pipeline --inbox data/inbox"),
        ("md", "## 6. Be the human reviewer\nList pending items through the API and approve one."),
        ("code", """from fastapi.testclient import TestClient
from src.api import app
api = TestClient(app)
pending = api.get("/queue").json()["pending"]
print(len(pending), "tickets waiting. First one:")
first = pending[0]
print(first["subject"], "|", first["reasons"]) ; print(first["draft"])
print(api.post(f"/queue/{first['id']}/approve", json={"reviewer": "trainer", "note": "looks good"}).json()["status"])"""),
        ("md", "## 7. Daily summary report"),
        ("code", "!python -m src.report --date 2026-11-20"),
        ("md", "## 8. The n8n workflow\nThe importable file is `n8n/support_triage_workflow.json`. n8n cannot run in "
               "Colab; on your own computer run n8n with Docker and import it (see README)."),
        ("code", """import json
wf = json.load(open("n8n/support_triage_workflow.json"))
for n in wf["nodes"]:
    print(f"{n['name']:28s} {n['type']}")"""),
        ("md", "## 9. Run the tests"),
        ("code", "!python -m pytest -q tests"),
    ]
    notebook(cells, HERE / "colab_quickstart.ipynb")


if __name__ == "__main__":
    build()
