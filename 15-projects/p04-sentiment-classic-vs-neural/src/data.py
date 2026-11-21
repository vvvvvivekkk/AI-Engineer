"""data.py - load the review CSVs and make one fixed train/test split used by all three models."""
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
LABELS = ["negative", "positive"]   # index 0 = negative, 1 = positive
SEED = 42


def load_split():
    """Return (train_df, test_df) - 80% / 20%, same balance of labels in both."""
    df = pd.read_csv(DATA_DIR / "reviews.csv")
    return train_test_split(df, test_size=0.2, random_state=SEED, stratify=df["label"])


def load_challenge() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "challenge.csv")
