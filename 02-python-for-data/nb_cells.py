"""
nb_cells.py - the text and code of every notebook in module 02.

build.py imports this file and turns each list of ("md", ...) / ("code", ...) cells into an
.ipynb with build_kit.notebook. Edit the notebooks HERE, then rerun build.py.
"""

RAW = "https://raw.githubusercontent.com/vvvvvivekkk/AI-Engineer/main/02-python-for-data/"

# A small cell every notebook uses to find the practice data (locally or by download in Colab).
LOADER_MD = """### Finding the practice data

The practice files live in the repo folders `data/` (CSV) and `excel/` (Excel).
The helper below looks for them one folder up from this notebook (that is where they are when you
run the notebook from the repo). If they are not there (for example in Google Colab), it downloads
them from GitHub into the current folder. You do not need to change anything."""

LOADER_CODE = f'''from pathlib import Path
import urllib.request

RAW_BASE = "{RAW}"

def data_path(rel_path):
    """Return a local path to a practice file such as 'data/sales.csv'."""
    for candidate in (Path("..") / rel_path, Path(rel_path)):
        if candidate.exists():
            return candidate
    # Not found locally -> download it from GitHub (works in Colab).
    target = Path(rel_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(RAW_BASE + rel_path, target)
    return target

print(data_path("data/sales.csv"))'''


