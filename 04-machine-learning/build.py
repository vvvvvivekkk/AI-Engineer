"""
build.py for module 04-machine-learning.

Regenerates: images/ (Mermaid + matplotlib), notebooks/, slides/, excel/, pdf/.
Run from the repo root:  python 04-machine-learning/build.py
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

IMG = HERE / "images"
NB = HERE / "notebooks"
IMG.mkdir(exist_ok=True)

TEAL = "#0F9D9A"
NAVY = "#1B263B"
ORANGE = "#E07A1F"


# ---------------------------------------------------------------------------
# 1. Mermaid diagrams
# ---------------------------------------------------------------------------
def build_mermaid():
    mermaid("""
flowchart LR
    A[Get data] --> B[Look at it]
    B --> C[Split train / test]
    C --> D[Train model on train]
    D --> E[Evaluate on test]
    E -->|not good enough| F[Improve: features, model, settings]
    F --> D
    E -->|good| G[Save and use model]
""", IMG / "ml-workflow.png")

    mermaid("""
flowchart TD
    ML[Machine learning] --> S[Supervised: data has labels]
    ML --> U[Unsupervised: no labels]
    S --> R[Regression: predict a number]
    S --> C[Classification: predict a category]
    U --> K[Clustering: find groups]
    R --> R1[e.g. house price]
    C --> C1[e.g. spam or not]
    K --> K1[e.g. customer segments]
""", IMG / "supervised-vs-unsupervised.png")

    mermaid("""
flowchart LR
    X[Raw features X] --> S1[Step 1: StandardScaler]
    S1 --> S2[Step 2: LogisticRegression]
    S2 --> P[Prediction]
    subgraph Pipeline
    S1
    S2
    end
""", IMG / "pipeline.png")

    mermaid("""
flowchart TD
    A[Load dataset] --> B[Explore: shape, balance, missing]
    B --> C[train_test_split, lock test set away]
    C --> D[Baseline model]
    D --> E[Pipeline: scaler + model]
    E --> F[Cross-validation on train]
    F --> G[GridSearchCV picks settings]
    G --> H[Final check on test set once]
    H --> I[joblib.dump to file]
""", IMG / "full-workflow.png")


# ---------------------------------------------------------------------------
# 2. matplotlib diagrams
# ---------------------------------------------------------------------------
def build_plots():
    rng = np.random.default_rng(0)

    # Linear regression fit
    x = rng.uniform(0, 10, 30)
    y = 3 * x + 5 + rng.normal(0, 3, 30)
    w, b = np.polyfit(x, y, 1)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(x, y, color=NAVY, label="training data")
    xs = np.linspace(0, 10, 50)
    ax.plot(xs, w * xs + b, color=TEAL, lw=3, label=f"best line: y = {w:.1f}x + {b:.1f}")
    for xi, yi in zip(x[:6], y[:6]):
        ax.plot([xi, xi], [yi, w * xi + b], color=ORANGE, lw=1)
    ax.set_xlabel("feature (e.g. size of house)")
    ax.set_ylabel("label (e.g. price)")
    ax.set_title("Linear regression: orange lines are errors it tries to shrink")
    ax.legend()
    fig.tight_layout(); fig.savefig(IMG / "linear-regression-fit.png", dpi=130); plt.close(fig)

    # Overfitting curves (polynomial degrees)
    x = np.sort(rng.uniform(0, 1, 18))
    y = np.sin(2 * np.pi * x) + rng.normal(0, 0.25, 18)
    xs = np.linspace(0, 1, 300)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
    for ax, deg, title in zip(axes, [1, 4, 15], ["Underfitting (degree 1)", "Good fit (degree 4)", "Overfitting (degree 15)"]):
        coef = np.polyfit(x, y, deg)
        ax.scatter(x, y, color=NAVY, zorder=3)
        ax.plot(xs, np.sin(2 * np.pi * xs), color="grey", ls="--", label="true pattern")
        ax.plot(xs, np.polyval(coef, xs), color=TEAL if deg == 4 else ORANGE, lw=2.5, label="model")
        ax.set_ylim(-2, 2); ax.set_title(title)
    axes[0].legend(loc="lower left")
    fig.tight_layout(); fig.savefig(IMG / "overfitting-curves.png", dpi=130); plt.close(fig)

    # Tree depth curve on breast cancer
    from sklearn.datasets import load_breast_cancer
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeClassifier
    X, yb = load_breast_cancer(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, yb, test_size=0.25, random_state=42, stratify=yb)
    depths = list(range(1, 13))
    tr, te = [], []
    for d in depths:
        t = DecisionTreeClassifier(max_depth=d, random_state=0).fit(Xtr, ytr)
        tr.append(t.score(Xtr, ytr)); te.append(t.score(Xte, yte))
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(depths, tr, "o-", color=NAVY, label="training accuracy")
    ax.plot(depths, te, "s-", color=ORANGE, label="test accuracy")
    ax.set_xlabel("max_depth of the decision tree"); ax.set_ylabel("accuracy")
    ax.set_title("Deeper trees memorise the training data")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(IMG / "tree-depth-curve.png", dpi=130); plt.close(fig)

    # Confusion matrix explainer
    fig, ax = plt.subplots(figsize=(6, 5))
    cells = [["TP = 15\n(caught spam)", "FN = 5\n(missed spam)"],
             ["FP = 10\n(false alarm)", "TN = 70\n(correctly ignored)"]]
    colors = [[TEAL, ORANGE], [ORANGE, TEAL]]
    for i in range(2):
        for j in range(2):
            ax.add_patch(plt.Rectangle((j, 1 - i), 1, 1, color=colors[i][j], alpha=0.85))
            ax.text(j + 0.5, 1.5 - i, cells[i][j], ha="center", va="center", fontsize=14, color="white", weight="bold")
    ax.set_xlim(0, 2); ax.set_ylim(0, 2)
    ax.set_xticks([0.5, 1.5]); ax.set_xticklabels(["Predicted: spam", "Predicted: not spam"], fontsize=11)
    ax.set_yticks([1.5, 0.5]); ax.set_yticklabels(["Actually: spam", "Actually: not spam"], fontsize=11)
    ax.set_title("Confusion matrix for 100 emails\n(teal = correct, orange = mistake)")
    ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)
    fig.tight_layout(); fig.savefig(IMG / "confusion-matrix.png", dpi=130); plt.close(fig)

    # K-means steps
    from sklearn.datasets import make_blobs
    Xb, yb_true = make_blobs(n_samples=150, centers=3, cluster_std=0.9, random_state=7)
    true_centres = np.array([Xb[yb_true == c].mean(0) for c in range(3)])
    start = true_centres + np.array([[2.5, -2.0], [-2.0, 2.5], [2.0, 2.0]])   # deliberately off-centre pins
    palette = np.array([TEAL, ORANGE, "#6A4C93"])

    def assign(c):
        return ((Xb[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)

    lab1 = assign(start)                                   # step 2: nearest pin
    cents = start.copy()
    for _ in range(10):                                    # step 3: move + reassign until stable
        lab = assign(cents)
        cents = np.array([Xb[lab == c].mean(0) for c in range(3)])
    lab_final = assign(cents)

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    panels = [("1. Drop k=3 random centroids", None, start),
              ("2. Assign each point to nearest", lab1, start),
              ("3. Move centroids to the middle, repeat", lab_final, cents)]
    for ax, (title, labs, cc) in zip(axes, panels):
        ax.scatter(Xb[:, 0], Xb[:, 1], c="lightgrey" if labs is None else palette[labs], s=18)
        ax.scatter(cc[:, 0], cc[:, 1], c="black", marker="X", s=200)
        ax.set_title(title); ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout(); fig.savefig(IMG / "kmeans-steps.png", dpi=130); plt.close(fig)

    # Cross-validation picture
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for r in range(5):
        for c in range(5):
            col = ORANGE if c == r else TEAL
            ax.add_patch(plt.Rectangle((c, 4 - r), 0.95, 0.8, color=col))
            ax.text(c + 0.47, 4.4 - r, "test" if c == r else "train", ha="center", va="center", color="white", fontsize=10)
        ax.text(5.15, 4.4 - r, f"round {r+1} -> score {['0.97','0.95','0.98','0.96','0.97'][r]}", va="center", fontsize=10)
    ax.set_xlim(0, 7.3); ax.set_ylim(-0.2, 5)
    ax.axis("off"); ax.set_title("5-fold cross-validation: average the 5 scores (here 0.966)")
    fig.tight_layout(); fig.savefig(IMG / "cross-validation.png", dpi=130); plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Notebooks
# ---------------------------------------------------------------------------
NB1 = [
("md", """# 04-01 · Your first model: linear regression on the diabetes data

