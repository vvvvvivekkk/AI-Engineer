"""
make_data.py - writes the three sample datasets used by this project into data/ as CSV files.

The datasets come bundled with scikit-learn (no internet needed). We still save them as CSV
so you can open them in Excel or pandas and see exactly what the model sees.

Run:  python make_data.py
"""
from pathlib import Path

from sklearn.datasets import load_breast_cancer, load_iris, load_wine

# Folder where the CSV files go (data/ next to this script)
DATA_DIR = Path(__file__).resolve().parent / "data"


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    # Each loader returns a "Bunch" (a dictionary-like object). as_frame=True gives a pandas table.
    loaders = {"wine": load_wine, "iris": load_iris, "breast_cancer": load_breast_cancer}
    for name, loader in loaders.items():
        bunch = loader(as_frame=True)
        df = bunch.frame.copy()                      # features + a "target" column with numbers 0,1,2...
        # Add a readable class name next to the number so humans can read the CSV.
        df["target_name"] = [bunch.target_names[i] for i in df["target"]]
        out = DATA_DIR / f"{name}.csv"
        df.to_csv(out, index=False)
        print(f"wrote {out.name}: {len(df)} rows, {df.shape[1] - 2} feature columns")


if __name__ == "__main__":
    main()