def nb01_numpy():
    return [
        ("md", """# 01 · NumPy basics: arrays, shapes and vectorisation

**What you will learn**
- what a NumPy **array** is (a grid of same-type numbers) and why it is faster than a list
- how to read an array's **shape**, **ndim** and **dtype**
- indexing and slicing in 1-D and 2-D
- **vectorisation** (maths on whole arrays without loops) and how much faster it is
- aggregations with `axis`, boolean masks, broadcasting and seeded random numbers

Run each cell with **Shift + Enter**. Read the text above each cell first."""),
        ("md", """## 1. Import NumPy

`import numpy as np` loads the library and gives it the short nickname `np`. Everyone uses this nickname, so code you find online will match."""),
        ("code", """import numpy as np
print("NumPy version:", np.__version__)"""),
        ("md", """## 2. A list versus an array

A Python **list** repeats itself when you multiply it. A NumPy **array** multiplies every number. Watch the difference."""),
        ("code", """price_list = [799, 2499, 1199, 249]
price_array = np.array(price_list)

print("list * 2  ->", price_list * 2)
print("array * 2 ->", price_array * 2)"""),
        ("md", """## 3. Shape, ndim and dtype

These three facts describe every array:
- **shape**: size along each direction
- **ndim**: number of directions (dimensions)
- **dtype**: the data type of every item

Below, a 2-D array of exam scores: 4 students (rows) × 3 subjects (columns)."""),
        ("code", """scores = np.array([
    [80, 72, 65],   # student 0: maths, science, english
    [65, 90, 70],   # student 1
    [70, 88, 92],   # student 2
    [95, 60, 75],   # student 3
])
print("shape:", scores.shape)
print("ndim: ", scores.ndim)
print("dtype:", scores.dtype)
print("size: ", scores.size, "numbers in total")"""),
        ("md", """## 4. Making arrays quickly

You rarely type arrays by hand. These helpers build them:
- `np.arange(start, stop, step)`: like `range`, but returns an array
- `np.linspace(start, stop, n)`: `n` evenly spaced numbers, including both ends
- `np.zeros(shape)` and `np.ones(shape)`: arrays full of 0 or 1"""),
        ("code", """print(np.arange(0, 10, 2))
print(np.linspace(0, 1, 5))
print(np.zeros((2, 3)))
print(np.ones(4, dtype=int))"""),
        ("md", """## 5. Indexing and slicing

Positions start at 0. In 2-D, write `[row, column]`. A colon `:` means "everything along this direction"."""),
        ("code", """print("student 0, all subjects:", scores[0])
print("student 2, science:     ", scores[2, 1])
print("all students, maths:    ", scores[:, 0])
print("students 1-2, first two subjects:\\n", scores[1:3, :2])"""),
        ("md", """## 6. Vectorised maths

Arithmetic between arrays of the same shape happens item by item. No loop needed.
Here we compute the bill for four orders: quantity × price × (1 − discount)."""),
        ("code", """quantity = np.array([2, 1, 3, 6])
price = np.array([799, 2499, 1199, 249])
discount = np.array([0.0, 0.10, 0.05, 0.0])

bill = quantity * price * (1 - discount)
print(bill)
print("total:", bill.sum())"""),
        ("md", """## 7. How much faster is vectorisation?

We time the same calculation on one million numbers, first with a Python loop, then with NumPy.
`time.perf_counter()` reads a precise clock. Your exact numbers will differ from your neighbour's; the gap is what matters."""),
        ("code", """import time

n = 1_000_000
rng = np.random.default_rng(42)
q = rng.integers(1, 6, n)
p = rng.integers(100, 3000, n)

start = time.perf_counter()
loop_result = [q[i] * p[i] for i in range(n)]
loop_seconds = time.perf_counter() - start

start = time.perf_counter()
vec_result = q * p
vec_seconds = time.perf_counter() - start

print(f"loop:       {loop_seconds:.3f} s")
print(f"vectorised: {vec_seconds:.4f} s")
print(f"vectorised is about {loop_seconds / vec_seconds:.0f}x faster")
print("same answer?", np.array_equal(np.array(loop_result), vec_result))"""),
        ("md", """## 8. Aggregations and `axis`

- `scores.mean()` averages everything.
- `axis=0` collapses the rows away: one answer **per column** (per subject).
- `axis=1` collapses the columns away: one answer **per row** (per student)."""),
        ("code", """print("overall mean:       ", scores.mean())
print("mean per subject:   ", scores.mean(axis=0))
print("mean per student:   ", scores.mean(axis=1))
print("best score per subj:", scores.max(axis=0))
print("which student is best at each subject:", scores.argmax(axis=0))"""),
        ("md", """## 9. Boolean masks

A comparison such as `price > 1000` gives an array of True/False values called a **mask**.
Putting the mask inside square brackets keeps only the True positions."""),
        ("code", """mask = price > 1000
print("mask:            ", mask)
print("expensive prices:", price[mask])
print("how many?        ", mask.sum())   # True counts as 1, False as 0"""),
        ("md", """## 10. Broadcasting

When shapes differ, NumPy stretches the smaller one if it can. Adding a single number affects every item.
Adding a row of 3 numbers to a 4×3 table adds that row to every row. Here we give +5 bonus marks in science only."""),
        ("code", """bonus = np.array([0, 5, 0])     # shape (3,) - one value per subject
print(scores + bonus)
print("scores + 1 (a single number is broadcast too):\\n", scores + 1)"""),
        ("md", """## 11. Reshape

`reshape` rearranges the same numbers into a new shape. The total count must stay the same (12 numbers can be 3×4, 2×6, 12×1, …)."""),
        ("code", """a = np.arange(12)
print(a)
print(a.reshape(3, 4))
print(a.reshape(2, -1))   # -1 means "work this one out for me" -> (2, 6)"""),
        ("md", """## 12. Random numbers with a seed

`np.random.default_rng(seed)` makes a random number generator. The same seed gives the same numbers every run, which makes work **reproducible**.
Run this cell twice: the output does not change."""),
        ("code", """rng = np.random.default_rng(42)
print("5 dice rolls:      ", rng.integers(1, 7, 5))
print("3 decimals in 0-1: ", rng.random(3).round(3))
heights = rng.normal(loc=165, scale=8, size=1000)   # mean 165 cm, spread 8 cm
print(f"1000 heights: mean={heights.mean():.1f}, std={heights.std():.1f}")"""),
        ("md", """## 13. Your turn (mini challenge)

The array below holds weekly study hours for 5 students over 4 weeks (rows = students, columns = weeks).
1. Print the total hours per student.
2. Print the average hours per week (one number per week).
3. Print which students studied more than 30 hours in total.

A worked answer follows in the next cell, but try first!"""),
        ("code", """hours = np.array([
    [5, 7, 6, 8],
    [10, 9, 11, 12],
    [2, 3, 1, 4],
    [8, 8, 9, 7],
    [6, 5, 7, 6],
])
# write your answer here"""),
        ("md", """### One possible answer"""),
        ("code", """total_per_student = hours.sum(axis=1)
print("total per student:", total_per_student)
print("average per week: ", hours.mean(axis=0))
print("students over 30h:", np.where(total_per_student > 30)[0])"""),
        ("md", """## Recap

- Arrays are same-type grids; check `shape`, `ndim`, `dtype` first.
- Use `[row, col]` and `:` to slice.
- Vectorised maths replaces loops and is much faster.
- `axis=0` gives one answer per column; `axis=1` one per row.
- Masks filter; broadcasting stretches; seeds make randomness repeatable.

Next: **02 · pandas loading and cleaning**."""),
    ]


