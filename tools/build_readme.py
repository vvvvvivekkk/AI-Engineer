"""
build_readme.py - generate the root README.md and add navigation bars to every module page.

    python tools/build_readme.py

* README.md is rebuilt from tools/course_meta.py plus each module's concepts.md headings,
  so the topic lists never drift out of date.
* Each module README.md and concepts.md, and each project README.md, gets a navigation bar
  (Home · Previous · Next + quick links) at the top and bottom, between
  <!-- nav:start --> / <!-- nav:end --> markers. Re-running replaces the bars, never duplicates them.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from course_meta import MODULES, PHASES, PROJECTS, REPO  # noqa: E402

COLAB = f"https://colab.research.google.com/github/{REPO}/blob/main/"
NAV_RE = re.compile(r"<!-- nav:start -->.*?<!-- nav:end -->\n*", re.S)


def gh_slug(heading: str) -> str:
    """GitHub's anchor for a heading: lower-case, drop punctuation, spaces -> hyphens."""
    h = re.sub(r"[`*_]", "", heading.strip().lower())
    h = "".join(ch for ch in h if ch.isalnum() or ch in " -" or unicodedata.category(ch).startswith("L"))
    return h.replace(" ", "-")


def topics(folder: str) -> list[tuple[str, str]]:
    """(heading text, anchor) for every '## ' section of a module's concepts.md."""
    p = ROOT / folder / "concepts.md"
    if not p.exists():
        return []
    out, in_code = [], False
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_code = not in_code
        if not in_code and line.startswith("## "):
            text = line[3:].strip()
            if re.search(r"glossary|key (terms|words)|what to do next|recap|summary", text, re.I):
                continue
            out.append((re.sub(r"^\d+\.\s*", "", text), gh_slug(text)))
    return out


def first(folder: str, sub: str, pattern: str) -> str | None:
    files = sorted((ROOT / folder / sub).glob(pattern))
    return f"{sub}/{files[0].name}" if files else None


def quick_links(folder: str, rel: str = "") -> str:
    """'📖 Lesson · 📄 PDF · 🎞️ Slides · ...' with paths relative to the page they appear on."""
    items = [("📖 Lesson", "concepts.md")]
    for label, sub, pat in [("📄 PDF handout", "pdf", "*-handout.pdf"), ("🎞️ Slides", "slides", "*.pptx")]:
        f = first(folder, sub, pat)
        if f:
            items.append((label, f))
    items += [("📓 Notebooks", "notebooks/"), ("✍️ Exercises", "exercises.md"), ("✅ Solutions", "solutions/"),
              ("🧑‍🏫 Trainer notes", "trainer-notes.md"), ("🔗 Resources", "resources.md")]
    return " · ".join(f"[{label}]({rel}{quote(path)})" for label, path in items if (ROOT / folder / path.rstrip('/')).exists())


def module_nav(i: int, page: str) -> tuple[str, str]:
    """Top and bottom navigation bars for module i. page = 'README.md' or 'concepts.md'."""
    folder, icon, title, *_ = MODULES[i]
    prev_ = MODULES[i - 1] if i > 0 else None
    next_ = MODULES[i + 1] if i + 1 < len(MODULES) else None
    parts = ["[🏠 Course home](../README.md)", "[🗺️ Roadmap](../ROADMAP.md)"]
    if prev_:
        parts.append(f"[⬅️ {prev_[0][:2]} {prev_[2]}](../{prev_[0]}/README.md)")
    if next_:
        parts.append(f"[{next_[0][:2]} {next_[2]} ➡️](../{next_[0]}/README.md)")
    bar = " · ".join(parts)
    here = "" if page == "README.md" else " · [📋 Module overview](README.md)"
    top = (f"<!-- nav:start -->\n> {bar}  \n> **{icon} Module {folder[:2]} · {title}**{here}  \n"
           f"> {quick_links(folder)}\n<!-- nav:end -->\n\n")
    bottom = f"\n\n<!-- nav:start -->\n---\n{bar}\n<!-- nav:end -->\n"
    return top, bottom


