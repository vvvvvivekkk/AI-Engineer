"""
build_root.py - regenerate the repo-level generated files:

  images/roadmap.png      the visual 24-week roadmap embedded in README.md / ROADMAP.md
  RESOURCES-MASTER.xlsx   every resource linked anywhere in the course

    python tools/build_root.py

RESOURCES-MASTER is built from two inputs:
  1. tools/resources_catalog.csv - the curated catalogue (title, url, type, level, free/paid,
     source, why) researched from the nine source repos (see SOURCES.md)
  2. every link found in each module's resources.md (so new links added by trainers appear too)
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                       # draw to files, no window needed
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "tools"))
from build_kit import workbook  # noqa: E402

# (start_week, length_in_weeks, module label, phase index)
SCHEDULE = [
    (1, 1, "00 Setup", 0), (2, 2, "01 Python basics", 0), (4, 2, "02 Python for data", 0), (6, 1, "03 Math for AI", 0),
    (7, 2, "04 Machine learning", 1), (9, 2, "05 Deep learning", 1), (11, 2, "06 NLP & transformers", 1),
    (13, 1, "07 LLMs & GenAI", 2), (14, 1, "08 Prompt & context eng.", 2), (15, 2, "09 RAG", 2),
    (17, 2, "10 Agentic AI", 2), (19, 1, "11 AI automation", 2),
    (20, 1, "12 Annotation & RLHF", 3), (21, 1, "13 Fine-tuning", 3), (22, 2, "14 Deployment & LLMOps", 3),
    (24, 1, "16 Careers", 3),
]
PROJECTS = [(8, "P1-2"), (10, "P3"), (12, "P4"), (16, "P5"), (18, "P8"), (19, "P9"), (20, "P6"), (21, "P10"), (23, "P7"), (24, "Capstone")]
PHASES = ["Foundations", "ML · DL · NLP", "LLM engineering", "Data · tuning · production · careers"]
COLORS = ["#4C78A8", "#0F9D9A", "#E45756", "#B279A2"]


def roadmap_png(out: Path) -> None:
    """Draw the 24-week plan as a timeline: one bar per module, coloured by phase."""
    fig, ax = plt.subplots(figsize=(14, 7.2), dpi=150)
    for row, (start, length, label, ph) in enumerate(SCHEDULE):
        y = len(SCHEDULE) - row                         # first module at the top
        ax.barh(y, length - 0.1, left=start - 0.5, color=COLORS[ph], height=0.7)
        ax.text(start - 0.5 + length + 0.1, y, label, va="center", fontsize=10)
    for wk, name in PROJECTS:                           # project milestones as diamonds on the axis
        ax.plot(wk, 0, marker="D", color="#333333", markersize=7)
        ax.text(wk, -0.75, name, ha="center", fontsize=8)
    ax.set_xlim(0.3, 28.5)
    ax.set_ylim(-1.4, len(SCHEDULE) + 1)
    ax.set_xticks(range(1, 25))
    ax.set_xlabel("Week")
    ax.set_yticks([])
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in COLORS]
    ax.legend(handles, PHASES, loc="upper right", frameon=False, fontsize=10)
    ax.set_title("Python to Pro AI Engineer: 24-week roadmap   (◆ = project milestone)", fontsize=14, loc="left")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)


WHY: dict[str, str] = {}
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
BARE_RE = re.compile(r"(?<![(\[<])(https?://[^\s)|>\]]+)")


def module_links(md: Path) -> list[tuple[str, str]]:
    """Return (title, url) pairs found in a resources.md file."""
    text = md.read_text(encoding="utf-8")
    pairs = [(t.strip(), u.rstrip(".,")) for t, u in LINK_RE.findall(text)]
    seen = {u for _, u in pairs}
    for line in text.splitlines():           # remember the author's one-line "why" next to each link
        links = LINK_RE.findall(line)
        if len(links) == 1:
            rest = LINK_RE.sub("", line)
            rest = re.sub(r"[|*_`]", " ", rest).strip(" -–—:\t")
            rest = re.sub(r"\s{2,}", " ", rest).strip(" -–—:")
            if len(rest) > 8:
                WHY.setdefault(links[0][1].rstrip(".,"), rest)
    for u in BARE_RE.findall(text):
        u = u.rstrip(".,")
        if u not in seen and "colab.research.google.com" not in u and "img.shields" not in u:
            pairs.append(("", u))
            seen.add(u)
    return pairs


def guess_meta(url: str, module: str) -> tuple[str, str, str]:
    """Best-guess (type, level, free/paid) for links that are not in the curated catalogue.
    Marked with '(auto)' so maintainers know to review them."""
    u = url.lower()
    if "github.com" in u:
        t = "repo"
    elif "arxiv.org" in u or "openreview" in u or "aclanthology" in u:
        t = "paper"
    elif "youtube.com" in u or "youtu.be" in u:
        t = "video"
    elif any(k in u for k in ("docs.", "/docs", "readthedocs", "documentation", "/reference", "/api")):
        t = "docs"
    elif any(k in u for k in ("course", "learn", "academy", "/tutorial")):
        t = "course"
    else:
        t = "article"
    num = int(module[:2]) if module[:2].isdigit() else 0
    level = "beginner" if num <= 3 else ("intermediate" if num <= 9 else "intermediate-advanced")
    return f"{t} (auto)", f"{level} (auto)", "Free (auto)"


def resources_master(out: Path) -> int:
    catalog: dict[str, dict] = {}
    cat_file = ROOT / "tools" / "resources_catalog.csv"
    if cat_file.exists():
        with cat_file.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                catalog.setdefault(r["url"], r)
    rows: dict[tuple[str, str], list] = {}
    # 1) links actually used in module resources.md files
    for mod in sorted(p for p in ROOT.iterdir() if p.is_dir() and re.match(r"\d\d-", p.name)):
        res = mod / "resources.md"
        if not res.exists():
            continue
        for title, url in module_links(res):
            c = catalog.get(url, {})
            if c:
                t, lv, fp, srcno = c["type"], c["level"], c["free_paid"], c["source"]
            else:
                (t, lv, fp), srcno = guess_meta(url, mod.name), "module author"
            rows[(mod.name, url)] = [mod.name, title or c.get("title", "") or url, url, t, lv, fp, srcno,
                                     c.get("why", "") or WHY.get(url, "")]
    # 2) curated catalogue entries not already used, under their planned module
    for url, c in catalog.items():
        key = (c["module"], url)
        if key not in rows and not any(k[1] == url for k in rows):
            rows[key] = [c["module"], c["title"], url, c["type"], c["level"], c["free_paid"], c["source"], c["why"]]
    header = ["Module", "Title", "Link", "Type", "Level", "Free/Paid", "Found in source #", "Why it's useful"]
    data = [header] + sorted(rows.values(), key=lambda r: (r[0], r[1].lower()))
    src = [["#", "Source", "URL"]] + [
        [1, "openbestof/awesome-ai", "https://github.com/openbestof/awesome-ai"],
        [2, "x1xhlol/system-prompts-and-models-of-ai-tools", "https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools"],
        [3, "pietro93/awesome-ai-training-jobs", "https://github.com/pietro93/awesome-ai-training-jobs"],
        [4, "taivop/awesome-data-annotation", "https://github.com/taivop/awesome-data-annotation"],
        [5, "opendilab/awesome-RLHF", "https://github.com/opendilab/awesome-RLHF"],
        [6, "ashishpatel26/500-AI-...-Projects-with-code", "https://github.com/ashishpatel26/500-AI-Machine-learning-Deep-learning-Computer-vision-NLP-Projects-with-code"],
        [7, "Eric-LLMs/awesome-ai-engineering", "https://github.com/Eric-LLMs/awesome-ai-engineering"],
        [8, "dipakkr/awesome-ai-engineering", "https://github.com/dipakkr/awesome-ai-engineering"],
        [9, "dave-nachman/awesome-ai-engineering", "https://github.com/dave-nachman/awesome-ai-engineering"],
        ["official", "Official documentation of the tool/library", ""],
    ]
    mods = sorted({r[0] for r in data[1:]})
    summary = [["Module", "Resources", "Free"]] + [
        [m, f'=COUNTIF(Resources!A:A,"{m}")', f'=COUNTIFS(Resources!A:A,"{m}",Resources!F:F,"Free*")'] for m in mods
    ] + [["TOTAL", f"=SUM(B2:B{len(mods)+1})", f"=SUM(C2:C{len(mods)+1})"]]
    workbook({"Resources": data, "Summary": summary, "Sources": src}, out,
             col_widths={"Resources": [24, 40, 50, 12, 16, 12, 10, 70]})
    return len(data) - 1


if __name__ == "__main__":
    roadmap_png(ROOT / "images" / "roadmap.png")
    n = resources_master(ROOT / "RESOURCES-MASTER.xlsx")
    print(f"roadmap.png written; RESOURCES-MASTER.xlsx has {n} resources")
