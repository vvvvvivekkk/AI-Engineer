"""
build_pdfs.py - build the course PDFs with a clickable table of contents and bookmarks.

    python tools/build_pdfs.py            # everything
    python tools/build_pdfs.py --book     # only the full course book
    python tools/build_pdfs.py --handouts # only the per-module handouts

Outputs
  pdf/AI-Engineer-Course-Book.pdf      every lesson in one book: Parts > Chapters > Sections
  pdf/Trainer-Handbook.pdf             ROADMAP + TRAINER-GUIDE + PLAN for the trainer team
  pdf/Projects-Guide.pdf               all 10 project READMEs
  NN-module/pdf/NN-module-handout.pdf  one handout per module (concepts.md) with its own contents page

Every relative link inside the lessons (to notebooks, code, other modules) is rewritten
to the matching GitHub URL, so clicking it in the PDF opens the file online.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from course_meta import MODULES, PHASES, PROJECTS, REPO  # noqa: E402

STYLE = ROOT / "tools" / "pdf_style.tex"
GH_BLOB = f"https://github.com/{REPO}/blob/main/"
EMOJI = re.compile(r"[\U0001F000-\U0001FFFF☀-➿⬀-⯿️‍]")
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)([^)]*)\)")
FENCE = re.compile(r"^\s*(```|~~~)")


def rewrite(md: str, folder: str, image_prefix: str, shift: int = 0) -> str:
    """Prepare one markdown file for inclusion in a PDF.
    - images: path made relative to the build folder (image_prefix)
    - other relative links: turned into GitHub URLs (folder = the file's folder in the repo)
    - headings: shifted down `shift` levels (outside code blocks)
    - emoji removed (the PDF fonts have no emoji glyphs)"""
    md = re.sub(r"<!-- nav:start -->.*?<!-- nav:end -->", "", md, flags=re.S)   # web-only navigation bars
    out, in_code = [], False
    for line in md.splitlines():
        if FENCE.match(line):
            in_code = not in_code
        elif not in_code and shift and re.match(r"^#{1,5} ", line):
            line = "#" * shift + line
        if not in_code:
            def fix(m):
                bang, text, target, rest = m.groups()
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    return m.group(0)
                if bang:
                    return f"{bang}[{text}]({image_prefix}{target}{rest})"
                path = (Path(folder) / target).as_posix()
                path = re.sub(r"[^/]+/\.\./", "", path)      # tidy "a/../b"
                return f"[{text}]({GH_BLOB}{path})"
            line = LINK.sub(fix, line)
        out.append(EMOJI.sub("", line))
    return "\n".join(out) + "\n"


def pandoc(md_text: str, out_pdf: Path, workdir: Path, meta: dict, book: bool = False) -> None:
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".md", dir=workdir, delete=False, encoding="utf-8") as f:
        f.write(md_text)
        tmp = Path(f.name)
    cmd = ["pandoc", str(tmp), "-o", str(out_pdf), "--pdf-engine=xelatex",
           "--resource-path", str(workdir), "-H", str(STYLE), "--toc",
           "--highlight-style", "tango",
           "-V", "geometry:margin=2.2cm", "-V", "mainfont=DejaVu Sans", "-V", "monofont=DejaVu Sans Mono",
           "-V", "fontsize=11pt", "-V", "colorlinks=true", "-V", "linkcolor=teal", "-V", "urlcolor=teal",
           "-V", "toccolor=navy", "-V", "toc-title=Contents"]
    if book:
        cmd += ["-V", "documentclass=report", "-V", "classoption=openany", "--top-level-division=part",
                "--toc-depth=2"]
    else:
        cmd += ["--toc-depth=2"]
    for k, v in meta.items():
        cmd += ["-M", f"{k}={v}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, cwd=workdir)
    finally:
        tmp.unlink(missing_ok=True)
    if r.returncode != 0:
        raise RuntimeError(f"pandoc failed for {out_pdf.name}:\n{r.stderr[-3000:]}")
    print(f"  wrote {out_pdf.relative_to(ROOT)}")


def strip_first_h1(md: str) -> tuple[str, str]:
    """Remove the first '# Title' line and return (title, rest)."""
    m = re.search(r"^# (.+)$", md, flags=re.M)
    if not m:
        return "", md
    return m.group(1).strip(), md[:m.start()] + md[m.end():]


def handouts() -> None:
    print("Module handouts")
    for folder, icon, title, phase, weeks, summary, analogy in MODULES:
        src = ROOT / folder / "concepts.md"
        if not src.exists():
            continue
        h1, body = strip_first_h1(src.read_text(encoding="utf-8"))
        body = rewrite(body, folder, "", shift=0)
        intro = (f"> **In one sentence:** {summary}\n>\n> **Everyday analogy:** {analogy}\n>\n"
                 f"> **Course week(s):** {weeks}  ·  [Open this module on GitHub]({GH_BLOB}{folder}) "
                 f"(notebooks, slides, exercises)\n\n")
        # concepts.md uses '##' for sections; promote so '##' -> section numbering looks right
        body = re.sub(r"(?m)^(#{2,6}) ", lambda m: m.group(1)[1:] + " ", body) if not re.search(r"(?m)^# ", body) else body
        pandoc(intro + body, ROOT / folder / "pdf" / f"{folder}-handout.pdf", ROOT / folder,
               {"title": EMOJI.sub("", h1 or title).strip(), "subtitle": "Python to Pro — AI Engineer curriculum · Handout",
                "date": date.today().strftime("%B %Y")})


def course_book() -> None:
    print("Course book")
    parts = []
    intro = (ROOT / "README.md").read_text(encoding="utf-8")
    parts.append("# Welcome\n\n"
                 "This book collects every lesson (`concepts.md`) of the *Python to Pro* AI Engineer curriculum "
                 "in teaching order. Use the **bookmarks panel** of your PDF reader to jump between Parts, "
                 "Chapters and Sections, or click any line of the contents pages. Links open the matching "
                 "notebook, code or slide deck on GitHub.\n\n"
                 "## How the course is organised\n\n"
                 + "\n".join(f"- **Part {num} — {name}:** {desc}" for num, name, _, desc in PHASES)
                 + "\n\n## The 24-week roadmap\n\n![Roadmap](images/roadmap.png)\n")
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    _, roadmap = strip_first_h1(roadmap)
    roadmap = re.sub(r"!\[Roadmap\]\(images/roadmap.png\)\n?", "", roadmap)
    parts.append("## Week by week\n" + rewrite(roadmap, ".", "", shift=1))
    for p_idx, (num, name, _, desc) in enumerate(PHASES):
        # The part divider page; its one-line description goes into each chapter's intro box instead
        parts.append(f"# Part {num} — {name}\n")
        for folder, icon, title, phase, weeks, summary, analogy in MODULES:
            if phase != p_idx:
                continue
            src = ROOT / folder / ("concepts.md" if folder != "15-projects" else "README.md")
            if not src.exists():
                continue
            h1, body = strip_first_h1(src.read_text(encoding="utf-8"))
            chapter = f"## {folder[:2]} · {title}\n\n"
            chapter += (f"> **Part {num} — {name}.** {desc}  \n> **In one sentence:** {summary}  \n> **Analogy:** {analogy}  \n"
                        f"> **Week(s):** {weeks} · [Open notebooks, slides and exercises on GitHub]({GH_BLOB}{folder})\n\n")
            body = rewrite(body, folder, f"{folder}/", shift=1)
            parts.append(chapter + body)
    parts.append("# Appendix\n\n## Sources and licences\n"
                 + rewrite(strip_first_h1((ROOT / "SOURCES.md").read_text(encoding="utf-8"))[1], ".", "", shift=1))
    pandoc("\n\n".join(parts), ROOT / "pdf" / "AI-Engineer-Course-Book.pdf", ROOT,
           {"title": "Python to Pro — AI Engineer", "subtitle": "The complete course book: every lesson in one place",
            "author": "AI-Engineer curriculum", "date": date.today().strftime("%B %Y")}, book=True)


def trainer_handbook() -> None:
    print("Trainer handbook")
    chunks = []
    for name in ["TRAINER-GUIDE.md", "ROADMAP.md", "PLAN.md"]:
        h1, body = strip_first_h1((ROOT / name).read_text(encoding="utf-8"))
        chunks.append(f"# {EMOJI.sub('', h1)}\n" + rewrite(body, ".", "", shift=0))
    for folder, *_ in MODULES:
        tn = ROOT / folder / "trainer-notes.md"
        if tn.exists():
            h1, body = strip_first_h1(tn.read_text(encoding="utf-8"))
            chunks.append(f"# Trainer notes: {folder}\n" + rewrite(body, folder, f"{folder}/", shift=0))
    pandoc("\n\n".join(chunks), ROOT / "pdf" / "Trainer-Handbook.pdf", ROOT,
           {"title": "Trainer Handbook", "subtitle": "How to run the Python to Pro AI Engineer course, with every module's session plan",
            "date": date.today().strftime("%B %Y")})


def projects_guide() -> None:
    print("Projects guide")
    chunks = []
    h1, body = strip_first_h1((ROOT / "15-projects" / "README.md").read_text(encoding="utf-8"))
    chunks.append("# Overview\n" + rewrite(body, "15-projects", "15-projects/", shift=0))
    for folder, title, level, _ in PROJECTS:
        rd = ROOT / "15-projects" / folder / "README.md"
        if rd.exists():
            _, body = strip_first_h1(rd.read_text(encoding="utf-8"))
            chunks.append(f"# {folder[:3].upper()} · {title}\n" +
                          rewrite(body, f"15-projects/{folder}", f"15-projects/{folder}/", shift=0))
    pandoc("\n\n".join(chunks), ROOT / "pdf" / "Projects-Guide.pdf", ROOT,
           {"title": "Projects Guide", "subtitle": "Ten portfolio projects, beginner to advanced",
            "date": date.today().strftime("%B %Y")})


if __name__ == "__main__":
    args = set(sys.argv[1:])
    if not args or "--handouts" in args:
        handouts()
    if not args or "--book" in args:
        course_book()
        trainer_handbook()
        projects_guide()