def project_nav(i: int) -> tuple[str, str]:
    folder, title, level, mod = PROJECTS[i]
    parts = ["[🏠 Course home](../../README.md)", "[🏗️ All projects](../README.md)"]
    if i > 0:
        parts.append(f"[⬅️ {PROJECTS[i-1][0][:3].upper()} {PROJECTS[i-1][1]}](../{PROJECTS[i-1][0]}/README.md)")
    if i + 1 < len(PROJECTS):
        parts.append(f"[{PROJECTS[i+1][0][:3].upper()} {PROJECTS[i+1][1]} ➡️](../{PROJECTS[i+1][0]}/README.md)")
    bar = " · ".join(parts)
    nb = f" · [▶️ Open in Colab]({COLAB}15-projects/{folder}/colab_quickstart.ipynb)" \
        if (ROOT / "15-projects" / folder / "colab_quickstart.ipynb").exists() else ""
    top = (f"<!-- nav:start -->\n> {bar}  \n> **{folder[:3].upper()} · {title}** · {level} · "
           f"best after module {mod}{nb}\n<!-- nav:end -->\n\n")
    return top, f"\n\n<!-- nav:start -->\n---\n{bar}\n<!-- nav:end -->\n"


def apply_nav(path: Path, top: str, bottom: str) -> None:
    text = NAV_RE.sub("", path.read_text(encoding="utf-8")).strip("\n")
    path.write_text(top + text + bottom, encoding="utf-8")


def module_card(i: int) -> str:
    folder, icon, title, phase, weeks, summary, analogy = MODULES[i]
    lines = [f"<details>\n<summary><b>{icon} {folder[:2]} · {title}</b> &nbsp;—&nbsp; <i>week {weeks}</i></summary>\n"]
    lines.append(f"\n**What it is:** {summary}\n\n**Think of it like this:** {analogy}\n")
    t = topics(folder)
    if t:
        lines.append("\n**Topics you'll learn**\n")
        for j, (text, anchor) in enumerate(t, 1):
            lines.append(f"{j}. [{text}]({folder}/concepts.md#{anchor})")
    if folder == "15-projects":
        lines.append("\n**Projects**\n")
        for p, ptitle, level, mod in PROJECTS:
            lines.append(f"- [{p[:3].upper()} · {ptitle}](15-projects/{p}/) · {level}")
    nbs = sorted((ROOT / folder / "notebooks").glob("*.ipynb"))
    if nbs:
        lines.append("\n**Hands-on notebooks** (click ▶️ to run in your browser, no install)\n")
        for nb in nbs:
            name = re.sub(r"^\d+[-_]", "", nb.stem).replace("-", " ").replace("_", " ")
            name = name.replace("colab only", "(GPU, Colab only)")
            name = name[:1].upper() + name[1:]
            lines.append(f"- [{name}]({folder}/notebooks/{quote(nb.name)}) · "
                         f"[▶️ Colab]({COLAB}{folder}/notebooks/{quote(nb.name)})")
    if folder != "15-projects":
        lines.append(f"\n**Open:** {quick_links(folder, folder + '/')}\n")
    lines.append("\n</details>\n")
    return "\n".join(lines)


def count(pattern: str) -> int:
    return sum(1 for p in ROOT.rglob(pattern) if ".git" not in p.parts and ".ipynb_checkpoints" not in p.parts)


