"""
build.py - regenerate this project's diagram (images/) and Colab notebook.

Run from anywhere:  python 15-projects/p06-response-rating-tool/build.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from build_kit import mermaid, notebook  # noqa: E402

PROJECT = HERE.name

ARCH = """
flowchart LR
  G[make_data.py<br/>100 prompts x 2 answers] --> C[(candidates.json)]
  C --> APP[Streamlit app.py<br/>rater picks A / B / tie<br/>+ 4-criterion rubric]
  C --> SIM[simulate_raters.py<br/>demo humans]
  APP --> R[(ratings.jsonl)]
  SIM --> R
  C --> J[judge.py<br/>rule or LLM judge<br/>asked in both orders]
  J --> JR[(judge_*.jsonl)]
  R --> K[agreement.py<br/>Cohen's kappa]
  JR --> K
  R --> X[export: preferences_hh.jsonl<br/>chosen / rejected]
  X --> P10[P10 DPO]
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
    cells = [
        ("md", "# P6 - Response-rating tool: quick start\nRate pairs of AI answers, export HH-RLHF-style preference "
               "data, and measure how well an automatic judge agrees with humans (Cohen's kappa). "
               "Runs on a normal CPU runtime - no GPU, no API key."),
        *SETUP,
        ("md", "## 3. Make the data\n100 prompts with two answers each (one has a planted flaw), plus simulated "
               "ratings from two pretend humans so the analysis works straight away."),
        ("code", "!python -m src.make_data\n!python -m src.simulate_raters"),
        ("md", "## 4. Run the rule-based judge and measure agreement\nThe judge is asked twice with the answers "
               "swapped to catch position bias."),
        ("code", "!python -m src.judge\n!python -m src.agreement"),
        ("md", "## 5. Export chosen/rejected pairs\nThis is the file P10 can use for DPO training."),
        ("code", """from src.ratings import DATA, export_preferences, load_candidates, read_jsonl
n = export_preferences(load_candidates(), read_jsonl(DATA / "ratings.jsonl"), DATA / "preferences_hh.jsonl", rater="sim_rater_1")
print(n, "pairs written")
print(open(DATA / "preferences_hh.jsonl").readline()[:300])"""),
        ("md", "## 6. (Optional) the tiny local LLM as judge\nSlow-ish and close to random with a 135M model - "
               "that is the lesson. Watch the position-consistency number."),
        ("code", "!python -m src.judge --judge llm --limit 6\n!python -m src.agreement --judge llm"),
        ("md", "## 7. Run the tests"),
        ("code", "!python -m pytest -q tests"),
        ("md", "## 8. Open the rating app (Colab only)\nStarts Streamlit in the background and opens it in a "
               "Colab window. Locally, run `streamlit run app.py` in a terminal instead."),
        ("code", """if IN_COLAB:
    subprocess.Popen(["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"])
    import time; time.sleep(5)
    from google.colab import output
    output.serve_kernel_port_as_window(8501)
else:
    print("Not in Colab: run `streamlit run app.py` in a terminal.")"""),
    ]
    notebook(cells, HERE / "colab_quickstart.ipynb")


if __name__ == "__main__":
    build()
