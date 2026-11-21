# Module 00 — Setup: tools, environment and accounts (week 1)

Get a working AI-engineering toolkit on your own computer and in the cloud, and learn to keep secret API keys safe. Every later module assumes you finished this one.

## Goals

After this module you can:

1. Install Python and check its version on Windows, macOS or Linux.
2. Move around in a **terminal** (a text window for typing commands) with `pwd`, `ls`, `cd` and `mkdir`.
3. Install VS Code with the Python and Jupyter extensions and run a `.py` file.
4. Explain what a `.ipynb` **notebook** is (a JSON file of cells and their outputs) and run one in Jupyter, VS Code and Google Colab.
5. Use Colab's runtimes (including the free T4 **GPU** — a chip that does many maths operations at once), mount Google Drive, upload files and use the Secrets panel.
6. Use **Git** and **GitHub**: configure, clone, `status / add / commit / push`, branches, pull requests and `.gitignore`.
7. Create, activate and deactivate a **virtual environment** (a private folder of packages for one project) on each operating system.
8. Install packages with `pip` and pin them in `requirements.txt`.
9. Store API keys in environment variables and a `.env` file loaded with `python-dotenv`, and never commit them.
10. Choose between Colab, Jupyter and VS Code for a given task.

## Prerequisites

None. A computer (Windows 10/11, macOS or Linux) with internet access and permission to install software, plus a Google account (for Colab). If you cannot install software, you can still do sections 5–7 of the lesson in Colab.

## Time estimate

- Reading `concepts.md`: 1.5–2 hours
- Doing all installs and the three notebooks: 2–3 hours (installs vary a lot by machine)
- Exercises: 2 hours
- Teaching session: 2 hours (see `trainer-notes.md`)

## Which tool for this module, and why

**All three, on purpose.** This module is where you install and try each tool. Start the notebooks in **Google Colab** (zero install) on day one, then open the same notebooks in **VS Code** once Python is installed. Run `code/check_env.py` from the **VS Code terminal**, inside your virtual environment.

## File map

| Path | What it is |
|---|---|
| `concepts.md` | The main lesson. Read this first. |
| `.env.example` | Safe template for API keys. Copy it to `.env` and fill in your own values. |
| `images/` | Diagrams used in the lesson (PNG) and their editable Mermaid sources (`.mmd`). |
| `notebooks/01-environment-check.ipynb` | Check Python, venv, packages; look inside a notebook's JSON; the run-order trap. |
| `notebooks/02-env-files-safely.ipynb` | Environment variables, `.env`, `load_dotenv`, `override`, safe display, the offline fallback pattern. |
| `notebooks/03-colab-and-requirements.ipynb` | Colab GPU, Drive, uploads, Secrets; reading and checking `requirements.txt`. |
| `code/check_env.py` | Reports Python version, venv, key packages and whether API keys are set (never prints them). |
| `code/dotenv_demo.py` | The safe key-loading pattern with an offline stand-in. |
| `code/inspect_notebook.py` | Prints the cells of any `.ipynb` to show it is JSON. |
| `slides/00-setup.pptx` | 18-slide teaching deck with speaker notes. |
| `pdf/00-setup-handout.pdf` | The lesson as a printable handout. |
| `excel/setup-checklist.xlsx` | Setup checklist (with progress formula), troubleshooting table (error → cause → fix), tool decision guide, command cheat sheet. |
| `exercises.md` | 12 exercises, easy to hard. |
| `solutions/solutions.md` | Worked solutions for every exercise. |
| `trainer-notes.md` | How to teach the session: timing table, common mistakes, check questions. |
| `resources.md` | The best external links, each with a reason. |
| `build.py` | Regenerates images, notebooks, slides, PDF and Excel. Run `python 00-setup/build.py` from the repo root. |

## Quick start

```bash
cd AI-Engineer/00-setup
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install python-dotenv jupyterlab
python code/check_env.py
```
