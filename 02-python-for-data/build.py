import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook

sys.path.insert(0, str(HERE))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

import make_data
from nb_cells import all_notebooks

IMG = HERE / "images"
NAVY, TEAL, GREY = "#1B263B", "#0F9D9A", "#5A6370"


# ---------------------------------------------------------------- diagrams (Mermaid)
def mermaid_diagrams():
    mermaid("""
flowchart LR
    A[Load<br/>CSV / Excel] --> B[Inspect<br/>shape, info, describe]
    B --> C[Clean<br/>duplicates, blanks, types]
    C --> D[Transform<br/>new columns, merge]
    D --> E[Analyse<br/>groupby, pivot]
    E --> F[Visualise<br/>matplotlib]
    F --> G[Save<br/>CSV / Excel report]
""", IMG / "data_workflow.png")
    mermaid("""
flowchart TD
    A[Messy file] --> B[1. Remove duplicate rows]
    B --> C[2. Clean text<br/>strip, title case, merge spellings]
    C --> D[3. Fix types<br/>text prices to numbers, dates]
    D --> E[4. Missing values<br/>drop, fill or keep]
    E --> F[5. Impossible values<br/>negative quantity]
    F --> G[Clean table + notes on every rule]
""", IMG / "cleaning_checklist.png")
    mermaid("""
flowchart LR
    T[Full table<br/>600 orders] --> S1[App rows]
    T --> S2[Store rows]
    T --> S3[Website rows]
    S1 --> A1[sum revenue]
    S2 --> A2[sum revenue]
    S3 --> A3[sum revenue]
    A1 --> C[Small result table<br/>one row per channel]
    A2 --> C
    A3 --> C
""", IMG / "split_apply_combine.png")
    mermaid("""
flowchart LR
    X[practice-datasets.xlsx<br/>several sheets] -->|pd.read_excel<br/>sheet_name=None| P[dict of DataFrames]
    P --> Q[clean, merge,<br/>groupby]
    Q -->|pd.ExcelWriter| R[report.xlsx<br/>one sheet per table]
    R -->|openpyxl| S[styled report<br/>bold headers, formats, formulas]
""", IMG / "excel_roundtrip.png")


# ---------------------------------------------------------------- diagrams (matplotlib)
def draw_grid(ax, x0, y0, rows, cols, vals=None, color=TEAL, size=0.6):
    for r in range(rows):
        for c in range(cols):
            ax.add_patch(Rectangle((x0 + c * size, y0 - r * size), size, size, facecolor=color,
                                   edgecolor="white", lw=2, alpha=0.85))
            if vals is not None:
                ax.text(x0 + c * size + size / 2, y0 - r * size + size / 2, str(vals[r][c]),
                        ha="center", va="center", color="white", fontsize=10, weight="bold")


def fig_array_shapes():
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.set_xlim(0, 12); ax.set_ylim(-2.5, 2); ax.axis("off")
    draw_grid(ax, 0.3, 0.5, 1, 4, [[799, 2499, 1199, 249]])
    ax.text(1.5, -0.6, "1-D array\nshape (4,)\none row of prices", ha="center", fontsize=11, color=NAVY)
    draw_grid(ax, 3.8, 1.1, 3, 2, [[80, 72], [65, 90], [70, 88]], color=NAVY)
    ax.text(4.4, -1.5, "2-D array\nshape (3, 2)\n3 students x 2 subjects", ha="center", fontsize=11, color=NAVY)
    for k, col in enumerate([TEAL, "#3BB4B1", "#76CFCC"]):
        draw_grid(ax, 7.6 + k * 0.35, 1.1 - k * 0.35, 3, 3, color=col)
    ax.text(8.8, -1.9, "3-D array\nshape (3, 3, 3)\ne.g. height x width x colour", ha="center", fontsize=11, color=NAVY)
    ax.set_title("Arrays: 1-D, 2-D and 3-D", fontsize=14, color=NAVY)
    fig.savefig(IMG / "array_shapes.png", dpi=150, bbox_inches="tight"); plt.close(fig)


