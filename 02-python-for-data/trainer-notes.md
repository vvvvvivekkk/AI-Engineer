# Module 02 — Trainer notes

These notes assume you have read `concepts.md` and run all four notebooks yourself at least once. Plan on about 3 hours of your own preparation the first time.

## 1. What students should be able to do after the session

- Create NumPy arrays, read their `shape` / `ndim` / `dtype`, slice them, and use `axis` correctly in `sum` / `mean`.
- Explain vectorisation and why it is faster than a loop.
- Load a CSV and an Excel sheet (including all sheets at once) into pandas.
- Run the five first-look checks and say what each one tells them.
- Filter rows with one or two conditions, add a computed column, and extract parts of a date.
- Clean a messy table: duplicates, text, types, missing values, impossible values, and write down the rules.
- Answer "per group" questions with `groupby` and `pivot_table`.
- Join two tables with `merge`, choose `left` vs `inner`, and check unmatched rows.
- Draw a line, bar, histogram and scatter chart with labels, and pick the right one for a question.
- Write a multi-sheet Excel report and style it with openpyxl.

## 2. Teaching sequence

This module is big. Run it as **two sessions of about 2 hours** (session A: NumPy + pandas basics + cleaning; session B: groupby, merge, charts, Excel, EDA). If you only have one 2-hour slot, use the plan for session A and set notebooks 03–04 as guided homework.

### Session A (2 hours)

| Time | Activity | Materials | Notes |
|---|---|---|---|
| 0:00–0:10 | Hook: show a messy CSV in a text editor and ask "how would you total revenue per city by hand?" | `data/sales_messy.csv` | Let them feel the pain first. |
| 0:10–0:15 | The data workflow map | slide 2, `images/data_workflow.png` | Refer back to it all day. |
| 0:15–0:40 | NumPy live: list vs array, shape, slicing, vectorisation timing, axis, masks | notebook 01, slides 3–5 | Make students predict outputs before each cell. |
| 0:40–0:50 | Pair exercise: exercises 1–3 | `exercises.md` | Walk around; watch for axis confusion. |
| 0:50–1:00 | Break | | |
| 1:00–1:25 | pandas basics: load CSV and Excel, five first-look checks, select, filter, loc/iloc, new column, dates | notebook 02 part 1, slides 6–8 | Show the `and` vs `&` error on purpose. |
| 1:25–1:50 | Cleaning the messy file step by step | notebook 02 part 2, slides 9–10 | After every step, ask "how do we check it worked?" |
| 1:50–2:00 | Recap + set exercises 4–7 as homework | slide 18 | |

### Session B (2 hours)

| Time | Activity | Materials | Notes |
|---|---|---|---|
| 0:00–0:10 | Review homework: one student shows their cleaning rules | exercise 7 | Compare different rule choices and totals. |
| 0:10–0:35 | groupby: split-apply-combine, named aggregation, two keys, pivot_table | notebook 03 §1–5, slides 11–12 | Turn English "per" questions into code together. |
| 0:35–0:55 | merge: products, customers, left vs inner, `indicator=True`, the C099 orders | notebook 03 §6–9, slide 13 | Count rows before and after every merge. |
| 0:55–1:05 | Break | | |
| 1:05–1:25 | Excel round-trip: ExcelWriter, openpyxl styling, formulas; open the file in Excel/LibreOffice/Sheets | notebook 03 §10–12, slide 15 | Show the live formula column. |
| 1:25–1:50 | Mini-EDA: charts and written findings | notebook 04, slides 14, 16 | Stress "no effect" is a valid finding. |
| 1:50–2:00 | Common mistakes, recap, assign exercises 8–12 | slides 17–18 | |

## 3. Common student mistakes and how to fix them

