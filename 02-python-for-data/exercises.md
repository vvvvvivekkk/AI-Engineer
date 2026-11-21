# Module 02 — Exercises

Work in a new notebook (Colab or Jupyter) or a `.py` file. The practice files are in `data/` (CSV) and `excel/practice-datasets.xlsx`. If you work in Colab, copy the `data_path` helper from the top of any module notebook so the files download automatically.

Exercises go from easy (1) to hard (12). Full worked answers are in [`solutions/solutions.md`](solutions/solutions.md), and runnable code is in [`solutions/solutions.py`](solutions/solutions.py). Try each one for at least 10 minutes before looking.

---

### Exercise 1 — Array warm-up (easy)
Create a NumPy array of the temperatures `[31, 33, 29, 35, 36, 30, 28]` (one week, °C).
1. Print its shape and dtype.
2. Print the average, the hottest and the coldest temperature.
3. Convert all values to Fahrenheit with one vectorised line (`F = C × 9/5 + 32`).

### Exercise 2 — Axis practice (easy)
Make this 3×4 array of weekly sales (rows = shops, columns = weeks):
```
[[12, 15, 11, 18],
 [20, 22, 19, 25],
 [ 7,  9,  6, 10]]
```
1. Total per shop. 2. Total per week. 3. Which week (index) had the highest total?
Before running, write down the shape you expect for answers 1 and 2.

### Exercise 3 — Masks (easy)
Using the temperature array from Exercise 1, print the days (positions) when it was above 32 °C, and how many such days there were.

### Exercise 4 — First look at a CSV (easy)
Load `data/students.csv`. Answer with code: how many rows and columns? Which columns have missing values, and how many? What is the median maths score?

### Exercise 5 — Filtering (medium)
From `data/sales.csv`:
1. How many orders came through the `Website` channel with a discount of 10 % or more?
2. Show the 5 orders with the largest quantity (only `order_id`, `product_id`, `quantity`).
3. How many distinct customers bought something in March 2026?

### Exercise 6 — New columns and dates (medium)
In `data/sales.csv` add a `revenue` column (quantity × unit_price × (1 − discount_pct/100)) and a `weekday` column. Which weekday has the highest total revenue? Are weekends (Saturday, Sunday) together bigger or smaller than the average of two weekdays?

### Exercise 7 — Clean the messy file yourself (medium)
Load `data/sales_messy.csv` and, **without looking at notebook 02**, produce a clean table where:
- there are no duplicate rows,
- `city` has exactly six clean city names plus `Unknown`,
- `price` is a number,
- there are no missing values and no negative quantities.
Print the final shape and the total revenue (quantity × price).

### Exercise 8 — groupby (medium)
From `data/students.csv`: for each section, compute the number of students, the average study hours, and the average maths score, using **named aggregation**. Sort by average maths score, highest first.

### Exercise 9 — merge (medium)
Merge `sales.csv` with `products.csv` and `customers.csv`.
1. Which **segment** (Retail / Student / Corporate) brings the most revenue?
2. Use `indicator=True` to list the order IDs whose customer is missing from `customers.csv`.
3. Explain in one sentence why an inner join would give a different total revenue.

### Exercise 10 — Excel round-trip (medium-hard)
Read **all** sheets of `excel/practice-datasets.xlsx` with one call. Then write a new workbook `outputs/city_report.xlsx` with three sheets:
- `Revenue by city` (orders and revenue per city),
- `Top 10 customers` (by revenue),
- `Products` (copied unchanged from the source workbook).
Finally, use openpyxl to make the header row bold and set column A to width 20 on every sheet.

### Exercise 11 — Charts (medium-hard)
Create one figure with **two** plots side by side (`plt.subplots(1, 2)`):
- left: a bar chart of total revenue per channel,
- right: a histogram of `study_hours_per_week` from the student data.
Give each plot a title and axis labels, and save the figure as `outputs/two_charts.png`.

### Exercise 12 — Your own mini-EDA (hard)
Using the student data, write **three questions** of your own (for example "Do students with attendance above 85 % score higher in science?"). For each question, compute the answer with pandas, draw one suitable chart, and write one sentence with the finding and a number. Save the summary tables to `outputs/student_eda.xlsx` (one sheet per question). Remember to decide what to do about missing values first, and say what you chose.
