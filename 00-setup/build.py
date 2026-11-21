"""
build.py for module 00-setup.

Regenerates: images/ (Mermaid diagrams), notebooks/, slides/, excel/, pdf/.
Run from the repo root:   python 00-setup/build.py
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook

IMG = HERE / "images"
NB = HERE / "notebooks"

# ---------------------------------------------------------------------------
# 1. Diagrams
# ---------------------------------------------------------------------------
DIAGRAMS = {
    "tool-decision": """
flowchart TD
    A[New task] --> B{Need a GPU?}
    B -- Yes --> C[Google Colab<br/>pick T4 GPU if needed]
    B -- No --> D{Building an app,<br/>many files or Git?}
    D -- Yes --> E[VS Code<br/>.py files + terminal]
    D -- No --> F{Exploring data or<br/>teaching step by step?}
    F -- Yes --> G{Can install<br/>software locally?}
    G -- Yes --> H[Jupyter / VS Code<br/>notebook]
    G -- No --> C
    F -- No --> E
""",
    "git-workflow": """
flowchart LR
    W[Working folder<br/>your edited files] -- git add --> S[Staging area<br/>next snapshot]
    S -- git commit --> L[Local repo<br/>history in .git]
    L -- git push --> R[GitHub<br/>remote: origin]
    R -- git pull --> W
    R -- git clone --> W
""",
    "branch-pr": """
flowchart LR
    M1[main] --> M2[main]
    M2 -- git switch -c feature --> F1[feature:<br/>commit 1]
    F1 --> F2[feature:<br/>commit 2]
    F2 -- git push --> PR[Pull request<br/>on GitHub]
    PR -- review + approve --> MG[Merge into main]
    M2 --> MG
    MG -- git pull --> M3[Your local main<br/>updated]
""",
    "venv": """
flowchart TD
    SYS[System Python 3.12<br/>installed once] --> V1[project-a/.venv<br/>pandas 1.5]
    SYS --> V2[project-b/.venv<br/>pandas 2.2]
    SYS --> V3[project-c/.venv<br/>torch + transformers]
    V1 --> R1[requirements.txt]
    V2 --> R2[requirements.txt]
    V3 --> R3[requirements.txt]
""",
    "secrets-flow": """
flowchart LR
    K[Provider website<br/>create API key] --> E[.env file<br/>NAME=value]
    E -- load_dotenv --> O[os.environ<br/>environment variables]
    O -- os.getenv --> C[Your Python code]
    E -.->|blocked by gitignore| G[GitHub]
    X[.env.example<br/>placeholders only] -- committed --> G
    CS[Colab Secrets panel] -- userdata.get --> C
""",
}


def build_images():
    for name, src in DIAGRAMS.items():
        mermaid(src, IMG / f"{name}.png")


# ---------------------------------------------------------------------------
# 2. Notebooks
# ---------------------------------------------------------------------------
NB1 = [
    ("md", """# 00 · Notebook 1 — Environment check

**Goal:** confirm your Python setup works, and learn what a notebook really is.

You will:
1. Run your first cells and see how outputs appear.
2. Find out which Python is running and whether you are in a **virtual environment** (a private folder of packages for one project).
3. List installed **packages** (code other people wrote that you can install).
4. Look inside a `.ipynb` file and see that it is plain **JSON** (a text format of `{ "key": value }` pairs).
5. See why the order you run cells in matters.

How to run a cell: click inside it and press **Shift + Enter**. This works in Jupyter, VS Code and Google Colab."""),
    ("md", """## 1. Your first cell

A **code cell** holds Python. When you run it, the result appears under it. The last line of a cell is shown automatically, even without `print`."""),
    ("code", """print("Hello from a notebook!")
2 + 2"""),
    ("md", """## 2. Which Python is this?

The `sys` module (a **module** is a file of ready-made Python code) knows about the Python that is running this notebook.
- `sys.version` is the version number.
- `sys.executable` is the exact program on disk. If it contains `.venv`, you are using a virtual environment."""),
    ("code", """import sys
import platform

print("Python version :", sys.version.split()[0])
print("Python program :", sys.executable)
print("Operating sys. :", platform.system(), platform.release())

if sys.version_info < (3, 10):
    print("WARNING: this course needs Python 3.10 or newer.")
else:
    print("Version OK for this course.")"""),
    ("md", """## 3. Am I inside a virtual environment? Am I in Colab?

Inside a virtual environment, `sys.prefix` (where packages are installed) differs from `sys.base_prefix` (the original Python install).

Google Colab is detected by trying to import its special `google.colab` module. `try` / `except` means "try this; if it fails with this error, do that instead" — you will learn it properly in module 01."""),
    ("code", """in_venv = sys.prefix != sys.base_prefix
print("Inside a virtual environment:", in_venv)

try:
    import google.colab  # this module only exists on Colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False
print("Running in Google Colab:", IN_COLAB)"""),
    ("md", """## 4. Which packages are installed?

`importlib.metadata` is part of Python's **standard library** (the modules that come with Python). It can tell us each package's version. We check the packages this course relies on. "missing" is not an error — you install those later with `pip`."""),
    ("code", """import importlib.metadata as meta

course_packages = ["pip", "python-dotenv", "ipykernel", "numpy", "pandas",
                   "matplotlib", "scikit-learn", "torch", "transformers"]

for name in course_packages:
    try:
        print(f"[ok]      {name:<15} {meta.version(name)}")
    except meta.PackageNotFoundError:
        print(f"[missing] {name:<15} install with: python -m pip install {name}")

all_names = {d.metadata["Name"] for d in meta.distributions() if d.metadata["Name"]}
print(f"\\nTotal packages installed: {len(all_names)}")"""),
    ("md", """## 5. Running terminal commands from a notebook

