"""
solutions.py - runnable answers to every exercise in 02-python-for-data/exercises.md.

Run:   python 02-python-for-data/solutions/solutions.py
Each exercise is one function; read them one at a time alongside solutions.md.
"""
from pathlib import Path                                  # file paths

import matplotlib                                         # plotting
matplotlib.use("Agg")                                     # save charts to files, no window
import matplotlib.pyplot as plt
import numpy as np                                        # arrays
import pandas as pd                                       # tables
from openpyxl import load_workbook                        # styling Excel files
from openpyxl.styles import Font

HERE = Path(__file__).resolve().parent                    # solutions/
DATA = HERE.parent / "data"                               # data/
XLSX = HERE.parent / "excel" / "practice-datasets.xlsx"   # the practice workbook
OUT = HERE.parent / "outputs"                             # results (ignored by git)
OUT.mkdir(exist_ok=True)


def ex1():
    temps = np.array([31, 33, 29, 35, 36, 30, 28])        # one week of temperatures in Celsius
    print("shape:", temps.shape, "dtype:", temps.dtype)
    print("mean:", temps.mean().round(2), "max:", temps.max(), "min:", temps.min())
    print("Fahrenheit:", temps * 9 / 5 + 32)              # one vectorised line for all 7 days
    return temps


def ex2():
    sales = np.array([[12, 15, 11, 18], [20, 22, 19, 25], [7, 9, 6, 10]])
    per_shop = sales.sum(axis=1)                          # shape (3,): one total per row (shop)
    per_week = sales.sum(axis=0)                          # shape (4,): one total per column (week)
    print("per shop:", per_shop, "per week:", per_week, "best week index:", per_week.argmax())


def ex3(temps):
    hot = temps > 32                                      # True where hotter than 32
    print("hot day positions:", np.where(hot)[0], "count:", hot.sum())


def ex4():
    st = pd.read_csv(DATA / "students.csv")
    print("shape:", st.shape)
    missing = st.isna().sum()
    print("missing:\n", missing[missing > 0])             # only the columns that have blanks
    print("median maths:", st["math"].median())


def load_sales():
    s = pd.read_csv(DATA / "sales.csv", parse_dates=["order_date"])
    s["revenue"] = s["quantity"] * s["unit_price"] * (1 - s["discount_pct"] / 100)
    return s


def ex5():
    s = load_sales()
    n = len(s[(s["channel"] == "Website") & (s["discount_pct"] >= 10)])
    print("website orders with >=10% discount:", n)
    print(s.nlargest(5, "quantity")[["order_id", "product_id", "quantity"]])   # nlargest = sort + head
    march = s[s["order_date"].dt.month == 3]
    print("distinct customers in March:", march["customer_id"].nunique())


def ex6():
    s = load_sales()
    s["weekday"] = s["order_date"].dt.day_name()
    by_day = s.groupby("weekday")["revenue"].sum().sort_values(ascending=False).round(0)
    print(by_day)
    weekend = by_day[["Saturday", "Sunday"]].sum()
    two_weekdays = by_day.drop(["Saturday", "Sunday"]).mean() * 2
    print(f"weekend total {weekend:,.0f} vs average two weekdays {two_weekdays:,.0f}")


def ex7():
    m = pd.read_csv(DATA / "sales_messy.csv").drop_duplicates()
    m["city"] = m["city"].str.strip().str.title().replace({"Bangalore": "Bengaluru", "New Delhi": "Delhi"})
    m["city"] = m["city"].fillna("Unknown")
    m["price"] = m["price"].str.replace(r"[^0-9.]", "", regex=True).astype(float)
    m = m.dropna(subset=["order_date"])
    m["quantity"] = m["quantity"].fillna(int(round(m["quantity"].median())))
    m = m[m["quantity"] > 0].copy()
    m["quantity"] = m["quantity"].astype(int)
    assert m.isna().sum().sum() == 0 and m.duplicated().sum() == 0
    print("cities:", sorted(m["city"].unique()))
    print("shape:", m.shape, "revenue:", (m["quantity"] * m["price"]).sum())


def ex8():
    st = pd.read_csv(DATA / "students.csv")
    out = st.groupby("section").agg(students=("student_id", "count"),
                                    avg_hours=("study_hours_per_week", "mean"),
                                    avg_math=("math", "mean")).round(2)
    print(out.sort_values("avg_math", ascending=False))


