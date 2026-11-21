"""Tests for Project 2. Run with:  python -m pytest -q"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import regression, segmentation
from src.gradient_descent import fit_gradient_descent, predict


def test_gradient_descent_recovers_a_known_line():
    # Make data from a line we know: y = 3*x1 - 2*x2 + 5 (no noise). GD should find 3, -2 and 5.
    rng = np.random.default_rng(0)
    X = rng.normal(size=(200, 2))
    y = 3 * X[:, 0] - 2 * X[:, 1] + 5
    w, b, history = fit_gradient_descent(X, y, lr=0.1, epochs=1000)
    assert np.allclose(w, [3, -2], atol=1e-3) and abs(b - 5) < 1e-3
    assert history[-1] < history[0]                 # the loss went down
    assert np.allclose(predict(X, w, b), y, atol=1e-2)


def test_regression_models_beat_the_mean_baseline(tmp_path):
    table = regression.run(tmp_path).set_index("model")
    assert table.loc["linear_regression", "RMSE"] < table.loc["baseline_mean", "RMSE"]
    assert table.loc["our_gradient_descent", "RMSE"] < table.loc["baseline_mean", "RMSE"]
    assert table.attrs["gd_vs_sklearn_max_weight_gap"] < 0.1  # GD matches the exact solution
    assert (tmp_path / "regression.png").exists()


def test_segmentation_finds_the_four_planted_groups(tmp_path):
    res = segmentation.run(tmp_path)
    assert res["best_k"] == 4
    assert res["ari"] > 0.9
    assert (tmp_path / "customers_with_segments.csv").exists()
