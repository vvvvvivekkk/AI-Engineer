# Module 00 — Exercises

Work through these in order. They go from easy (1–4) to medium (5–9) to hard (10–12). Worked solutions are in [`solutions/solutions.md`](solutions/solutions.md). Try each one for at least 15 minutes before looking.

---

## Easy

### 1. Version detective
Open a terminal. Find and write down: (a) your Python version, (b) your pip version, (c) your Git version. Then answer: which command did you use for Python — `python`, `python3` or `py`? Why that one on your system?

### 2. Terminal treasure hunt
Using only the terminal (no mouse, no file explorer):
1. Go to your home folder.
2. Create a folder `ai-course/week1/practice`. (Hint: `mkdir` can make nested folders — on macOS/Linux with `mkdir -p`, in PowerShell `mkdir` does it by default.)
3. Move into `practice` and print the full path.
4. Go back up two levels with one command.
5. List the contents to confirm `week1` exists.

Write down every command you typed.

### 3. Notebook anatomy
Open `notebooks/01-environment-check.ipynb` in a plain text editor (Notepad, TextEdit, or VS Code via right-click → **Open With…** → **Text Editor**). Find: (a) the key that holds the list of cells, (b) one `"cell_type": "markdown"` cell, (c) one code cell's `"outputs"`. Then run `python code/inspect_notebook.py notebooks/01-environment-check.ipynb` and compare.

### 4. Pick the tool
For each task, say whether you would use Colab, local Jupyter, or VS Code, and give one reason:
1. Fine-tuning a small language model.
2. Looking through a CSV of your company's customer data.
3. Building a chatbot web API that a team will maintain.
4. Teaching a first Python lesson in a lab where nothing can be installed.
5. Writing a script that runs every night on a server.

---

## Medium

### 5. Colab GPU round trip
In Google Colab:
1. Create a new notebook named `gpu-check.ipynb`.
2. Switch the runtime to a T4 GPU.
3. Run `!nvidia-smi` and a cell that prints `torch.cuda.is_available()`.
4. Write a file `hello.txt` to `/content/`, then mount Drive and copy it to `/content/drive/MyDrive/`.
5. Disconnect the runtime (**Runtime → Disconnect and delete runtime**), reconnect, and check which copy of `hello.txt` still exists. Explain why.

### 6. Your first repo, end to end
1. Create a new empty repository on GitHub called `ai-course-practice`.
2. Clone it to your computer.
3. Add a `hello.py` that prints your name.
4. Commit with a good message and push.
5. Confirm the file shows on GitHub. Paste the output of `git log --oneline`.

### 7. A clean project skeleton
In a new folder `my-first-ai-project`:
1. Create a virtual environment named `.venv` and activate it.
2. Install `python-dotenv` and `requests`.
3. Write a hand-written, pinned `requirements.txt` with only those two packages (use `pip show` to find the versions).
4. Create a `.gitignore` that ignores `.env`, `.venv/` and `__pycache__/`.
5. Copy this module's `.env.example` into the project.
6. Deactivate, delete `.venv`, recreate it and reinstall from `requirements.txt` to prove it works.

### 8. Load a key safely
In the project from exercise 7, create a `.env` containing `MY_SERVICE_KEY=practice-value-123`. Write `app.py` that:
- loads `.env` with `python-dotenv`,
- prints `Key loaded: True` or `Key loaded: False`,
- prints the key's length but **not** the key,
- prints a friendly message if the key is missing.

Then run `git status` and confirm `.env` is not listed.

### 9. Branch and pull request
In your `ai-course-practice` repo:
1. Create a branch `add-readme`.
2. Add a `README.md` with a one-paragraph description.
3. Push the branch and open a pull request on GitHub.
4. Merge it on GitHub, then update your local `main`.
5. Delete the branch locally (`git branch -d add-readme`).

---

## Hard

### 10. Extend `check_env.py`
Copy `code/check_env.py` to `check_env_plus.py` and add:
1. A check that warns if a file named `.env` exists in the current folder but `.gitignore` in the same folder does not contain `.env`.
2. A new key name `GROQ_API_KEY` in the list.
3. A `--json` option that prints the results as JSON instead of text (still never including key values).

### 11. Diagnose the broken setup
A student sends you this. Explain what went wrong in each case and the exact fix:
1. `pip install pandas` succeeded, but in VS Code's notebook `import pandas` gives `ModuleNotFoundError`.
2. On Windows, `.venv\Scripts\Activate.ps1` prints "running scripts is disabled on this system".
3. `git push` says `! [rejected] main -> main (fetch first)`.
4. They committed `.env` with a real OpenAI key yesterday, then deleted the file today and pushed again. They think they are safe.
5. In Colab, the model they trained an hour ago is gone after lunch.

### 12. Make (and fix) a merge conflict on purpose
In your practice repo:
1. On `main`, create `plan.txt` with the line `Week 1: setup`. Commit and push.
2. Create branch `alice` and change the line to `Week 1: setup and Git`. Commit.
3. Switch back to `main` and change the same line to `Week 1: install Python`. Commit.
4. Run `git merge alice`. Read the conflict markers, resolve the file to `Week 1: install Python, setup and Git`, and complete the merge.
5. Write three sentences explaining what each marker (`<<<<<<<`, `=======`, `>>>>>>>`) means.
