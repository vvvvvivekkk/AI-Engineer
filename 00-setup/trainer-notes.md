# Module 00 — Trainer notes

Read `concepts.md` fully and do every install yourself on at least one operating system before teaching. Setup sessions go wrong in boring, predictable ways; the troubleshooting sheet in `excel/setup-checklist.xlsx` lists the ones you will meet.

**Before the session**
- Send students the install list two days early: Python (python.org), VS Code, Git, a Google account and a GitHub account. Ask them to try installing at home and to bring the exact error message if something fails.
- Print or share the **Setup checklist** sheet. Students tick off steps (type `Y` in column F); the bottom row counts progress.
- Have Colab ready as a fallback for anyone whose laptop cannot install software. Nobody should sit idle.
- Test the Wi-Fi with several devices. Installs are big downloads.

**Jargon to define the first time you say it:** terminal, PATH, interpreter, package, virtual environment, kernel, runtime, GPU, repository, commit, branch, pull request, API key, environment variable.

---

## 1. What students should be able to do after the session

1. Open a terminal and use `pwd`, `ls`, `cd`, `mkdir`, Tab completion and Ctrl + C.
2. Show their Python version and run a `.py` file from VS Code and from the terminal.
3. Run a notebook in VS Code and in Colab, and explain that a `.ipynb` is JSON that stores outputs.
4. Switch a Colab runtime to a T4 GPU, mount Drive and add a secret.
5. Create, activate and deactivate a `.venv`; install packages with `python -m pip`; write a pinned `requirements.txt`.
6. Clone a repo, commit, push, create a branch and open a pull request.
7. Store a key in `.env`, load it with `python-dotenv`, and explain why `.env` is in `.gitignore`.
8. Choose Colab, Jupyter or VS Code for a task and justify it.

## 2. Teaching sequence (2-hour session)

| Time | Segment | What you do | What students do |
|---|---|---|---|
| 0:00–0:10 | Hook + kitchen analogy | Slides 1–2. "The first week of every engineering job is setup." Show the finished state: `check_env.py` printing all OK. | Listen; open the setup checklist. |
| 0:10–0:25 | Python + terminal | Slides 3–4. Live: `python --version`, then the five-command terminal session. Walk the room for PATH problems. | Install/check Python; make `ai-course` folder. |
| 0:25–0:40 | VS Code | Slide 5. Install the two extensions live, open the folder, create and run `hello.py`. Show Command Palette and Select Interpreter. | Same steps, tick checklist. |
| 0:40–0:55 | Notebooks + Colab | Slides 6–7. Open a `.ipynb` as text to prove it is JSON. Click the Colab badge on notebook 01, switch to T4, run all. Demo the run-order trap (section 8). Show Secrets panel. | Run notebook 01 in Colab; try the run-order experiment. |
| 0:55–1:00 | Which tool? | Slide 8 + decision flowchart. Quick-fire: you name a task, students shout the tool. | Answer exercise 4 aloud. |
| 1:00–1:05 | Break | — | Catch-up time for slow installs. |
| 1:05–1:30 | Git + GitHub | Slides 9–11. Configure name/email. Create a GitHub repo, clone, add, commit, push. Then branch → PR → merge with a volunteer. | Exercise 6, then pair up for exercise 9. |
| 1:30–1:45 | venv + pip | Slides 12–13. Create `.venv` on Windows and Mac side by side (or show the table). Install `python-dotenv`, freeze to `requirements.txt`. | Exercise 7 steps 1–4. |
| 1:45–1:55 | Keys + `.env` | Slides 14–16. Copy `.env.example` to `.env`, run `dotenv_demo.py` before/after, run `git status` to show `.env` is ignored. Tell the leaked-key story. | Exercise 8. |
| 1:55–2:00 | Recap + homework | Slides 17–18. Everyone runs `python code/check_env.py`. Assign exercises 5, 10–12. | Run the checker; read their own report. |

If installs ate the time, cut Colab Drive/uploads (students can do notebook 03 at home) — never cut `.gitignore` and keys.

## 3. Common student mistakes and how to fix them