**Goal:** go through the whole machine learning workflow once, slowly: load data → look at it → split → baseline → train → measure → interpret.

**Words used here** (full explanations in `concepts.md`):
- **feature** — an input column; **label** (target) — the column we want to predict.
- **regression** — predicting a number.
- **train/test split** — hiding some rows so we can test the model fairly.

Runs in a few seconds on any laptop or on Google Colab. No internet needed: the dataset ships inside scikit-learn."""),
("md", """## Step 1 · Import the tools

- `numpy` and `pandas` for tables of numbers, `matplotlib` for charts.
- From scikit-learn (`sklearn`) we import a dataset loader, the split function, two models and some metrics."""),
("code", """import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import sklearn
print("scikit-learn version:", sklearn.__version__)"""),
("md", """## Step 2 · Load the data

`return_X_y=True` gives us the features `X` and the label `y` separately. `as_frame=True` makes them pandas objects so they print nicely.

The dataset: 442 diabetes patients. 10 features (age, sex, body-mass index `bmi`, blood pressure `bp`, six blood measurements `s1`–`s6`). The label is a number measuring how much the disease progressed one year later. Note: the features have already been **scaled** (centred around 0) by the dataset authors, which is why age looks like 0.038 rather than 59."""),
("code", """X, y = load_diabetes(return_X_y=True, as_frame=True)
print("X shape:", X.shape, " -> rows, columns")
print("y shape:", y.shape)
X.head()"""),
("md", """## Step 3 · Look at the data before modelling

Always check: how big are the label values, are there missing values, which features seem related to the label? `.describe()` gives summary statistics. `.corr()` gives the **correlation** (a number from -1 to 1 saying how strongly two columns move together)."""),
("code", """print(y.describe().round(1))
print("\\nMissing values in X:", int(X.isna().sum().sum()))
print("\\nCorrelation of each feature with the label:")
print(X.corrwith(y).sort_values(ascending=False).round(2))"""),
("md", """`bmi` (body-mass index) and `s5` have the strongest link to the label. Let us see `bmi` on a chart: each dot is one patient."""),
("code", """plt.figure(figsize=(6, 4))
plt.scatter(X["bmi"], y, alpha=0.5)
plt.xlabel("bmi (scaled)")
plt.ylabel("disease progression")
plt.title("Higher BMI tends to mean more progression")
plt.show()"""),
("md", """## Step 4 · Split into training and test sets

We hide 20% of the patients as a test set. The model never sees them during training. `random_state=42` makes the random split repeatable."""),
("code", """X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("training rows:", len(X_train), "  test rows:", len(X_test))"""),
("md", """## Step 5 · A baseline: the laziest possible model

A **baseline** is a very simple model that tells us what "no skill" looks like. `DummyRegressor` always predicts the average of the training labels, whatever the input. Any real model must beat this."""),
("code", """baseline = DummyRegressor(strategy="mean")
baseline.fit(X_train, y_train)
base_pred = baseline.predict(X_test)
print("baseline always predicts:", round(base_pred[0], 1))
print("baseline MAE:", round(mean_absolute_error(y_test, base_pred), 1))"""),
("md", """## Step 6 · Train a linear regression

The three-step pattern you will use with every scikit-learn model:
1. create it, 2. `.fit()` on training data, 3. `.predict()` on new data."""),
("code", """model = LinearRegression()
model.fit(X_train, y_train)
pred = model.predict(X_test)
print("first five predictions:", pred[:5].round(1))
print("first five true values:", y_test.values[:5])"""),
("md", """## Step 7 · Measure the errors — first by hand, then with scikit-learn