def readme() -> str:
    n_nb, n_slides = count("*.ipynb"), count("*.pptx")
    n_pdf = count("*.pdf")
    pages = ""
    try:
        from pypdf import PdfReader
        pages = f" ({len(PdfReader(str(ROOT / 'pdf' / 'AI-Engineer-Course-Book.pdf')).pages)} pages)"
    except Exception:  # noqa: BLE001
        pass
    badge = lambda label, msg, color: f"![{label}](https://img.shields.io/badge/{quote(label)}-{quote(msg)}-{color}?style=for-the-badge)"
    out = []
    out.append(f"""<div align="center">

# 🚀 Python to Pro — AI Engineer

### From *"I've never written code"* to *"I build, evaluate and ship LLM apps, RAG systems and agents"* in 24 weeks

{badge("modules", "17", "1B263B")} {badge("projects", "10", "0F9D9A")} {badge("notebooks", str(n_nb), "E45756")} {badge("duration", "24 weeks", "B279A2")} {badge("level", "beginner → pro", "4C78A8")}

**[🗺️ Roadmap](ROADMAP.md)** · **[📚 Course book PDF](pdf/AI-Engineer-Course-Book.pdf)** · **[🧑‍🏫 Trainer guide](TRAINER-GUIDE.md)** · **[🏗️ Projects](15-projects/)** · **[🔗 All resources](RESOURCES-MASTER.xlsx)** · **[❓ FAQ](#-faq)**

</div>

---

## 👋 What is this?

A complete, free course for **trainers and students who are starting from zero**. Every lesson is written in plain English: each piece of jargon is **defined the first time it appears**, and every big idea comes with an **everyday analogy** and a **diagram**.

Each of the 17 modules gives you everything needed to **learn it alone** and then **teach it to others**:

| 📖 Lesson | 📄 PDF | 📓 Notebooks | 🎞️ Slides | ✍️ Practice | 🧑‍🏫 Teaching kit |
|:--:|:--:|:--:|:--:|:--:|:--:|
| `concepts.md`: plain-English lesson with analogies and diagrams | Printable handout with a clickable contents page | Run in Colab with one click, no install needed | `.pptx` deck with speaker notes | Exercises easy → hard, with full solutions | Session plan, common mistakes, check questions |

## 🧭 Start here

| I am… | Do this first | Then |
|---|---|---|
| 🧑‍🏫 **A trainer** learning to teach this | Read the [Trainer guide](TRAINER-GUIDE.md) | Work through [00 · Setup](00-setup/) as a student, then each module's `trainer-notes.md` |
| 🎓 **A student** | Open the [Roadmap](ROADMAP.md) | Follow it week by week, starting at [00 · Setup](00-setup/) |
| 📖 **Someone who prefers reading** | Download the [course book PDF](pdf/AI-Engineer-Course-Book.pdf){pages} | Use the PDF's bookmarks panel to jump to any chapter |
| ⚡ **Already coding in Python** | Skim modules 01–02 | Jump to [04 · Machine Learning](04-machine-learning/) or [07 · LLMs](07-llms-and-genai/) |
| 🏷️ **Aiming at AI-trainer / annotation jobs** | Do 00 → 01 → 07 → 08 | Then [12 · Data annotation & RLHF](12-data-annotation-and-rlhf/) and [16 · Careers](16-careers/) |

## 🗺️ The learning path

```mermaid
flowchart LR
  subgraph P1["🧱 Part I · Foundations"]
    M00["00 Setup"] --> M01["01 Python"] --> M02["02 Data"] --> M03["03 Math"]
  end
  subgraph P2["🧠 Part II · ML, DL & NLP"]
    M04["04 ML"] --> M05["05 Deep learning"] --> M06["06 NLP"]
  end
  subgraph P3["🤖 Part III · LLM engineering"]
    M07["07 LLMs"] --> M08["08 Prompts"] --> M09["09 RAG"] --> M10["10 Agents"] --> M11["11 Automation"]
  end
  subgraph P4["🚀 Part IV · Production & careers"]
    M12["12 Annotation & RLHF"] --> M13["13 Fine-tuning"] --> M14["14 Deployment"] --> M16["16 Careers"]
  end
  M03 --> M04
  M06 --> M07
  M11 --> M12
```

![24-week roadmap](images/roadmap.png)

<sub>Each bar is a module; ◆ marks a project milestone. Full week-by-week plan with checkpoints: **[ROADMAP.md](ROADMAP.md)**.</sub>

## 📚 Download the PDFs

| PDF | What's inside | Best for |
|---|---|---|
| 📕 **[Course book](pdf/AI-Engineer-Course-Book.pdf)**{pages} | Every lesson in one book, organised as **Parts → Chapters → Sections**, with clickable contents and bookmarks | Reading offline, printing, tablets |
| 🧑‍🏫 **[Trainer handbook](pdf/Trainer-Handbook.pdf)** | Trainer guide, roadmap, plan, and **every module's session plan** | The trainer team |
| 🏗️ **[Projects guide](pdf/Projects-Guide.pdf)** | All 10 project write-ups with architecture and interview prep | Portfolio building |
| 📄 **Module handouts** | One short PDF per module (links in each module card below) | Handing out in class |

> 💡 **Tip:** in any PDF, open your reader's **bookmarks / outline panel** (sidebar) to see the full hierarchy and jump around. Every link to a notebook or file opens it on GitHub.

## 📦 All modules

| # | Module | Week | In one sentence | Open |
|:--:|---|:--:|---|---|""")
    for folder, icon, title, phase, weeks, summary, analogy in MODULES:
        links = []
        if (ROOT / folder / "concepts.md").exists():
            links.append(f"[📖]({folder}/concepts.md \"Lesson\")")
        f = first(folder, "pdf", "*-handout.pdf")
        if f:
            links.append(f"[📄]({folder}/{f} \"PDF handout\")")
        f = first(folder, "slides", "*.pptx")
        if f:
            links.append(f"[🎞️]({folder}/{f} \"Slides\")")
        if (ROOT / folder / "notebooks").exists():
            links.append(f"[📓]({folder}/notebooks/ \"Notebooks\")")
        out.append(f"| {folder[:2]} | {icon} **[{title}]({folder}/)** | {weeks} | {summary} | {' '.join(links) or '[🏗️](15-projects/)'} |")
    out.append("\n<sub>📖 lesson · 📄 PDF handout · 🎞️ slides · 📓 notebooks</sub>\n")

    out.append("## 🔍 Module details\n\nClick a module to see **what it is, an everyday analogy, every topic (each links straight to that section of the lesson), and its notebooks.**\n")
    for p_idx, (num, name, icon, desc) in enumerate(PHASES):
        out.append(f"### {icon} Part {num} · {name}\n\n*{desc}*\n")
        for i, m in enumerate(MODULES):
            if m[3] == p_idx:
                out.append(module_card(i))
    out.append("""## 🏗️ Projects

Ten portfolio projects that build on each other, from a beginner classifier to a fine-tuned model. Each has an **architecture diagram**, setup for **Colab and local**, a **file-by-file walkthrough** and a **"how to explain it in an interview"** section.

| # | Project | Level | Do it after |
|:--:|---|---|:--:|""")
    for p, title, level, mod in PROJECTS:
        out.append(f"| {p[:3].upper()} | [{title}](15-projects/{p}/) | {level} | module {mod} |")
    out.append(f"""
<sub>🟢 beginner · 🟡 intermediate · 🔴 advanced. How the projects connect: [15-projects](15-projects/README.md)</sub>

## 🧑‍🎓 How to study one module (about 8–10 hours)

1. **Read** the module's `README.md`: goals, prerequisites, time and which tool to use.
2. **Learn** from `concepts.md` (or its PDF handout). Don't skip the analogies.
3. **Do** the notebooks in order. Press ▶️ **Colab**, then run each cell and read the text above it.
4. **Practise** with `exercises.md`. Try them before opening `solutions/`.
5. **Check** yourself against that week's checkpoint in the [Roadmap](ROADMAP.md).
6. **Teaching it?** Read `trainer-notes.md` and present from `slides/`.

## ⚡ Quick start

**Option A: no install (recommended to begin).** Click any **▶️ Colab** link above. It opens in Google Colab, then press *Runtime → Run all*.

**Option B: on your own computer**
```bash
git clone https://github.com/{REPO}.git
cd AI-Engineer
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
jupyter lab                      # or open the folder in VS Code
```

## ❓ FAQ

<details><summary><b>Do I need to know programming or maths first?</b></summary>

No. Module 00 starts from installing Python, and module 03 teaches only the maths intuition you need, with pictures and no proofs.
</details>

<details><summary><b>Do I need a GPU or a powerful laptop?</b></summary>

No. Every notebook runs on an ordinary CPU or on free Google Colab. Only two optional fine-tuning notebooks need Colab's free T4 GPU, and they say so at the top.
</details>

<details><summary><b>Do I need paid API keys (OpenAI, Anthropic, Gemini)?</b></summary>

No. Every notebook runs without keys, using small free models or clearly labelled stand-ins. If you have a key, copy a `.env.example` to `.env` and add it, and the notebooks will use the real API. **Never commit `.env` to GitHub.**
</details>

<details><summary><b>How long does it take?</b></summary>

About 24 weeks at 8–10 hours a week. The [Roadmap](ROADMAP.md) also has a 12-week fast track, an 8-week AI-trainer track and a 36-week part-time plan.
</details>

<details><summary><b>I'm a trainer. How do we split the course across a team?</b></summary>

See the [Trainer guide](TRAINER-GUIDE.md). It covers team roles, a suggested split for 5 trainers, a 4-week ramp-up plan and how to run each week. Every module's session plan is collected in the [Trainer handbook PDF](pdf/Trainer-Handbook.pdf).
</details>

<details><summary><b>Where do the external links come from?</b></summary>

From nine curated open-source lists plus official documentation. Every resource is in [RESOURCES-MASTER.xlsx](RESOURCES-MASTER.xlsx) (filter by module, type, level and free/paid). Sources and licences are listed in [SOURCES.md](SOURCES.md).
</details>

## 🛠️ For maintainers

| Command | What it does |
|---|---|
| `python NN-module/build.py` | Rebuild one module's slides, notebooks, diagrams and Excel |
| `python tools/build_pdfs.py` | Rebuild the course book, trainer handbook, projects guide and all handouts |
| `python tools/build_readme.py` | Rebuild this README and the navigation bars on every page |
| `python tools/build_root.py` | Rebuild the roadmap image and `RESOURCES-MASTER.xlsx` |
| `python tools/check_module.py --all --run` | Check every module against the standard and run every notebook |

Rules for writing a module: [tools/MODULE-STANDARD.md](tools/MODULE-STANDARD.md) · Plan: [PLAN.md](PLAN.md)

## 📜 Licence

Course material and code: [MIT](LICENSE). Linked third-party resources keep their own licences ([SOURCES.md](SOURCES.md)).

<div align="center"><sub>{n_nb} notebooks · {n_slides} slide decks · {n_pdf} PDFs · 17 modules · 10 projects</sub></div>
""")
    return "\n".join(out)


def main() -> None:
    for i, (folder, *_rest) in enumerate(MODULES):
        for page in ["README.md", "concepts.md"]:
            p = ROOT / folder / page
            if p.exists() and not (folder == "15-projects" and page == "concepts.md"):
                apply_nav(p, *module_nav(i, page))
    for i, (folder, *_rest) in enumerate(PROJECTS):
        p = ROOT / "15-projects" / folder / "README.md"
        if p.exists():
            apply_nav(p, *project_nav(i))
    (ROOT / "README.md").write_text(readme(), encoding="utf-8")
    print("README.md and navigation bars updated")


if __name__ == "__main__":
    main()
