"""
build.py - regenerates this project's architecture diagram (images/) and Colab notebook.

Run from anywhere:  python 15-projects/p02-regression-and-segmentation/build.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from build_kit import mermaid, notebook  # noqa: E402

PROJECT = "15-projects/p02-regression-and-segmentation"

DIAGRAM = """
flowchart TD
    M[make_data.py] --> D1[data/diabetes.csv]
    M --> D2[data/customers.csv<br/>synthetic, 4 hidden groups]
    D1 --> GD[hand-written<br/>gradient descent]
    D1 --> SK[Linear / Ridge /<br/>Gradient Boosting]
    GD --> R[MAE, RMSE, R2<br/>residual plot]
    SK --> R
    D2 --> S[scale features]
    S --> K[K-means for k = 2..8<br/>elbow + silhouette]
    K --> P[profiles + names<br/>PCA 2-D plot]
    R --> O[reports/]
    P --> O
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
        ("md", "# P2 quickstart - regression and customer segmentation\n\n"
               "Part A predicts diabetes progression (including gradient descent written by hand). "
               "Part B groups synthetic customers with K-means. CPU only, about 15 seconds."),
        ("md", "## 1. Get the code\nIn Colab this clones the repo. If the project folder already exists, "
               "the clone is skipped."),
        ("code", GET_CODE),
        ("md", "## 2. Install packages (Colab only)"),
        ("code", INSTALL),
        ("md", "## 3. (Re)create the sample data\nSeeded, so the file is identical every time."),
        ("code", "!{sys.executable} make_data.py"),
        ("md", "## 4. Run both parts"),
        ("code", "!{sys.executable} main.py"),
        ("md", "## 5. Look at the charts\nLeft: gradient descent's error falling. Right: residuals. "
               "Then the elbow, silhouette and PCA plots for segmentation."),
        ("code", "from IPython.display import Image, display\n"
                 "display(Image('reports/regression.png'))\n"
                 "display(Image('reports/segmentation.png'))"),
        ("md", "## 6. Run the tests"),
        ("code", "!{sys.executable} -m pytest -q"),
    ], HERE / "colab_quickstart.ipynb")
    print("built diagram + notebook")


if __name__ == "__main__":
    build()
