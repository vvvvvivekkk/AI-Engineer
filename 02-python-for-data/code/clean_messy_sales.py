"""
clean_messy_sales.py - cleans data/sales_messy.csv and saves outputs/sales_clean.csv.

It follows the cleaning checklist from concepts.md, printing what it changed at each step.
Run:   python 02-python-for-data/code/clean_messy_sales.py
"""
from pathlib import Path                            # Path builds file paths that work on any OS

import pandas as pd                                 # pandas = tables in Python

HERE = Path(__file__).resolve().parent              # the folder this script lives in (code/)
DATA = HERE.parent / "data"                         # the data/ folder next to code/
OUT = HERE.parent / "outputs"                       # results go to outputs/ (ignored by git)


def clean(messy: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the messy sales table."""
    df = messy.copy()                               # work on a copy so the original stays untouched

    # 1. Duplicates: identical rows exported twice
    before = len(df)                                # remember the row count
    df = df.drop_duplicates()                       # keep the first copy of each repeated row
    print(f"1. removed {before - len(df)} duplicate rows")

    # 2. Text: strip spaces, fix capitals, merge different spellings
    df["city"] = (df["city"].str.strip()            # " pune " -> "pune"
                  .str.title()                      # "pune" -> "Pune"
                  .replace({"Bangalore": "Bengaluru", "New Delhi": "Delhi"}))   # one name per city
    df["product"] = df["product"].str.strip().str.title()                          # same idea for products
    print("2. cities now:", sorted(df["city"].dropna().unique()))

    # 3. Types: prices like "1,299" or "Rs 799" become numbers
    df["price"] = (df["price"].str.replace(r"[^0-9.]", "", regex=True)   # delete anything not a digit or dot
                   .astype(float))                                       # text -> decimal number
    print("3. price is now", df["price"].dtype)

    # 4. Missing values: decide per column
    df = df.dropna(subset=["order_date"])           # no date -> cannot use the order -> drop it
    median_qty = int(round(df["quantity"].median()))   # a typical quantity, as a whole number
    df["quantity"] = df["quantity"].fillna(median_qty) # fill blanks (pandas 3 style, no inplace)
    df["city"] = df["city"].fillna("Unknown")       # keep the row, label the blank city
    print(f"4. filled missing quantity with {median_qty}; blanks left: {int(df.isna().sum().sum())}")

    # 5. Impossible values: quantity must be positive
    bad = (df["quantity"] <= 0).sum()               # count the impossible rows
    df = df[df["quantity"] > 0].copy()              # keep only sensible rows (copy = independent table)
    print(f"5. removed {bad} rows with quantity <= 0")

    # Final types and a revenue column
    df["quantity"] = df["quantity"].astype(int)     # quantities are whole numbers
    df["order_date"] = pd.to_datetime(df["order_date"])   # text dates -> real dates
    df["revenue"] = df["quantity"] * df["price"]    # money per order
    return df


if __name__ == "__main__":                          # only runs when you execute this file directly
    messy = pd.read_csv(DATA / "sales_messy.csv")   # load the dirty file
    print("loaded", messy.shape)
    clean_df = clean(messy)                         # run every cleaning step
    OUT.mkdir(exist_ok=True)                        # make outputs/ if it does not exist
    clean_df.to_csv(OUT / "sales_clean.csv", index=False)   # save without the row-number column
    print("saved", OUT / "sales_clean.csv", clean_df.shape)
