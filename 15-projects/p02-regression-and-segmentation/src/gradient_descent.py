"""
gradient_descent.py - linear regression trained "by hand" with NumPy, no scikit-learn.

Idea (module 03): a linear model predicts  y_hat = X @ w + b
  * X  - the table of features (one row per patient)
  * w  - one weight per feature (how much that feature pushes the prediction up or down)
  * b  - the bias (the prediction when every feature is 0)
We measure how wrong we are with the mean squared error (MSE): the average of (y_hat - y)^2.
The gradient tells us which direction makes the error go UP, so we step the other way:
  w = w - learning_rate * dMSE/dw        b = b - learning_rate * dMSE/db
Analogy: walking downhill in fog by feeling which way the ground slopes under your feet.
"""
from __future__ import annotations

import numpy as np


def fit_gradient_descent(X: np.ndarray, y: np.ndarray, lr: float = 0.1, epochs: int = 2000):
    """Return (weights, bias, loss_history). X should be scaled (similar ranges per column)."""
    n_rows, n_features = X.shape
    w = np.zeros(n_features)          # start with every weight at zero
    b = float(y.mean())               # start the bias at the average answer (a sensible guess)
    history = []
    for _ in range(epochs):           # one "epoch" = one pass over all rows
        y_hat = X @ w + b             # predictions for every row at once (vectorised)
        error = y_hat - y             # how far off each prediction is
        history.append(float((error ** 2).mean()))   # MSE for this step
        # Gradients of MSE (from calculus): average of 2 * error * feature
        grad_w = 2 * X.T @ error / n_rows
        grad_b = 2 * error.mean()
        w -= lr * grad_w              # take a small step downhill
        b -= lr * grad_b
    return w, b, history


def predict(X: np.ndarray, w: np.ndarray, b: float) -> np.ndarray:
    return X @ w + b