| Mistake | What they see | Fix |
|---|---|---|
| Using `and` / `or` in a pandas filter | `ValueError: The truth value of a Series is ambiguous` | Use `&` / `|` and put brackets around each condition: `df[(df.a > 1) & (df.b == "x")]`. |
| Single brackets for several columns | `KeyError: ('a', 'b')` | Use a list inside the brackets: `df[["a", "b"]]`. |
| Mixing up `axis=0` and `axis=1` | Answer has the wrong length | Predict the shape first. "axis=0 squashes the rows away → one value per column." |
| `df["col"].fillna(0, inplace=True)` (from old tutorials) | `ChainedAssignmentError` warning and the column still has NaN | pandas 3 uses Copy-on-Write. Write `df["col"] = df["col"].fillna(0)`. |
| Dates left as text | `.dt` fails with `Can only use .dt accessor with datetimelike values`; months sort wrongly | `parse_dates=["col"]` in `read_csv`, or `pd.to_datetime(df["col"])`. |
| Merging on a column that is not unique in the right table | Row count grows after the merge | Count rows before/after; check `df["key"].duplicated().sum()` on the lookup table. |
| Using an inner join by default | Totals are slightly too small; orders silently vanish | Use `how="left"` when the left table is the main data; check with `indicator=True`. |
| Forgetting `index=False` in `to_csv` / `to_excel` | An extra unnamed column of 0, 1, 2… appears when the file is reopened | Add `index=False` unless the index carries meaning (e.g. after groupby). |
| `FileNotFoundError` for the data | The notebook cannot find `data/sales.csv` | The notebook's working folder is `notebooks/`, so the file is at `../data/`. Use the `data_path` helper, which also works in Colab. |
| Reading a formula cell written by openpyxl and getting NaN | Values are missing in pandas | openpyxl stores formulas, not results. Compute in pandas; use formulas only for humans in Excel. |
| Charts with no title or labels | Nobody knows what the chart shows | Make "title, x label, y label, units" a checklist item for every chart. |
| `ModuleNotFoundError: openpyxl` locally | `read_excel` fails | `pip install openpyxl` (Colab already has it). |

## 4. Questions to check understanding (with answers)

1. **What is the shape of an array holding 30 students' scores in 4 subjects?** (30, 4).
2. **For that array, what does `.mean(axis=0)` give?** Four numbers: the average of each subject.
3. **Why is `prices * 2` different for a list and an array?** A list repeats itself; an array multiplies every number (vectorisation).
4. **Name the five first-look checks.** `shape`, `head()`, `info()`, `describe()`, `isna().sum()`.
5. **What is the difference between `loc` and `iloc`?** `loc` selects by labels/conditions; `iloc` selects by integer positions.
6. **When would you drop a row with a missing value instead of filling it?** When the row is useless without that value (e.g. no order date for a time analysis), or when a fill value would be a misleading guess.
7. **Why might the median be a better fill value than the mean?** The median is not pulled around by a few extreme values.
8. **Turn "average maths score per section" into code.** `df.groupby("section")["math"].mean()`.
9. **After a left join from sales to customers, some `city` values are NaN. Why?** Those sales have a `customer_id` that does not exist in the customer table.
10. **Which chart for "how are exam scores spread out"?** A histogram.
11. **How do you write three DataFrames into one Excel file?** A `with pd.ExcelWriter(path) as w:` block with three `to_excel(w, sheet_name=...)` calls.
12. **Study hours and maths have correlation 0.78. Does studying cause higher marks?** Not proven. Correlation shows they move together; other factors (interest, prior knowledge) could explain both.

## 5. Adapting for faster or slower groups

**Slower groups**
- Spend session A on NumPy and loading/selecting only; move cleaning to session B and the Excel part to a third session.
- Use the pandas cheat sheet (`excel/pandas-cheatsheet.xlsx`) as a printed handout.
- Do exercises 1–6 together on screen, typing slowly and saying each step aloud.
- Skip broadcasting and `pivot_table`; `groupby` + `unstack` is enough.

**Faster groups**
- Ask them to rewrite the cleaning steps as one reusable function (see `code/clean_messy_sales.py`) and test it with `assert` statements.
- Add `pd.cut` (binning numbers into bands) and `merge` with `validate="many_to_one"` (pandas raises an error if the lookup key is not unique).
- Challenge: rebuild one chart with seaborn (`sns.barplot`) and compare the code length.
- Exercise 12 with a real public dataset from the UCI repository (see `resources.md`), downloaded once and used offline.
