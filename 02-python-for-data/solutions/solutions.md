# Module 02 — Worked solutions

Runnable code for every answer is in [`solutions.py`](solutions.py) (run `python 02-python-for-data/solutions/solutions.py`). Numbers below come from the practice data generated with seed 42; if you rebuild the data with a different seed, your numbers will differ.

---

## Exercise 1 — Array warm-up
```python
import numpy as np
temps = np.array([31, 33, 29, 35, 36, 30, 28])
print(temps.shape, temps.dtype)          # (7,) int64
print(temps.mean(), temps.max(), temps.min())   # 31.71..., 36, 28
print(temps * 9 / 5 + 32)                # [87.8 91.4 84.2 95. 96.8 86. 82.4]
```
**Why:** `temps * 9 / 5 + 32` is vectorised; the formula is applied to all seven numbers at once. Shape `(7,)` means "one row of 7".

## Exercise 2 — Axis practice
```python
sales = np.array([[12, 15, 11, 18], [20, 22, 19, 25], [7, 9, 6, 10]])
sales.sum(axis=1)            # per shop  -> [56 86 32]   shape (3,)
sales.sum(axis=0)            # per week  -> [39 46 36 53] shape (4,)
sales.sum(axis=0).argmax()   # 3 (the fourth week)
```
**Why:** `axis=1` collapses the columns, leaving one number per row (shop). `axis=0` collapses the rows, leaving one number per column (week). `argmax` returns the **position** of the largest value, not the value.

## Exercise 3 — Masks
```python
hot = temps > 32
np.where(hot)[0]   # [1 3 4]
hot.sum()          # 3
```
**Why:** `np.where(mask)` returns the positions where the mask is True. Summing a boolean array counts the Trues.

## Exercise 4 — First look at a CSV
```python
st = pd.read_csv("data/students.csv")
st.shape                      # (120, 7)
st.isna().sum()               # attendance_pct 4, science 6
st["math"].median()           # 71.0
```

## Exercise 5 — Filtering
```python
s = pd.read_csv("data/sales.csv", parse_dates=["order_date"])
len(s[(s["channel"] == "Website") & (s["discount_pct"] >= 10)])     # 93
s.nlargest(5, "quantity")[["order_id", "product_id", "quantity"]]   # top one: O10425, 9 gel pen sets
s[s["order_date"].dt.month == 3]["customer_id"].nunique()           # 41
```
**Common slip:** writing `and` instead of `&`, or forgetting brackets around each condition. `nlargest(5, "quantity")` is a shortcut for `sort_values("quantity", ascending=False).head(5)`.

## Exercise 6 — New columns and dates
```python
s["revenue"] = s["quantity"] * s["unit_price"] * (1 - s["discount_pct"] / 100)
s["weekday"] = s["order_date"].dt.day_name()
s.groupby("weekday")["revenue"].sum().sort_values(ascending=False)
```
Sunday is the top day (about Rs 202,900), then Saturday. The weekend together (about Rs 374,100) is clearly bigger than an average pair of weekdays (about Rs 261,500). This matches how the data was generated: weekend days were made 25 % more likely to have orders.

## Exercise 7 — Clean the messy file
Steps (any order that gives the same result is fine, but removing duplicates first is easiest):
1. `drop_duplicates()` → 80 rows.
2. `city`: `.str.strip().str.title()`, then replace `Bangalore → Bengaluru`, `New Delhi → Delhi`, then fill blanks with `"Unknown"`.
3. `price`: `.str.replace(r"[^0-9.]", "", regex=True).astype(float)`.
4. Drop rows with no `order_date`; fill missing `quantity` with the rounded median (2).
5. Keep only `quantity > 0`.

Final shape `(77, 7)`, total revenue **Rs 135,779**. If your answer differs slightly, compare your rules for missing values: different (sensible) rules give slightly different totals. That is fine as long as you wrote your rules down.

## Exercise 8 — groupby
```python
st.groupby("section").agg(students=("student_id", "count"),
                          avg_hours=("study_hours_per_week", "mean"),
                          avg_math=("math", "mean")).round(2).sort_values("avg_math", ascending=False)
```
| section | students | avg_hours | avg_math |
|---|---|---|---|
| C | 36 | 7.87 | 73.17 |
| A | 40 | 7.68 | 71.95 |
| B | 44 | 7.32 | 69.27 |

The differences between sections are small; the section that studies a bit more scores a bit more.

## Exercise 9 — merge
1. Retail brings the most revenue (≈ Rs 495,700), then Student (≈ Rs 363,200), then Corporate (≈ Rs 165,400).
2. `indicator=True` shows three `left_only` orders: `O10058`, `O10302`, `O10489` (customer `C099`).
3. An inner join drops those three orders, so total revenue falls from Rs 1,027,970 to Rs 1,024,262. A left join keeps every sale, which is what you want when sales are the main table.

## Exercise 10 — Excel round-trip
Key lines:
```python
sheets = pd.read_excel("excel/practice-datasets.xlsx", sheet_name=None)   # dict of all sheets
with pd.ExcelWriter("outputs/city_report.xlsx", engine="openpyxl") as w:
    by_city.to_excel(w, sheet_name="Revenue by city")
    top10.to_excel(w, sheet_name="Top 10 customers", index=False)
    sheets["Products"].to_excel(w, sheet_name="Products", index=False)
wb = load_workbook("outputs/city_report.xlsx")
for ws in wb.worksheets:
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.column_dimensions["A"].width = 20
wb.save("outputs/city_report.xlsx")
```
**Check:** open the file; there should be three tabs, bold headers, and a wide first column.

## Exercise 11 — Charts
```python
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
a1.bar(by_channel.index, by_channel.values); a1.set_title("Revenue per channel"); a1.set_xlabel("Channel"); a1.set_ylabel("Revenue (Rs)")
a2.hist(st["study_hours_per_week"], bins=15); a2.set_title("Study hours per week"); a2.set_xlabel("Hours"); a2.set_ylabel("Students")
fig.tight_layout(); fig.savefig("outputs/two_charts.png", dpi=150)
```
`plt.subplots(1, 2)` returns the figure and **two** axes; unpack them into two names.

## Exercise 12 — Your own mini-EDA
Answers will vary. A model answer (in `solutions.py`):

- **Missing values:** science blanks filled with the median (so every student counts); rows with missing attendance dropped only for the attendance question.
- **Q1.** Do students with attendance above 85 % score higher in science? Yes: average science ≈ 82.0 vs ≈ 69.8.
- **Q2.** Does maths rise with study hours? Using bands made with `pd.cut` (0–5, 5–10, 10+ hours): average maths rises from ≈ 58.3 to ≈ 86.2.
- **Q3.** Which section is strongest in each subject? Differences are within about 3 marks; no section is clearly better.

What a trainer should look for: questions written first, a stated missing-value rule, one chart per question, one sentence per finding containing a number, and the Excel file with one sheet per question.
