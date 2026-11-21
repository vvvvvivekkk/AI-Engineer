# Module 00 — Solutions

Worked answers for [`../exercises.md`](../exercises.md). Commands are shown for macOS/Linux first, then Windows PowerShell where they differ.

---

## 1. Version detective

```bash
python --version            # or python3 --version / py --version
python -m pip --version
git --version
```

- On **Windows**, `python` works if you ticked "Add python.exe to PATH"; `py` (the Python launcher) always works after a python.org install.
- On **macOS/Linux**, `python3` is the safe command, because `python` may not exist or may point to something else. Inside an activated virtual environment, `python` works everywhere.
- Using `python -m pip` instead of plain `pip` guarantees you see the pip that belongs to that Python.

## 2. Terminal treasure hunt

macOS / Linux:
```bash
cd ~
mkdir -p ai-course/week1/practice
cd ai-course/week1/practice
pwd
cd ../..
ls
```

Windows PowerShell:
```powershell
cd ~
mkdir ai-course\week1\practice
cd ai-course\week1\practice
pwd
cd ..\..
ls
```

`cd ../..` goes up two levels: `..` means "the parent folder", so `../..` is "the parent of the parent". After it you are in `ai-course`, and `ls` shows `week1`.

## 3. Notebook anatomy

(a) The list of cells is under the top-level key `"cells"`.
(b) A markdown cell looks like `{"cell_type": "markdown", "metadata": {}, "source": "# 00 · Notebook 1 ..."}`.
(c) A code cell has `"outputs": [ {"output_type": "stream", "name": "stdout", "text": "Hello from a notebook!\n"} ]` plus `"execution_count"`.

`inspect_notebook.py` prints the same information as a table: each cell's index, type, number of outputs and first line. The lesson: outputs live inside the file, so anything printed (including a secret) is saved and shared.

## 4. Pick the tool

1. **Colab** — fine-tuning needs a GPU; Colab gives a free T4.
2. **Local Jupyter (or VS Code notebook)** — private customer data should stay on your machine, and a notebook is ideal for exploring.
3. **VS Code** — a team app has many `.py` files, tests and Git branches.
4. **Colab** — nothing to install; only a browser and Google account.
5. **VS Code** — a script that runs unattended must be a `.py` file, version-controlled, run top to bottom.

## 5. Colab GPU round trip

```python
!nvidia-smi
import torch
print(torch.cuda.is_available())          # True on a T4 runtime

from pathlib import Path
Path("/content/hello.txt").write_text("hi")
from google.colab import drive
drive.mount("/content/drive")
import shutil
shutil.copy("/content/hello.txt", "/content/drive/MyDrive/hello.txt")
```

After **Disconnect and delete runtime** and reconnecting: `/content/hello.txt` is gone, and `/content/drive/MyDrive/hello.txt` is still there (after mounting again). The runtime is a temporary virtual machine whose disk is wiped; Drive is permanent storage in your Google account.

## 6. Your first repo, end to end

```bash
# On GitHub: + (top right) -> New repository -> name ai-course-practice -> Create repository
cd ~/ai-course
git clone https://github.com/YOUR-NAME/ai-course-practice.git
cd ai-course-practice
echo 'print("Hello, I am Asha")' > hello.py
git status                     # hello.py is red (untracked)
git add hello.py
git status                     # hello.py is green (staged)
git commit -m "Add hello script"
git push
git log --oneline              # e.g.  3f2a1bc (HEAD -> main, origin/main) Add hello script
```

If `git push` fails with "Author identity unknown", run the two `git config --global` commands from the lesson first. If it says password authentication was removed, run `gh auth login` or use a personal access token.

## 7. A clean project skeleton

```bash
mkdir my-first-ai-project && cd my-first-ai-project
python3 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\Activate.ps1
python -m pip install python-dotenv requests
python -m pip show python-dotenv requests | grep -E "Name|Version"
```

