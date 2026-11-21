"""
make_data.py - creates the synthetic (made-up but realistic) practice datasets for module 02.

Called by build.py. Everything uses a fixed random seed (42), so the files come out
identical every time you rebuild. Nothing here is real customer data.

Outputs:
  data/products.csv, data/customers.csv, data/sales.csv, data/students.csv, data/sales_messy.csv
  excel/practice-datasets.xlsx  (one sheet per dataset + an About sheet)
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import workbook  # noqa: E402

DATA = HERE / "data"
EXCEL = HERE / "excel"
SEED = 42


def make_products() -> pd.DataFrame:
    rows = [
        ("P001", "Wireless Mouse", "Electronics", 799),
        ("P002", "Bluetooth Headphones", "Electronics", 2499),
        ("P003", "USB-C Charger", "Electronics", 1199),
        ("P004", "A5 Notebook (5 pack)", "Stationery", 249),
        ("P005", "Gel Pen Set", "Stationery", 149),
        ("P006", "Desk Organizer", "Stationery", 599),
        ("P007", "Steel Water Bottle", "Home", 449),
        ("P008", "Ceramic Mug Set", "Home", 699),
        ("P009", "LED Desk Lamp", "Home", 1499),
        ("P010", "Cotton T-Shirt", "Clothing", 499),
        ("P011", "Hoodie", "Clothing", 1299),
        ("P012", "Backpack", "Clothing", 1799),
    ]
    return pd.DataFrame(rows, columns=["product_id", "product_name", "category", "unit_price"])


def make_customers(rng: np.random.Generator, n: int = 60) -> pd.DataFrame:
    first = ["Aarav", "Diya", "Kabir", "Meera", "Rohan", "Ananya", "Arjun", "Isha", "Vikram", "Sneha",
             "Rahul", "Priya", "Karthik", "Lakshmi", "Nikhil", "Pooja", "Siddharth", "Tanvi", "Varun", "Zara"]
    last = ["Sharma", "Reddy", "Iyer", "Patel", "Khan", "Nair", "Gupta", "Rao", "Das", "Menon",
            "Singh", "Joshi", "Kulkarni", "Bose", "Verma"]
    cities = ["Hyderabad", "Bengaluru", "Chennai", "Mumbai", "Delhi", "Pune"]
    city_p = [0.26, 0.22, 0.14, 0.16, 0.12, 0.10]
    segments = ["Retail", "Student", "Corporate"]
    seg_p = [0.55, 0.30, 0.15]
    names = set()
    while len(names) < n:
        names.add(f"{rng.choice(first)} {rng.choice(last)}")
    start = pd.Timestamp("2024-01-01")
    signup = start + pd.to_timedelta(rng.integers(0, 730, n), unit="D")
    df = pd.DataFrame({
        "customer_id": [f"C{i:03d}" for i in range(1, n + 1)],
        "customer_name": sorted(names),
        "city": rng.choice(cities, n, p=city_p),
        "segment": rng.choice(segments, n, p=seg_p),
        "signup_date": signup.normalize(),
    })
    return df


def make_sales(rng: np.random.Generator, products: pd.DataFrame, customers: pd.DataFrame, n: int = 600) -> pd.DataFrame:
    # Some customers buy far more often than others (realistic "heavy users").
    cust_w = rng.dirichlet(np.ones(len(customers)) * 0.8)
    prod_w = np.array([10, 5, 7, 12, 14, 5, 9, 6, 4, 11, 6, 5], dtype=float)
    prod_w /= prod_w.sum()
    # Orders grow a little each month (Jan..Jun 2026), with a June spike.
    days = pd.date_range("2026-01-01", "2026-06-30", freq="D")
    month_boost = {1: 1.0, 2: 1.0, 3: 1.15, 4: 1.2, 5: 1.3, 6: 1.6}
    day_w = np.array([month_boost[d.month] * (1.25 if d.dayofweek >= 5 else 1.0) for d in days])
    day_w /= day_w.sum()
    order_dates = np.sort(rng.choice(days, n, p=day_w))
    cust = rng.choice(customers["customer_id"], n, p=cust_w)
    prod = rng.choice(products["product_id"], n, p=prod_w)
    price = products.set_index("product_id").loc[prod, "unit_price"].to_numpy()
    qty = np.clip(rng.poisson(1.2, n) + 1, 1, 6)
    # Cheap items are bought in bigger quantities.
    qty = np.where(price < 300, qty + rng.integers(0, 4, n), qty)
    discount = rng.choice([0, 5, 10, 15, 20], n, p=[0.45, 0.2, 0.18, 0.12, 0.05])
    channel = rng.choice(["Website", "App", "Store"], n, p=[0.45, 0.35, 0.20])
    df = pd.DataFrame({
        "order_id": [f"O{10001 + i}" for i in range(n)],
        "order_date": pd.to_datetime(order_dates).normalize(),
        "customer_id": cust,
        "product_id": prod,
        "quantity": qty,
        "unit_price": price,
        "discount_pct": discount,
        "channel": channel,
    })
    # Three orders from a customer id that is NOT in customers.csv -> teaches left joins / indicator.
    df.loc[[57, 301, 488], "customer_id"] = "C099"
    return df


def make_students(rng: np.random.Generator, n: int = 120) -> pd.DataFrame:
    hours = np.clip(rng.normal(8, 3, n), 1, 18).round(1)
    attendance = np.clip(62 + hours * 2 + rng.normal(0, 7, n), 45, 100).round(0)
    math = np.clip(30 + 3.4 * hours + 0.2 * attendance + rng.normal(0, 8, n), 5, 100).round(0)
    science = np.clip(32 + 2.8 * hours + 0.25 * attendance + rng.normal(0, 9, n), 5, 100).round(0)
    english = np.clip(55 + 1.0 * hours + rng.normal(0, 11, n), 10, 100).round(0)
    df = pd.DataFrame({
        "student_id": [f"S{i:03d}" for i in range(1, n + 1)],
        "section": rng.choice(["A", "B", "C"], n),
        "study_hours_per_week": hours,
        "attendance_pct": attendance,
        "math": math,
        "science": science,
        "english": english,
    })
    # Realistic gaps: some scores and attendance values were never recorded.
    df.loc[rng.choice(n, 6, replace=False), "science"] = np.nan
    df.loc[rng.choice(n, 4, replace=False), "attendance_pct"] = np.nan
    return df


def make_messy(rng: np.random.Generator, sales: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """A deliberately dirty export: the kind of file people really get from other teams."""
    base = sales.head(80).merge(customers, on="customer_id", how="left").merge(products, on="product_id", how="left",
                                                                             suffixes=("", "_p"))
    city_variants = {
        "Hyderabad": ["Hyderabad", "hyderabad", " Hyderabad", "HYDERABAD", "Hyderabad "],
        "Bengaluru": ["Bengaluru", "bengaluru", "Bangalore", "Bengaluru "],
        "Chennai": ["Chennai", "chennai "],
        "Mumbai": ["Mumbai", "MUMBAI", "mumbai"],
        "Delhi": ["Delhi", "delhi", "New Delhi"],
        "Pune": ["Pune", "pune "],
    }
    city = [rng.choice(city_variants.get(c, ["Hyderabad"])) if isinstance(c, str) else "" for c in base["city"]]
    product = [p if rng.random() < 0.7 else (p.lower() if rng.random() < 0.5 else p.upper()) for p in base["product_name"]]

    def fmt_price(v):
        r = rng.random()
        if r < 0.5:
            return str(int(v))
        if r < 0.8:
            return f"{int(v):,}"
        return f"Rs {int(v)}"

    price = [fmt_price(v) for v in base["unit_price"]]
    qty = base["quantity"].astype("float").copy()
    messy = pd.DataFrame({
        "order_id": base["order_id"],
        "order_date": base["order_date"].dt.strftime("%Y-%m-%d"),
        "customer_name": base["customer_name"].fillna("Unknown"),
        "city": city,
        "product": product,
        "quantity": qty,
        "price": price,
    })
    messy.loc[[3, 17, 42, 66], "quantity"] = np.nan          # missing quantities
    messy.loc[25, "quantity"] = -2                           # a typo (negative quantity)
    messy.loc[[9, 51], "order_date"] = None                  # missing dates
    messy.loc[[12, 70], "city"] = ""                         # blank city
    dupes = messy.loc[[5, 20, 33, 48, 60]]                   # five rows exported twice
    messy = pd.concat([messy, dupes], ignore_index=True)
    messy = messy.sample(frac=1, random_state=SEED).reset_index(drop=True)
    return messy


def df_rows(df: pd.DataFrame) -> list[list]:
    """DataFrame -> list of lists for build_kit.workbook (header first, NaN -> empty cell)."""
    out = [list(df.columns)]
    for rec in df.itertuples(index=False):
        row = []
        for v in rec:
            if isinstance(v, pd.Timestamp):
                row.append(v.to_pydatetime().date())
            elif isinstance(v, float) and np.isnan(v):
                row.append(None)
            elif isinstance(v, (np.integer,)):
                row.append(int(v))
            elif isinstance(v, (np.floating,)):
                row.append(float(v))
            else:
                row.append(v)
        out.append(row)
    return out


def build_all() -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(SEED)
    products = make_products()
    customers = make_customers(rng)
    sales = make_sales(rng, products, customers)
    students = make_students(rng)
    messy = make_messy(rng, sales, customers, products)

    DATA.mkdir(exist_ok=True)
    EXCEL.mkdir(exist_ok=True)
    products.to_csv(DATA / "products.csv", index=False)
    customers.to_csv(DATA / "customers.csv", index=False, date_format="%Y-%m-%d")
    sales.to_csv(DATA / "sales.csv", index=False, date_format="%Y-%m-%d")
    students.to_csv(DATA / "students.csv", index=False)
    messy.to_csv(DATA / "sales_messy.csv", index=False)

    about = [
        ["Sheet", "Rows", "What it contains"],
        ["Sales", len(sales), "One row per order, Jan-Jun 2026. Revenue = quantity * unit_price * (1 - discount_pct/100)."],
        ["Customers", len(customers), "One row per customer: city, segment (Retail/Student/Corporate), signup date."],
        ["Products", len(products), "12 products in 4 categories with list price in rupees."],
        ["Students", len(students), "Study hours, attendance and three exam scores. Some values are missing on purpose."],
        ["Messy_Sales", len(messy), "A dirty export: duplicates, blanks, mixed-case cities, prices stored as text."],
        ["Note", "", "All data is synthetic (generated by make_data.py with seed 42). It is not real."],
    ]
    workbook({
        "About": about,
        "Sales": df_rows(sales),
        "Customers": df_rows(customers),
        "Products": df_rows(products),
        "Students": df_rows(students),
        "Messy_Sales": df_rows(messy),
    }, EXCEL / "practice-datasets.xlsx", col_widths={"About": [14, 8, 90]})
    return {"products": products, "customers": customers, "sales": sales, "students": students, "messy": messy}


if __name__ == "__main__":
    d = build_all()
    for k, v in d.items():
        print(k, v.shape)
