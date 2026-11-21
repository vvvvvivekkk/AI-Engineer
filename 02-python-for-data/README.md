# Module 02 — Python for Data (NumPy, pandas, matplotlib, Excel)

**Weeks 4–5 of the course · about 8–12 hours of study for a learner · two 2-hour teaching sessions**

## Goals
After this module you can:
- work with NumPy arrays (shape, slicing, `axis`, vectorised maths, masks)
- load CSV and Excel files into pandas, inspect them and clean them
- answer questions with filtering, `groupby`, `pivot_table` and `merge`
- draw clear line, bar, histogram and scatter charts with matplotlib
- read multiple Excel sheets and write styled, multi-sheet Excel reports (pandas + openpyxl)
- run a small exploratory data analysis (EDA) from questions to written findings

## Prerequisites
- Module 00 (setup) and Module 01 (Python basics): variables, lists, dicts, loops, functions, `import`.
- Libraries: `numpy`, `pandas`, `matplotlib`, `openpyxl` (all pre-installed in Google Colab; locally `pip install numpy pandas matplotlib openpyxl`).
- Built and tested with NumPy 2.5 and **pandas 3.0**. pandas 3 changed a few old habits (see the warning box in `concepts.md` §4.2).

## Which tool to use, and why
- **Google Colab** — recommended for students. Nothing to install, and the notebooks download the practice data automatically. Click the "Open in Colab" badge at the top of each notebook.
- **Jupyter / VS Code with the Jupyter extension** — recommended for trainers preparing the session, because you can open the Excel outputs directly in Excel or LibreOffice next to the notebook.
- **VS Code (plain `.py` files)** — for the scripts in `code/` and `solutions/solutions.py`.

## Suggested order
1. Read `concepts.md` (or the PDF handout) sections 1–4.
2. Run `notebooks/01-numpy-basics.ipynb` and `notebooks/02-pandas-loading-and-cleaning.ipynb`.
3. Read `concepts.md` sections 5–9.
4. Run `notebooks/03-groupby-merge-excel.ipynb` and `notebooks/04-mini-eda.ipynb`.
5. Do `exercises.md`; check with `solutions/`.

## File map
| Path | What it is |
|---|---|
| `concepts.md` | The main lesson, with analogies and diagrams |
| `pdf/02-python-for-data-handout.pdf` | `concepts.md` as a printable handout |
| `notebooks/01-numpy-basics.ipynb` | Arrays, shapes, slicing, vectorisation (timed), axis, masks, broadcasting, seeds |
| `notebooks/02-pandas-loading-and-cleaning.ipynb` | Load CSV/Excel, first-look checks, filtering, dates; cleaning a messy file |
| `notebooks/03-groupby-merge-excel.ipynb` | groupby, pivot tables, merge (left vs inner), multi-sheet Excel report styled with openpyxl |
| `notebooks/04-mini-eda.ipynb` | A full mini-EDA on sales and student data with charts and written findings |
| `data/` | Practice CSVs: `sales.csv` (600 orders), `customers.csv`, `products.csv`, `students.csv`, `sales_messy.csv` (dirty on purpose) |
| `excel/practice-datasets.xlsx` | The same datasets as sheets of one workbook (About, Sales, Customers, Products, Students, Messy_Sales) |
| `excel/pandas-cheatsheet.xlsx` | One-page reference of every command in this module, filterable by area |
| `code/numpy_basics.py` | NumPy tour as a commented script |
| `code/clean_messy_sales.py` | The cleaning checklist as a reusable function |
| `code/excel_report.py` | Read all sheets → summarise → write and style a multi-sheet report |
| `code/mini_eda.py` | Compact EDA that saves charts as PNG files |
| `slides/02-python-for-data.pptx` | 18-slide teaching deck with speaker notes |
| `exercises.md` / `solutions/` | 12 exercises (easy → hard) with worked answers and runnable code |
| `trainer-notes.md` | Learning outcomes, timing tables, common mistakes, check questions |
| `resources.md` | Curated links |
| `images/` | Diagrams used in the lesson (`.mmd` files are editable Mermaid sources) |
| `build.py`, `make_data.py`, `nb_cells.py` | Regenerate data, images, notebooks, slides, Excel and PDF |

## About the data
All datasets are **synthetic** (made up by `make_data.py` with random seed 42) but shaped like real business and school data: Indian cities, rupee prices, six months of orders, some customers who buy much more than others, and deliberate problems (duplicates, blanks, mixed spellings, prices stored as text, an unknown customer ID). Nothing is real personal data.

Scripts and notebooks write their results into an `outputs/` folder, which git ignores.

## Rebuild everything
```bash
python 02-python-for-data/build.py
python tools/check_module.py 02-python-for-data --run
```