def fig_merge_joins():
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    from matplotlib.patches import Circle
    titles = [("inner", "keep only matches"), ("left", "keep all left rows"), ("outer", "keep everything")]
    for ax, (name, sub) in zip(axes, titles):
        ax.set_xlim(-2.2, 2.2); ax.set_ylim(-1.6, 1.6); ax.set_aspect("equal"); ax.axis("off")
        left_fill = TEAL if name in ("left", "outer") else "white"
        right_fill = TEAL if name == "outer" else "white"
        ax.add_patch(Circle((-0.55, 0), 1.0, facecolor=left_fill, edgecolor="none", alpha=0.6))
        ax.add_patch(Circle((0.55, 0), 1.0, facecolor=right_fill, edgecolor="none", alpha=0.6))
        # the overlap (matching rows) is kept by every join type
        clip = Circle((0.55, 0), 1.0, transform=ax.transData)
        ov = Circle((-0.55, 0), 1.0, facecolor=TEAL, edgecolor="none", alpha=0.95)
        ax.add_patch(ov); ov.set_clip_path(clip)
        ax.add_patch(Circle((-0.55, 0), 1.0, facecolor="none", edgecolor=NAVY, lw=2))
        ax.add_patch(Circle((0.55, 0), 1.0, facecolor="none", edgecolor=NAVY, lw=2))
        ax.text(-1.0, 0, "sales", ha="center", va="center", fontsize=10, color=NAVY)
        ax.text(1.0, 0, "customers", ha="center", va="center", fontsize=9, color=NAVY)
        ax.text(0, 0, "match", ha="center", va="center", fontsize=9, color=NAVY, weight="bold",
                bbox=dict(facecolor=TEAL, edgecolor="none", alpha=0.9, boxstyle="round"))
        ax.set_title(f'how="{name}"\n{sub}', color=NAVY, fontsize=12)
    fig.suptitle("Shaded = rows kept after the merge", color=GREY, y=0.02, fontsize=10)
    fig.savefig(IMG / "merge_joins.png", dpi=150, bbox_inches="tight"); plt.close(fig)


def fig_chart_gallery(d):
    sales, products, students = d["sales"].copy(), d["products"], d["students"]
    sales["revenue"] = sales["quantity"] * sales["unit_price"] * (1 - sales["discount_pct"] / 100)
    full = sales.merge(products.drop(columns="unit_price"), on="product_id")
    monthly = sales.groupby(sales["order_date"].dt.to_period("M"))["revenue"].sum() / 1000
    by_cat = full.groupby("category")["revenue"].sum().sort_values() / 1000
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    axes[0, 0].plot(monthly.index.astype(str), monthly.values, marker="o", color=NAVY)
    axes[0, 0].set_title("LINE: change over time"); axes[0, 0].set_ylabel("revenue (k Rs)")
    axes[0, 0].set_ylim(0, monthly.max() * 1.15)
    axes[0, 1].barh(by_cat.index, by_cat.values, color=TEAL)
    axes[0, 1].set_title("BAR: compare groups"); axes[0, 1].set_xlabel("revenue (k Rs)")
    axes[1, 0].hist(students["math"], bins=15, color=TEAL, edgecolor="white")
    axes[1, 0].set_title("HISTOGRAM: how values spread"); axes[1, 0].set_xlabel("maths score"); axes[1, 0].set_ylabel("students")
    axes[1, 1].scatter(students["study_hours_per_week"], students["math"], color=NAVY, alpha=0.6, s=18)
    axes[1, 1].set_title("SCATTER: do two numbers move together?"); axes[1, 1].set_xlabel("study hours / week"); axes[1, 1].set_ylabel("maths score")
    fig.tight_layout()
    fig.savefig(IMG / "chart_gallery.png", dpi=150, bbox_inches="tight"); plt.close(fig)


def fig_missing_map(d):
    messy = d["messy"].copy()
    messy["city"] = messy["city"].replace("", np.nan)
    m = messy.isna().to_numpy().T.astype(int)
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.imshow(m, aspect="auto", cmap=matplotlib.colors.ListedColormap(["#E8EEF2", "#D1495B"]))
    ax.set_yticks(range(len(messy.columns)), messy.columns)
    ax.set_xlabel("row number"); ax.set_title("Where are the blanks in sales_messy.csv? (red = missing)", color=NAVY)
    fig.savefig(IMG / "missing_map.png", dpi=150, bbox_inches="tight"); plt.close(fig)