A line starting with `!` is sent to the **terminal** (the text window for typing commands) instead of Python. This is handy in Colab, where you have no separate terminal. Here we ask the terminal for the Python version and pip's version."""),
    ("code", """!python --version
!python -m pip --version"""),
    ("md", """## 6. Run the module's checker script

The module ships `code/check_env.py`, a full health report. It prints whether API keys are set **without printing the keys**.

The cell below finds the script next to this notebook. In Colab the repo files are not there, so it downloads the script from GitHub first."""),
    ("code", """from pathlib import Path
import subprocess, urllib.request

script = Path("../code/check_env.py")
if not script.exists():
    # Running in Colab or elsewhere: fetch the script from the course repo.
    url = "https://raw.githubusercontent.com/vvvvvivekkk/AI-Engineer/main/00-setup/code/check_env.py"
    script = Path("check_env.py")
    try:
        urllib.request.urlretrieve(url, script)
    except Exception as err:
        print("Could not download the script:", err)

if script.exists():
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    print(result.stdout[-3000:])"""),
    ("md", """## 7. A notebook is JSON

A `.ipynb` file is a text file in JSON format. It stores every cell **and its outputs**. That is why you must never print a secret in a notebook: the printed text gets saved in the file.

The `nbformat` package (installed with Jupyter) can build a notebook in memory. We make a tiny two-cell notebook and print its JSON text."""),
    ("code", """import json
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

tiny = new_notebook()
tiny.cells.append(new_markdown_cell("# My tiny notebook"))
tiny.cells.append(new_code_cell("print(2 + 2)"))

text = nbformat.writes(tiny)          # the exact text that would be saved to a .ipynb file
print(text[:700])"""),
    ("md", """Look at the printout: a `"cells"` list, each cell with a `"cell_type"` (`markdown` or `code`) and a `"source"` (its text). Code cells also have `"outputs"` and an `"execution_count"` (the number in `[ ]` beside a cell).

Now we read **this** notebook file, if it is available, and count its cells by type."""),
    ("code", """nb_file = Path("01-environment-check.ipynb")
if nb_file.exists():
    data = json.loads(nb_file.read_text(encoding="utf-8"))
    kinds = [c["cell_type"] for c in data["cells"]]
    print("Cells in this notebook:", len(kinds))
    print("Markdown cells:", kinds.count("markdown"), "| Code cells:", kinds.count("code"))
else:
    print("This notebook's file is not on disk here (normal in Colab).")"""),
    ("md", """## 8. Run order matters: the kernel's memory

The **kernel** is the Python process behind the notebook. It remembers variables in the order you *ran* cells, not the order they appear.

Try this experiment:
1. Run the next two cells in order. You will see `10`.
2. Change `price = 5` to `price = 7` in the first cell but **do not run it**. Run only the second cell again. It still prints `10` — the kernel never saw your edit.
3. Fix: **restart the kernel and run all** (Jupyter: *Kernel → Restart Kernel and Run All Cells…*; Colab: *Runtime → Restart session and run all*; VS Code: *Restart*, then *Run All*)."""),
    ("code", """price = 5
quantity = 2"""),
    ("md", """The cell below uses the variables created above."""),
    ("code", """total = price * quantity
print(total)"""),
    ("md", """## Summary

- You ran code cells and saw outputs.
- You found which Python is running and whether a virtual environment is active.
- You listed installed packages and ran `check_env.py`.
- You saw that a `.ipynb` file is JSON that also stores outputs — so never print secrets.
- When a notebook behaves strangely: restart the kernel and run all.

Next: **Notebook 2 — working with `.env` safely**."""),
]

