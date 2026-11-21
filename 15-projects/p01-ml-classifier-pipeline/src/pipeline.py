"""
pipeline.py - all the machine-learning logic for Project 1.

Big picture (read this first):
  1. load a table of numbers (features) and the right answers (labels)
  2. split it into a TRAIN part (to learn from) and a TEST part (kept hidden until the end)
  3. try four different models, each wrapped in a Pipeline, using 5-fold cross-validation
  4. tune the best model's settings with GridSearchCV
  5. score the tuned model once on the hidden test part and save a report

Jargon used here:
  * Pipeline        - a chain of steps (e.g. "scale the numbers" then "fit a model") that
                      behaves like one model. It stops test data leaking into the scaling step.
  * cross-validation - split the training data into k slices ("folds"); train on k-1, score on
                      the one left out; repeat k times; average. A fairer score than one split.
  * hyperparameter  - a setting you choose before training (e.g. number of trees), not learned.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw charts to files, no window needed (works on servers and Colab)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer, load_iris, load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, classification_report,
                             confusion_matrix, f1_score)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SEED = 42  # one fixed "random seed" so every run gives the same numbers
LOADERS = {"wine": load_wine, "iris": load_iris, "breast_cancer": load_breast_cancer}


# ---------------------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------------------
def load_dataset(name: str) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Return (features X, labels y, class names) for 'wine', 'iris' or 'breast_cancer'."""
    if name not in LOADERS:
        raise ValueError(f"unknown dataset {name!r}; choose from {list(LOADERS)}")
    csv = DATA_DIR / f"{name}.csv"
    if csv.exists():
        # Preferred path: read the committed CSV (same numbers as scikit-learn's copy)
        df = pd.read_csv(csv)
        # Keep class names in the order of their number (0, 1, 2 ...)
        names = df.drop_duplicates("target").sort_values("target")["target_name"].tolist()
        X = df.drop(columns=["target", "target_name"])
        y = df["target"]
    else:
        # Fallback: load straight from scikit-learn (also offline)
        bunch = LOADERS[name](as_frame=True)
        X, y, names = bunch.data, bunch.target, list(bunch.target_names)
    return X, y, names


def split(X, y, test_size: float = 0.2):
    """Hold back 20% as a test set. stratify=y keeps the class mix the same in both parts."""
    return train_test_split(X, y, test_size=test_size, random_state=SEED, stratify=y)


# ---------------------------------------------------------------------------
# 2. Candidate models - each one is "scaler + model" in a Pipeline
# ---------------------------------------------------------------------------
def build_candidates() -> dict[str, Pipeline]:
    """Four classic classifiers. Scaling matters for LogReg and k-NN; trees ignore it (harmless)."""
    return {
        "logistic_regression": Pipeline([("scale", StandardScaler()),
                                         ("model", LogisticRegression(max_iter=5000))]),
        "knn": Pipeline([("scale", StandardScaler()),
                         ("model", KNeighborsClassifier())]),
        "decision_tree": Pipeline([("scale", StandardScaler()),
                                   ("model", DecisionTreeClassifier(random_state=SEED))]),
        "random_forest": Pipeline([("scale", StandardScaler()),
                                   ("model", RandomForestClassifier(n_estimators=200, random_state=SEED))]),
    }


# Settings to try for each model during tuning. "model__C" means "parameter C of the step named model".
PARAM_GRIDS = {
    "logistic_regression": {"model__C": [0.01, 0.1, 1, 10]},
    "knn": {"model__n_neighbors": [3, 5, 7, 11], "model__weights": ["uniform", "distance"]},
    "decision_tree": {"model__max_depth": [2, 3, 5, None], "model__min_samples_leaf": [1, 3, 5]},
    "random_forest": {"model__max_depth": [None, 5], "model__max_features": ["sqrt", 0.5]},
}


def compare_models(X_train, y_train, folds: int = 5) -> pd.DataFrame:
    """Score every candidate with k-fold cross-validation. Returns a table sorted best-first."""
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=SEED)
    rows = []
    for name, pipe in build_candidates().items():
        # cross_validate trains the pipeline `folds` times and scores each held-out fold
        res = cross_validate(pipe, X_train, y_train, cv=cv, scoring=["accuracy", "f1_macro"])
        rows.append({
            "model": name,
            "cv_accuracy_mean": res["test_accuracy"].mean(),
            "cv_accuracy_std": res["test_accuracy"].std(),     # spread: small = stable model
            "cv_f1_macro_mean": res["test_f1_macro"].mean(),   # F1 averaged over classes equally
        })
    return pd.DataFrame(rows).sort_values("cv_f1_macro_mean", ascending=False).reset_index(drop=True)


