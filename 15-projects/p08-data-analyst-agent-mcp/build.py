"""
build.py - regenerate this project's diagrams (images/) and Colab notebook.

Run from anywhere:  python 15-projects/p08-data-analyst-agent-mcp/build.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from build_kit import mermaid, notebook  # noqa: E402

PROJECT = HERE.name

ARCH = """
flowchart LR
  Q[Business question] --> L[agent.py loop<br/>max steps, error handling]
  L <--> P[Planner<br/>scripted / Claude / GPT / Ollama]
  L --> T[tools.py]
  T --> S[sql_query<br/>read-only guard]
  T --> C[python_calc<br/>AST-checked pandas]
  T --> G[make_chart<br/>PNG]
  T --> N[search_notes]
  S --> DB[(sales.db)]
  N --> NO[(notes/*.md)]
  L --> LOG[(trajectories.jsonl)]
  M[mcp_server.py] --> T
  CL[MCP client<br/>Claude Desktop / Code] <--> M
"""

LOOP = """
flowchart TD
  A[question + history] --> B[planner.next_action]
  B -->|final| Z[return answer]
  B -->|invalid reply| R{2 in a row?}
  R -- no --> A
  R -- yes --> Z
  B -->|tool + args| C[call_tool]
  C -->|result or error| D[append to history]
  D --> E{steps < max?}
  E -- yes --> A
  E -- no --> Z
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
    mermaid(LOOP, HERE / "images" / "agent_loop.png")
    cells = [
        ("md", "# P8 - Data-analyst agent + MCP server: quick start\nAn agent answers business questions by calling "
               "SQL, pandas, chart and notes tools on a synthetic sales database. The same tools are exposed through "
               "an MCP server. CPU runtime, no API key (the default planner is deterministic)."),
        *SETUP,
        ("md", "## 3. Build the database\n~11,500 orders for 2025 with three planted anomalies."),
        ("code", "!python -m src.make_db"),
        ("md", "## 4. Ask the agent a question\nEach step shows the tool call and a preview of its result."),
        ("code", "!python -m src.agent \"Which region's revenue fell most last quarter, and why?\""),
        ("md", "## 5. Run the 5 test tasks\nChecks the exact tool sequence and key facts in each answer."),
        ("code", "!python -m src.run_tasks --planner scripted"),
        ("md", "## 6. Look at the chart the agent made"),
        ("code", """from IPython.display import Image, display
display(Image("outputs/charts/monthly-revenue-2025.png"))"""),
        ("md", "## 7. The MCP server\nList the tools and call them through the official MCP SDK - in-process and "
               "over stdio (a real subprocess, like Claude Desktop would start)."),
        ("code", "!python -m src.mcp_check 2>/dev/null"),
        ("md", "## 8. Run the tests"),
        ("code", "!python -m pytest -q tests"),
        ("md", "## 9. (Optional) a real LLM planner\nIn Colab, add `ANTHROPIC_API_KEY` under the key icon (Secrets), "
               "then run the next cell. Without a key it explains what is missing."),
        ("code", """import os
try:
    from google.colab import userdata
    os.environ["ANTHROPIC_API_KEY"] = userdata.get("ANTHROPIC_API_KEY") or ""
except Exception:
    pass
if os.getenv("ANTHROPIC_API_KEY", "").startswith("sk-"):
    os.environ["LLM_PROVIDER"] = "anthropic"
    !python -m src.run_tasks --planner llm
else:
    print("No ANTHROPIC_API_KEY found - skipping the Claude planner (the scripted planner ran above).")"""),
    ]
    notebook(cells, HERE / "colab_quickstart.ipynb")


if __name__ == "__main__":
    build()
