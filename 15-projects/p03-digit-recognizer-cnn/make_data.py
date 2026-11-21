"""
make_data.py - saves scikit-learn's bundled 8x8 handwritten digits as data/digits.csv.

Each row = one image: 64 columns p0..p63 (pixel brightness 0-16, read left-to-right, top-to-bottom)
plus a "label" column (the digit 0-9). 1,797 images, no internet needed.

Run:  python make_data.py
"""
from pathlib import Path

import pandas as pd
from sklearn.datasets import load_digits

DATA_DIR = Path(__file__).resolve().parent / "data"


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    digits = load_digits()
    df = pd.DataFrame(digits.data.astype(int), columns=[f"p{i}" for i in range(64)])
    df["label"] = digits.target
    df.to_csv(DATA_DIR / "digits.csv", index=False)
    print(f"wrote data/digits.csv: {len(df)} images of 8x8 pixels")


if __name__ == "__main__":
    main()
