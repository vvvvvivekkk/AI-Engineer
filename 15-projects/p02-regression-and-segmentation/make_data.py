"""
make_data.py - creates the two sample datasets for Project 2 in data/.

1. data/diabetes.csv  - scikit-learn's bundled diabetes dataset (442 patients, 10 features,
                        target = a measure of disease progression one year later).
2. data/customers.csv - 600 made-up shop customers in 4 hidden groups, generated with a fixed
                        random seed so everyone gets exactly the same file.

Run:  python make_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import load_diabetes, make_blobs

DATA_DIR = Path(__file__).resolve().parent / "data"
SEED = 7


def make_diabetes() -> pd.DataFrame:
    # as_frame=True returns a pandas table; the features are already centred and scaled by sklearn
    return load_diabetes(as_frame=True).frame


def make_customers(n: int = 600) -> pd.DataFrame:
    """Synthetic customers. make_blobs draws points around 4 centres ("blobs") = 4 hidden segments."""
    # Centres in (annual spend in $, visits per month, days since last visit)
    centres = [
        [3000, 12, 4],     # loyal big spenders
        [ 800,  3, 20],    # occasional shoppers
        [2000,  6, 90],    # used to be good, drifting away ("at risk")
        [ 300,  1, 200],   # nearly lost
    ]
    # Each column has its own natural spread (dollars vary by hundreds, visits by a few).
    spread = np.array([350, 1.2, 12])
    # make_blobs works best with a spread of 1, so we build blobs in "spread units"
    # (centre / spread) and multiply back afterwards.
    X, hidden = make_blobs(n_samples=n, centers=np.asarray(centres) / spread,
                           cluster_std=1.0, random_state=SEED)
    X = X * spread
    X[:, 0] = X[:, 0].clip(50)            # spend can't be negative
    X[:, 1] = X[:, 1].clip(0.5)           # at least one visit every two months
    X[:, 2] = X[:, 2].clip(0)             # days can't be negative
    df = pd.DataFrame(X, columns=["annual_spend", "visits_per_month", "days_since_last_visit"])
    # A derived column: average basket = spend / (visits per year)
    df["avg_basket"] = df["annual_spend"] / (df["visits_per_month"] * 12)
    df = df.round(2)
    df.insert(0, "customer_id", [f"C{i:04d}" for i in range(n)])
    df["hidden_segment"] = hidden  # the "true" group - only for checking; never used to train
    return df


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    make_diabetes().to_csv(DATA_DIR / "diabetes.csv", index=False)
    make_customers().to_csv(DATA_DIR / "customers.csv", index=False)
    print("wrote data/diabetes.csv and data/customers.csv")


if __name__ == "__main__":
    main()
