"""
regression.py - Part A: predict diabetes disease progression (a number) from 10 features.

Regression = predicting a number (not a category). We compare:
  * our hand-written gradient descent (src/gradient_descent.py)
  * scikit-learn LinearRegression (the exact "closed-form" answer)
  * Ridge (linear regression with a penalty on big weights, to reduce overfitting)
  * GradientBoostingRegressor (many small decision trees, each fixing the last one's errors)
Metrics:
  * MAE  - mean absolute error: average size of the miss, in the target's units
  * RMSE - root mean squared error: like MAE but punishes big misses more
  * R^2  - share of the target's variation the model explains (1 = perfect, 0 = no better than the mean)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .gradient_descent import fit_gradient_descent, predict

DATA = Path(__file__).resolve().parents[1] / "data" / "diabetes.csv"
SEED = 42


def load() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(DATA)
    return df.drop(columns=["target"]), df["target"]


def scores(y_true, y_pred) -> dict:
    return {"MAE": mean_absolute_error(y_true, y_pred),
            "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "R2": r2_score(y_true, y_pred)}


def run(out_dir: Path) -> pd.DataFrame:
    X, y = load()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED)

    # --- 1. Hand-written gradient descent. Scale first: GD hates columns with very different ranges.
    scaler = StandardScaler().fit(X_train)           # learn mean/spread from TRAIN only
    Xs_train, Xs_test = scaler.transform(X_train), scaler.transform(X_test)
    w, b, history = fit_gradient_descent(Xs_train, y_train.to_numpy(), lr=0.1, epochs=5000)

    # --- 2. scikit-learn models (each in a pipeline with the same scaling)
    models = {
        "linear_regression": make_pipeline(StandardScaler(), LinearRegression()),
        "ridge(alpha=1)": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
        "gradient_boosting": GradientBoostingRegressor(n_estimators=150, max_depth=2,
                                                       learning_rate=0.05, random_state=SEED),
    }
    rows = [{"model": "our_gradient_descent", **scores(y_test, predict(Xs_test, w, b))}]
    preds = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds[name] = model.predict(X_test)
        rows.append({"model": name, **scores(y_test, preds[name])})
    # A "baseline" that always predicts the training average - every real model must beat this
    rows.append({"model": "baseline_mean", **scores(y_test, np.full(len(y_test), y_train.mean()))})
    table = pd.DataFrame(rows)

    # --- 3. Did our hand-written GD find the same weights as scikit-learn? (it should, closely)
    sk_w = models["linear_regression"][-1].coef_
    max_gap = float(np.abs(sk_w - w).max())

    # --- 4. Charts: GD loss curve and residuals of the best model
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(history)
    axes[0].set(yscale="log", xlabel="epoch", ylabel="training MSE (log scale)",
                title="Gradient descent: error goes downhill")
    best = table[table.model.isin(models)].sort_values("RMSE").iloc[0]["model"]
    residuals = y_test - preds[best]                  # residual = true - predicted
    axes[1].scatter(preds[best], residuals, alpha=0.6)
    axes[1].axhline(0, color="black", lw=1)
    axes[1].set(xlabel="predicted progression", ylabel="residual (true - predicted)",
                title=f"Residuals of {best}")
    fig.tight_layout()
    fig.savefig(out_dir / "regression.png", dpi=110)
    plt.close(fig)

    table.attrs["gd_vs_sklearn_max_weight_gap"] = max_gap
    table.attrs["best"] = best
    return table
