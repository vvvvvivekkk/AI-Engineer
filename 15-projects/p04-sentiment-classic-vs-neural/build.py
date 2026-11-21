"""
build.py - regenerates this project's architecture diagram (images/) and Colab notebook.

Run from anywhere:  python 15-projects/p04-sentiment-classic-vs-neural/build.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from build_kit import mermaid, notebook  # noqa: E402

PROJECT = "15-projects/p04-sentiment-classic-vs-neural"

DIAGRAM = """
flowchart LR
    G[make_data.py<br/>templates + word banks] --> R[data/reviews.csv<br/>1,000 labelled]
    G --> C[data/challenge.csv<br/>40 tricky reviews]
    R --> S[same 80/20 split]
    S --> M1[TF-IDF +<br/>logistic regression]
    S --> M2[PyTorch<br/>embedding bag]
    S --> M3[zero-shot transformers<br/>NLI / SST-2 / LLM]
    M1 --> E[accuracy, speed,<br/>failure cases]
    M2 --> E
    M3 --> E
    C --> E
    E --> O[reports/comparison.md]
"""

GET_CODE = f'''
import os, subprocess, sys
from pathlib import Path

PROJECT = "{PROJECT}"
if Path("main.py").exists() and Path("requirements.txt").exists():
    print("Already inside the project folder - no clone needed.")
elif Path("../../" + PROJECT).exists():
    os.chdir("../../" + PROJECT)          # repo already on disk two levels up
else:
    if not Path("AI-Engineer").exists():  # first run in Colab: download the repo
        subprocess.run(["git", "clone", "--depth", "1",
                        "https://github.com/vvvvvivekkk/AI-Engineer.git"], check=True)
    os.chdir(Path("AI-Engineer") / PROJECT)
print("Working folder:", Path.cwd())
'''

INSTALL = '''
import sys, subprocess
from pathlib import Path
# Only install in Colab. Locally you already did "pip install -r requirements.txt" in a venv.
# Colab ships its own PyTorch, so we skip the torch line to save a big download.
if "google.colab" in sys.modules:
    reqs = [l for l in Path("requirements.txt").read_text().splitlines()
            if l.strip() and not l.startswith(("#", "torch"))]
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", *reqs], check=True)
    print("installed", len(reqs), "packages")
else:
    print("Not in Colab - skipping install.")
'''


def build():
    mermaid(DIAGRAM, HERE / "images" / "architecture.png")
    notebook([
        ("md", "# P4 quickstart - sentiment: classic vs neural vs zero-shot\n\n"
               "Three approaches on the same reviews: TF-IDF + logistic regression, a tiny PyTorch "
               "network, and pretrained transformers used zero-shot. CPU is enough; the first run "
               "downloads two small Hugging Face models (25 MB and 260 MB). About 5 minutes."),
        ("md", "## 1. Get the code\nIn Colab this clones the repo. If the project folder already exists, "
               "the clone is skipped."),
        ("code", GET_CODE),
        ("md", "## 2. Install packages (Colab only)"),
        ("code", INSTALL),
        ("md", "## 3. (Re)create the data\nSeeded templates, so the reviews are identical every run."),
        ("code", "!{sys.executable} make_data.py\n"
                 "import pandas as pd\n"
                 "pd.read_csv('data/reviews.csv').head()"),
        ("md", "## 4. Train and compare all models"),
        ("code", "!{sys.executable} main.py"),
        ("md", "## 5. Read the comparison and the tricky cases"),
        ("code", "from IPython.display import Markdown, display\n"
                 "display(Markdown(Path('reports/comparison.md').read_text()))\n"
                 "pd.read_csv('reports/challenge_predictions.csv').head(12)"),
        ("md", "## 6. Run the tests"),
        ("code", "!{sys.executable} -m pytest -q"),
    ], HERE / "colab_quickstart.ipynb")
    print("built diagram + notebook")


if __name__ == "__main__":
    build()