NB2 = [
    ("md", """# 00 · Notebook 2 — Working with `.env` files safely

**Goal:** learn the safe pattern for API keys that every later module uses.

Words used here:
- **API key** — a secret password that lets your code use a paid online service. Anyone with it can spend your money.
- **Environment variable** — a named value stored outside your code, in the settings of the running program.
- **`.env` file** — a text file of `NAME=value` lines that holds your secrets locally. It is never committed to Git.
- **python-dotenv** — a small package that reads `.env` into environment variables.

This notebook never uses a real key. It creates a throw-away `.env` with a fake value in a temporary folder and deletes it at the end."""),
    ("md", """## 1. Install check

`python-dotenv` is installed under the name `python-dotenv` but imported as `dotenv`. In Colab it may be missing; the cell installs it quietly if needed using `%pip` (the notebook version of `pip`, which installs into the running kernel)."""),
    ("code", """try:
    import dotenv
except ImportError:
    %pip install -q python-dotenv
    import dotenv

import importlib.metadata as meta
print("python-dotenv version:", meta.version("python-dotenv"))"""),
    ("md", """## 2. Environment variables with `os`

`os.environ` behaves like a dictionary of every environment variable. `os.getenv("NAME")` returns the value, or `None` if it does not exist. Asking for a missing key with `getenv` never crashes, which makes it the safe way to read keys."""),
    ("code", """import os

print("HOME or USERPROFILE is set:", bool(os.getenv("HOME") or os.getenv("USERPROFILE")))
print("A made-up variable:", os.getenv("DEFINITELY_NOT_SET_123"))
print("With a default value:", os.getenv("DEFINITELY_NOT_SET_123", "fallback"))"""),
    ("md", """## 3. Make a practice `.env` file

We write a `.env` into a **temporary folder** (a folder the operating system cleans up), so we cannot accidentally commit it. The value is obviously fake."""),
    ("code", """import tempfile
from pathlib import Path

practice_dir = Path(tempfile.mkdtemp())
env_path = practice_dir / ".env"
env_path.write_text(
    "# practice file - fake values only\\n"
    "DEMO_API_KEY=demo-not-a-real-key-123\\n"
    "APP_ENV=development\\n",
    encoding="utf-8",
)
print("Wrote:", env_path)
print("File contents (safe to show - fake values):")
print(env_path.read_text())"""),
    ("md", """## 4. Load it with `load_dotenv`

`load_dotenv(path)` copies each `NAME=value` line into the environment variables of this running Python. It returns `True` if it found the file.

Then we read the value with `os.getenv`. Notice how we **report** that the key is set without showing it."""),
    ("code", """from dotenv import load_dotenv

found = load_dotenv(env_path)
print("File found and loaded:", found)

key = os.getenv("DEMO_API_KEY")
print("DEMO_API_KEY is set:", key is not None)
print("APP_ENV =", os.getenv("APP_ENV"))   # not a secret, fine to print"""),
    ("md", """## 5. Showing a key safely (when you must)

Sometimes you need to confirm *which* key is loaded. Show only that it exists and its length, or at most the last 2 characters. Never the whole thing. The function below does that."""),
    ("code", """def describe_secret(value):
    \"\"\"Describe a secret without revealing it.\"\"\"
    if value is None:
        return "NOT SET"
    if value.strip() == "" or "your-key-here" in value:
        return "EMPTY or PLACEHOLDER"
    return f"set ({len(value)} characters, ends with ...{value[-2:]})"

print("DEMO_API_KEY:", describe_secret(os.getenv("DEMO_API_KEY")))
print("OPENAI_API_KEY:", describe_secret(os.getenv("OPENAI_API_KEY")))"""),
    ("md", """## 6. `override`: who wins if a variable is already set?

By default `load_dotenv` does **not** replace a variable that already exists in the environment. That lets a server's real settings win over a developer's `.env`. Pass `override=True` to let the file win."""),
    ("code", """os.environ["APP_ENV"] = "production"          # pretend the server set this

load_dotenv(env_path)                            # default: override=False
print("After default load :", os.getenv("APP_ENV"))

load_dotenv(env_path, override=True)
print("After override=True:", os.getenv("APP_ENV"))"""),
    ("md", """## 7. Read a `.env` without touching the environment

`dotenv_values(path)` returns the file as a plain dictionary. Useful for checking which names a file defines. We print only the **names**, not the values."""),
    ("code", """from dotenv import dotenv_values

values = dotenv_values(env_path)
print("Names defined in the file:", list(values.keys()))"""),
    ("md", """## 8. Is `.env` protected by `.gitignore`?

A **`.gitignore`** file lists files Git must never track. This small helper reads a `.gitignore` and checks whether `.env` is covered. We test it on two pretend files: a good one and a dangerous one. (Real Git matching has more rules; this is a simple check.)"""),
    ("code", """def env_is_ignored(gitignore_text):
    lines = [line.strip() for line in gitignore_text.splitlines()]
    lines = [line for line in lines if line and not line.startswith("#")]
    return ".env" in lines or "*.env" in lines or ".env*" in lines

good = "# secrets\\n.env\\n.venv/\\n__pycache__/\\n"
bad = ".venv/\\n__pycache__/\\n"
print("Good .gitignore protects .env:", env_is_ignored(good))
print("Bad  .gitignore protects .env:", env_is_ignored(bad))

repo_gitignore = Path("../../.gitignore")
if repo_gitignore.exists():
    print("This course repo protects .env:", env_is_ignored(repo_gitignore.read_text()))"""),
    ("md", """## 9. The pattern every later module uses

1. Try to load the key (from `.env` locally, or Colab Secrets on Colab).
2. If it exists, make the real API call.
3. If not, use a clearly-labelled **offline stand-in** so the notebook still runs.

`google.colab.userdata.get(...)` reads a value from Colab's **Secrets** panel (the key icon in Colab's left sidebar). Outside Colab that import fails, so we guard it."""),
    ("code", """def get_key(name):
    # 1) Colab Secrets panel (only exists in Colab)
    try:
        from google.colab import userdata
        try:
            return userdata.get(name)
        except Exception:
            pass  # secret not created, or notebook access not switched on
    except ImportError:
        pass
    # 2) Environment variables, filled from .env by load_dotenv()
    load_dotenv()
    value = os.getenv(name)
    if value and "your-key-here" not in value:
        return value
    return None


def ask_llm(question):
    key = get_key("OPENAI_API_KEY")
    if key:
        # The real call is taught in module 07, for example:
        # from openai import OpenAI
        # client = OpenAI(api_key=key)
        return "(real key found - module 07 makes the real call here)"
    return f"[OFFLINE STAND-IN] I would answer: {question!r}"


print(ask_llm("Why should .env never be committed?"))"""),
    ("md", """## 10. Clean up

We delete the practice file and folder, and remove the demo variables from this session."""),
    ("code", """import shutil

shutil.rmtree(practice_dir)
for name in ["DEMO_API_KEY", "APP_ENV"]:
    os.environ.pop(name, None)
print("Practice folder removed:", not practice_dir.exists())
print("DEMO_API_KEY now:", os.getenv("DEMO_API_KEY"))"""),
    ("md", """## Summary

- Read keys with `os.getenv("NAME")` — it returns `None` instead of crashing.
- Keep keys in `.env`, load them with `load_dotenv()`, and list `.env` in `.gitignore`.
- Commit a `.env.example` with placeholder values so teammates know which names to set.
- In Colab, use the **Secrets** panel and `userdata.get`.
- Never print a key. Notebook outputs are saved in the file.
- If a key ever leaks: **revoke it on the provider's website first**, then clean up."""),
]