def nb02_pandas_clean():
    return [
        ("md", """# 02 · pandas: loading, exploring and cleaning data

**What you will learn**
- load CSV and Excel files into a **DataFrame** (a table)
- the five first-look questions: `shape`, `head`, `info`, `describe`, `isna().sum()`
- select columns, filter rows, `loc` / `iloc`, sort, add columns, dates
- clean a messy file: duplicates, missing values, messy text, numbers stored as text, impossible values
- save the cleaned result"""),
        ("md", LOADER_MD),
        ("code", LOADER_CODE),
        ("md", """## 1. Import pandas and load a CSV

`pd.read_csv` reads a CSV file into a DataFrame. `parse_dates=["order_date"]` turns that column into real dates instead of text."""),
        ("code", """import pandas as pd
print("pandas version:", pd.__version__)

sales = pd.read_csv(data_path("data/sales.csv"), parse_dates=["order_date"])
sales.head()"""),
        ("md", """## 2. The five first-look questions

Always run these on a new table. Here are the first two: size and the column types."""),
        ("code", """print("shape (rows, columns):", sales.shape)
sales.info()"""),
        ("md", """`describe()` gives summary statistics for the number columns: count, mean, std (spread), min, quartiles (25 %, 50 % = median, 75 %) and max."""),
        ("code", """sales.describe()"""),
        ("md", """And how many blanks are in each column? `isna()` marks every missing cell True; `.sum()` counts the Trues per column."""),
        ("code", """sales.isna().sum()"""),
        ("md", """## 3. Selecting columns

One name in brackets gives a **Series** (one column). A list of names (double brackets) gives a **DataFrame**."""),
        ("code", """print(type(sales["quantity"]))
sales[["order_id", "product_id", "quantity"]].head(3)"""),
        ("md", """## 4. Filtering rows with conditions

A condition creates a True/False mask, exactly like NumPy. Combine conditions with `&` (and) and `|` (or), and wrap each one in brackets."""),
        ("code", """big_orders = sales[sales["quantity"] >= 5]
print("orders with 5+ items:", len(big_orders))

app_discounted = sales[(sales["channel"] == "App") & (sales["discount_pct"] > 0)]
print("discounted app orders:", len(app_discounted))

store_or_app = sales[sales["channel"].isin(["Store", "App"])]
print("store or app orders:", len(store_or_app))"""),
        ("md", """## 5. `loc` (by label) and `iloc` (by position)

- `loc[rows, columns]` uses names and conditions.
- `iloc[rows, columns]` uses integer positions, like NumPy slicing."""),
        ("code", """print(sales.loc[sales["discount_pct"] == 20, ["order_id", "unit_price", "discount_pct"]].head(3))
print()
print(sales.iloc[0:3, 0:4])"""),
        ("md", """## 6. Adding a column and sorting

Revenue for each order = quantity × unit price × (1 − discount ÷ 100). pandas computes it for all rows at once."""),
        ("code", """sales["revenue"] = sales["quantity"] * sales["unit_price"] * (1 - sales["discount_pct"] / 100)
sales.sort_values("revenue", ascending=False).head(5)"""),
        ("md", """## 7. Working with dates

Because `order_date` is a real datetime, `.dt` gives us its parts. `to_period("M")` turns a date into its month (like `2026-03`)."""),
        ("code", """sales["month"] = sales["order_date"].dt.to_period("M")
sales["weekday"] = sales["order_date"].dt.day_name()
print(sales[["order_date", "month", "weekday"]].head())
print()
print("first order:", sales["order_date"].min().date(), "| last order:", sales["order_date"].max().date())"""),
        ("md", """## 8. Counting categories with `value_counts`

`value_counts()` counts each distinct value. It is the fastest way to understand a text column and to spot typos."""),
        ("code", """sales["channel"].value_counts()"""),
        ("md", """## 9. Loading from Excel

The same data also lives in `excel/practice-datasets.xlsx`, one dataset per sheet. `sheet_name=None` loads **every** sheet into a dictionary."""),
        ("code", """xlsx = data_path("excel/practice-datasets.xlsx")
sheets = pd.read_excel(xlsx, sheet_name=None)
for name, table in sheets.items():
    print(f"{name:12s} {table.shape}")"""),
        ("md", """Load a single sheet by name. The `About` sheet explains what each sheet holds."""),
        ("code", """about = pd.read_excel(xlsx, sheet_name="About")
about"""),
        ("md", """# Part 2 · Cleaning a messy file

`sales_messy.csv` is a deliberately dirty export: the kind of file you really receive. We clean it step by step, checking after every step."""),
        ("code", """messy = pd.read_csv(data_path("data/sales_messy.csv"))
print("shape:", messy.shape)
messy.head(8)"""),
        ("md", """## 10. Diagnose before you fix

Look at types, blanks, duplicates and the distinct values of text columns. Notice:
- `price` is text (`str`), not a number
- `city` has many spellings of the same city
- some rows are exact duplicates"""),
        ("code", """print(messy.dtypes, "\\n")
print("missing per column:\\n", messy.isna().sum(), "\\n")
print("duplicate rows:", messy.duplicated().sum())
print("\\ncity spellings:", sorted(messy["city"].dropna().unique()))"""),
        ("md", """## 11. Remove duplicates

`drop_duplicates()` keeps the first copy of each repeated row. We count rows before and after so we know what changed."""),
        ("code", """before = len(messy)
messy = messy.drop_duplicates()
print(f"removed {before - len(messy)} duplicate rows -> {len(messy)} rows left")"""),
        ("md", """## 12. Clean the text columns

`.str.strip()` removes spaces at both ends, `.str.title()` makes "hyderabad" into "Hyderabad", and `replace` merges different names for the same city.
We do the same for the product names. Then `value_counts()` confirms the result."""),
        ("code", """messy["city"] = (messy["city"]
                 .str.strip()
                 .str.title()
                 .replace({"Bangalore": "Bengaluru", "New Delhi": "Delhi"}))
messy["product"] = messy["product"].str.strip().str.title()
messy["city"].value_counts(dropna=False)"""),
        ("md", """## 13. Turn text prices into numbers

Prices look like `"1,299"` or `"Rs 799"`. We delete every character that is not a digit or a dot (a **regular expression** `[^0-9.]` does that), then convert with `astype(float)`."""),
        ("code", """print("before:", messy["price"].head(6).tolist())
messy["price"] = messy["price"].str.replace(r"[^0-9.]", "", regex=True).astype(float)
print("after: ", messy["price"].head(6).tolist())
print("dtype now:", messy["price"].dtype)"""),
        ("md", """## 14. Handle missing values

Decide per column, based on meaning:
- **order_date** missing → we cannot place the order in time, so **drop** those rows.
- **quantity** missing → we fill with the **median** quantity (a typical order), rounded to a whole number because nobody buys half a mouse. Note: we write `messy["quantity"] = messy["quantity"].fillna(...)`; the old `inplace=True` style does not work in pandas 3.
- **city** missing → fill with the label `"Unknown"` so the rows still count in totals."""),
        ("code", """messy = messy.dropna(subset=["order_date"])
median_qty = int(round(messy["quantity"].median()))
messy["quantity"] = messy["quantity"].fillna(median_qty)
messy["city"] = messy["city"].fillna("Unknown")
print("median quantity used:", median_qty)
messy.isna().sum()"""),
        ("md", """## 15. Remove impossible values and fix types

A negative quantity is a typo. We keep only positive quantities, then store quantity as a whole number and the date as a real date."""),
        ("code", """print("rows with quantity <= 0:")
print(messy[messy["quantity"] <= 0])
messy = messy[messy["quantity"] > 0].copy()
messy["quantity"] = messy["quantity"].astype(int)
messy["order_date"] = pd.to_datetime(messy["order_date"])
messy.dtypes"""),
        ("md", """## 16. Check the cleaned table and save it

`.copy()` above makes `messy` its own independent table (good practice after filtering).
We save into an `outputs/` folder (created if missing). The repo's `.gitignore` ignores `outputs/`, so your experiments do not clutter the project."""),
        ("code", """messy["revenue"] = messy["quantity"] * messy["price"]
print("clean shape:", messy.shape)
print("total revenue in this export: Rs", round(messy["revenue"].sum()))

out = Path("outputs")
out.mkdir(exist_ok=True)
messy.to_csv(out / "sales_clean.csv", index=False)
print("saved", out / "sales_clean.csv")"""),
        ("md", """## Recap

1. Load (`read_csv`, `read_excel`) → 2. look (`shape`, `head`, `info`, `describe`, `isna().sum()`) →
3. clean (duplicates, text, types, missing, impossible values) → 4. save.

Write down every cleaning rule you applied. Next: **03 · groupby, merge and Excel reports**."""),
    ]


