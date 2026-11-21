<!-- nav:start -->
> [🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 00 Setup](../00-setup/README.md) · [02 Python for Data ➡️](../02-python-for-data/README.md)  
> **🐍 Module 01 · Python Basics**  
> [📖 Lesson](concepts.md) · [📄 PDF handout](pdf/01-python-basics-handout.pdf) · [🎞️ Slides](slides/01-python-basics.pptx) · [📓 Notebooks](notebooks/) · [✍️ Exercises](exercises.md) · [✅ Solutions](solutions/) · [🧑‍🏫 Trainer notes](trainer-notes.md) · [🔗 Resources](resources.md)
<!-- nav:end -->

# Module 01 — Python basics (weeks 2–3)

Zero-to-confident Python for future AI engineers. You learn the core language with many small runnable examples, practise reading error messages calmly, and finish with a mini-project.

## Goals

After this module you can:

1. Use values, **types** (`int`, `float`, `str`, `bool`, `None`) and **variables** (names that refer to values), and convert between types.
2. Work with strings: indexing, slicing, methods and **f-strings** (text with values inserted).
3. Choose and use the four built-in **collections**: list, tuple, dict and set.
4. Make decisions with `if` / `elif` / `else` and repeat work with `for` and `while`.
5. Write list, dict and set **comprehensions** (one-line collection builders).
6. Write **functions** with parameters, defaults, keyword arguments and return values.
7. Handle errors with `try` / `except` / `else` / `finally` and raise your own.
8. **Read a traceback** (Python's error report) from the bottom up and find the line to fix.
9. Read and write text and JSON files with `open`, `pathlib` and `json`.
10. Import standard-library modules and your own `.py` files.
11. Write and use a simple **class** (a blueprint for objects).

## Prerequisites

Module 00 (Python installed, or a Google Colab account; you know how to run a notebook cell and a `.py` file). No programming experience needed.

## Time estimate

- Reading `concepts.md`: 2–3 hours
- Four notebooks: 4–5 hours
- Exercises: 4–6 hours
- Teaching: two 2-hour sessions (see `trainer-notes.md`)

## Which tool, and why

**Notebooks first (Colab or VS Code/Jupyter), then VS Code for scripts.** Notebooks give instant feedback after every line, which is ideal while learning syntax. Click the **Open in Colab** badge at the top of each notebook if you have nothing installed. Run the scripts in `code/` from the **VS Code terminal** to get used to real `.py` programs and real tracebacks. The text adventure needs a terminal because it waits for typed input.

## File map

| Path | What it is |
|---|---|
| `concepts.md` | The main lesson, with diagrams. Read it first. |
| `images/` | Diagrams (PNG) and their Mermaid sources (`.mmd`). |
| `notebooks/01-basics.ipynb` | print, types, variables, arithmetic, strings, f-strings, if/elif/else, loops. |
| `notebooks/02-collections.ipynb` | Lists, tuples, dicts, sets, the copy trap, counting, comprehensions. |
| `notebooks/03-functions-errors-files.ipynb` | Functions, exceptions, reading tracebacks, files, JSON, modules, classes. |
| `notebooks/04-mini-project-grade-calculator.ipynb` | Mini-project: messy CSV → graded report → JSON; bonus text adventure. |
| `code/basics_tour.py` | Values, strings, conditions and loops in one commented script. |
| `code/collections_tour.py` | Lists, tuples, dicts, sets, comprehensions. |
| `code/student.py` | A small class, also importable as a module. |
| `code/traceback_demo.py` | Six common errors with full tracebacks; `--crash` for a real crash. |
| `code/grade_calculator.py` | The mini-project as a script; accepts your own CSV path. |
| `code/text_adventure.py` | A playable text game (`--auto` replays a winning run). |
| `slides/01-python-basics.pptx` | 18-slide deck with speaker notes. |
| `pdf/01-python-basics-handout.pdf` | The lesson as a printable handout. |
| `excel/python-cheatsheet.xlsx` | Cheat sheet (topic, concept, syntax, example, common mistake) and an error guide. |
| `exercises.md` | 14 exercises, easy to hard. |
| `solutions/solutions.py` | Runnable solutions for every exercise. `solutions/solutions.md` explains them. |
| `trainer-notes.md` | Session plans, common mistakes, check questions. |
| `resources.md` | Best external links, each with a reason. |
| `build.py` | Regenerates images, notebooks, slides, PDF and Excel: `python 01-python-basics/build.py`. |

## Quick start

```bash
cd AI-Engineer/01-python-basics
python code/basics_tour.py
python code/traceback_demo.py
python code/text_adventure.py
```

<!-- nav:start -->
---
[🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 00 Setup](../00-setup/README.md) · [02 Python for Data ➡️](../02-python-for-data/README.md)
<!-- nav:end -->