# ---------------------------------------------------------------- Excel cheat sheet
def cheat_sheet():
    rows = [["Area", "Task", "Code", "Notes"]]
    add = lambda *r: rows.append(list(r))
    add("Import", "Standard imports", "import numpy as np; import pandas as pd; import matplotlib.pyplot as plt", "Everyone uses these nicknames")
    add("NumPy", "Make an array", "np.array([1, 2, 3])", "All items share one dtype")
    add("NumPy", "Shape / dims / type", "a.shape, a.ndim, a.dtype", "Check these first")
    add("NumPy", "Evenly spaced numbers", "np.arange(0, 10, 2); np.linspace(0, 1, 5)", "linspace includes both ends")
    add("NumPy", "Slice 2-D", "a[row, col]; a[:, 0]; a[1:3, :2]", ": means everything along that direction")
    add("NumPy", "Aggregate per column / row", "a.mean(axis=0); a.sum(axis=1)", "axis=0 squashes rows away -> one value per column")
    add("NumPy", "Filter with a mask", "a[a > 10]", "Comparison gives True/False array")
    add("NumPy", "Reshape", "a.reshape(3, 4); a.reshape(2, -1)", "-1 = work it out")
    add("NumPy", "Seeded random numbers", "rng = np.random.default_rng(42); rng.integers(1, 7, 5)", "Same seed -> same numbers")
    add("Load", "Read CSV", 'pd.read_csv("data/sales.csv", parse_dates=["order_date"])', "parse_dates makes real dates")
    add("Load", "Read one Excel sheet", 'pd.read_excel("file.xlsx", sheet_name="Sales")', "Needs openpyxl installed")
    add("Load", "Read ALL Excel sheets", 'pd.read_excel("file.xlsx", sheet_name=None)', "Returns dict {sheet name: DataFrame}")
    add("Load", "Read part of a sheet", 'pd.read_excel(p, sheet_name="Sales", usecols="A:E", nrows=100)', "")
    add("Inspect", "Size", "df.shape", "(rows, columns)")
    add("Inspect", "First / last rows", "df.head(); df.tail(3)", "")
    add("Inspect", "Types and blanks", "df.info()", "")
    add("Inspect", "Summary statistics", "df.describe()", "count, mean, std, min, quartiles, max")
    add("Inspect", "Blanks per column", "df.isna().sum()", "")
    add("Inspect", "Count categories", 'df["city"].value_counts()', "Best way to spot typos")
    add("Select", "One column (Series)", 'df["price"]', "")
    add("Select", "Several columns", 'df[["a", "b"]]', "Double brackets")
    add("Select", "By label", 'df.loc[df["qty"] > 3, ["order_id", "qty"]]', "rows, columns")
    add("Select", "By position", "df.iloc[0:5, 0:3]", "")
    add("Filter", "One condition", 'df[df["qty"] > 3]', "")
    add("Filter", "Two conditions", 'df[(df["a"] > 1) & (df["b"] == "App")]', "Use & and |, brackets around each")
    add("Filter", "In a list", 'df[df["city"].isin(["Pune", "Delhi"])]', "")
    add("Transform", "New column", 'df["revenue"] = df["qty"] * df["price"]', "Vectorised")
    add("Transform", "Sort", 'df.sort_values("revenue", ascending=False)', "")
    add("Transform", "Rename columns", 'df.rename(columns={"old": "new"})', "")
    add("Transform", "Date parts", 'df["d"].dt.month; df["d"].dt.day_name(); df["d"].dt.to_period("M")', "Column must be datetime")
    add("Transform", "Convert type", 'df["qty"].astype(int); pd.to_datetime(df["d"])', "")
    add("Clean", "Drop duplicates", "df.drop_duplicates()", "Count rows before/after")
    add("Clean", "Drop rows with blanks", 'df.dropna(subset=["order_date"])', "")
    add("Clean", "Fill blanks", 'df["qty"] = df["qty"].fillna(df["qty"].median())', "pandas 3: do NOT use inplace=True on a column")
    add("Clean", "Tidy text", 'df["city"].str.strip().str.title()', "")
    add("Clean", "Merge spellings", 'df["city"].replace({"Bangalore": "Bengaluru"})', "")
    add("Clean", "Text to number", 'df["price"].str.replace(r"[^0-9.]", "", regex=True).astype(float)', "Removes Rs, commas")
    add("Group", "Sum per group", 'df.groupby("city")["revenue"].sum()', "")
    add("Group", "Named aggregation", 'df.groupby("city").agg(orders=("order_id", "count"), rev=("revenue", "sum"))', "new=(column, function)")
    add("Group", "Two keys", 'df.groupby(["month", "channel"])["revenue"].sum().unstack()', "unstack -> columns")
    add("Group", "Pivot table", 'pd.pivot_table(df, index="month", columns="channel", values="revenue", aggfunc="sum")', "margins=True adds totals")
    add("Merge", "Left join", 'sales.merge(customers, on="customer_id", how="left")', "Keeps every sale")
    add("Merge", "Check matches", 'sales.merge(c, on="customer_id", how="left", indicator=True)["_merge"].value_counts()', "left_only = no match")
    add("Merge", "Stack tables vertically", "pd.concat([df1, df2], ignore_index=True)", "Same columns")
    add("Excel", "Write one sheet", 'df.to_excel("out.xlsx", sheet_name="Data", index=False)', "")
    add("Excel", "Write many sheets", 'with pd.ExcelWriter("out.xlsx", engine="openpyxl") as w: df.to_excel(w, sheet_name="A")', "One with-block, many to_excel calls")
    add("Excel", "Open for styling", 'from openpyxl import load_workbook; wb = load_workbook("out.xlsx"); ws = wb["A"]', "")
    add("Excel", "Bold header", "for c in ws[1]: c.font = Font(bold=True)", "from openpyxl.styles import Font")
    add("Excel", "Column width / format", 'ws.column_dimensions["A"].width = 18; ws["C2"].number_format = "#,##0"', "")
    add("Excel", "Live formula", 'ws["D2"] = "=B2/C2"; wb.save("out.xlsx")', "Excel calculates it on open")
    add("Save", "Write CSV", 'df.to_csv("out.csv", index=False)', "")
    add("Plot", "Figure + axes", "fig, ax = plt.subplots(figsize=(8, 4))", "")
    add("Plot", "Line / bar / hist / scatter", "ax.plot(x, y); ax.bar(x, h); ax.hist(v, bins=20); ax.scatter(x, y)", "Pick chart from the question")
    add("Plot", "Labels", 'ax.set_title("..."); ax.set_xlabel("..."); ax.set_ylabel("...")', "Always label with units")
    add("Plot", "Save image", 'fig.savefig("chart.png", dpi=150, bbox_inches="tight")', "")
    add("Plot", "Quick pandas plot", 'df.groupby("city")["revenue"].sum().plot(kind="bar")', "Uses matplotlib underneath")
    workbook({"pandas cheat sheet": rows}, HERE / "excel" / "pandas-cheatsheet.xlsx",
             col_widths={"pandas cheat sheet": [11, 26, 80, 42]})