def nb03_group_merge_excel():
    return [
        ("md", """# 03 · groupby, merge and Excel reports

**What you will learn**
- answer "per group" questions with `groupby` and named aggregation
- lay a summary out as a grid with `pivot_table`
- join tables with `merge` (inner vs left) and check the result with `indicator=True`
- write a multi-sheet Excel report with `ExcelWriter`, then style it with **openpyxl**"""),
        ("md", LOADER_MD),
        ("code", LOADER_CODE),
        ("md", """## 1. Load the three related tables

- `sales`: one row per order, with `customer_id` and `product_id`
- `products`: product name, category, price
- `customers`: name, city, segment"""),
        ("code", """import pandas as pd

sales = pd.read_csv(data_path("data/sales.csv"), parse_dates=["order_date"])
products = pd.read_csv(data_path("data/products.csv"))
customers = pd.read_csv(data_path("data/customers.csv"), parse_dates=["signup_date"])

sales["revenue"] = sales["quantity"] * sales["unit_price"] * (1 - sales["discount_pct"] / 100)
sales["month"] = sales["order_date"].dt.to_period("M")
print(sales.shape, products.shape, customers.shape)"""),
        ("md", """## 2. A first groupby

"Total revenue **per** channel." Split by channel, sum the revenue in each group, combine into a small Series."""),
        ("code", """sales.groupby("channel")["revenue"].sum().round(0)"""),
        ("md", """## 3. Several numbers at once (named aggregation)

The pattern is `new_column=(existing_column, function)`. Common functions: `"sum"`, `"mean"`, `"count"`, `"min"`, `"max"`, `"median"`, `"nunique"` (number of distinct values)."""),
        ("code", """by_channel = sales.groupby("channel").agg(
    orders=("order_id", "count"),
    customers=("customer_id", "nunique"),
    revenue=("revenue", "sum"),
    avg_order=("revenue", "mean"),
).round(0).sort_values("revenue", ascending=False)
by_channel"""),
        ("md", """## 4. Grouping by two columns

Pass a list of columns. The result has a two-level index (month, then channel). `.unstack()` turns the inner level into columns, which is easier to read."""),
        ("code", """monthly_channel = sales.groupby(["month", "channel"])["revenue"].sum().round(0)
print(monthly_channel.head(6))
monthly_channel.unstack()"""),
        ("md", """## 5. Pivot tables

`pivot_table` does the same in one call, like Excel's PivotTable. `margins=True` adds an "All" total row and column."""),
        ("code", """pivot = pd.pivot_table(sales, index="month", columns="channel", values="revenue",
                       aggfunc="sum", margins=True, margins_name="Total").round(0)
pivot"""),
        ("md", """## 6. Merge sales with products

`merge(..., on="product_id", how="left")` keeps every sale and adds the product's name and category.
We drop the duplicate price column from products first (sales already has `unit_price`)."""),
        ("code", """print("rows before:", len(sales))
full = sales.merge(products.drop(columns="unit_price"), on="product_id", how="left")
print("rows after: ", len(full))
full[["order_id", "product_id", "product_name", "category", "revenue"]].head()"""),
        ("md", """## 7. Merge with customers and look for problems

`indicator=True` adds a `_merge` column telling us whether each row matched (`both`) or only existed in the left table (`left_only`).
Three orders come from customer `C099`, who is missing from the customer table. A left join keeps them (with blank city); an inner join would silently drop them."""),
        ("code", """check = full.merge(customers, on="customer_id", how="left", indicator=True)
print(check["_merge"].value_counts())
print()
print(check.loc[check["_merge"] == "left_only", ["order_id", "customer_id", "customer_name", "city"]])"""),
        ("code_md_guard", ""),
    ]


