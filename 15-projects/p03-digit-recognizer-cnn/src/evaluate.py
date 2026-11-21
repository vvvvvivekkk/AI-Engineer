"""
evaluate.py - pictures that help you understand what the network learned and where it fails.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix


def plot_curves(histories: dict, out_png: Path) -> None:
    """Training vs validation loss per epoch for each model. A widening gap = overfitting."""
    fig, axes = plt.subplots(1, len(histories), figsize=(5.5 * len(histories), 4), squeeze=False)
    for ax, (name, h) in zip(axes[0], histories.items()):
        ax.plot(h["train_loss"], label="train")
        ax.plot(h["val_loss"], label="validation")
        ax.axvline(h["best_epoch"] - 1, ls="--", color="grey", label=f"best epoch {h['best_epoch']}")
        ax.set(title=f"{name} loss", xlabel="epoch", ylabel="cross-entropy loss")
        ax.legend()
    fig.tight_layout()
    fig.savefig(out_png, dpi=110)
    plt.close(fig)


def plot_confusion(y_true, y_pred, title: str, out_png: Path) -> np.ndarray:
    m = confusion_matrix(y_true, y_pred, labels=list(range(10)))
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ConfusionMatrixDisplay(m, display_labels=list(range(10))).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_png, dpi=110)
    plt.close(fig)
    return m


def plot_misclassified(images, y_true, y_pred, out_png: Path, max_n: int = 16) -> int:
    """Show the test images the model got wrong, with 'true -> predicted' above each."""
    wrong = np.flatnonzero(y_true != y_pred)
    n = min(len(wrong), max_n)
    cols = 8
    rows = max(1, int(np.ceil(n / cols)))
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 1.3, rows * 1.5), squeeze=False)
    for ax in axes.ravel():
        ax.axis("off")
    for ax, idx in zip(axes.ravel(), wrong[:n]):
        ax.imshow(images[idx, 0], cmap="gray_r")
        ax.set_title(f"{y_true[idx]}->{y_pred[idx]}", fontsize=9, color="crimson")
    fig.suptitle(f"Misclassified test digits ({len(wrong)} total, showing {n})")
    fig.tight_layout()
    fig.savefig(out_png, dpi=110)
    plt.close(fig)
    return int(len(wrong))


def plot_filters(cnn, out_png: Path) -> None:
    """The 16 learned 3x3 filters of the CNN's first layer (dark = strong positive weight)."""
    w = cnn.features[0].weight.detach().numpy()[:, 0]   # shape (16, 3, 3)
    fig, axes = plt.subplots(2, 8, figsize=(9, 2.6))
    for ax, f in zip(axes.ravel(), w):
        ax.imshow(f, cmap="gray_r")
        ax.axis("off")
    fig.suptitle("First-layer CNN filters (tiny pattern detectors)")
    fig.tight_layout()
    fig.savefig(out_png, dpi=110)
    plt.close(fig)