Doing it by hand once shows there is no magic:
- **MAE** = average of |true − predicted|
- **MSE** = average of (true − predicted)²
- **RMSE** = square root of MSE (back in the label's units)
- **R²** = 1 − (model's squared error ÷ squared error of always guessing the average)"""),
("code", """errors = y_test.values - pred
mae_hand = np.mean(np.abs(errors))
mse_hand = np.mean(errors ** 2)
rmse_hand = np.sqrt(mse_hand)
r2_hand = 1 - np.sum(errors ** 2) / np.sum((y_test.values - y_test.mean()) ** 2)

print(f"By hand      MAE={mae_hand:.2f}  RMSE={rmse_hand:.2f}  R2={r2_hand:.3f}")
print(f"scikit-learn MAE={mean_absolute_error(y_test, pred):.2f}  "
      f"RMSE={np.sqrt(mean_squared_error(y_test, pred)):.2f}  R2={r2_score(y_test, pred):.3f}")"""),
("md", """**How to read this:** on average we are about 43 units off, against about 64 for the baseline. R² ≈ 0.45 means the model explains about 45% of the variation between patients. Medical data is noisy, so this is a normal, honest result — do not expect 99% on real-world regression.

## Step 8 · Picture the predictions

If the model were perfect, every dot would sit on the dashed diagonal line."""),
("code", """plt.figure(figsize=(5, 5))
plt.scatter(y_test, pred, alpha=0.6)
lims = [y.min(), y.max()]
plt.plot(lims, lims, "k--", label="perfect prediction")
plt.xlabel("true value"); plt.ylabel("predicted value")
plt.title("Predicted vs true (test set)")
plt.legend(); plt.show()"""),
("md", """## Step 9 · Look inside the model

Linear regression learned one **weight** (coefficient) per feature plus an **intercept**. A positive weight means "when this feature goes up, the prediction goes up". Because these features were pre-scaled to similar ranges, we can roughly compare the sizes of the weights."""),
("code", """weights = pd.Series(model.coef_, index=X.columns).sort_values()
print("intercept:", round(model.intercept_, 1))
weights.plot.barh(figsize=(6, 4), title="Learned weights")
plt.show()"""),
("md", """## Step 10 · Predict for a brand-new patient

A trained model is a function. Give it one new row with the same 10 columns and it returns a number. Here we invent a patient by copying one test row and raising their BMI."""),
("code", """new_patient = X_test.iloc[[0]].copy()
print("original prediction:", model.predict(new_patient).round(1))
new_patient["bmi"] += 0.05
print("with higher bmi:    ", model.predict(new_patient).round(1))"""),
("md", """## Recap

- You loaded data, explored it, split it, built a baseline and a real model.
- You computed MAE, RMSE and R² by hand and matched scikit-learn.
- Always compare with a baseline, and always measure on the test set.

**Try it:** replace `LinearRegression()` with `from sklearn.linear_model import Ridge` and `Ridge(alpha=1.0)`. Does the test MAE change?"""),
]

NB2 = [
("md", """# 04-02 · Classification and the metrics that matter

**Goal:** train a classifier on the breast-cancer dataset and understand every evaluation number: confusion matrix, accuracy, precision, recall, F1, the decision threshold, and ROC-AUC. Then see why accuracy can lie.

**Words:** **classification** — predicting a category. **positive class** — the class we are hunting for (here: malignant). **probability** — a number from 0 to 1 saying how sure the model is."""),
("md", """## Step 1 · Imports"""),
("code", """import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.datasets import load_breast_cancer, load_wine, make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (confusion_matrix, ConfusionMatrixDisplay, accuracy_score,
                             precision_score, recall_score, f1_score, classification_report,
                             roc_auc_score, RocCurveDisplay)"""),
("md", """## Step 2 · Load the data and choose the positive class

In this dataset `0 = malignant` (cancer) and `1 = benign` (not cancer). We are hunting for cancer, so we flip the labels: `1 = malignant`. Then "positive" means "malignant", which makes precision and recall easier to talk about."""),
("code", """data = load_breast_cancer(as_frame=True)
X = data.data
y = (data.target == 0).astype(int)   # 1 = malignant (positive), 0 = benign
print(X.shape)
print("class counts:", y.value_counts().to_dict(), " -> 1 = malignant")
print("share malignant:", round(y.mean(), 3))"""),
("md", """## Step 3 · Split with stratify

`stratify=y` keeps the same share of malignant cases (about 37%) in both training and test sets."""),
("code", """X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)
print("train malignant share:", round(y_train.mean(), 3), " test:", round(y_test.mean(), 3))"""),
("md", """## Step 4 · Train logistic regression inside a pipeline

The 30 features have very different sizes (some around 0.05, some around 1000). We put a `StandardScaler` in front of the model inside a **pipeline**, so scaling is learned from the training data only. Concepts section 11 and 13 explain why."""),
("code", """clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
clf.fit(X_train, y_train)
pred = clf.predict(X_test)
proba = clf.predict_proba(X_test)[:, 1]    # probability of class 1 (malignant)
print("first 8 predictions:   ", pred[:8])
print("first 8 probabilities: ", proba[:8].round(3))"""),
("md", """## Step 5 · The confusion matrix, box by box

`confusion_matrix(y_true, y_pred)` returns a 2×2 grid. With labels ordered `[0, 1]`, the layout is:

```
               predicted 0   predicted 1
actual 0   [[     TN            FP     ],
actual 1    [     FN            TP     ]]
```

Careful: scikit-learn puts the negative class first, so TP is in the **bottom-right**. `.ravel()` flattens it into `tn, fp, fn, tp`."""),
("code", """cm = confusion_matrix(y_test, pred)
print(cm)
tn, fp, fn, tp = cm.ravel()
print(f"TP={tp} (cancer, caught)   FN={fn} (cancer, MISSED)")
print(f"FP={fp} (healthy, false alarm)   TN={tn} (healthy, correctly cleared)")
ConfusionMatrixDisplay(cm, display_labels=["benign", "malignant"]).plot(cmap="Blues")
plt.show()"""),
("md", """## Step 6 · Every metric from the four boxes

We calculate each one by hand from `tp, fp, fn, tn`, then check against scikit-learn's functions."""),
("code", """accuracy  = (tp + tn) / (tp + tn + fp + fn)
precision = tp / (tp + fp)
recall    = tp / (tp + fn)
f1        = 2 * precision * recall / (precision + recall)

print(f"accuracy : by hand {accuracy:.3f}  sklearn {accuracy_score(y_test, pred):.3f}")
print(f"precision: by hand {precision:.3f}  sklearn {precision_score(y_test, pred):.3f}")
print(f"recall   : by hand {recall:.3f}  sklearn {recall_score(y_test, pred):.3f}")
print(f"f1       : by hand {f1:.3f}  sklearn {f1_score(y_test, pred):.3f}")"""),
("md", """`classification_report` prints precision, recall and F1 for **each** class, plus averages. **support** = how many true examples of that class were in the test set. **macro avg** = plain average over classes; **weighted avg** = average weighted by support."""),
("code", """print(classification_report(y_test, pred, target_names=["benign", "malignant"]))"""),
("md", """## Step 7 · Moving the threshold

`predict()` uses a threshold of 0.5 on the probability. In cancer screening a missed cancer (FN) is far worse than a false alarm (FP), so a doctor might accept more false alarms to catch more cancers. Watch recall go up and precision go down as the threshold drops."""),
("code", """for threshold in [0.9, 0.7, 0.5, 0.3, 0.1]:
    p = (proba >= threshold).astype(int)
    tn_, fp_, fn_, tp_ = confusion_matrix(y_test, p).ravel()
    print(f"threshold {threshold:.1f}: TP={tp_:2d} FN={fn_:2d} FP={fp_:2d}  "
          f"precision={precision_score(y_test, p):.3f} recall={recall_score(y_test, p):.3f}")"""),
("md", """## Step 8 · ROC curve and AUC

The **ROC curve** plots recall (true positive rate) against the false positive rate for every possible threshold. **AUC** (area under the curve) summarises it: 1.0 is perfect, 0.5 is a coin flip. AUC uses the probabilities, not the 0/1 predictions."""),
("code", """auc = roc_auc_score(y_test, proba)
print("ROC-AUC:", round(auc, 4))
RocCurveDisplay.from_predictions(y_test, proba, name="logistic regression")
plt.plot([0, 1], [0, 1], "k--", label="coin flip")
plt.legend(); plt.show()"""),
("md", """## Step 9 · The accuracy trap (class imbalance)

We generate fake data where only **5%** of rows are positive (think: fraud). A "model" that always predicts "not fraud" gets about 95% accuracy — and catches zero fraud. Precision/recall reveal the truth.

`make_classification` builds a synthetic dataset; `weights=[0.95]` makes 95% of rows class 0."""),
("code", """Xi, yi = make_classification(n_samples=2000, n_features=10, weights=[0.95], random_state=0)
Xi_tr, Xi_te, yi_tr, yi_te = train_test_split(Xi, yi, test_size=0.3, random_state=0, stratify=yi)

lazy = DummyClassifier(strategy="most_frequent").fit(Xi_tr, yi_tr)
real = LogisticRegression(max_iter=1000).fit(Xi_tr, yi_tr)
for name, m in [("always 'no fraud'", lazy), ("logistic regression", real)]:
    p = m.predict(Xi_te)
    print(f"{name:20s} accuracy={accuracy_score(yi_te, p):.3f}  "
          f"recall={recall_score(yi_te, p, zero_division=0):.3f}  "
          f"precision={precision_score(yi_te, p, zero_division=0):.3f}")"""),
("md", """The lazy model's accuracy looks great but its recall is 0. **Lesson:** with imbalanced classes, always look at the confusion matrix, precision and recall.

## Step 10 · Multi-class classification (three wine types)

Everything works the same with more than two classes. The confusion matrix becomes 3×3: rows are the true class, columns the predicted class, and the diagonal holds the correct answers."""),
("code", """wine = load_wine()
Xw_tr, Xw_te, yw_tr, yw_te = train_test_split(wine.data, wine.target, test_size=0.3,
                                              random_state=1, stratify=wine.target)
wine_clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(Xw_tr, yw_tr)
pw = wine_clf.predict(Xw_te)
print(confusion_matrix(yw_te, pw))
print(classification_report(yw_te, pw, target_names=wine.target_names))"""),
("md", """## Recap

- Confusion matrix → TP, FP, FN, TN → every other metric.
- **Precision**: of what I flagged, how much was right. **Recall**: of what was there, how much I found.
- The threshold trades precision against recall; choose it from the real cost of each mistake.
- AUC judges the probability scores across all thresholds.
- Accuracy alone lies when classes are imbalanced.

Use `excel/04-ml-metrics.xlsx` → *Confusion Matrix Calculator* to practise with your own numbers."""),
]

NB3 = [
("md", """# 04-03 · Decision trees, random forests and k-means

**Goal:** meet three new models.
- **Decision tree** — a flowchart of yes/no questions.
- **Random forest** — many trees voting together (an **ensemble**).
- **k-means** — an **unsupervised** method that finds groups without labels.

Everything runs in seconds."""),
("md", """## Step 1 · Imports"""),
("code", """import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.datasets import load_wine, load_iris, make_blobs
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, adjusted_rand_score"""),
("md", """## Step 2 · A small decision tree on the wine data

178 wines, 13 chemical measurements, 3 grape types. We limit the tree to `max_depth=2` (at most two questions in a row) so we can read it. `max_depth` is a **hyperparameter** — a setting we choose, not something the model learns."""),
("code", """wine = load_wine(as_frame=True)
X, y = wine.data, wine.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)

tree = DecisionTreeClassifier(max_depth=2, random_state=0)
tree.fit(X_train, y_train)
print("train accuracy:", round(tree.score(X_train, y_train), 3))
print("test accuracy: ", round(tree.score(X_test, y_test), 3))"""),
("md", """`export_text` prints the tree as plain text: each line is a question, and each leaf says which class it predicts. Notice that a tree needs **no scaling** — it only compares a feature with a cut-off."""),
("code", """print(export_text(tree, feature_names=list(X.columns)))"""),
("md", """The same tree as a picture. Each box shows the question, the **gini** impurity (0 = the box contains only one class; higher = more mixed), how many training samples reached it, and the class counts."""),
("code", """plt.figure(figsize=(12, 5))
plot_tree(tree, feature_names=X.columns, class_names=wine.target_names, filled=True, fontsize=9)
plt.show()"""),
("md", """## Step 3 · What happens when we let the tree grow?

We train trees of increasing depth and compare training and test accuracy. When training accuracy hits 1.0 but test accuracy does not improve, the tree is memorising — **overfitting**."""),
("code", """for depth in [1, 2, 3, 5, None]:
    t = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X_train, y_train)
    print(f"max_depth={str(depth):4s}  train={t.score(X_train, y_train):.3f}  "
          f"test={t.score(X_test, y_test):.3f}  leaves={t.get_n_leaves()}")"""),
("md", """## Step 4 · Random forest: many trees vote

`n_estimators=200` grows 200 trees, each on a random sample of rows and features. `n_jobs=1` uses one CPU core (polite on shared machines; use `-1` on your own laptop for all cores)."""),
("code", """forest = RandomForestClassifier(n_estimators=200, random_state=0, n_jobs=1)
forest.fit(X_train, y_train)
print("forest train accuracy:", round(forest.score(X_train, y_train), 3))
print("forest test accuracy: ", round(forest.score(X_test, y_test), 3))"""),
("md", """**Feature importances** tell us how much each feature helped the forest's decisions (they add up to 1). This is a quick way to explain a model to a non-technical audience."""),
("code", """imp = pd.Series(forest.feature_importances_, index=X.columns).sort_values()
imp.plot.barh(figsize=(6, 5), title="Random forest feature importances (wine)")
plt.show()"""),
("md", """## Step 5 · k-means on synthetic blobs

Now the **unsupervised** part. `make_blobs` creates points around 3 hidden centres. We give k-means the points **without** the true groups and ask for `n_clusters=3`. `n_init=10` runs the algorithm 10 times from different random starts and keeps the best."""),
("code", """Xb, true_groups = make_blobs(n_samples=300, centers=3, cluster_std=1.0, random_state=42)
km = KMeans(n_clusters=3, n_init=10, random_state=42)
labels = km.fit_predict(Xb)

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].scatter(Xb[:, 0], Xb[:, 1], c="grey", s=15); axes[0].set_title("What k-means is given (no labels)")
axes[1].scatter(Xb[:, 0], Xb[:, 1], c=labels, cmap="viridis", s=15)
axes[1].scatter(*km.cluster_centers_.T, c="red", marker="X", s=200, label="centroids")
axes[1].set_title("What k-means found"); axes[1].legend()
plt.show()"""),
("md", """## Step 6 · Choosing k with the elbow plot

**Inertia** = total squared distance from each point to its centroid. More clusters always lower it, so we look for the "elbow" where the curve stops dropping steeply."""),
("code", """ks = range(1, 9)
inertias = [KMeans(n_clusters=k, n_init=10, random_state=42).fit(Xb).inertia_ for k in ks]
plt.plot(ks, inertias, "o-")
plt.xlabel("k (number of clusters)"); plt.ylabel("inertia")
plt.title("Elbow at k = 3"); plt.show()"""),
("md", """## Step 7 · k-means on real data (iris) — did it find the species?

We hide the iris species, scale the 4 measurements, and cluster into 3 groups. Cluster numbers are arbitrary (cluster "0" need not be species "0"), so we use the **adjusted Rand index (ARI)**: 1.0 = groups match the species perfectly, about 0 = random."""),
("code", """iris = load_iris()
Xi = StandardScaler().fit_transform(iris.data)
iris_labels = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(Xi)
print("ARI vs true species:", round(adjusted_rand_score(iris.target, iris_labels), 3))
print(pd.crosstab(iris.target, iris_labels, rownames=["true species"], colnames=["cluster"]))"""),
("md", """One species (setosa) is found perfectly, but the other two species get mixed up quite a lot, because their measurements overlap. That is typical: clusters are a useful *suggestion*, not ground truth. (Try it without scaling — on iris the result changes, which shows how sensitive k-means is to feature scale.)

## Recap

- Trees: readable, no scaling needed, but overfit when deep.
- Random forests: many trees vote → usually more accurate and more stable.
- k-means: groups unlabelled data; you choose k (elbow plot helps); scale features first."""),
]

NB4 = [
("md", """# 04-04 · Overfitting, cross-validation, pipelines and saving models

**Goal:** the professional habits.
1. See overfitting with your own eyes.
2. Measure models fairly with **cross-validation**.
3. Avoid **data leakage** with a **pipeline**.
4. Tune settings with `GridSearchCV`.
5. Save and load the finished model with `joblib`."""),
("md", """## Step 1 · Imports"""),
("code", """import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib

from sklearn.datasets import load_breast_cancer, load_digits
from sklearn.model_selection import (train_test_split, cross_val_score, KFold,
                                     StratifiedKFold, GridSearchCV)
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error"""),
("md", """## Step 2 · Overfitting you can see

We make 20 noisy points from a smooth wave. Then we fit polynomial curves of degree 1, 4 and 15. A **polynomial** of degree d is a curve with up to d bends; higher degree = more flexible.

`PolynomialFeatures(degree)` creates columns x, x², x³, … and `LinearRegression` fits weights for them. We measure error on separate test points."""),
("code", """rng = np.random.default_rng(0)
x = np.sort(rng.uniform(0, 1, 20)).reshape(-1, 1)
y = np.sin(2 * np.pi * x).ravel() + rng.normal(0, 0.25, 20)
x_test = rng.uniform(0, 1, 100).reshape(-1, 1)
y_test = np.sin(2 * np.pi * x_test).ravel() + rng.normal(0, 0.25, 100)
grid = np.linspace(0, 1, 300).reshape(-1, 1)

fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), sharey=True)
for ax, degree in zip(axes, [1, 4, 15]):
    m = make_pipeline(PolynomialFeatures(degree), LinearRegression()).fit(x, y)
    tr = mean_squared_error(y, m.predict(x))
    te = mean_squared_error(y_test, m.predict(x_test))
    ax.scatter(x, y, color="black", zorder=3)
    ax.plot(grid, m.predict(grid), lw=2)
    ax.set_ylim(-2, 2)
    ax.set_title(f"degree {degree}\\ntrain MSE={tr:.3f}  test MSE={te:.3f}")
plt.show()"""),
("md", """Read the titles: degree 15 has the **lowest training error** but a **much higher test error**. It memorised the noise. Degree 1 is bad on both (underfitting). Degree 4 is the sweet spot.

## Step 3 · The train/test gap for decision trees

Same idea on real data: as `max_depth` grows, training accuracy climbs to 100% while test accuracy stalls or drops."""),
("code", """X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
depths = range(1, 13)
train_acc, test_acc = [], []
for d in depths:
    t = DecisionTreeClassifier(max_depth=d, random_state=0).fit(X_train, y_train)
    train_acc.append(t.score(X_train, y_train)); test_acc.append(t.score(X_test, y_test))
plt.plot(depths, train_acc, "o-", label="train")
plt.plot(depths, test_acc, "s-", label="test")
plt.xlabel("max_depth"); plt.ylabel("accuracy"); plt.legend(); plt.grid(alpha=0.3)
plt.title("The gap between the lines = overfitting"); plt.show()"""),
("md", """## Step 4 · Why one split is not enough

Change only the `random_state` of the split and the test score moves around. One split is partly luck."""),
("code", """model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
for seed in range(5):
    a, b, c, d = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    print(f"split seed {seed}: test accuracy = {model.fit(a, c).score(b, d):.3f}")"""),
("md", """## Step 5 · k-fold cross-validation

`cross_val_score` cuts the data into k **folds**, trains on k−1, tests on the remaining one, and repeats so every fold is tested once. We get k scores; report the mean and the standard deviation (spread).

`StratifiedKFold` keeps the class mix the same in every fold; `shuffle=True` mixes rows first."""),
("code", """cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
scores = cross_val_score(model, X_train, y_train, cv=cv)
print("5 fold scores:", scores.round(3))
print(f"mean = {scores.mean():.3f}  +/- {scores.std():.3f}")"""),
("md", """Let us peek at what the folds are. Each round, a different fifth of the training rows is held out."""),
("code", """for i, (tr_idx, va_idx) in enumerate(cv.split(X_train, y_train), start=1):
    print(f"round {i}: train on {len(tr_idx)} rows, validate on {len(va_idx)} rows "
          f"(first validation row ids: {va_idx[:5]})")"""),
("md", """## Step 6 · Comparing models fairly

Use the **same** folds for every candidate. Here: scaled logistic regression vs a single tree vs a random forest."""),
("code", """candidates = {
    "logistic (scaled)": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "decision tree":     DecisionTreeClassifier(max_depth=4, random_state=0),
    "random forest":     RandomForestClassifier(n_estimators=150, random_state=0, n_jobs=1),
}
for name, m in candidates.items():
    s = cross_val_score(m, X_train, y_train, cv=cv)
    print(f"{name:18s} {s.mean():.3f} +/- {s.std():.3f}")"""),
("md", """## Step 7 · Data leakage, demonstrated

**Data leakage** = information from the validation/test data sneaking into training. A classic beginner leak is choosing features using the *whole* dataset before cross-validating.

To make the effect obvious, we use pure random noise: 100 rows, 5,000 random features, random labels. No model can genuinely do better than ~50%.

- **Leaky way:** pick the 20 features most correlated with the label using *all* rows, then cross-validate.
- **Correct way:** put the feature picker *inside* a pipeline so it only sees each training fold.

`SelectKBest` keeps the k features with the strongest statistical link to the label."""),
("code", """from sklearn.feature_selection import SelectKBest, f_classif
rng = np.random.default_rng(1)
X_noise = rng.normal(size=(100, 5000))
y_noise = rng.integers(0, 2, 100)
cv_noise = StratifiedKFold(5, shuffle=True, random_state=0)

X_leaky = SelectKBest(f_classif, k=20).fit_transform(X_noise, y_noise)   # peeks at ALL labels
leaky = cross_val_score(LogisticRegression(max_iter=1000), X_leaky, y_noise, cv=cv_noise).mean()

honest_pipe = make_pipeline(SelectKBest(f_classif, k=20), LogisticRegression(max_iter=1000))
honest = cross_val_score(honest_pipe, X_noise, y_noise, cv=cv_noise).mean()
print(f"leaky accuracy on pure noise:  {leaky:.2f}   <- fake skill!")
print(f"honest accuracy on pure noise: {honest:.2f}   <- near a coin flip (0.5), the truth")"""),
("md", """The leaky number looks impressive but is a lie: the data is random. (The honest number wobbles around 0.5 because 100 rows is a small sample.) **Lesson:** every step that learns from data (scaling, feature selection, filling missing values) must go *inside* the pipeline.

## Step 8 · A named Pipeline + GridSearchCV

`Pipeline` takes a list of `(name, step)` pairs. Names let us refer to a step's settings as `stepname__setting` (two underscores). `GridSearchCV` tries every combination in `param_grid` with cross-validation and keeps the best.

We use the **digits** dataset (1,797 images of 8×8 pixels, flattened to 64 numbers)."""),
("code", """digits = load_digits()
Xd_train, Xd_test, yd_train, yd_test = train_test_split(
    digits.data, digits.target, test_size=0.2, random_state=0, stratify=digits.target)

pipe = Pipeline([
    ("scale", StandardScaler()),
    ("model", LogisticRegression(max_iter=2000)),
])
param_grid = {"model__C": [0.01, 0.1, 1.0, 10.0]}   # C: smaller = stronger regularisation
search = GridSearchCV(pipe, param_grid, cv=3, n_jobs=1)
search.fit(Xd_train, yd_train)
print("best setting:", search.best_params_)
print("best CV accuracy:", round(search.best_score_, 3))
pd.DataFrame(search.cv_results_)[["param_model__C", "mean_test_score", "std_test_score"]]"""),
("md", """Only now, once, do we touch the test set."""),
("code", """best_model = search.best_estimator_
print("final test accuracy:", round(best_model.score(Xd_test, yd_test), 3))"""),
("md", """## Step 9 · Save and load the model with joblib

`joblib.dump` writes the whole pipeline (scaler + model) to one file. `joblib.load` brings it back, ready to predict — no retraining.

⚠️ Only load model files you trust: loading can run code. Record your scikit-learn version alongside the file."""),
("code", """import sklearn
path = "digits_model.joblib"
joblib.dump(best_model, path)
print("saved", path, "-", round(os.path.getsize(path) / 1024, 1), "KB, sklearn", sklearn.__version__)

loaded = joblib.load(path)
print("loaded model predicts:", loaded.predict(Xd_test[:10]))
print("true labels:          ", yd_test[:10])
print("same accuracy?", loaded.score(Xd_test, yd_test) == best_model.score(Xd_test, yd_test))

os.remove(path)   # tidy up so the course folder stays clean; in a real project keep it!"""),
("md", """## Recap

- Overfitting = great on training data, worse on new data. Watch the train/test gap.
- Cross-validation gives a fairer score (mean ± spread) than one split.
- Put every data-learning step inside a `Pipeline` to avoid leakage.
- `GridSearchCV` tunes settings with CV; test set used once at the end.
- `joblib.dump` / `joblib.load` save and restore the full pipeline."""),
]


def build_notebooks():
    notebook(NB1, NB / "01-first-model-regression.ipynb")
    notebook(NB2, NB / "02-classification-and-metrics.ipynb")
    notebook(NB3, NB / "03-trees-forests-kmeans.ipynb")
    notebook(NB4, NB / "04-overfitting-cv-pipelines.ipynb")


# ---------------------------------------------------------------------------
# 4. Slides
# ---------------------------------------------------------------------------
def build_slides():
    I = lambda n: str(IMG / n)
    deck = {
        "title": "Module 04 - Machine Learning",
        "subtitle": "Python to Pro AI Engineer curriculum - weeks 7-8",
        "slides": [
            {"title": "What is machine learning?",
             "bullets": ["Normal code: you write the rules", "ML: the computer learns rules from examples",
                         "Model = the learned function", "Training = learning; prediction = using it on new data"],
             "notes": "Start with the contrast. In normal programming we write if-statements. In machine learning we show examples with answers, and an algorithm finds the rules. The thing it produces is called a model. Ask the class for one task where writing the rules by hand would be very hard, for example recognising handwriting."},
            {"title": "Analogy: the used-car salesperson",
             "bullets": ["500 old sales = training data", "Year, km, brand = features", "Sale price = label",
                         "The salesperson's 'feel' = the model", "Pricing a new car = prediction"],
             "notes": "Tell this as a story. A new employee learns prices by looking at old sales. After a while they can guess the price of a car they have never seen. Map each part of the story to the ML word. Keep this table on the board for the whole session."},
            {"title": "The ML workflow", "image": I("ml-workflow.png"),
             "bullets": ["Same loop every time", "Split BEFORE training", "Evaluate on data the model never saw"],
             "notes": "This is the loop we follow in every notebook. Point at each box. Stress that splitting happens before any training, and that we loop back to improve when results are not good enough."},
            {"title": "Supervised vs unsupervised", "image": I("supervised-vs-unsupervised.png"),
             "bullets": ["Supervised: every row has the answer", "  Regression = a number", "  Classification = a category",
                         "Unsupervised: no answers, find structure", "  Clustering = groups"],
             "notes": "Quick test for students: could the answer be 3.7? Then it is regression. Must it be one name from a list? Then classification. Unsupervised is sorting a box of mixed buttons without being told what the piles should be."},
            {"title": "Train / test split",
             "bullets": ["Hide ~20% of rows as a test set", "Train only on the rest", "Test score estimates real-world performance",
                         "random_state = repeatable randomness", "stratify=y keeps class mix the same"],
             "code": "from sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(\n    X, y, test_size=0.2,\n    random_state=42, stratify=y)",
             "notes": "Analogy: a teacher keeps 20 of 100 practice questions back for the exam. If the exam reused studied questions, memorising would score 100 percent. The test set is our honest exam. Always unpack in this exact order: X_train, X_test, y_train, y_test."},
            {"title": "The scikit-learn pattern",
             "bullets": ["1. Create the model", "2. .fit(X_train, y_train)", "3. .predict(X_test)", "Same three lines for every model"],
             "code": "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression()\nmodel.fit(X_train, y_train)\npreds = model.predict(X_test)",
             "notes": "This is the most useful slide in the module. Every estimator in scikit-learn follows create, fit, predict. Once students know it they can try any model by changing one line."},
            {"title": "Linear regression", "image": I("linear-regression-fit.png"),
             "bullets": ["Best straight line through the data", "prediction = w x feature + b", "Picks weights that minimise squared errors"],
             "notes": "The orange lines are the errors. Linear regression squares them, adds them up and chooses the line with the smallest total. That is called least squares. With many features each feature gets its own weight."},
            {"title": "Regression metrics with real numbers",
             "bullets": ["Errors: -4, 3, -1, -8 minutes", "MAE = (4+3+1+8)/4 = 4.0", "MSE = (16+9+1+64)/4 = 22.5", "RMSE = sqrt(22.5) = 4.74",
                         "R2: 1 = perfect, 0 = as good as guessing the average"],
             "notes": "Work this on the board. MAE is the average mistake size. RMSE punishes big mistakes more, so if RMSE is much bigger than MAE there are a few large errors. R squared compares with always predicting the average."},
            {"title": "Logistic regression = classification",
             "bullets": ["Weighted sum squashed to 0..1 by the sigmoid", "Output read as a probability", "Threshold (0.5) turns probability into a class",
                         "predict() gives classes, predict_proba() gives probabilities"],
             "notes": "Despite its name logistic regression is a classifier. It is like a doctor weighing several test results and saying I am 90 percent sure. If you see a ConvergenceWarning, scale the features or raise max_iter."},
            {"title": "Confusion matrix: 100 emails", "image": I("confusion-matrix.png"),
             "bullets": ["TP: spam, flagged", "FN: spam, missed", "FP: real email, flagged", "TN: real email, left alone"],
             "notes": "Second word is what the model said, first word is whether it was right. Go box by box. Positive does not mean good, it means the thing we hunt for."},
            {"title": "Every metric from four boxes",
             "bullets": ["Accuracy = (15+70)/100 = 0.85", "Precision = 15/(15+10) = 0.60", "Recall = 15/(15+5) = 0.75",
                         "F1 = 2x0.6x0.75/(0.6+0.75) = 0.667", "Fishing net: recall = fish caught, precision = no boots"],
             "notes": "Have students compute these with a calculator before you reveal them. Then open the Excel confusion matrix calculator and change the numbers live. Ask: in cancer screening, which mistake is worse? Missing cancer, so we focus on recall."},
            {"title": "Trees and forests",
             "bullets": ["Decision tree = 20 Questions", "max_depth = how many questions in a row", "Random forest = many trees vote",
                         "Wisdom of the crowd: errors cancel", "No scaling needed"],
             "notes": "A tree asks yes or no questions about features. Deep trees memorise. A forest trains hundreds of slightly different trees and takes a vote, like averaging many people's guesses of sweets in a jar."},
            {"title": "k-means clustering", "image": I("kmeans-steps.png"),
             "bullets": ["Unsupervised: no labels", "Drop k centroids, assign, move, repeat", "Choose k with the elbow plot", "Scale features first"],
             "notes": "Ice-cream vans on a beach. Vans park at random, people walk to the nearest van, each van moves to the middle of its crowd, repeat. After a few rounds the vans sit in the middle of natural crowds."},
            {"title": "Overfitting vs underfitting", "image": I("overfitting-curves.png"),
             "bullets": ["Underfit: bad on train AND test", "Overfit: great on train, bad on test", "Watch the train/test gap"],
             "notes": "Underfitting is the student who did not study. Overfitting is the student who memorised last year's answers. The wiggly curve passes through nearly every training point but would make silly predictions between them."},
            {"title": "Tree depth: seeing the gap", "image": I("tree-depth-curve.png"),
             "bullets": ["Training accuracy climbs to 100%", "Test accuracy stalls", "Fixes: simpler model, regularisation, more data, ensembles"],
             "notes": "This chart comes from the breast cancer data. As we allow deeper trees, training accuracy reaches 1.0 but test accuracy stops improving. The gap between the lines is overfitting."},
            {"title": "Cross-validation", "image": I("cross-validation.png"),
             "bullets": ["Split into 5 folds", "Each fold is the test once", "Report mean +/- spread", "Fairer than one lucky split"],
             "notes": "Judge a cricketer on five matches, not one. Use cross validation on the training set to compare models and choose settings, then use the test set only once at the very end."},
            {"title": "Pipelines stop data leakage", "image": I("pipeline.png"),
             "bullets": ["Chain scaler + model into one object", "Scaler learns from training folds only", "One object to fit, score and save"],
             "notes": "Data leakage is when test information sneaks into training. Scaling or selecting features on the whole dataset before splitting is the classic leak. In notebook 4 a leaky workflow gets fake skill on pure random noise. Pipelines prevent this. Analogy: a coffee machine that always runs the steps in the right order."},
            {"title": "Save the model with joblib",
             "bullets": ["dump = save to a file", "load = bring it back, no retraining", "Only load files you trust", "Record the scikit-learn version"],
             "code": "import joblib\njoblib.dump(pipe, 'model.joblib')\nloaded = joblib.load('model.joblib')\nloaded.predict(X_test[:5])",
             "notes": "Training can be slow, so we save the trained pipeline. Warn students: loading a joblib or pickle file can run code, so never load a file from a stranger. Versions matter too."},
            {"title": "Common mistakes",
             "bullets": ["Testing on the training data", "Scaling before splitting (leakage)", "Trusting accuracy on imbalanced data",
                         "Mixing up X_train/X_test order", "No baseline to compare with", "Using the test set to tune settings"],
             "notes": "Go through each and ask the group how to fix it. Fixes: always split first, use pipelines, look at the confusion matrix, unpack in the documented order, start with DummyClassifier or DummyRegressor, and tune with cross validation."},
            {"title": "Recap and exercises",
             "bullets": ["Split, baseline, pipeline, CV, test once, save", "Pick the metric that matches the cost of mistakes",
                         "Exercises: exercises.md (easy to hard)", "Calculator: excel/04-ml-metrics.xlsx"],
             "notes": "Summarise the workflow in one breath. Then set exercises one to four in class and the rest as homework. Point students to the solutions folder only after they have tried."},
        ],
    }
    slides(deck, HERE / "slides" / "04-machine-learning.pptx")


# ---------------------------------------------------------------------------
# 5. Excel
# ---------------------------------------------------------------------------
def build_excel():
    cheat = [
        ["Metric", "Task", "Formula (plain)", "Range / best", "Use it when", "Watch out"],
        ["Accuracy", "Classification", "(TP+TN) / all", "0..1, higher better", "Classes balanced, mistakes cost the same", "Lies with class imbalance"],
        ["Precision", "Classification", "TP / (TP+FP)", "0..1, higher better", "False alarms are costly (spam filter)", "Can be high while missing most positives"],
        ["Recall (sensitivity, TPR)", "Classification", "TP / (TP+FN)", "0..1, higher better", "Misses are costly (cancer, fraud)", "Saying 'positive' always gives recall 1"],
        ["Specificity (TNR)", "Classification", "TN / (TN+FP)", "0..1, higher better", "Need to clear negatives correctly", "Ignores how many positives you find"],
        ["F1 score", "Classification", "2*P*R / (P+R)", "0..1, higher better", "Need balance of precision and recall", "Ignores true negatives"],
        ["False positive rate", "Classification", "FP / (FP+TN)", "0..1, lower better", "x-axis of the ROC curve", "= 1 - specificity"],
        ["ROC-AUC", "Classification", "Area under TPR-vs-FPR curve", "0.5 = coin flip, 1 = perfect", "Judge scores before choosing a threshold", "Can look rosy on very imbalanced data"],
        ["MAE", "Regression", "mean(|true - pred|)", "0..inf, lower better", "Easy to explain average error", "Same units as the label"],
        ["MSE", "Regression", "mean((true - pred)^2)", "0..inf, lower better", "Training objective of linear regression", "Units are squared; hard to read"],
        ["RMSE", "Regression", "sqrt(MSE)", "0..inf, lower better", "Punish big errors more", "Sensitive to outliers"],
        ["R-squared", "Regression", "1 - SS_model / SS_mean", "<=1, 1 perfect, 0 = guess the mean", "Compare with always predicting average", "Can be negative"],
        ["Inertia", "Clustering (k-means)", "sum of squared distance to centroid", "lower = tighter clusters", "Elbow plot to choose k", "Always falls as k grows"],
        ["Adjusted Rand index", "Clustering vs known labels", "agreement of two groupings", "~0 random, 1 identical", "Check clusters against hidden labels", "Needs true labels"],
    ]
    calc = [
        ["Item", "Value", "How it is calculated", "Plain meaning"],
        ["True Positives (TP)", 15, "type your number", "Positive, and model said positive"],
        ["False Negatives (FN)", 5, "type your number", "Positive, but model said negative (a miss)"],
        ["False Positives (FP)", 10, "type your number", "Negative, but model said positive (false alarm)"],
        ["True Negatives (TN)", 70, "type your number", "Negative, and model said negative"],
        ["Total", "=SUM(B2:B5)", "TP+FN+FP+TN", "All examples"],
        ["Actual positives", "=B2+B3", "TP+FN", "How many real positives existed"],
        ["Actual negatives", "=B4+B5", "FP+TN", "How many real negatives existed"],
        ["Accuracy", "=IFERROR((B2+B5)/B6,0)", "(TP+TN)/Total", "Share of all answers that were right"],
        ["Precision", "=IFERROR(B2/(B2+B4),0)", "TP/(TP+FP)", "When it says positive, how often right"],
        ["Recall (sensitivity)", "=IFERROR(B2/(B2+B3),0)", "TP/(TP+FN)", "Share of real positives found"],
        ["Specificity", "=IFERROR(B5/(B5+B4),0)", "TN/(TN+FP)", "Share of real negatives correctly cleared"],
        ["F1 score", "=IFERROR(2*B10*B11/(B10+B11),0)", "2PR/(P+R)", "Balance of precision and recall"],
        ["False positive rate", "=IFERROR(B4/(B4+B5),0)", "FP/(FP+TN)", "Share of negatives wrongly flagged"],
        ["Prevalence", "=IFERROR(B7/B6,0)", "(TP+FN)/Total", "How common the positive class is"],
        ["Accuracy of 'always negative'", "=IFERROR(B8/B6,0)", "Actual negatives/Total", "Baseline to beat - if close to Accuracy, beware"],
    ]
    practice = [
        ["Scenario", "TP", "FN", "FP", "TN", "Accuracy", "Precision", "Recall", "F1", "Which metric matters most and why"],
        ["Spam filter (100 emails)", 15, 5, 10, 70, "=(B2+E2)/SUM(B2:E2)", "=B2/(B2+D2)", "=B2/(B2+C2)", "=2*G2*H2/(G2+H2)", "Precision: losing real email is worse"],
        ["Cancer screening (1000 people)", 45, 5, 95, 855, "=(B3+E3)/SUM(B3:E3)", "=B3/(B3+D3)", "=B3/(B3+C3)", "=2*G3*H3/(G3+H3)", "Recall: a missed cancer is worst"],
        ["Fraud model (10000 txns)", 30, 70, 20, 9880, "=(B4+E4)/SUM(B4:E4)", "=B4/(B4+D4)", "=B4/(B4+C4)", "=2*G4*H4/(G4+H4)", "High accuracy but recall only 30% - bad"],
        ["Breast cancer notebook (143 tumours)", 49, 4, 1, 89, "=(B5+E5)/SUM(B5:E5)", "=B5/(B5+D5)", "=B5/(B5+C5)", "=2*G5*H5/(G5+H5)", "Recall: 4 cancers missed despite 96.5% accuracy"],
    ]
    workbook({"Metrics Cheat Sheet": cheat, "Confusion Matrix Calculator": calc, "Practice Scenarios": practice},
             HERE / "excel" / "04-ml-metrics.xlsx",
             col_widths={"Metrics Cheat Sheet": [24, 22, 30, 28, 40, 38],
                         "Confusion Matrix Calculator": [30, 14, 26, 46],
                         "Practice Scenarios": [34, 8, 8, 8, 8, 11, 11, 11, 11, 44]})
    # number formats for percentages
    from openpyxl import load_workbook
    p = HERE / "excel" / "04-ml-metrics.xlsx"
    wb = load_workbook(p)
    ws = wb["Confusion Matrix Calculator"]
    for r in range(9, 17):
        ws.cell(r, 2).number_format = "0.0%"
    ws2 = wb["Practice Scenarios"]
    for r in range(2, 6):
        for c in range(6, 10):
            ws2.cell(r, c).number_format = "0.0%"
    wb.save(p)


if __name__ == "__main__":
    build_mermaid()
    build_plots()
    build_notebooks()
    build_slides()
    build_excel()
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / "04-machine-learning-handout.pdf",
                      title="Module 04 - Machine Learning (handout)")
    print("04-machine-learning built.")
