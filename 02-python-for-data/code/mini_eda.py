"""
mini_eda.py - a compact exploratory data analysis of the sales data that saves charts as PNGs.

Run:   python 02-python-for-data/code/mini_eda.py
Output: charts and a findings.txt in 02-python-for-data/outputs/
"""
from pathlib import Path                                   # file paths

import matplotlib                                          # the plotting library
matplotlib.use("Agg")                                      # draw to files, no window needed (works on servers)
import matplotlib.pyplot as plt                            # the part of matplotlib we call directly
import pandas as pd                                        # tables

HERE = Path(__file__).resolve().parent                     # code/
DATA = HERE.parent / "data"                                # data/
OUT = HERE.parent / "outputs"                              # outputs/
OUT.mkdir(exist_ok=True)                                   # create it if missing

# --- Load and merge ---------------------------------------------------------------------
sales = pd.read_csv(DATA / "sales.csv", parse_dates=["order_date"])   # orders, with real dates
products = pd.read_csv(DATA / "products.csv")                          # product details
df = sales.merge(products.drop(columns="unit_price"), on="product_id", how="left")   # add category
df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)  # money per order
df["month"] = df["order_date"].dt.strftime("%Y-%m")       # month label like "2026-04"

# --- Chart 1: revenue by month (line = change over time) -------------------------------
monthly = df.groupby("month")["revenue"].sum()             # one total per month
fig, ax = plt.subplots(figsize=(8, 4))                     # a blank figure with one plot area
ax.plot(monthly.index, monthly.values, marker="o")         # draw the line with dots
ax.set_title("Revenue by month")                           # always a title...
ax.set_xlabel("Month")                                     # ...and labelled axes
ax.set_ylabel("Revenue (Rs)")
ax.set_ylim(0, monthly.max() * 1.15)                       # start at zero so changes are not exaggerated
fig.savefig(OUT / "revenue_by_month.png", dpi=150, bbox_inches="tight")   # save as an image
plt.close(fig)                                             # free the memory

# --- Chart 2: revenue by category (bar = compare groups) -------------------------------
by_cat = df.groupby("category")["revenue"].sum().sort_values()   # totals, smallest first
fig, ax = plt.subplots(figsize=(7, 4))
ax.barh(by_cat.index, by_cat.values)                       # horizontal bars leave room for labels
ax.set_title("Revenue by category")
ax.set_xlabel("Revenue (Rs)")
fig.savefig(OUT / "revenue_by_category.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# --- Chart 3: order size distribution (histogram = spread) ----------------------------
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(df["revenue"], bins=30)                            # 30 buckets, count orders in each
ax.set_title("How big are orders?")
ax.set_xlabel("Revenue per order (Rs)")
ax.set_ylabel("Number of orders")
fig.savefig(OUT / "order_size_hist.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# --- Findings in plain sentences -----------------------------------------------------
lines = [
    f"Total revenue Jan-Jun 2026: Rs {df['revenue'].sum():,.0f} from {len(df)} orders.",
    f"Best month: {monthly.idxmax()} (Rs {monthly.max():,.0f}).",
    f"Top category: {by_cat.idxmax()} (Rs {by_cat.max():,.0f}).",
    f"Median order: Rs {df['revenue'].median():,.0f}; mean order: Rs {df['revenue'].mean():,.0f}.",
]
(OUT / "findings.txt").write_text("\n".join(lines), encoding="utf-8")   # save the findings
print("\n".join(lines))                                    # and show them
print("charts saved in", OUT)
