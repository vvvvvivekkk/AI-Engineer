"""
build.py - regenerates this project's architecture diagram (images/) and Colab notebook.

Run from anywhere:  python 15-projects/p01-ml-classifier-pipeline/build.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from build_kit import mermaid, notebook  # noqa: E402

PROJECT = "15-projects/p01-ml-classifier-pipeline"

DIAGRAM = """
flowchart LR
    A[make_data.py<br/>bundled sklearn data] --> B[data/*.csv]
    B --> C[train / test split<br/>80% / 20%]
    C --> D[4 Pipelines<br/>scaler + model]
    D --> E[5-fold<br/>cross-validation]
    E --> F[GridSearchCV<br/>tune the winner]
    F --> G[score once on<br/>hidden test set]
    G --> H[reports/<br/>markdown + confusion PNG]
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
        ("md", "# P1 quickstart - classic classifiers in a scikit-learn Pipeline\n\n"
               "This notebook downloads the project (in Colab), installs its packages, runs it and "
               "shows the results. Locally it uses the folder you already have. CPU is enough."),
        ("md", "## 1. Get the code\nIn Colab this clones the repo. If the project folder already exists, "
               "the clone is skipped."),
        ("code", GET_CODE),
        ("md", "## 2. Install packages (Colab only)"),
        ("code", INSTALL),
        ("md", "## 3. (Re)create the sample data\nThe CSVs are already committed; this shows where they come from."),
        ("code", "!{sys.executable} make_data.py"),
        ("md", "## 4. Run the experiment on all three datasets\nTakes about 20 seconds on a CPU."),
        ("code", "!{sys.executable} main.py"),
        ("md", "## 5. Look at one report and its confusion matrix"),
        ("code", "from IPython.display import Markdown, Image, display\n"
                 "display(Markdown(Path('reports/report_breast_cancer.md').read_text()))\n"
                 "display(Image('reports/confusion_breast_cancer.png'))"),
        ("md", "## 6. Run the tests\n`pytest` runs every function whose name starts with `test_`."),
        ("code", "!{sys.executable} -m pytest -q"),
    ], HERE / "colab_quickstart.ipynb")
    print("built diagram + notebook")


if __name__ == "__main__":
    build()