# nb03 continues - kept as a separate list so the file stays readable
def nb03_rest():
    return [
        ("md", """Compare the row counts of a left join and an inner join. The difference is exactly the unmatched orders."""),
        ("code", """left = full.merge(customers, on="customer_id", how="left")
inner = full.merge(customers, on="customer_id", how="inner")
print("left join rows: ", len(left))
print("inner join rows:", len(inner))
full = left  # keep the left join for the rest of the notebook
full["city"] = full["city"].fillna("Unknown")"""),
        ("md", """## 8. Questions that need the merged table

Now "revenue per category" and "revenue per city" are one groupby each."""),
        ("code", """by_category = full.groupby("category").agg(units=("quantity", "sum"), revenue=("revenue", "sum")).round(0)
by_city = full.groupby("city").agg(orders=("order_id", "count"), revenue=("revenue", "sum")).round(0)
print(by_category.sort_values("revenue", ascending=False), "\\n")
print(by_city.sort_values("revenue", ascending=False))"""),
        ("md", """## 9. Top customers

Group by customer name, sum, sort, keep the top 5. `reset_index()` turns the group labels back into a normal column."""),
        ("code", """top_customers = (full.groupby(["customer_id", "customer_name"])["revenue"].sum()
                 .sort_values(ascending=False).head(5).round(0).reset_index())
top_customers"""),
        ("md", """## 10. Write a multi-sheet Excel report

`pd.ExcelWriter` keeps one workbook open while we add several sheets. The `with` block saves and closes the file at the end.
`index=False` skips the row numbers when they mean nothing."""),
        ("code", """from pathlib import Path
out = Path("outputs")
out.mkdir(exist_ok=True)
report_path = out / "sales_report.xlsx"

with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
    by_channel.to_excel(writer, sheet_name="By channel")
    by_category.to_excel(writer, sheet_name="By category")
    by_city.to_excel(writer, sheet_name="By city")
    pivot.astype(float).to_excel(writer, sheet_name="Month x channel")
    top_customers.to_excel(writer, sheet_name="Top customers", index=False)
    full.drop(columns=["month"]).to_excel(writer, sheet_name="Raw data", index=False)

print("written:", report_path)"""),
        ("md", """## 11. Style it with openpyxl

pandas writes values only. **openpyxl** can open the file and change its look: bold headers, column widths, number formats, and even live formulas.
Here we style the "By category" sheet and add a formula column that computes each category's share of revenue. Excel will calculate the formula when the file is opened."""),
        ("code", """from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

wb = load_workbook(report_path)
ws = wb["By category"]

header_fill = PatternFill("solid", fgColor="1B263B")
for cell in ws[1]:                       # row 1 = header row
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = header_fill

ws["D1"] = "share_of_revenue"
ws["D1"].font = Font(bold=True, color="FFFFFF")
ws["D1"].fill = header_fill
last = ws.max_row
for r in range(2, last + 1):
    ws[f"D{r}"] = f"=C{r}/SUM($C$2:$C${last})"   # a live Excel formula
    ws[f"D{r}"].number_format = "0.0%"
    ws[f"C{r}"].number_format = "#,##0"

for col, width in zip("ABCD", [16, 10, 14, 18]):
    ws.column_dimensions[col].width = width

wb.save(report_path)
print("sheets:", wb.sheetnames)"""),
        ("md", """## 12. Read it back

When pandas reads a cell that holds a formula written by openpyxl, it gets nothing useful (the file has never been calculated by Excel).
That is why we compute numbers in pandas and only use formulas for things a human might want to change in Excel."""),
        ("code", """back = pd.read_excel(report_path, sheet_name=None)
for name, table in back.items():
    print(f"{name:16s} {table.shape}")
back["By category"]"""),
        ("md", """## Recap

- `groupby(...).agg(name=(col, func))` answers "per group" questions.
- `pivot_table` makes an Excel-style grid.
- `merge(on=..., how="left")` adds columns from another table; always count rows and use `indicator=True` to spot unmatched keys.
- `ExcelWriter` writes several sheets; `openpyxl` styles them and adds formulas.

Next: **04 · mini EDA**."""),
    ]