NB3 = [
    ("md", """# 00 · Notebook 3 — Colab tour and `requirements.txt`

**Goal:** practise the Colab features from the lesson, and learn how a `requirements.txt` file pins versions.

This notebook runs anywhere. Colab-only cells check first whether they are in Colab and explain what they would do otherwise.

For the GPU part in Colab: **Runtime → Change runtime type → Hardware accelerator: T4 GPU → Save**, then run all cells. Locally you will see "CPU only", which is fine."""),
    ("md", """## 1. Where am I running?"""),
    ("code", """import sys, os
from pathlib import Path

try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

print("In Colab:", IN_COLAB)
print("Current folder:", Path.cwd())"""),
    ("md", """## 2. Is there a GPU?

A **GPU** (graphics processing unit) does many maths operations at once and makes deep learning much faster. PyTorch (a deep learning library, module 05) can tell us if one is visible. On Colab with a T4 runtime this prints the GPU name."""),
    ("code", """try:
    import torch
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))
    else:
        print("CPU only (in Colab: Runtime -> Change runtime type -> T4 GPU)")
except ImportError:
    print("PyTorch not installed")"""),
    ("md", """In Colab you can also run `!nvidia-smi`, a terminal command that shows the GPU, its memory and what is using it. We only run it when a GPU exists, because elsewhere the command is not found."""),
    ("code", """import shutil
if shutil.which("nvidia-smi"):
    !nvidia-smi
else:
    print("nvidia-smi not available here (no NVIDIA GPU).")"""),
    ("md", """## 3. Mounting Google Drive

**Mounting** connects a storage drive so it appears as a folder. Colab's disk is wiped when the runtime disconnects, so save anything important to Drive.

In Colab, the cell asks you to choose your Google account and allow access. Then your files are under `/content/drive/MyDrive/`. Outside Colab it only explains."""),
    ("code", """if IN_COLAB:
    from google.colab import drive
    drive.mount("/content/drive")
    save_dir = Path("/content/drive/MyDrive/ai-course")
    save_dir.mkdir(parents=True, exist_ok=True)
    print("Save long-lived files in:", save_dir)
else:
    print("Not in Colab. Locally your files already persist on disk.")"""),
    ("md", """## 4. Uploading and downloading files

`files.upload()` shows a **Choose Files** button under the cell. The chosen file lands in `/content/`. `files.download(name)` sends a file back to your computer. You can also use the **folder icon → Upload** button in Colab's left sidebar.

To keep the notebook runnable top to bottom, the upload line is commented out. Remove the `#` in Colab to try it."""),
    ("code", """sample = Path("sample_results.csv")
sample.write_text("student,score\\nAsha,88\\nRavi,92\\n", encoding="utf-8")
print("Created", sample, "with", len(sample.read_text().splitlines()), "lines")

if IN_COLAB:
    from google.colab import files
    # uploaded = files.upload()          # remove the # to try uploading
    # files.download(str(sample))        # remove the # to download the CSV
    print("In Colab: un-comment the lines above to try upload/download.")
else:
    print("Not in Colab: the file is simply on your disk at", sample.resolve())"""),
    ("md", """## 5. Colab Secrets

Click the **key icon** in Colab's left sidebar → **+ Add new secret** → Name `OPENAI_API_KEY`, Value = your key → switch on **Notebook access**. Then `userdata.get` reads it. The value is stored in your Google account, not in the notebook."""),
    ("code", """if IN_COLAB:
    from google.colab import userdata
    try:
        key = userdata.get("OPENAI_API_KEY")
        print("OPENAI_API_KEY found in Colab Secrets:", key is not None)
    except Exception as err:
        print("Secret not available:", type(err).__name__)
else:
    print("Not in Colab: use a .env file instead (see notebook 2).")"""),
    ("md", """## 6. `requirements.txt`: the shopping list

A **requirements.txt** lists the packages a project needs, one per line. **Pinning** with `==` fixes an exact version so the project behaves the same on every machine.

We write a small example file, then read it back line by line."""),
    ("code", """req = Path("example-requirements.txt")
req.write_text(
    "# example requirements file\\n"
    "numpy==2.1.3\\n"
    "pandas>=2.0,<4\\n"
    "python-dotenv\\n",
    encoding="utf-8",
)
for line in req.read_text().splitlines():
    print(line)"""),
    ("md", """## 7. Which lines are pinned, and do they match what is installed?

We split each line into the package name and the version rule, then compare with what is installed. An unpinned line (no version) is flagged, because it can install a different version next month."""),
    ("code", """import re
import importlib.metadata as meta

for line in req.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    name = re.split(r"[=<>~!]", line)[0].strip()
    rule = line[len(name):] or "(no version - UNPINNED)"
    try:
        installed = meta.version(name)
    except meta.PackageNotFoundError:
        installed = "not installed"
    exact = rule.startswith("==")
    match = exact and rule[2:] == installed
    note = "matches" if match else ("differs" if exact else "")
    print(f"{name:<14} wants {rule:<24} installed {installed:<12} {note}")"""),
    ("md", """## 8. `pip freeze` style output

`pip freeze` prints every installed package as `name==version`. Below we produce the first few lines the same way using `importlib.metadata`, so the notebook does not modify anything. In a terminal you would run `python -m pip freeze > requirements.txt`."""),
    ("code", """dists = sorted({(d.metadata["Name"], d.version) for d in meta.distributions() if d.metadata["Name"]},
               key=lambda pair: pair[0].lower())
for name, version in dists[:8]:
    print(f"{name}=={version}")
print("...", len(dists), "packages in total")"""),
    ("md", """## 9. Clean up"""),
    ("code", """for f in [sample, req]:
    f.unlink(missing_ok=True)
print("Removed practice files.")"""),
    ("md", """## Summary

- Colab: choose a **T4 GPU** runtime for deep learning; check with `torch.cuda.is_available()` or `!nvidia-smi`.
- The Colab disk is temporary: mount **Drive** or download your results.
- Upload with the Files panel or `files.upload()`; store keys in the **Secrets** panel.
- `requirements.txt` with `==` pins versions; `pip freeze > requirements.txt` records your environment; `pip install -r requirements.txt` rebuilds it."""),
]


