"""
build_kit.py - shared helpers used to generate the teaching materials in every module.

Every module folder has a small `build.py` that imports these helpers so that
all slides, PDFs, notebooks and spreadsheets look the same across the course.

Usage inside a module's build.py:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
    from build_kit import *
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_SLUG = "vvvvvivekkk/AI-Engineer"   # GitHub owner/repo, used for Colab badges
BRANCH = "main"                          # branch the Colab badge points at
ROOT = Path(__file__).resolve().parents[1]
PUPPETEER_CFG = ROOT / "tools" / "puppeteer.json"

# Course colour palette (dark navy + teal accent), used on slides and charts
NAVY = (0x1B, 0x26, 0x3B)
TEAL = (0x0F, 0x9D, 0x9A)
LIGHT = (0xF4, 0xF6, 0xF8)
GREY = (0x5A, 0x63, 0x70)


# --------------------------------------------------------------------------
# Diagrams
# --------------------------------------------------------------------------
def mermaid(src: str, out_png: Path | str, scale: int = 2) -> Path:
    """Render a Mermaid diagram (text) to a PNG file using the mermaid CLI (mmdc).
    Also saves the .mmd source next to the PNG so trainers can edit it."""
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    mmd = out_png.with_suffix(".mmd")
    mmd.write_text(src.strip() + "\n", encoding="utf-8")
    cmd = ["mmdc", "-i", str(mmd), "-o", str(out_png), "-b", "white", "-s", str(scale)]
    if PUPPETEER_CFG.exists():
        cmd[1:1] = ["-p", str(PUPPETEER_CFG)]
    subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    return out_png


# --------------------------------------------------------------------------
# Notebooks
# --------------------------------------------------------------------------
def colab_badge(nb_rel_path: str) -> str:
    """Markdown for an 'Open in Colab' badge. nb_rel_path is relative to repo root."""
    url = f"https://colab.research.google.com/github/{REPO_SLUG}/blob/{BRANCH}/{nb_rel_path}"
    return f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({url})"


def notebook(cells: list[tuple[str, str]], out_path: Path | str) -> Path:
    """Build a .ipynb from a list of ("md", text) / ("code", text) tuples.

    Rules enforced automatically:
      * the first cell is a markdown cell with the Open-in-Colab badge
      * every code cell must be directly preceded by a markdown cell (raises otherwise)
    """
    import nbformat
    from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

    out_path = Path(out_path).resolve()
    rel = out_path.relative_to(ROOT).as_posix()
    nb = new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    nb.metadata["colab"] = {"provenance": []}

    first_md = cells[0][1] if cells and cells[0][0] == "md" else ""
    nb.cells.append(new_markdown_cell(colab_badge(rel) + "\n\n" + first_md.strip()))
    rest = cells[1:] if first_md else cells

    prev = "md"
    for i, (kind, text) in enumerate(rest):
        text = text.strip("\n")
        if kind == "md":
            nb.cells.append(new_markdown_cell(text))
        elif kind == "code":
            if prev != "md":
                raise ValueError(f"{out_path.name}: code cell #{i} is not preceded by a markdown cell")
            nb.cells.append(new_code_cell(text))
        else:
            raise ValueError(f"unknown cell kind {kind!r}")
        prev = kind
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, str(out_path))
    return out_path


def run_notebook(path: Path | str, timeout: int = 900) -> tuple[bool, str]:
    """Execute a notebook top to bottom in a temp copy. Returns (ok, message).
    The saved notebook keeps its outputs so students can preview results on GitHub."""
    import nbformat
    from nbclient import NotebookClient

    path = Path(path)
    nb = nbformat.read(str(path), as_version=4)
    client = NotebookClient(nb, timeout=timeout, kernel_name="python3",
                            resources={"metadata": {"path": str(path.parent)}})
    try:
        client.execute()
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[-1500:]}"
    nbformat.write(nb, str(path))
    return True, "ok"


# --------------------------------------------------------------------------
# Slides (.pptx)
# --------------------------------------------------------------------------
def slides(deck: dict, out_path: Path | str) -> Path:
    """Build a teaching deck with python-pptx.

    deck = {
      "title": "Module 00 - Setup",
      "subtitle": "Python Pro AI Engineer curriculum",
      "slides": [
         {"title": "...", "bullets": ["...", "  sub-bullet (2 leading spaces)"],
          "notes": "speaker notes for the trainer", "image": "path/to.png" (optional),
          "code": "short code snippet" (optional)},
         ...
      ]
    }
    """
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.util import Emu, Inches, Pt

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    W, H = prs.slide_width, prs.slide_height
    blank = prs.slide_layouts[6]

    def bg(slide, rgb):
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(*rgb)

    def textbox(slide, x, y, w, h, text, size, color, bold=False, font="Calibri"):
        tb = slide.shapes.add_textbox(x, y, w, h)
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text
        p.font.size, p.font.bold, p.font.name = Pt(size), bold, font
        p.font.color.rgb = RGBColor(*color)
        return tf

    # Title slide
    s = prs.slides.add_slide(blank)
    bg(s, NAVY)
    textbox(s, Inches(0.8), Inches(2.4), W - Inches(1.6), Inches(1.5), deck["title"], 44, (255, 255, 255), True)
    textbox(s, Inches(0.8), Inches(3.9), W - Inches(1.6), Inches(1), deck.get("subtitle", ""), 22, TEAL)
    bar = s.shapes.add_shape(1, Inches(0.8), Inches(3.75), Inches(2.5), Emu(60000))
    bar.fill.solid(); bar.fill.fore_color.rgb = RGBColor(*TEAL); bar.line.fill.background()

    for i, sd in enumerate(deck["slides"], start=1):
        s = prs.slides.add_slide(blank)
        bg(s, LIGHT)
        band = s.shapes.add_shape(1, 0, 0, W, Inches(1.1))
        band.fill.solid(); band.fill.fore_color.rgb = RGBColor(*NAVY); band.line.fill.background()
        textbox(s, Inches(0.5), Inches(0.18), W - Inches(1), Inches(0.8), sd["title"], 30, (255, 255, 255), True)
        textbox(s, W - Inches(1.2), H - Inches(0.5), Inches(1), Inches(0.4), str(i), 12, GREY)

        has_side = bool(sd.get("image") or sd.get("code"))
        text_w = Inches(6.6) if has_side else W - Inches(1.2)
        bullets = sd.get("bullets", [])
        if bullets:
            tb = s.shapes.add_textbox(Inches(0.6), Inches(1.4), text_w, H - Inches(2.2))
            tf = tb.text_frame
            tf.word_wrap = True
            for j, b in enumerate(bullets):
                level = 1 if b.startswith("  ") else 0
                p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
                p.text = ("• " if level == 0 else "– ") + b.strip()
                p.level = level
                p.font.size = Pt(22 if level == 0 else 18)
                p.font.color.rgb = RGBColor(*(NAVY if level == 0 else GREY))
                p.space_after = Pt(10)
        if sd.get("image"):
            img = Path(sd["image"])
            if img.exists():
                left = Inches(7.4) if bullets else Inches(1.5)
                maxw = Inches(5.5) if bullets else W - Inches(3)
                pic = s.shapes.add_picture(str(img), left, Inches(1.5))
                ratio = min(maxw / pic.width, (H - Inches(2.3)) / pic.height, 1.0)
                pic.width, pic.height = int(pic.width * ratio), int(pic.height * ratio)
        elif sd.get("code"):
            left = Inches(7.4) if bullets else Inches(0.6)
            width = Inches(5.5) if bullets else W - Inches(1.2)
            box = s.shapes.add_shape(1, left, Inches(1.4), width, H - Inches(2.2))
            box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0x1E, 0x1E, 0x1E); box.line.fill.background()
            tf = box.text_frame
            tf.word_wrap = True
            for j, line in enumerate(sd["code"].strip("\n").split("\n")):
                p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
                p.text = line
                p.font.name, p.font.size = "Consolas", Pt(14)
                p.font.color.rgb = RGBColor(0xD4, 0xD4, 0xD4)
        if sd.get("notes"):
            s.notes_slide.notes_text_frame.text = sd["notes"]

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_path))
    return out_path


# --------------------------------------------------------------------------
# PDF handout
# --------------------------------------------------------------------------
def pdf_from_markdown(md_path: Path | str, out_pdf: Path | str, title: str | None = None) -> Path:
    """Convert a markdown file (with embedded PNG images) into a PDF handout with pandoc + xelatex.
    Images are resolved relative to the markdown file's folder."""
    md_path, out_pdf = Path(md_path).resolve(), Path(out_pdf).resolve()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["pandoc", str(md_path), "-o", str(out_pdf), "--pdf-engine=xelatex",
           "--resource-path", str(md_path.parent),
           "-V", "geometry:margin=2cm", "-V", "mainfont=DejaVu Sans", "-V", "monofont=DejaVu Sans Mono",
           "-V", "fontsize=11pt", "-V", "colorlinks=true", "--highlight-style", "tango"]
    if title:
        cmd += ["-M", f"title={title}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=md_path.parent)
    if r.returncode != 0:
        # Fallback: strip emoji / exotic glyphs that xelatex fonts lack, then retry once.
        txt = md_path.read_text(encoding="utf-8")
        clean = re.sub(r"[\U0001F000-\U0001FFFF☀-➿️]", "", txt)
        with tempfile.NamedTemporaryFile("w", suffix=".md", dir=md_path.parent, delete=False, encoding="utf-8") as f:
            f.write(clean)
            tmp = f.name
        try:
            cmd[1] = tmp
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=md_path.parent)
        finally:
            os.unlink(tmp)
        if r.returncode != 0:
            raise RuntimeError(f"pandoc failed for {md_path}:\n{r.stderr[-2000:]}")
    return out_pdf


