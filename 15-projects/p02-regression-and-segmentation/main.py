"""
main.py - runs Project 2.

    python main.py                  # both parts
    python main.py --part regression
    python main.py --part segmentation
Charts and tables are written to reports/.
"""
import argparse
from pathlib import Path

import pandas as pd

from src import regression, segmentation

HERE = Path(__file__).resolve().parent
pd.set_option("display.width", 120)


def main() -> None:
    ap = argparse.ArgumentParser(description="Regression + customer segmentation")
    ap.add_argument("--part", choices=["regression", "segmentation", "all"], default="all")
    ap.add_argument("--out", default=str(HERE / "reports"))
    args = ap.parse_args()
    out = Path(args.out)

    if args.part in ("regression", "all"):
        table = regression.run(out)
        print("=== Part A: diabetes progression (test set) ===")
        print(table.round(2).to_string(index=False))
        print(f"best model: {table.attrs['best']}")
        print(f"hand-written GD vs scikit-learn: largest weight difference = "
              f"{table.attrs['gd_vs_sklearn_max_weight_gap']:.4f}")
        table.round(3).to_csv(out / "regression_scores.csv", index=False)

    if args.part in ("segmentation", "all"):
        res = segmentation.run(out)
        print("\n=== Part B: customer segmentation ===")
        print(res["k_table"].round(3).to_string(index=False))
        print(f"chosen k = {res['best_k']} (highest silhouette)")
        print(res["profile"].round(1).to_string())
        print(f"agreement with the hidden true groups (adjusted Rand index, 1 = perfect): {res['ari']:.3f}")
        res["profile"].round(2).to_csv(out / "segment_profiles.csv")

    print(f"\nCharts and tables written to {out}")


if __name__ == "__main__":
    main()
