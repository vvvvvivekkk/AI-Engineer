"""
data.py - loads the digit images and turns them into PyTorch tensors.

Jargon:
  * tensor     - PyTorch's version of a NumPy array (a grid of numbers) that can also track gradients
  * DataLoader - hands the model the data in small shuffled "batches" (e.g. 64 images at a time)
  * validation set - a slice of the training data we use to decide when to stop training.
                     The TEST set stays untouched until the very end.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

CSV = Path(__file__).resolve().parents[1] / "data" / "digits.csv"
SEED = 0


def load_arrays() -> tuple[np.ndarray, np.ndarray]:
    """Return images as (N, 1, 8, 8) floats scaled to 0..1, and labels as (N,) ints."""
    if CSV.exists():
        df = pd.read_csv(CSV)
        pixels, labels = df.drop(columns=["label"]).to_numpy(), df["label"].to_numpy()
    else:  # fallback: straight from scikit-learn (also offline)
        from sklearn.datasets import load_digits
        d = load_digits()
        pixels, labels = d.data, d.target
    # 1 channel (greyscale) x 8 rows x 8 columns; divide by 16 so values are between 0 and 1
    images = (pixels / 16.0).astype("float32").reshape(-1, 1, 8, 8)
    return images, labels.astype("int64")


def split(images, labels):
    """70% train, 15% validation, 15% test, each with the same mix of digits (stratified)."""
    x_tr, x_tmp, y_tr, y_tmp = train_test_split(images, labels, test_size=0.30,
                                                random_state=SEED, stratify=labels)
    x_val, x_te, y_val, y_te = train_test_split(x_tmp, y_tmp, test_size=0.50,
                                                random_state=SEED, stratify=y_tmp)
    return (x_tr, y_tr), (x_val, y_val), (x_te, y_te)


def augment(images: torch.Tensor, generator: torch.Generator) -> torch.Tensor:
    """Data augmentation: make slightly changed copies so the model can't memorise exact pixels.
    Each image is shifted by up to 1 pixel in each direction and gets a little random noise."""
    out = images.clone()
    shifts = torch.randint(-1, 2, (len(images), 2), generator=generator)
    # Group images by their shift (only 9 combinations) and slide each group in one go - fast.
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            mask = (shifts[:, 0] == dy) & (shifts[:, 1] == dx)
            if mask.any() and (dy or dx):
                out[mask] = torch.roll(images[mask], shifts=(dy, dx), dims=(2, 3))  # slide the picture
    noise = torch.randn(images.shape, generator=generator) * 0.05
    return (out + noise).clamp(0, 1)


def loader(x, y, batch_size=64, shuffle=False) -> DataLoader:
    ds = TensorDataset(torch.from_numpy(x), torch.from_numpy(y))
    g = torch.Generator().manual_seed(SEED)  # makes shuffling repeatable
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, generator=g)
