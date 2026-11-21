# Module Standard (read before building or editing any module)

This curriculum is written for **a trainer who knows nothing yet**. They learn the topic from this repo alone, then teach it to students. So:

- Explain at true beginner level. **Define every piece of jargon the first time it appears in each file** (bold the term, then a plain-English definition, e.g. "**array** — a grid of numbers that all have the same type").
- Use an everyday analogy for every major concept.
- Short sentences. No "simply", "just", "obviously".
- Your own words only. Link to sources; never paste large chunks from them. Quotes ≤ 15 words, and rarely.
- Never put an API key, token or password in any file. Read keys from environment variables / a `.env` file; ship `.env.example` with placeholders like `ANTHROPIC_API_KEY=your-key-here`.

## Folder layout (every module `NN-name/`)

```
NN-name/
  README.md          goals, prerequisites, time estimate, which tool (Colab / Jupyter / VS Code) and why, file map
  concepts.md        the main lesson: plain-English explanations + analogies + embedded diagrams
  images/            PNG diagrams you create (Mermaid via build_kit.mermaid, or matplotlib) + .mmd sources
  notebooks/         runnable .ipynb (Open-in-Colab badge first, markdown cell before EVERY code cell)
  code/              .py scripts; comment every line or small group of lines in plain English
  slides/            NN-name.pptx teaching deck (build_kit.slides), 12-20 slides with speaker notes
  pdf/               NN-name-handout.pdf generated from concepts.md (build_kit.pdf_from_markdown)
  excel/             .xlsx where useful (practice data, cheat sheet, resource tracker) (build_kit.workbook)
  exercises.md       8-15 exercises, graded easy -> hard
  solutions/         worked solutions (.md and/or .py), one per exercise or one combined file
  trainer-notes.md   how to teach it, common student mistakes (with fixes), a 1-2 hour session plan table
  resources.md       best links (from /home/claude/work/source-notes/<module>.md), each with one line on why
  build.py           regenerates images/, notebooks/, slides/, pdf/, excel/ from source (uses tools/build_kit.py)
```

`build.py` starts with:

```python
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook
```

and must be re-runnable (`python NN-name/build.py`). Write the markdown files by hand first; build.py makes the generated artefacts. The PDF must be built AFTER concepts.md and images exist.

## Notebook rules

- Build notebooks with `build_kit.notebook([...])` so the badge and the markdown-before-code rule are automatic.
- Each notebook must run **top to bottom with no internet API keys** on a CPU in under ~10 minutes. Verify with `python tools/check_module.py NN-name --run` — it must print PASS.
- Code that needs an API key (OpenAI / Anthropic / Gemini) must detect the missing key and fall back to a clearly-labelled offline stand-in (e.g. a fake response object or a tiny local model) so the notebook still runs. Show the real call in the code, guarded by `if os.getenv("ANTHROPIC_API_KEY"):`.
- Hugging Face downloads work; prefer tiny models (e.g. `sshleifer/tiny-gpt2`, `sentence-transformers/all-MiniLM-L6-v2`, `distilbert-base-uncased-finetuned-sst-2-english`, `HuggingFaceTB/SmolLM2-135M-Instruct`).
- Avoid datasets that download at run time from non-HF hosts (no `sklearn.datasets.fetch_*`, no torchvision downloads). Use `sklearn.datasets.load_*`, generated synthetic data, or small CSVs you create in the module's folder.
- A notebook that genuinely needs a GPU must have `colab-only` in its filename (e.g. `03-qlora-colab-only.ipynb`); it is not executed locally, so be extra careful it is correct and say "Runtime → Change runtime type → T4 GPU" in its first cell.
- Notebooks keep their executed outputs (check_module --run saves them) so students can preview on GitHub.
- Use relative paths that work both locally (cwd = notebooks/) and in Colab. If a notebook needs a data file from the repo, include a cell that downloads it from `https://raw.githubusercontent.com/vvvvvivekkk/AI-Engineer/main/...` when the file isn't found locally.

## Slides
12-20 content slides: what/why, analogy, diagram slides (use images/), a code slide or two, common mistakes, recap, exercise prompt. Speaker notes on every slide written so a new trainer can read them aloud.

## trainer-notes.md must include
1. What students should be able to do after the session
2. Teaching sequence + timing table for a 1-2 hour session (e.g. | 0:00-0:10 | Hook / analogy | ... |)
3. Common student mistakes and how to fix them (at least 6)
4. Questions to check understanding (with answers)
5. How to adapt for faster / slower groups

## Style for diagrams
Mermaid `flowchart LR` or `TD`, short labels, ≤ 12 nodes per diagram. Every concepts.md has at least 2 embedded diagrams: `![Alt text](images/name.png)`.

## Done = 
`python NN-name/build.py && python tools/check_module.py NN-name --run` prints `[PASS]`.
Do not run git commands; the lead commits.