| Mistake | What it looks like | Fix |
|---|---|---|
| Did not tick **Add python.exe to PATH** (Windows) | `'python' is not recognized…` | Re-run the installer → **Modify** → tick "Add Python to environment variables", or use `py`. Always open a **new** terminal afterwards. |
| Microsoft Store opens when typing `python` | Store window appears | Settings → Apps → Advanced app settings → App execution aliases → switch off both python entries. |
| Typing commands in the wrong folder | `No such file or directory`, `not a git repository` | Teach `pwd` as the first debugging step. `cd` into the project. |
| Forgot to activate the venv | Packages "disappear"; prompt lacks `(.venv)` | Look for `(.venv)` at the start of the prompt before every `pip install`. Use `python -m pip`. |
| Wrong interpreter / kernel in VS Code | `ModuleNotFoundError` in VS Code but works in terminal | **Python: Select Interpreter** and **Select Kernel** → choose `.venv`. |
| PowerShell blocks activation | "running scripts is disabled" | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`. |
| Typing the `$` prompt symbol from tutorials | `$: command not found` | Explain that `$` / `>` only show the prompt. |
| Running cells out of order | Variables have "wrong" values; `NameError` | Restart kernel and run all. Make it a habit before saving. |
| Expecting Colab files to persist | "My files vanished" | Mount Drive, save there, or download. |
| Committing `.env` or `.venv` | `git status` lists them | Write `.gitignore` before the first commit. If a key was committed: revoke it first. |
| Using GitHub account password for `git push` | "Support for password authentication was removed" | `gh auth login`, Git Credential Manager, or a personal access token. |
| Pasting a key into a notebook cell "to test" | Key visible in the file / on GitHub | Delete the output, revoke the key, use Secrets or `.env`. Model the right habit yourself every time. |

## 4. Questions to check understanding (with answers)

1. **What is the difference between Git and GitHub?** Git is a program on your computer that records snapshots of files. GitHub is a website that stores Git repositories online and adds collaboration tools such as pull requests.
2. **Why does each project get its own virtual environment?** Different projects need different package versions. A venv keeps each project's packages separate, so upgrading one project cannot break another.
3. **You printed an API key in a notebook, then deleted the cell's code but not its output, and pushed. Is the key exposed?** Yes. Outputs are saved inside the `.ipynb` JSON. Revoke the key.
4. **What does `load_dotenv()` do?** It reads `NAME=value` lines from a `.env` file and puts them into the running program's environment variables, so `os.getenv("NAME")` can read them.
5. **Why commit `.env.example` but not `.env`?** `.env.example` shows which variable names are needed, with fake values. `.env` holds real secrets.
6. **When is Colab the wrong choice?** For private data that must not leave your machine, offline work, and multi-file apps or long-running services.
7. **What does `git add` do that `git commit` does not?** `add` moves changes into the staging area (choosing what goes in the next snapshot). `commit` saves the staged changes as a snapshot in history.
8. **What does `==` mean in `requirements.txt`, and why use it?** It pins an exact version, so everyone installs the same version and the project behaves the same everywhere.
9. **Your notebook shows `NameError` for a variable you can see defined above. Why?** The defining cell was not run in this kernel session (or the kernel restarted). Run all cells from the top.
10. **A key leaked. What is the first thing to do?** Revoke it on the provider's website and create a new one.

## 5. Adapting for faster or slower groups

**Slower groups / many install problems**
- Split into two sessions: (1) Python, terminal, VS Code, Colab; (2) Git, venv, pip, keys.
- Run everything in Colab first so the concepts land, then do local installs as guided homework with the troubleshooting sheet.
- Pair a student whose install worked with one whose did not.
- Skip branches and PRs in session one; teach only `clone → add → commit → push`.

**Faster groups**
- Introduce **uv** (`uv venv`, `uv pip install -r requirements.txt`) and compare speed.
- Have them set up SSH keys for GitHub instead of HTTPS.
- Exercise 10 (extend `check_env.py`) and exercise 12 (merge conflict) in class.
- Ask them to add a GitHub Actions workflow later in module 14; for now, have them read their repo's **Settings → Code security** page to see secret scanning and push protection.