def build_notebooks():
    notebook(NB1, NB / "01-environment-check.ipynb")
    notebook(NB2, NB / "02-env-files-safely.ipynb")
    notebook(NB3, NB / "03-colab-and-requirements.ipynb")


# ---------------------------------------------------------------------------
# 3. Slides
# ---------------------------------------------------------------------------
def build_slides():
    deck = {
        "title": "Module 00 - Setting up your AI toolkit",
        "subtitle": "Python to Pro AI Engineer curriculum",
        "slides": [
            {"title": "Why setup matters",
             "bullets": ["Every later module assumes this toolkit works",
                         "Most beginner 'code' problems are really setup problems",
                         "Today: Python, terminal, VS Code, notebooks, Colab, Git, venv, pip, API keys",
                         "Goal: a clean project that runs on any machine and leaks no secrets"],
             "notes": "Open by telling students that the first week of any engineering job is setup. Today we build the kitchen before we cook. If something breaks today, that is normal and is exactly what this session is for. By the end, everyone will run one script that reports their setup is ready."},
            {"title": "The kitchen analogy",
             "bullets": ["Python = the cook's skills (the language)",
                         "VS Code = the countertop (where you write)",
                         "Notebook = a recipe card you cook from step by step",
                         "Colab = a borrowed restaurant kitchen with big ovens (GPUs)",
                         "Git = photo album of every version; GitHub = shared cloud album",
                         "venv = a spice rack per recipe; pip = the spice shop"],
             "notes": "Read each line and pause. Ask students which item they think they will use most. Keep coming back to this analogy all session: when someone is confused about venvs, say 'separate spice rack'."},
            {"title": "Installing Python",
             "bullets": ["Use Python 3.11 - 3.13 from python.org",
                         "Windows: tick 'Add python.exe to PATH' on the first screen",
                         "macOS: run 'Install Certificates.command' after installing",
                         "Linux: sudo apt install python3 python3-venv python3-pip",
                         "Check: python --version (python3 on macOS/Linux)"],
             "code": "PS> python --version\nPython 3.12.4\n\n$ python3 --version\nPython 3.12.4",
             "notes": "The single most common Windows failure is forgetting the PATH checkbox. If 'python' opens the Microsoft Store, switch off App execution aliases in Settings. On Mac, remind them the command is python3 until they activate a virtual environment."},
            {"title": "The terminal",
             "bullets": ["A text window for typing commands to the computer",
                         "pwd = where am I?  ls = what is here?  cd = move",
                         "mkdir = make folder;  Ctrl+C = stop;  Tab = autocomplete",
                         "Up arrow repeats earlier commands",
                         "Avoid spaces in folder names"],
             "code": "cd ~\nmkdir ai-course\ncd ai-course\npwd\npython --version",
             "notes": "Do this live. Have every student type the five commands on the right. Explain that the terminal always stands inside one folder, the working directory. Many errors like 'file not found' are because they are standing in the wrong folder."},
            {"title": "VS Code + extensions",
             "bullets": ["Install from code.visualstudio.com",
                         "Extensions view (Ctrl+Shift+X): install Python and Jupyter by Microsoft",
                         "Command Palette (Ctrl+Shift+P) finds any command",
                         "Python: Select Interpreter chooses which Python runs",
                         "Ctrl+` opens the built-in terminal"],
             "notes": "Show the Activity Bar on the left: Explorer, Search, Source Control, Run, Extensions. Install the two extensions live. Then open the ai-course folder, create hello.py and click the play button in the top right."},
            {"title": "What is a .ipynb notebook?",
             "bullets": ["Cells: Markdown (notes) and code (runs)",
                         "Outputs are saved inside the file",
                         "The file itself is JSON text",
                         "Kernel remembers RUN order, not page order",
                         "Confused? Restart kernel and run all"],
             "code": "{\n  \"cells\": [\n    {\"cell_type\": \"code\",\n     \"source\": [\"print(2+2)\"],\n     \"outputs\": [...]}\n  ],\n  \"nbformat\": 4\n}",
             "notes": "Open a notebook in a plain text editor to prove it is JSON. Stress the security point: if you print an API key, it is saved in the file and will be pushed to GitHub. Then demo the run-order trap from notebook 1, section 8."},
            {"title": "Google Colab",
             "bullets": ["Free notebooks on Google's computers, in the browser",
                         "Runtime -> Change runtime type -> T4 GPU",
                         "Disk is wiped when the runtime disconnects",
                         "Mount Drive to keep files; Files panel to upload",
                         "Key icon = Secrets panel for API keys"],
             "code": "from google.colab import drive\ndrive.mount('/content/drive')\n\nfrom google.colab import userdata\nkey = userdata.get('OPENAI_API_KEY')",
             "notes": "Analogy: a borrowed restaurant kitchen that is cleaned the moment you leave. Show the Connect button, the RAM/Disk graph, changing to a T4 GPU, and the key icon. Free-tier limits change; tell students to check the official FAQ rather than trusting numbers they read online."},
            {"title": "Colab vs Jupyter vs VS Code",
             "bullets": ["Need a GPU or no install? Colab",
                         "Exploring data on your own machine? Jupyter",
                         "Building an app, many files, Git? VS Code"],
             "image": str(IMG / "tool-decision.png"),
             "notes": "Walk the flowchart from the top. Give three examples and let students choose: training an image model (Colab), exploring a sales CSV (Jupyter), building a chatbot API (VS Code). Point out VS Code also opens notebooks, so many engineers use it for everything."},
            {"title": "Git and GitHub",
             "bullets": ["Git: snapshots of your project on your computer",
                         "GitHub: website that hosts those snapshots",
                         "add -> staging; commit -> history; push -> GitHub",
                         "pull brings teammates' work down"],
             "image": str(IMG / "git-workflow.png"),
             "notes": "Analogy: essay-final, essay-final-2, essay-REALLY-final. Git replaces that with one folder and a labelled history. Configure user.name and user.email live. Students must use the same email as their GitHub account."},
            {"title": "The daily Git loop",
             "bullets": ["git pull before you start",
                         "git status: read it every time",
                         "git add, git commit -m \"message\", git push",
                         "Messages finish: 'This commit will...'"],
             "code": "git status\ngit add hello.py\ngit commit -m \"Add hello script\"\ngit push\ngit log --oneline",
             "notes": "Have students make a repo on GitHub, clone it, add hello.py and push. Read git status out loud together: red means changed but not staged, green means staged. If push asks for a password on Linux, they need a personal access token or gh auth login."},
            {"title": "Branches and pull requests",
             "bullets": ["Branch = a safe copy to experiment on",
                         "git switch -c feature, commit, push",
                         "On GitHub: Compare & pull request",
                         "Review in 'Files changed', then Merge"],
             "image": str(IMG / "branch-pr.png"),
             "notes": "Analogy: photocopy a chapter, scribble on the copy, and only replace the real chapter once an editor approves. Pair students: each opens a PR on a partner's repo and the partner reviews and merges it."},
            {"title": "Virtual environments",
             "bullets": ["One private package folder per project",
                         "Create: python -m venv .venv",
                         "Activate: source .venv/bin/activate (mac/Linux)",
                         "Activate: .venv\\Scripts\\Activate.ps1 (Windows)",
                         "Prompt shows (.venv); leave with deactivate"],
             "image": str(IMG / "venv.png"),
             "notes": "Analogy: a separate spice rack per recipe, so changing one recipe never spoils another. On Windows PowerShell, if activation is blocked, run Set-ExecutionPolicy RemoteSigned -Scope CurrentUser once. Never commit .venv."},
            {"title": "pip and requirements.txt",
             "bullets": ["python -m pip install pandas",
                         "Pin versions with ==  (e.g. pandas==2.2.3)",
                         "pip freeze > requirements.txt records them",
                         "pip install -r requirements.txt rebuilds them"],
             "code": "numpy==2.1.3\npandas==2.2.3\npython-dotenv==1.2.1\nrequests>=2.31,<3",
             "notes": "Explain pinning as writing the exact brand and size on a shopping list, so whoever shops buys the same thing. Using python -m pip guarantees pip installs into the Python you expect."},
            {"title": "API keys and environment variables",
             "bullets": ["API key = secret password for a paid service",
                         "Anyone with your key can spend your money",
                         "Keep it in an environment variable, not in code",
                         "os.getenv('NAME') returns None if missing"],
             "code": "import os\nkey = os.getenv('OPENAI_API_KEY')\nprint('Key set:', key is not None)",
             "notes": "Analogy: the recipe book is public, but the secret ingredient is in a locked drawer in your own kitchen. Show that printing 'key is not None' tells you what you need without revealing the key."},
            {"title": ".env + python-dotenv",
             "bullets": [".env holds NAME=value lines, stays on your machine",
                         "load_dotenv() copies them into the environment",
                         ".env is listed in .gitignore",
                         ".env.example (placeholders) IS committed"],
             "image": str(IMG / "secrets-flow.png"),
             "notes": "Demo: copy .env.example to .env, run code/dotenv_demo.py before and after adding a fake value. Then run git status and show .env does not appear because of .gitignore."},
            {"title": "Never commit keys",
             "bullets": ["Bots scan GitHub for keys within minutes",
                         "Check git status before every commit",
                         "Never paste keys in code or print them in notebooks",
                         "Leaked? Revoke the key FIRST, then clean up",
                         "Deleting the file later does not remove it from history"],
             "notes": "Tell a short story: a student pushes a key on Friday night and wakes up to a big bill. The fix is always revoke first. Ask: why is deleting the file in a new commit not enough? Answer: the old commit still contains it."},
            {"title": "Common mistakes",
             "bullets": ["'python' not found -> PATH box not ticked",
                         "Package installed but 'No module named' -> wrong interpreter/kernel",
                         "Forgot to activate venv -> installed into the wrong place",
                         "Colab files vanished -> runtime reset; use Drive",
                         ".env committed -> missing .gitignore; revoke the key"],
             "notes": "Each of these comes with a fix in the troubleshooting sheet in excel/setup-checklist.xlsx. Encourage students to read the last line of every error message first and search the troubleshooting table."},
            {"title": "Recap and exercise",
             "bullets": ["Run: python code/check_env.py",
                         "Every line should be OK or explained",
                         "Exercise: make a repo with venv, requirements.txt, .gitignore, .env.example",
                         "Push it to GitHub and open one pull request"],
             "notes": "Finish by having everyone run check_env.py and read their report. Then set the exercise from exercises.md (numbers 6 to 9). Students who finish early do exercise 12, a merge conflict on purpose."},
        ],
    }
    slides(deck, HERE / "slides" / "00-setup.pptx")