def tune(model_name: str, X_train, y_train, folds: int = 5) -> GridSearchCV:
    """Try every combination in PARAM_GRIDS[model_name] with cross-validation; keep the best."""
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=SEED)
    search = GridSearchCV(build_candidates()[model_name], PARAM_GRIDS[model_name],
                          cv=cv, scoring="f1_macro", n_jobs=1)
    search.fit(X_train, y_train)  # after fitting, search.best_estimator_ is retrained on all train data
    return search


# ---------------------------------------------------------------------------
# 3. Final evaluation on the hidden test set
# ---------------------------------------------------------------------------
@dataclass
class Evaluation:
    accuracy: float
    f1_macro: float
    report: str            # per-class precision / recall / F1 as text
    matrix: np.ndarray     # confusion matrix: rows = true class, columns = predicted class
    class_names: list[str]


def evaluate(model, X_test, y_test, class_names: list[str]) -> Evaluation:
    pred = model.predict(X_test)
    return Evaluation(
        accuracy=accuracy_score(y_test, pred),
        f1_macro=f1_score(y_test, pred, average="macro"),
        report=classification_report(y_test, pred, target_names=class_names, digits=3),
        matrix=confusion_matrix(y_test, pred),
        class_names=class_names,
    )


def plot_confusion(ev: Evaluation, title: str, out_png: Path) -> Path:
    """Save the confusion matrix as a picture. Big numbers on the diagonal = good."""
    fig, ax = plt.subplots(figsize=(5, 4.5))
    ConfusionMatrixDisplay(ev.matrix, display_labels=ev.class_names).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(title)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=120)
    plt.close(fig)
    return out_png


def medical_note(ev: Evaluation) -> str:
    """Breast-cancer only: count the two kinds of mistakes, which have very different costs."""
    # In scikit-learn's breast cancer data, class 0 = malignant (cancer), class 1 = benign.
    m = ev.matrix
    false_negatives = int(m[0, 1])  # really malignant, predicted benign -> a missed cancer (worst)
    false_positives = int(m[1, 0])  # really benign, predicted malignant -> a scare + extra test
    return (f"Missed cancers (false negatives): {false_negatives}. "
            f"False alarms (false positives): {false_positives}. "
            "In screening, a false negative is far more costly, so we would accept more false "
            "alarms to push false negatives toward zero (e.g. by lowering the decision threshold).")


# ---------------------------------------------------------------------------
# 4. The whole experiment for one dataset
# ---------------------------------------------------------------------------
def run_experiment(name: str, out_dir: Path) -> dict:
    """Run steps 1-5 for one dataset; write a markdown report + confusion matrix PNG."""
    X, y, class_names = load_dataset(name)
    X_train, X_test, y_train, y_test = split(X, y)

    table = compare_models(X_train, y_train)          # step 3: compare 4 models
    best_name = table.loc[0, "model"]
    search = tune(best_name, X_train, y_train)        # step 4: tune the winner
    ev = evaluate(search.best_estimator_, X_test, y_test, class_names)  # step 5: test once

    out_dir.mkdir(parents=True, exist_ok=True)
    png = plot_confusion(ev, f"{name}: tuned {best_name}", out_dir / f"confusion_{name}.png")

    lines = [
        f"# Report: {name}",
        "",
        f"Rows: {len(X)} (train {len(X_train)}, test {len(X_test)}), features: {X.shape[1]}, "
        f"classes: {', '.join(class_names)}",
        "",
        "## 5-fold cross-validation on the training set",
        "",
        table.to_markdown(index=False, floatfmt=".3f") if _has_tabulate() else table.to_string(index=False),
        "",
        f"## Tuned winner: {best_name}",
        "",
        f"Best settings: `{search.best_params_}` (CV F1-macro {search.best_score_:.3f})",
        "",
        "## Hidden test set (used once)",
        "",
        f"Accuracy {ev.accuracy:.3f}, F1-macro {ev.f1_macro:.3f}",
        "",
        "```",
        ev.report.rstrip(),
        "```",
        "",
        f"![confusion matrix]({png.name})",
    ]
    if name == "breast_cancer":
        lines += ["", "## Which mistakes matter?", "", medical_note(ev)]
    (out_dir / f"report_{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"dataset": name, "best_model": best_name, "test_accuracy": ev.accuracy,
            "test_f1_macro": ev.f1_macro, "cv_table": table}


def _has_tabulate() -> bool:
    """DataFrame.to_markdown needs the optional 'tabulate' package; fall back to plain text."""
    try:
        import tabulate  # noqa: F401
        return True
    except ImportError:
        return False