# ---------------------------------------------------------------- slides
def deck():
    I = lambda n: str(IMG / n)
    return {
        "title": "Module 02 - Python for Data",
        "subtitle": "NumPy, pandas, matplotlib and Excel",
        "slides": [
            {"title": "Why data skills come first",
             "bullets": ["Every AI system learns from data", "Someone must load, check, clean and reshape it",
                         "Much of a real ML project is data preparation", "Today: NumPy, pandas, matplotlib, Excel"],
             "notes": "Start with the big picture. Every model they will build later, from a spam filter to a RAG chatbot, needs data that a person has loaded and cleaned. Today we learn the three libraries that do that work: NumPy for numbers, pandas for tables, matplotlib for charts, plus reading and writing Excel."},
            {"title": "The data workflow", "image": I("data_workflow.png"),
             "bullets": ["Load", "Inspect", "Clean", "Transform", "Analyse", "Visualise", "Save"],
             "notes": "This is the map for the whole session. Read the seven steps aloud. Tell students every notebook walks along this line, and when they are lost they should ask: which step am I on?"},
            {"title": "NumPy array = egg tray of numbers", "image": I("array_shapes.png"),
             "bullets": ["All items share one type (dtype)", "shape = size along each direction", "1-D row, 2-D table, 3-D stack"],
             "notes": "An array is a grid of numbers of the same type. Use the egg tray analogy: one row of eggs is 1-D, a whole tray is 2-D, a stack of trays is 3-D. Always check shape, ndim and dtype first. Ask: what is the shape of a table with 5 students and 3 subjects? Answer: (5, 3)."},
            {"title": "Vectorisation: one beep for the whole trolley",
             "bullets": ["List * 2 repeats the list", "Array * 2 doubles every number", "No Python loop -> tens to hundreds of times faster",
                         "Shorter code, fewer bugs"],
             "code": "import numpy as np\nq = np.array([2, 1, 3])\np = np.array([799, 2499, 1199])\nbill = q * p          # item by item\nprint(bill.sum())",
             "notes": "Show the list versus array difference live. Then run the timing cell in notebook 01. The analogy: a loop is a cashier scanning each item; vectorisation is a scanner reading the whole trolley in one beep."},
            {"title": "axis: the most confused word in NumPy",
             "bullets": ["axis=0 squashes the rows away", "  -> one answer per column", "axis=1 squashes the columns away", "  -> one answer per row",
                         "Masks: a[a > 10] keeps the True positions"],
             "code": "scores.mean(axis=0)  # per subject\nscores.mean(axis=1)  # per student\nprices[prices > 1000]",
             "notes": "Draw a 3 by 2 table on the board. Point down the columns for axis 0 and across the rows for axis 1. Make students predict the shape of the answer before running the code. Then introduce masks: a comparison makes True and False values, and putting them in brackets filters."},
            {"title": "pandas: Excel you can rerun",
             "bullets": ["Series = one labelled column", "DataFrame = a table of Series", "index = the row labels",
                         "read_csv / read_excel load files"],
             "code": "import pandas as pd\nsales = pd.read_csv('data/sales.csv',\n          parse_dates=['order_date'])\nsales.head()",
             "notes": "A DataFrame is a spreadsheet tab, a Series is one column, the index is the grey row numbers. The big advantage over Excel: every step is written down as code, so it can be rerun on next month's file in one second."},
            {"title": "Five first-look questions",
             "bullets": ["df.shape - how big?", "df.head() - what does it look like?", "df.info() - types and blanks",
                         "df.describe() - typical values", "df.isna().sum() - blanks per column"],
             "notes": "Make these five a habit. Have students run them on sales.csv and say one thing they learned from each. For describe, explain median as the middle value and std as how spread out the numbers are."},
            {"title": "Selecting and filtering",
             "bullets": ['df["col"] -> Series; df[["a","b"]] -> DataFrame', "Conditions make a True/False mask", "Use & and |, brackets around each condition",
                         "loc = by label, iloc = by position"],
             "code": "df[(df['channel'] == 'App')\n   & (df['discount_pct'] > 0)]\ndf.loc[df['qty'] > 3, ['order_id','qty']]\ndf.iloc[0:5, 0:3]",
             "notes": "The number one error here is writing and instead of the ampersand, or forgetting brackets around each condition. Show the error message on purpose so students recognise it. loc is finding a house by its address, iloc is the third house from the corner."},
            {"title": "Cleaning is a checklist", "image": I("cleaning_checklist.png"),
             "bullets": ["Duplicates", "Text: strip, title, merge spellings", "Types: text prices to numbers", "Missing: drop, fill, keep", "Impossible values"],
             "notes": "Open sales_messy.csv in a text editor first so students see the mess with their own eyes. Then walk the checklist in notebook 02. Stress that every rule must be written down, because cleaning choices change the answers."},
            {"title": "Missing values: decide by meaning", "image": I("missing_map.png"),
             "bullets": ["Drop the row if it is useless without it", "Fill with a sensible value (median, 'Unknown')", "Keep it and be careful",
                         "pandas 3: df['c'] = df['c'].fillna(x)", "  not inplace=True on a column"],
             "notes": "The red marks show where blanks are in the messy file. There is no single correct rule. A missing date means we cannot place the order in time, so we drop it. A missing quantity can be filled with the median. Warn about the pandas 3 change: the old inplace style silently does nothing."},
            {"title": "groupby = split, apply, combine", "image": I("split_apply_combine.png"),
             "bullets": ["Any question with 'per' is a groupby", "Split into groups", "Apply sum / mean / count", "Combine into a small table"],
             "notes": "Coins analogy: sort coins into piles by type, count each pile, write the counts on one sheet. Ask students to turn three English questions into groupby code: revenue per city, average score per section, orders per channel."},
            {"title": "Named aggregation and pivot tables",
             "bullets": ["new_name=(column, function)", "Several summaries in one call", "pivot_table = Excel PivotTable", "margins=True adds totals"],
             "code": "sales.groupby('channel').agg(\n  orders=('order_id', 'count'),\n  revenue=('revenue', 'sum'),\n)\npd.pivot_table(sales, index='month',\n  columns='channel', values='revenue',\n  aggfunc='sum')",
             "notes": "Named aggregation gives tidy column names. Pivot tables will feel familiar to anyone who used Excel. Show both on the sales data and compare with the unstack version."},
            {"title": "merge: joining tables on a key", "image": I("merge_joins.png"),
             "bullets": ["on = the shared key column", "left keeps every row of the main table", "inner keeps matches only",
                         "Count rows before and after", "indicator=True shows unmatched rows"],
             "notes": "Guest list analogy: a left join keeps everyone on the guest list even without a badge. Our sales file has three orders from customer C099 who is not in the customer table. Show that a left join keeps 600 rows and an inner join keeps 597. Always count rows."},
            {"title": "Pick the chart from the question", "image": I("chart_gallery.png"),
             "bullets": ["Line: change over time", "Bar: compare groups", "Histogram: spread of values", "Scatter: relationship", "Title + axis labels + units, always"],
             "notes": "Point at each chart and say the question it answers. Then show the basic pattern fig, ax = plt.subplots, ax.plot, set_title, set_xlabel, set_ylabel. A figure is the sheet of paper, an axes is one graph on it."},
            {"title": "Excel in and out", "image": I("excel_roundtrip.png"),
             "bullets": ["read_excel(sheet_name=None) -> all sheets", "ExcelWriter -> many sheets in one file", "openpyxl -> bold, widths, formats, formulas",
                         "Formulas are calculated by Excel, not pandas"],
             "notes": "Many teams live in Excel, so this is a practical superpower. Show the multi-sheet report from notebook 03 opened in Excel or LibreOffice. Point out the share_of_revenue column, which is a live formula."},
            {"title": "Mini EDA: detective work",
             "bullets": ["1. Write questions first", "2. Load and check", "3. Clean and merge", "4. One column at a time", "5. Two columns together",
                         "6. Findings in sentences, backed by numbers", "7. Save results"],
             "notes": "EDA is getting to know a dataset before modelling. Run notebook 04. Emphasise that finding no effect, like discounts not changing order size, is a valid result. Explain correlation from minus one to plus one and repeat: correlation is not causation."},
            {"title": "Common mistakes",
             "bullets": ["and/or instead of & / | in filters", "Forgetting double brackets for several columns", "inplace=True on a column (pandas 3)",
                         "Merging without counting rows", "Dates left as text", "Charts without labels"],
             "notes": "Go through each mistake and ask who has made it already today. Each one has a fix in trainer-notes.md. Encourage students to read the last line of an error message first."},
            {"title": "Recap and exercises",
             "bullets": ["NumPy: arrays, shape, axis, vectorisation", "pandas: load, inspect, clean, groupby, merge", "matplotlib: right chart for the question",
                         "Excel: read many sheets, write styled reports", "Now: exercises.md (easy -> hard)"],
             "notes": "Summarise in one sentence per library. Then set exercises 1 to 6 in class and the rest as homework. Remind them the cheat sheet in the excel folder lists every command from today."},
        ],
    }


def main():
    d = make_data.build_all()
    print("datasets written")
    mermaid_diagrams()
    fig_array_shapes(); fig_merge_joins(); fig_chart_gallery(d); fig_missing_map(d)
    print("images written")
    for name, cells in all_notebooks().items():
        notebook(cells, HERE / "notebooks" / name)
    print("notebooks written")
    cheat_sheet()
    slides(deck(), HERE / "slides" / "02-python-for-data.pptx")
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / "02-python-for-data-handout.pdf",
                      title="Module 02 - Python for Data")
    print("slides, excel, pdf written")


if __name__ == "__main__":
    main()