def ex9():
    s = load_sales()
    p = pd.read_csv(DATA / "products.csv").drop(columns="unit_price")
    c = pd.read_csv(DATA / "customers.csv")
    full = s.merge(p, on="product_id", how="left").merge(c, on="customer_id", how="left", indicator=True)
    print(full.groupby("segment")["revenue"].sum().sort_values(ascending=False).round(0))
    print("unmatched orders:", full.loc[full["_merge"] == "left_only", "order_id"].tolist())
    inner_total = s.merge(c, on="customer_id", how="inner")["revenue"].sum()
    print(f"left total {full['revenue'].sum():,.0f} vs inner total {inner_total:,.0f}")


def ex10():
    sheets = pd.read_excel(XLSX, sheet_name=None)          # every sheet in one call
    s, c = sheets["Sales"], sheets["Customers"]
    s["revenue"] = s["quantity"] * s["unit_price"] * (1 - s["discount_pct"] / 100)
    full = s.merge(c, on="customer_id", how="left")
    full["city"] = full["city"].fillna("Unknown")
    by_city = full.groupby("city").agg(orders=("order_id", "count"), revenue=("revenue", "sum")).round(0)
    top10 = (full.groupby(["customer_id", "customer_name"])["revenue"].sum()
             .nlargest(10).round(0).reset_index())
    path = OUT / "city_report.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        by_city.to_excel(w, sheet_name="Revenue by city")
        top10.to_excel(w, sheet_name="Top 10 customers", index=False)
        sheets["Products"].to_excel(w, sheet_name="Products", index=False)
    wb = load_workbook(path)
    for ws in wb.worksheets:
        for cell in ws[1]:
            cell.font = Font(bold=True)
        ws.column_dimensions["A"].width = 20
    wb.save(path)
    print("written", path, wb.sheetnames)


def ex11():
    s = load_sales()
    st = pd.read_csv(DATA / "students.csv")
    by_channel = s.groupby("channel")["revenue"].sum()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    a1.bar(by_channel.index, by_channel.values)
    a1.set_title("Revenue per channel"); a1.set_xlabel("Channel"); a1.set_ylabel("Revenue (Rs)")
    a2.hist(st["study_hours_per_week"], bins=15)
    a2.set_title("Study hours per week"); a2.set_xlabel("Hours"); a2.set_ylabel("Students")
    fig.tight_layout()
    fig.savefig(OUT / "two_charts.png", dpi=150)
    plt.close(fig)
    print("saved two_charts.png")


def ex12():
    st = pd.read_csv(DATA / "students.csv")
    # Missing-value decision: drop rows with missing attendance for Q1 (it is the grouping column);
    # fill missing science with the median so every student counts in Q2/Q3.
    st["science"] = st["science"].fillna(st["science"].median())
    q1 = st.dropna(subset=["attendance_pct"]).assign(high_att=lambda d: d["attendance_pct"] > 85)
    q1 = q1.groupby("high_att")["science"].mean().round(1).to_frame("avg_science")
    st["hours_band"] = pd.cut(st["study_hours_per_week"], bins=[0, 5, 10, 20], labels=["0-5", "5-10", "10+"])
    q2 = st.groupby("hours_band", observed=True)["math"].mean().round(1).to_frame("avg_math")
    q3 = st.groupby("section")[["math", "science", "english"]].mean().round(1)
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))
    q1["avg_science"].plot(kind="bar", ax=axes[0], title="Science: attendance > 85%?")
    q2["avg_math"].plot(kind="bar", ax=axes[1], title="Maths by study-hours band")
    q3.plot(kind="bar", ax=axes[2], title="Subject averages by section")
    fig.tight_layout(); fig.savefig(OUT / "student_eda.png", dpi=120); plt.close(fig)
    print(f"Q1: high attendance science avg {q1.loc[True, 'avg_science']} vs {q1.loc[False, 'avg_science']}")
    print(f"Q2: maths avg rises from {q2['avg_math'].iloc[0]} (0-5h) to {q2['avg_math'].iloc[-1]} (10h+)")
    print("Q3:\n", q3)
    with pd.ExcelWriter(OUT / "student_eda.xlsx", engine="openpyxl") as w:
        q1.to_excel(w, sheet_name="Q1 attendance")
        q2.to_excel(w, sheet_name="Q2 study hours")
        q3.to_excel(w, sheet_name="Q3 sections")


if __name__ == "__main__":
    t = ex1()
    for i, f in enumerate([ex2, lambda: ex3(t), ex4, ex5, ex6, ex7, ex8, ex9, ex10, ex11, ex12], start=2):
        print(f"\n===== Exercise {i} =====")
        f()