# ---------------------------------------------------------------------------
# 4. Excel: checklist + troubleshooting + decision guide + commands
# ---------------------------------------------------------------------------
def build_excel():
    checklist = [["#", "Area", "Step", "How to check", "Expected result", "Done? (Y/N)", "Notes"]]
    steps = [
        ("Python", "Install Python 3.11-3.13", "python --version (python3 on macOS/Linux)", "Python 3.1x.x"),
        ("Python", "Python is on PATH (Windows)", "Open a NEW PowerShell, type python --version", "Version prints, Store does not open"),
        ("Terminal", "Can open a terminal", "PowerShell / Terminal / Ctrl+Alt+T", "A prompt waiting for input"),
        ("Terminal", "Made a course folder", "cd ~ ; mkdir ai-course ; cd ai-course ; pwd", "Path ends in ai-course"),
        ("VS Code", "Install VS Code", "Open VS Code from the Start menu / Applications", "VS Code window opens"),
        ("VS Code", "Python extension installed", "Extensions view (Ctrl+Shift+X), search Python", "Python by Microsoft shows 'Installed'"),
        ("VS Code", "Jupyter extension installed", "Extensions view, search Jupyter", "Jupyter by Microsoft shows 'Installed'"),
        ("VS Code", "Run hello.py", "Click the play button top-right of the editor", "Hello text in the terminal"),
        ("Notebooks", "Jupyter installed", "python -m pip install jupyterlab notebook ; jupyter lab", "Browser opens at localhost:8888"),
        ("Notebooks", "Notebook runs in VS Code", "Open a .ipynb, Select Kernel, Shift+Enter", "Output under the cell"),
        ("Colab", "Opened Colab", "colab.research.google.com -> New notebook", "Notebook in Drive/Colab Notebooks"),
        ("Colab", "Switched to T4 GPU", "Runtime -> Change runtime type -> T4 GPU ; !nvidia-smi", "Tesla T4 listed"),
        ("Colab", "Mounted Drive", "drive.mount('/content/drive')", "/content/drive/MyDrive exists"),
        ("Colab", "Added a secret", "Key icon -> Add new secret -> Notebook access on", "userdata.get returns a value"),
        ("Git", "Git installed", "git --version", "git version 2.x"),
        ("Git", "Name and email set", "git config --global --list", "user.name and user.email shown"),
        ("GitHub", "Account created and signed in", "gh auth status (or push once)", "Logged in to github.com"),
        ("GitHub", "Cloned a repo", "git clone <url> ; cd <repo>", "Folder with a .git inside"),
        ("GitHub", "First push", "git add . ; git commit -m 'msg' ; git push", "Commit visible on GitHub"),
        ("GitHub", "Opened a pull request", "git switch -c test ; push ; Compare & pull request", "PR page on GitHub"),
        ("venv", "Created .venv", "python -m venv .venv", ".venv folder exists"),
        ("venv", "Activated .venv", "source .venv/bin/activate or .venv\\Scripts\\Activate.ps1", "Prompt starts with (.venv)"),
        ("venv", "VS Code uses .venv", "Python: Select Interpreter -> .venv", "Status bar shows .venv"),
        ("pip", "Installed packages", "python -m pip install python-dotenv", "Successfully installed"),
        ("pip", "Wrote requirements.txt", "python -m pip freeze > requirements.txt", "File lists name==version"),
        ("Secrets", ".gitignore has .env and .venv/", "Open .gitignore", "Both lines present"),
        ("Secrets", "Created .env from .env.example", "cp .env.example .env (Copy-Item on Windows)", ".env exists, not shown by git status"),
        ("Secrets", "Ran the checker", "python code/check_env.py", "Keys reported as set / NOT SET, never shown"),
    ]
    for i, (area, step, how, exp) in enumerate(steps, start=1):
        checklist.append([i, area, step, how, exp, "", ""])
    n = len(steps)
    checklist.append(["", "", "", "", "Steps done:", f'=COUNTIF(F2:F{n+1},"Y")&" of {n}"', ""])

    trouble = [["Error message (what you see)", "Where", "Likely cause", "Fix"],
        ["'python' is not recognized as an internal or external command", "Windows terminal", "Python not on PATH", "Re-run installer, tick 'Add python.exe to PATH' (Modify), then open a NEW terminal. Or use 'py'."],
        ["Typing python opens the Microsoft Store", "Windows", "App execution alias shortcut", "Settings -> Apps -> Advanced app settings -> App execution aliases: switch off python.exe and python3.exe"],
        ["command not found: python", "macOS / Linux", "Command is python3 outside a venv", "Use python3, or activate your venv"],
        ["running scripts is disabled on this system", "PowerShell, activating venv", "Execution policy blocks scripts", "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"],
        ["The virtual environment was not created successfully because ensurepip is not available", "Ubuntu/Debian", "python3-venv package missing", "sudo apt install python3-venv (or python3.X-venv)"],
        ["ModuleNotFoundError: No module named 'dotenv'", "Python / notebook", "Package not installed in THIS Python, or wrong kernel", "Activate venv, python -m pip install python-dotenv; in VS Code pick the .venv interpreter/kernel"],
        ["pip: command not found / 'pip' is not recognized", "Terminal", "pip not on PATH", "Use python -m pip ... instead"],
        ["error: externally-managed-environment", "pip on recent Linux/macOS Homebrew", "System Python protected from pip", "Create and activate a venv, then install there"],
        ["SSL: CERTIFICATE_VERIFY_FAILED", "macOS Python downloads", "Certificates not installed", "Run 'Install Certificates.command' in the Python folder in Applications"],
        ["Could not find a version that satisfies the requirement X==1.2.3", "pip install -r", "Version does not exist for your Python version", "Check the package page on pypi.org; adjust the pin or Python version"],
        ["fatal: not a git repository (or any of the parent directories)", "Git", "You are not inside a repo folder", "cd into the repo, or run git init"],
        ["Author identity unknown / Please tell me who you are", "git commit", "user.name/email not set", "git config --global user.name ... and user.email ..."],
        ["remote: Support for password authentication was removed", "git push", "GitHub rejects account passwords", "Use gh auth login, Git Credential Manager, or a personal access token"],
        ["! [rejected] main -> main (fetch first)", "git push", "GitHub has commits you do not have", "git pull, fix any conflicts, then git push"],
        ["CONFLICT (content): Merge conflict in file.py", "git pull / merge", "Same lines changed in two places", "Open file, choose the right lines, remove <<<< ==== >>>> markers, git add, git commit"],
        ["error: src refspec main does not match any", "first git push", "No commits yet, or branch is named master", "Make a commit first; check branch with git branch"],
        ["Push blocked: secret detected (push protection)", "git push to GitHub", "A key is in your commit", "Revoke the key, remove it from the commit (amend/rewrite), use .env"],
        [".env shows up in git status", "Git", ".env not in .gitignore", "Add .env to .gitignore BEFORE committing; if committed already, revoke the key"],
        ["Kernel not found / Select a kernel", "VS Code notebook", "No Python chosen for the notebook", "Click Select Kernel (top right) -> Python Environments -> .venv; install ipykernel if asked"],
        ["NameError: name 'x' is not defined (in a notebook)", "Notebook", "Cell defining x was not run, or kernel restarted", "Run cells from the top; Restart kernel and Run All"],
        ["Files disappeared in Colab", "Colab", "Runtime disconnected; disk wiped", "Save to /content/drive/MyDrive after drive.mount, or download results"],
        ["Cannot connect to GPU backend / no GPU available", "Colab", "Free GPUs busy or quota used", "Try later, use CPU, or a paid tier"],
        ["torch.cuda.is_available() is False in Colab", "Colab", "Runtime still set to CPU", "Runtime -> Change runtime type -> T4 GPU -> Save, then re-run"],
        ["SecretNotFoundError / NotebookAccessError", "Colab userdata.get", "Secret missing or Notebook access off", "Key icon -> add the secret -> switch on Notebook access"],
        ["os.getenv returns None even though .env exists", "Python", "load_dotenv not called, or .env in another folder", "Call load_dotenv() first; check the file is named exactly .env; pass the path"],
        ["401 Unauthorized / invalid API key", "API call", "Key wrong, revoked, or placeholder text", "Create a new key, paste with no spaces/quotes, check check_env.py says 'set'"],
    ]

    decision = [["Situation", "Best tool", "Why"],
        ["First lesson, nothing installed", "Google Colab", "Zero install, works in any browser"],
        ["Training a neural network / fine-tuning", "Google Colab (T4 GPU)", "Free GPU; most laptops have none"],
        ["Student laptop is old or slow", "Google Colab", "Google's computers do the work"],
        ["Exploring a CSV, trying ideas", "Jupyter (local) or VS Code notebook", "Fast feedback, files stay on disk"],
        ["Private or company data", "Jupyter / VS Code (local)", "Data never leaves your computer"],
        ["Working offline", "Jupyter / VS Code", "Colab needs internet"],
        ["Building an app, API or agent", "VS Code", "Many .py files, terminal, debugger"],
        ["Team project with Git and pull requests", "VS Code", "Source Control panel built in"],
        ["Code that others will run or deploy", "VS Code (.py files)", "Scripts run top to bottom, testable"],
        ["Teaching step by step with explanations", "Notebook (any of the three)", "Text, code and results together"],
    ]

    commands = [["Task", "Windows (PowerShell)", "macOS / Linux"],
        ["Where am I?", "pwd", "pwd"],
        ["List files", "ls  (or dir)", "ls"],
        ["Change folder", "cd folder", "cd folder"],
        ["Up one folder", "cd ..", "cd .."],
        ["Make folder", "mkdir name", "mkdir name"],
        ["Python version", "python --version  (or py --version)", "python3 --version"],
        ["Create venv", "python -m venv .venv", "python3 -m venv .venv"],
        ["Activate venv", ".venv\\Scripts\\Activate.ps1", "source .venv/bin/activate"],
        ["Leave venv", "deactivate", "deactivate"],
        ["Install package", "python -m pip install pkg", "python -m pip install pkg"],
        ["Save requirements", "python -m pip freeze > requirements.txt", "python -m pip freeze > requirements.txt"],
        ["Install requirements", "python -m pip install -r requirements.txt", "python -m pip install -r requirements.txt"],
        ["Set env var (this window)", "$env:NAME = \"value\"", "export NAME=\"value\""],
        ["Copy .env.example", "Copy-Item .env.example .env", "cp .env.example .env"],
        ["Clone repo", "git clone URL", "git clone URL"],
        ["Daily Git loop", "git status ; git add . ; git commit -m \"msg\" ; git push", "same"],
        ["New branch", "git switch -c name", "git switch -c name"],
        ["Start Jupyter", "jupyter lab", "jupyter lab"],
    ]
    workbook({"Setup checklist": checklist, "Troubleshooting": trouble,
              "Which tool": decision, "Commands": commands},
             HERE / "excel" / "setup-checklist.xlsx",
             col_widths={"Setup checklist": [5, 12, 32, 48, 36, 12, 25],
                         "Troubleshooting": [55, 26, 38, 70],
                         "Which tool": [40, 34, 44],
                         "Commands": [26, 50, 50]})


def build_pdf():
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / "00-setup-handout.pdf",
                      title="Module 00 - Setting up your AI toolkit")


if __name__ == "__main__":
    build_images()
    build_notebooks()
    build_slides()
    build_excel()
    build_pdf()
    print("00-setup built.")
