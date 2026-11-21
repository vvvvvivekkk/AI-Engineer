"""
make_db.py - build a small, fake sales database with a few planted problems.

**SQLite** - a whole database stored in one file (data/sales.db). Python can
read it with the built-in `sqlite3` module; no server needed.

Tables:
  regions(region_id, name)
  products(product_id, name, category, unit_price)
  orders(order_id, order_date, region_id, product_id, quantity, discount, revenue)

Twelve months of orders (2025-01-01 .. 2025-12-31) are generated with NumPy
using a fixed **seed** (so the "random" data is the same every run).

Planted anomalies (the agent should find these):
  1. North region, Q4 (Oct-Dec): the Smart Kettle stops selling (supplier
     problem) -> North has the biggest quarter-on-quarter revenue drop.
  2. South region, August: a promo code gives 50% discounts on many orders.
  3. West region, 14 July: a system glitch inserts 40 duplicate orders.
Ops notes explaining these live in data/notes/*.md (for the search_notes tool).

Run:  python -m src.make_db
"""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DATA / "sales.db"
SEED = 7

REGIONS = ["North", "South", "East", "West"]
PRODUCTS = [  # name, category, unit price (dollars)
    ("Smart Kettle", "Kitchen", 60.0), ("Coffee Grinder", "Kitchen", 45.0), ("Blender Pro", "Kitchen", 90.0),
    ("Desk Lamp", "Home Office", 35.0), ("Ergo Chair", "Home Office", 220.0), ("Monitor Arm", "Home Office", 75.0),
    ("Yoga Mat", "Fitness", 25.0), ("Dumbbell Set", "Fitness", 80.0), ("Water Bottle", "Fitness", 15.0),
    ("Air Purifier", "Home", 150.0),
]
NOTES = {
    "2025-10-ops-north.md": "# Ops note - October 2025, North warehouse\n\nOur Smart Kettle supplier failed a safety audit on 28 September. "
                            "The North warehouse could not restock Smart Kettles from October until at least January. "
                            "Kettle-plus-grinder and kettle-plus-blender bundles were also paused, so other Kitchen sales in the North fell too. "
                            "Other regions are served by a different supplier and were not affected.\n",
    "2025-08-marketing-south.md": "# Marketing note - August 2025, South region\n\nThe SUMMER50 promo code was meant for staff only "
                                  "but leaked on social media. Many South customers received a 50% discount during August. "
                                  "The code was disabled on 31 August. Margin in the South fell sharply that month.\n",
    "2025-07-it-incident.md": "# IT incident - 14 July 2025\n\nA retry bug in the checkout service wrote some West region orders twice on 14 July. "
                              "Finance should exclude duplicated order rows (same date, product, quantity and region) from reports.\n",
    "2025-q3-summary.md": "# Q3 2025 business summary\n\nRevenue grew in every region in Q3. Fitness products sold best in summer. "
                          "Ergo Chair remains the highest-revenue product overall.\n",
}


def build(path: Path = DB_PATH, seed: int = SEED) -> Path:
    rng = np.random.default_rng(seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()                                   # always rebuild from scratch
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE regions(region_id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE products(product_id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT, unit_price REAL);
        CREATE TABLE orders(order_id INTEGER PRIMARY KEY, order_date TEXT, region_id INTEGER, product_id INTEGER,
                            quantity INTEGER, discount REAL, revenue REAL,
                            FOREIGN KEY(region_id) REFERENCES regions(region_id),
                            FOREIGN KEY(product_id) REFERENCES products(product_id));
    """)
    cur.executemany("INSERT INTO regions VALUES (?, ?)", list(enumerate(REGIONS, 1)))
    cur.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", [(i, *p) for i, p in enumerate(PRODUCTS, 1)])

    rows, oid = [], 1
    day = date(2025, 1, 1)
    while day.year == 2025:
        season = 1.0 + 0.05 * np.sin((day.timetuple().tm_yday - 80) / 365 * 2 * np.pi)   # yearly wave, peak in June
        for rid, region in enumerate(REGIONS, 1):
            for _ in range(rng.poisson(8 * season)):                                # ~8 orders/day/region
                pid = int(rng.integers(1, len(PRODUCTS) + 1))
                name = PRODUCTS[pid - 1][0]
                if region == "North" and name == "Smart Kettle" and day.month >= 10:
                    continue                                                        # anomaly 1: no kettles
                if region == "North" and PRODUCTS[pid - 1][1] == "Kitchen" and day.month >= 10 and rng.random() < 0.8:
                    continue                                    # ...and kettle bundles (grinder/blender) fall too
                qty = int(rng.integers(1, 5))
                discount = float(rng.choice([0, 0, 0, 0.05, 0.1]))
                if region == "South" and day.month == 8 and rng.random() < 0.6:
                    discount = 0.5                                                  # anomaly 2: leaked promo
                revenue = round(qty * PRODUCTS[pid - 1][2] * (1 - discount), 2)
                rows.append((oid, day.isoformat(), rid, pid, qty, discount, revenue))
                oid += 1
        day += timedelta(days=1)

    dupes = [r for r in rows if r[1] == "2025-07-14" and r[2] == REGIONS.index("West") + 1]
    for r in (dupes * 10)[:40]:                                                     # anomaly 3: duplicates
        rows.append((oid, *r[1:]))
        oid += 1
    cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
    con.commit()
    con.close()

    notes_dir = DATA / "notes"
    notes_dir.mkdir(exist_ok=True)
    for name, text in NOTES.items():
        (notes_dir / name).write_text(text, encoding="utf-8")
    return path


if __name__ == "__main__":
    p = build()
    con = sqlite3.connect(p)
    n = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    print(f"wrote {p.name}: {n} orders, {len(NOTES)} notes in data/notes/")
