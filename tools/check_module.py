"""
check_module.py - verify that a module (or project) folder meets the course standard.

    python tools/check_module.py 00-setup            # structure checks only
    python tools/check_module.py 00-setup --run      # also execute every notebook
    python tools/check_module.py --all --run

Checks for modules:
  README.md, concepts.md, exercises.md, trainer-notes.md, resources.md exist and are non-trivial
  images/ has at least one .png, and concepts.md embeds at least one of them
  notebooks/ has >=1 .ipynb, each with an Open-in-Colab badge and a markdown cell before every code cell
  code/ has >=1 .py that compiles, solutions/ is non-empty
  slides/*.pptx, pdf/*.pdf exist (excel/*.xlsx optional but reported)
  every image linked in a .md file exists
  no secrets (API-key-looking strings) anywhere in the folder
"""
from __future__ import annotations

import argparse
import json
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

SECRET_RE = re.compile(r"(sk-[A-Za-z0-9_\-]{20,}|sk-ant-[A-Za-z0-9_\-]{20,}|AIza[0-9A-Za-z_\-]{30,}|hf_[A-Za-z0-9]{30,}|ghp_[A-Za-z0-9]{30,})")
REQUIRED_MD = ["README.md", "concepts.md", "exercises.md", "trainer-notes.md", "resources.md"]
SKIP_RUN_MARKER = "colab-only"   # notebooks whose filename contains this are not executed locally


def check_notebook(nb_path: Path) -> list[str]:
    errs = []
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    cells = nb.get("cells", [])
    if not cells or "colab-badge.svg" not in "".join(cells[0].get("source", "")):
        errs.append(f"{nb_path.name}: first cell lacks Open-in-Colab badge")
    for i, c in enumerate(cells):
        if c["cell_type"] == "code" and (i == 0 or cells[i - 1]["cell_type"] != "markdown"):
            errs.append(f"{nb_path.name}: code cell {i} not preceded by markdown")
    return errs


def check_module(folder: Path, run: bool) -> tuple[list[str], list[str]]:
    errs, notes = [], []
    is_project = folder.parent.name == "15-projects"
    if is_project:
        for f in ["README.md", "requirements.txt", ".env.example"]:
            if not (folder / f).exists():
                errs.append(f"missing {f}")
        if (folder / "requirements.txt").exists():
            for line in (folder / "requirements.txt").read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "==" not in line:
                    errs.append(f"requirements.txt: unpinned '{line}'")
    else:
        for f in REQUIRED_MD:
            p = folder / f
            if not p.exists():
                errs.append(f"missing {f}")
            elif len(p.read_text(encoding="utf-8")) < 400:
                errs.append(f"{f} looks too short")
        for sub, pat in [("images", "*.png"), ("notebooks", "*.ipynb"), ("code", "*.py"),
                         ("slides", "*.pptx"), ("pdf", "*.pdf")]:
            if not list((folder / sub).glob(pat)):
                errs.append(f"{sub}/ has no {pat}")
        if not (folder / "solutions").exists() or not any((folder / "solutions").iterdir()):
            errs.append("solutions/ empty or missing")
        if not list((folder / "excel").glob("*.xlsx")):
            notes.append("no excel/*.xlsx (optional)")
        c = folder / "concepts.md"
        if c.exists() and "images/" not in c.read_text(encoding="utf-8"):
            errs.append("concepts.md embeds no image from images/")

    # broken local image links in markdown
    for md in folder.rglob("*.md"):
        for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)\)", md.read_text(encoding="utf-8")):
            target = m.group(1)
            if target.startswith(("http://", "https://")):
                continue
            if not (md.parent / target).exists():
                errs.append(f"{md.relative_to(folder)}: broken image link {target}")

    for py in folder.rglob("*.py"):
        if "checkpoint" in str(py):
            continue
        try:
            py_compile.compile(str(py), doraise=True)
        except py_compile.PyCompileError as e:
            errs.append(f"{py.relative_to(folder)} does not compile: {e.msg[:200]}")

    for f in folder.rglob("*"):
        if f.is_file() and f.suffix in {".py", ".md", ".ipynb", ".txt", ".json", ".yaml", ".yml", ".env", ".example", ".toml"}:
            if SECRET_RE.search(f.read_text(encoding="utf-8", errors="ignore")):
                errs.append(f"possible secret in {f.relative_to(folder)}")

    for nb in sorted(folder.rglob("*.ipynb")):
        if ".ipynb_checkpoints" in str(nb):
            continue
        errs += check_notebook(nb)
        if run:
            if SKIP_RUN_MARKER in nb.name:
                notes.append(f"{nb.name}: colab-only (GPU) - not executed locally")
                continue
            from build_kit import run_notebook
            ok, msg = run_notebook(nb)
            (notes if ok else errs).append(f"run {nb.name}: {msg}")
    return errs, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modules", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    targets = [ROOT / m for m in a.modules]
    if a.all:
        targets = sorted(p for p in ROOT.iterdir() if p.is_dir() and re.match(r"\d\d-", p.name) and p.name != "15-projects")
        targets += sorted(p for p in (ROOT / "15-projects").iterdir() if p.is_dir()) if (ROOT / "15-projects").exists() else []
    bad = 0
    for t in targets:
        errs, notes = check_module(t, a.run)
        status = "PASS" if not errs else "FAIL"
        bad += bool(errs)
        print(f"[{status}] {t.relative_to(ROOT)}")
        for e in errs:
            print("   ERROR:", e)
        for n in notes:
            print("   note: ", n)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
