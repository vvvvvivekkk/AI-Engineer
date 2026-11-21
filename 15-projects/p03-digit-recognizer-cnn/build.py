"""
build.py - regenerates this project's architecture diagram (images/) and Colab notebook.

Run from anywhere:  python 15-projects/p03-digit-recognizer-cnn/build.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from build_kit import mermaid, notebook  # noqa: E402

PROJECT = "15-projects/p03-digit-recognizer-cnn"

DIAGRAM = """
flowchart LR
    A[data/digits.csv<br/>1,797 images 8x8] --> B[split<br/>70 / 15 / 15]
    B --> C[DataLoader<br/>batches of 64]
    C --> D{model}
    D --> E[MLP<br/>flatten + dense]
    D --> F[CNN<br/>conv + pool]
    E --> G[training loop<br/>Adam + early stopping]
    F --> G
    G --> H[test set<br/>accuracy]
    H --> I[reports/<br/>confusion, mistakes, filters]
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
        ("md", "# P3 quickstart - digit recogniser: MLP vs CNN in PyTorch\n\n"
               "This notebook downloads the project (in Colab), installs its packages, runs it and "
               "shows the results. Locally it uses the folder you already have. CPU is enough (2-3 minutes); "
               "a Colab GPU is not needed."),
        ("md", "## 1. Get the code\nIn Colab this clones the repo. If the project folder already exists, "
               "the clone is skipped."),
        ("code", GET_CODE),
        ("md", "## 2. Install packages (Colab only)"),
        ("code", INSTALL),
        ("md", "## 3. (Re)create the sample data\nSaves the 1,797 bundled digit images to data/digits.csv."),
        ("code", "!{sys.executable} make_data.py"),
        ("md", "## 4. Train the MLP and the CNN\nEarly stopping ends training when validation loss stops improving."),
        ("code", "!{sys.executable} main.py"),
        ("md", "## 5. Look at the results\nLoss curves, the CNN's confusion matrix, its mistakes and its learned filters."),
        ("code", "from IPython.display import Image, display\n"
                 "for f in ['loss_curves', 'confusion_cnn', 'misclassified_cnn', 'cnn_filters']:\n"
                 "    display(Image(f'reports/{f}.png'))"),
        ("md", "## 6. Run the tests\n`pytest` runs every function whose name starts with `test_`."),
        ("code", "!{sys.executable} -m pytest -q"),
    ], HERE / "colab_quickstart.ipynb")
    print("built diagram + notebook")


if __name__ == "__main__":
    build()