# --------------------------------------------------------------------------
# Excel workbooks
# --------------------------------------------------------------------------
def workbook(sheets: dict[str, list[list]], out_path: Path | str, col_widths: dict[str, list[int]] | None = None) -> Path:
    """Write an .xlsx. sheets = {"Sheet name": [[header...], [row...], ...]}.
    Header row is bold on navy, columns auto-sized, header frozen, auto-filter on.
    Cells whose text starts with '=' are kept as live Excel formulas.
    URLs are turned into clickable hyperlinks."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    wb.remove(wb.active)
    for name, rows in sheets.items():
        ws = wb.create_sheet(name[:31])
        for r in rows:
            ws.append(r)
        if not rows:
            continue
        hdr_fill = PatternFill("solid", fgColor="1B263B")
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = hdr_fill
            c.alignment = Alignment(vertical="center", wrap_text=True)
        for row in ws.iter_rows(min_row=2):
            for c in row:
                if isinstance(c.value, str) and c.value.startswith(("http://", "https://")):
                    c.hyperlink = c.value
                    c.font = Font(color="0F6E9D", underline="single")
                c.alignment = Alignment(vertical="top", wrap_text=True)
        widths = (col_widths or {}).get(name)
        for i, col in enumerate(ws.columns, start=1):
            if widths and i <= len(widths):
                w = widths[i - 1]
            else:
                w = min(60, max(10, max(len(str(c.value or "")) for c in col) + 2))
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(out_path))
    return out_path
