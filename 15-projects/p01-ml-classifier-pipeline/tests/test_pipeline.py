"""Tests for Project 1. Run with:  python -m pytest -q"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so "import src" works from anywhere

from src.pipeline import build_candidates, compare_models, evaluate, load_dataset, run_experiment, split


def test_load_dataset_shapes():
    X, y, names = load_dataset("wine")
    assert X.shape == (178, 13)          # 178 wines, 13 chemical measurements
    assert len(names) == 3 and set(y.unique()) == {0, 1, 2}


def test_split_is_stratified():
    X, y, _ = load_dataset("iris")
    _, _, y_train, y_test = split(X, y)
    # each of the 3 species keeps the same share (10 of 30) in the test set
    assert sorted(y_test.value_counts().tolist()) == [10, 10, 10]


def test_every_candidate_is_a_scaler_plus_model_pipeline():
    for pipe in build_candidates().values():
        assert [name for name, _ in pipe.steps] == ["scale", "model"]


def test_iris_models_beat_chance():
    X, y, names = load_dataset("iris")
    X_train, X_test, y_train, y_test = split(X, y)
    table = compare_models(X_train, y_train, folds=3)
    assert table["cv_accuracy_mean"].max() > 0.9    # chance would be ~0.33
    model = build_candidates()["logistic_regression"].fit(X_train, y_train)
    ev = evaluate(model, X_test, y_test, names)
    assert ev.accuracy > 0.85 and ev.matrix.shape == (3, 3)


def test_run_experiment_writes_report(tmp_path):
    result = run_experiment("iris", tmp_path)
    assert (tmp_path / "report_iris.md").exists()
    assert (tmp_path / "confusion_iris.png").exists()
    assert result["test_accuracy"] > 0.85