`requirements.txt` (your version numbers may differ — use what `pip show` printed):
```text
python-dotenv==1.2.1
requests==2.32.3
```

`.gitignore`:
```text
.env
.venv/
__pycache__/
```

```bash
cp ../AI-Engineer/00-setup/.env.example .     # Windows: Copy-Item ..\AI-Engineer\00-setup\.env.example .
deactivate
rm -rf .venv                                   # Windows: Remove-Item -Recurse -Force .venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -c "import dotenv, requests; print('ok')"
```

If the last line prints `ok`, the project is reproducible from `requirements.txt` alone.

## 8. Load a key safely

`.env`:
```text
MY_SERVICE_KEY=practice-value-123
```

`app.py` — see [`app.py`](app.py) in this folder. Output:
```text
Key loaded: True
Key length: 18
```

Remove the line from `.env` and run again: it prints `Key loaded: False` and the friendly message. `git status` does not list `.env` because `.gitignore` contains `.env`.

## 9. Branch and pull request

```bash
git switch -c add-readme
printf "# AI course practice\n\nMy practice repo for the AI Engineer course.\n" > README.md
git add README.md
git commit -m "Add README"
git push -u origin add-readme
```

On GitHub: click **Compare & pull request** → write a title → **Create pull request** → **Merge pull request** → **Confirm merge**.

```bash
git switch main
git pull                     # brings the merged README down
git branch -d add-readme     # safe delete: works because it is merged
```

## 10. Extend `check_env.py`

See [`check_env_plus.py`](check_env_plus.py). Key ideas:
- `gitignore_protects_env()` reads `.gitignore` and looks for a `.env` line.
- `GROQ_API_KEY` is added to `KEY_NAMES`.
- `--json` uses `argparse` with `action="store_true"`, then `json.dumps(results, indent=2)`. The results dictionary only ever holds statuses like `"set"` or `"NOT SET"`, so the JSON cannot leak a key.

## 11. Diagnose the broken setup

1. **pip installed into a different Python than the notebook's kernel.** Fix: in VS Code click **Select Kernel** and choose the environment where pandas was installed (or activate the venv the kernel uses and run `python -m pip install pandas` there). In a notebook, `%pip install pandas` installs into the running kernel.
2. **PowerShell's execution policy blocks scripts.** Fix: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`, then activate again. (Or use Command Prompt with `.venv\Scripts\activate.bat`.)
3. **GitHub has commits they do not have locally.** Fix: `git pull`, resolve any conflicts, then `git push`.
4. **They are not safe.** The key is still in the earlier commit in the history, and bots may already have copied it. Fix: revoke the key on the OpenAI dashboard immediately, create a new one, put it only in `.env`, add `.env` to `.gitignore`, and check usage for unexpected charges. Optionally rewrite history with `git filter-repo`, but revoking is the essential step.
5. **The Colab runtime was recycled and its disk wiped.** Fix: save models and results to mounted Google Drive (`/content/drive/MyDrive/...`) or download them before leaving.

## 12. Merge conflict on purpose

```bash
echo "Week 1: setup" > plan.txt
git add plan.txt && git commit -m "Add plan" && git push
git switch -c alice
echo "Week 1: setup and Git" > plan.txt
git commit -am "Alice's plan"
git switch main
echo "Week 1: install Python" > plan.txt
git commit -am "Main's plan"
git merge alice                # CONFLICT (content): Merge conflict in plan.txt
```

`plan.txt` now contains:
```text
<<<<<<< HEAD
Week 1: install Python
=======
Week 1: setup and Git
>>>>>>> alice
```

Edit it to exactly:
```text
Week 1: install Python, setup and Git
```

```bash
git add plan.txt
git commit -m "Merge alice: combine plans"
```

Explanation: `<<<<<<< HEAD` starts the version from the branch you are on (here `main`). `=======` separates your version from the incoming one. `>>>>>>> alice` ends the incoming version from the branch being merged. You must delete all three marker lines and keep the text you want.
