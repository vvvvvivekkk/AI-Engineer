"""
solutions.py - runnable solutions for module 04 exercises 2-12.
Run:  python solutions.py         (about 30-60 seconds on a laptop CPU)
Each section prints its answer; see solutions.md for the explanations.
"""
# standard tools
from pathlib import Path
import numpy as np
import joblib
import sklearn
import matplotlib
matplotlib.use("Agg")                     # draw charts to files, no window needed
import matplotlib.pyplot as plt

# datasets that ship with scikit-learn (no downloads)
from sklearn.datasets import load_iris, load_diabetes, load_wine, load_breast_cancer, load_digits
# splitting, cross-validation and searching
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
# preprocessing and pipelines
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline, Pipeline
# models
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from sklearn.svm import SVC
# metrics
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score, confusion_matrix,
                             precision_score, recall_score, adjusted_rand_score)

HERE = Path(__file__).resolve().parent


def ex2():
    # numbers from the question
    tp = 35                 # said positive AND had COVID
    fp = 50 - 35            # said positive but healthy
    fn = 40 - 35            # had COVID but test said negative
    tn = 200 - tp - fp - fn # everyone else
    acc = (tp + tn) / 200
    prec = tp / (tp + fp)
    rec = tp / (tp + fn)
    f1 = 2 * prec * rec / (prec + rec)
    print(f"Ex2: TP={tp} FN={fn} FP={fp} TN={tn} acc={acc:.3f} prec={prec:.3f} rec={rec:.3f} f1={f1:.3f}")


def ex3():
    true = np.array([50, 60, 80, 100])
    pred = np.array([55, 58, 70, 110])
    print(f"Ex3: MAE={mean_absolute_error(true, pred):.2f} MSE={mean_squared_error(true, pred):.2f} "
          f"RMSE={np.sqrt(mean_squared_error(true, pred)):.3f}")


def ex4():
    iris = load_iris()
    X_tr, X_te, y_tr, y_te = train_test_split(iris.data, iris.target, test_size=0.25,
                                              random_state=0, stratify=iris.target)
    m = LogisticRegression(max_iter=1000).fit(X_tr, y_tr)
    print("Ex4: accuracy", round(m.score(X_te, y_te), 3))
    print(confusion_matrix(y_te, m.predict(X_te)))


def ex5():
    X, y = load_diabetes(return_X_y=True)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=1)
    for name, m in [("dummy", DummyRegressor()), ("linear", LinearRegression()),
                    ("forest", RandomForestRegressor(n_estimators=200, random_state=0, n_jobs=1))]:
        p = m.fit(X_tr, y_tr).predict(X_te)
        print(f"Ex5: {name:7s} MAE={mean_absolute_error(y_te, p):.1f} R2={r2_score(y_te, p):.3f}")


def ex6():
    X, y = load_wine(return_X_y=True)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
    depths, tr, te = range(1, 11), [], []
    for d in depths:
        t = DecisionTreeClassifier(max_depth=d, random_state=0).fit(X_tr, y_tr)
        tr.append(t.score(X_tr, y_tr)); te.append(t.score(X_te, y_te))
    print("Ex6: train", np.round(tr, 3))
    print("Ex6: test ", np.round(te, 3))
    plt.plot(depths, tr, "o-", label="train"); plt.plot(depths, te, "s-", label="test")
    plt.xlabel("max_depth"); plt.ylabel("accuracy"); plt.legend()
    plt.savefig(HERE / "ex6_depth_curve.png", dpi=100); plt.close()


def ex7():
    d = load_breast_cancer()
    X, y = d.data, (d.target == 0).astype(int)        # 1 = malignant
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X_tr, y_tr)
    proba = clf.predict_proba(X_te)[:, 1]
    best = None
    for t in np.round(np.arange(0.05, 0.96, 0.05), 2):
        p = (proba >= t).astype(int)
        rec = recall_score(y_te, p)
        if rec >= 0.98:
            best = t                                   # keep the highest threshold that still qualifies
    p = (proba >= best).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_te, p).ravel()
    print(f"Ex7: threshold={best} recall={recall_score(y_te, p):.3f} "
          f"precision={precision_score(y_te, p):.3f} false alarms={fp} missed={fn}")


def ex8():
    X, y = load_breast_cancer(return_X_y=True)
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    for name, m in [("logistic+scale", make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))),
                    ("knn+scale", make_pipeline(StandardScaler(), KNeighborsClassifier())),
                    ("knn no scale", KNeighborsClassifier())]:
        s = cross_val_score(m, X, y, cv=cv)
        print(f"Ex8: {name:15s} {s.mean():.3f} +/- {s.std():.3f}")


def ex9():
    digits = load_digits()
    Xs = StandardScaler().fit_transform(digits.data)
    labels = KMeans(n_clusters=10, n_init=10, random_state=0).fit_predict(Xs)
    print("Ex9: ARI", round(adjusted_rand_score(digits.target, labels), 3))
    for c in range(10):
        members = digits.target[labels == c]
        counts = np.bincount(members, minlength=10)
        print(f"     cluster {c}: size={len(members):3d} most common digit={counts.argmax()} "
              f"purity={counts.max() / len(members):.2f}")


def ex10():
    X, y = load_breast_cancer(return_X_y=True)
    leaky = cross_val_score(SVC(), StandardScaler().fit_transform(X), y, cv=5).mean()
    honest = cross_val_score(make_pipeline(StandardScaler(), SVC()), X, y, cv=5).mean()
    print(f"Ex10: leaky={leaky:.4f} honest={honest:.4f}")


def ex11():
    X, y = load_wine(return_X_y=True)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
    pipe = Pipeline([("forest", RandomForestClassifier(random_state=0, n_jobs=1))])
    grid = {"forest__n_estimators": [50, 200], "forest__max_depth": [2, 4, None]}
    search = GridSearchCV(pipe, grid, cv=5, n_jobs=1).fit(X_tr, y_tr)
    print("Ex11: best", search.best_params_, "CV", round(search.best_score_, 3),
          "test", round(search.score(X_te, y_te), 3))


def ex12():
    # --- train_and_save part ---
    X, y = load_digits(return_X_y=True)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    candidates = {
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=0.1)),
        "random_forest": make_pipeline(RandomForestClassifier(n_estimators=200, random_state=0, n_jobs=1)),
    }
    scores = {n: cross_val_score(m, X_tr, y_tr, cv=cv).mean() for n, m in candidates.items()}
    best_name = max(scores, key=scores.get)
    best = candidates[best_name].fit(X_tr, y_tr)
    acc = best.score(X_te, y_te)
    model_path = HERE / "digits.joblib"
    joblib.dump(best, model_path)
    (HERE / "model_info.txt").write_text(
        f"scikit-learn={sklearn.__version__}\nmodel={best_name}\ntest_accuracy={acc:.3f}\n")
    print("Ex12: CV scores", {k: round(v, 3) for k, v in scores.items()}, "chosen", best_name,
          "test", round(acc, 3))
    # --- predict part (a separate program would do only this) ---
    loaded = joblib.load(model_path)
    correct = int((loaded.predict(X_te[:20]) == y_te[:20]).sum())
    print(f"Ex12: loaded model got {correct}/20 correct")
    model_path.unlink(); (HERE / "model_info.txt").unlink()   # tidy up the course folder


if __name__ == "__main__":
    for f in [ex2, ex3, ex4, ex5, ex6, ex7, ex8, ex9, ex10, ex11, ex12]:
        f()