def nb04_eda():
    return [
        ("md", """# 04 · Mini exploratory data analysis (EDA)

**EDA** = getting to know a dataset by asking questions, computing summaries and drawing charts.
We follow the recipe from `concepts.md`:
1. write questions → 2. load & check → 3. clean & merge → 4. one column at a time → 5. two columns together → 6. write findings → 7. save.

**Our questions**
- Q1. How did revenue change month by month?
- Q2. Which product categories and cities bring the most revenue?
- Q3. Do bigger discounts come with bigger orders?
- Q4. In the student data: do students who study more score higher? Which section does best?"""),
        ("md", LOADER_MD),
        ("code", LOADER_CODE),
        ("md", """## 1. Load, merge and add helper columns

The same steps as notebook 03, in one cell."""),
        ("code", """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sales = pd.read_csv(data_path("data/sales.csv"), parse_dates=["order_date"])
products = pd.read_csv(data_path("data/products.csv"))
customers = pd.read_csv(data_path("data/customers.csv"))

df = (sales.merge(products.drop(columns="unit_price"), on="product_id", how="left")
           .merge(customers, on="customer_id", how="left"))
df["city"] = df["city"].fillna("Unknown")
df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
df["month"] = df["order_date"].dt.to_period("M").astype(str)
print(df.shape)
df.head(3)"""),
        ("md", """## 2. Quick checks

Missing values, the date range, and basic numbers. The only blanks should be the three orders from the unknown customer (no name/segment)."""),
        ("code", """print(df.isna().sum()[lambda s: s > 0])
print("dates:", df["order_date"].min().date(), "to", df["order_date"].max().date())
df[["quantity", "unit_price", "discount_pct", "revenue"]].describe().round(1)"""),
        ("md", """## 3. One column at a time: how big is a typical order?

A **histogram** shows how values are spread. Most orders are small; a few are large. The **median** (middle value) is a better "typical order" than the mean when there is a long tail of big values."""),
        ("code", """fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(df["revenue"], bins=30, color="#0F9D9A", edgecolor="white")
ax.axvline(df["revenue"].median(), color="#1B263B", linestyle="--", label=f"median = Rs {df['revenue'].median():.0f}")
ax.axvline(df["revenue"].mean(), color="orange", linestyle=":", label=f"mean = Rs {df['revenue'].mean():.0f}")
ax.set_title("How big are orders? (revenue per order)")
ax.set_xlabel("Revenue per order (Rs)")
ax.set_ylabel("Number of orders")
ax.legend()
plt.show()"""),
        ("md", """## 4. Q1 · Revenue by month (line chart)

A line chart is the right choice for change over time."""),
        ("code", """monthly = df.groupby("month")["revenue"].sum()
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(monthly.index, monthly.values / 1000, marker="o", color="#1B263B")
for x, y in zip(monthly.index, monthly.values / 1000):
    ax.annotate(f"{y:.0f}k", (x, y), textcoords="offset points", xytext=(0, 8), ha="center")
ax.set_title("Q1 · Revenue by month, 2026")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (thousand Rs)")
ax.set_ylim(0, monthly.max() / 1000 * 1.2)
plt.show()
print((monthly.pct_change() * 100).round(1).rename("% change vs previous month"))"""),
        ("md", """## 5. Q2 · Categories and cities (bar charts)

Bar charts compare groups. Horizontal bars (`barh`) leave room for long labels. We sort so the biggest bar is on top."""),
        ("code", """by_cat = df.groupby("category")["revenue"].sum().sort_values()
by_city = df.groupby("city")["revenue"].sum().sort_values()

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].barh(by_cat.index, by_cat.values / 1000, color="#0F9D9A")
axes[0].set_title("Revenue by category")
axes[0].set_xlabel("thousand Rs")
axes[1].barh(by_city.index, by_city.values / 1000, color="#1B263B")
axes[1].set_title("Revenue by city")
axes[1].set_xlabel("thousand Rs")
plt.tight_layout()
plt.show()"""),
        ("md", """### A month × category grid

`pivot_table` plus `imshow` (draw a grid of colours) gives a simple **heatmap**: darker = more revenue."""),
        ("code", """grid = pd.pivot_table(df, index="category", columns="month", values="revenue", aggfunc="sum") / 1000
fig, ax = plt.subplots(figsize=(8, 3.5))
im = ax.imshow(grid.values, cmap="Blues")
ax.set_xticks(range(len(grid.columns)), grid.columns)
ax.set_yticks(range(len(grid.index)), grid.index)
for i in range(grid.shape[0]):
    for j in range(grid.shape[1]):
        ax.text(j, i, f"{grid.values[i, j]:.0f}", ha="center", va="center", fontsize=9)
ax.set_title("Revenue (thousand Rs) by category and month")
fig.colorbar(im, ax=ax)
plt.show()"""),
        ("md", """## 6. Q3 · Do bigger discounts mean bigger orders?

Group by discount level and look at the average quantity. If discounts drive bigger orders, the numbers should rise from left to right."""),
        ("code", """disc = df.groupby("discount_pct").agg(orders=("order_id", "count"),
                                      avg_quantity=("quantity", "mean"),
                                      avg_revenue=("revenue", "mean")).round(2)
print(disc)
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.bar(disc.index.astype(str), disc["avg_quantity"], color="#0F9D9A")
ax.set_title("Q3 · Average quantity per order by discount")
ax.set_xlabel("Discount (%)")
ax.set_ylabel("Average quantity")
plt.show()"""),
        ("md", """In this synthetic data the discount was assigned at random, so there is no real pattern: average quantity is roughly flat.
That is a valid finding! EDA often tells you that an assumed effect is *not* there."""),
        ("md", """## 7. Q4 · Students: do study hours relate to scores?

Load the student data, fill the few missing science scores with the median, and draw a **scatter plot** (one dot per student)."""),
        ("code", """students = pd.read_csv(data_path("data/students.csv"))
print(students.isna().sum()[lambda s: s > 0])
students["science"] = students["science"].fillna(students["science"].median())

fig, ax = plt.subplots(figsize=(7, 4))
ax.scatter(students["study_hours_per_week"], students["math"], alpha=0.7, color="#1B263B")
slope, intercept = np.polyfit(students["study_hours_per_week"], students["math"], 1)
xs = np.linspace(students["study_hours_per_week"].min(), students["study_hours_per_week"].max(), 50)
ax.plot(xs, slope * xs + intercept, color="#0F9D9A", label=f"trend: +{slope:.1f} marks per extra hour")
ax.set_title("Q4 · Study hours vs maths score")
ax.set_xlabel("Study hours per week")
ax.set_ylabel("Maths score")
ax.legend()
plt.show()"""),
        ("md", """**Correlation** (−1 to +1) puts a number on "how strongly do these move together in a straight line?".
`corr(numeric_only=True)` computes it for every pair of number columns."""),
        ("code", """corr = students.corr(numeric_only=True).round(2)
corr"""),
        ("md", """Which section does best? Group by section and average the three subjects."""),
        ("code", """students["average"] = students[["math", "science", "english"]].mean(axis=1)
students["passed"] = students["average"] >= 60
section_summary = students.groupby("section").agg(
    students=("student_id", "count"),
    avg_hours=("study_hours_per_week", "mean"),
    avg_score=("average", "mean"),
    pass_rate=("passed", "mean"),
).round(2)
section_summary"""),
        ("md", """## 8. Write the findings

Good findings are short sentences backed by numbers. The cell below builds them from the results, so they stay correct if the data changes."""),
        ("code", """best_month = monthly.idxmax()
findings = [
    f"Q1: Revenue was highest in {best_month} (Rs {monthly.max():,.0f}); June was {monthly.iloc[-1] / monthly.iloc[0]:.2f}x January.",
    f"Q2: {by_cat.idxmax()} is the top category (Rs {by_cat.max():,.0f}); {by_city.idxmax()} is the top city.",
    f"Q3: Average quantity ranges only from {disc['avg_quantity'].min()} to {disc['avg_quantity'].max()} across discounts - no clear effect.",
    f"Q4: Study hours and maths score have correlation {corr.loc['study_hours_per_week', 'math']}: a strong positive link (not proof of cause).",
]
for f in findings:
    print("-", f)"""),
        ("md", """## 9. Save the results for people (Excel) and programs (CSV)"""),
        ("code", """from pathlib import Path
out = Path("outputs")
out.mkdir(exist_ok=True)
with pd.ExcelWriter(out / "eda_summary.xlsx", engine="openpyxl") as writer:
    pd.DataFrame({"finding": findings}).to_excel(writer, sheet_name="Findings", index=False)
    monthly.round(0).to_frame("revenue").to_excel(writer, sheet_name="Monthly")
    by_cat.round(0).to_frame("revenue").to_excel(writer, sheet_name="By category")
    disc.to_excel(writer, sheet_name="Discounts")
    section_summary.to_excel(writer, sheet_name="Sections")
df.to_csv(out / "sales_enriched.csv", index=False)
print("saved:", sorted(p.name for p in out.iterdir()))"""),
        ("md", """## Recap

You ran a full mini-EDA: questions → checks → merge → univariate charts → bivariate comparisons → written findings → saved outputs.
This is the same workflow you will use before every machine-learning project in Module 04."""),
    ]


def all_notebooks():
    nb3 = [c for c in nb03_group_merge_excel() if c[0] != "code_md_guard"] + nb03_rest()
    return {
        "01-numpy-basics.ipynb": nb01_numpy(),
        "02-pandas-loading-and-cleaning.ipynb": nb02_pandas_clean(),
        "03-groupby-merge-excel.ipynb": nb3,
        "04-mini-eda.ipynb": nb04_eda(),
    }
