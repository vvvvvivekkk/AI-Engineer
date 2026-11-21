"""
segmentation.py - Part B: group customers into segments with K-means (unsupervised learning).

Unsupervised = there are no "right answers" to learn from; the algorithm finds structure itself.
K-means in one sentence: drop k pins on the map, give every customer to the nearest pin, move each
pin to the middle of its customers, repeat until the pins stop moving.

How we choose k (the number of groups):
  * elbow method - plot "inertia" (total squared distance from customers to their pin) for k=2..8;
                   it always falls, but look for the bend where adding groups stops helping much
  * silhouette   - for each customer: how close it is to its own group vs the next-nearest group,
                   from -1 (wrong group) to +1 (clearly in the right group). Higher average = better.
PCA (principal component analysis) squeezes the features into 2 numbers so we can draw a 2-D picture.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

DATA = Path(__file__).resolve().parents[1] / "data" / "customers.csv"
# avg_basket is left out on purpose: it is a ratio with a long tail, and it would mostly
# repeat information already in spend and visits (try adding it back as an experiment).
FEATURES = ["annual_spend", "visits_per_month", "days_since_last_visit"]
SEED = 42


def load() -> pd.DataFrame:
    return pd.read_csv(DATA)


def choose_k(Xs, k_values=range(2, 9)) -> pd.DataFrame:
    """Fit K-means for each k; record inertia (for the elbow) and silhouette."""
    rows = []
    for k in k_values:
        km = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(Xs)
        rows.append({"k": k, "inertia": km.inertia_, "silhouette": silhouette_score(Xs, km.labels_)})
    return pd.DataFrame(rows)


def name_segment(row: pd.Series, overall: pd.Series) -> str:
    """Give each cluster a human-friendly name from its averages (simple rules, easy to explain)."""
    if row.days_since_last_visit > 150:
        return "lost"
    if row.days_since_last_visit > 60:
        return "at risk"
    if row.annual_spend > overall.annual_spend and row.visits_per_month > overall.visits_per_month:
        return "loyal big spenders"
    return "occasional"


def run(out_dir: Path) -> dict:
    df = load()
    # Scale so "dollars" (hundreds) don't drown out "visits" (single digits) in the distance math
    Xs = StandardScaler().fit_transform(df[FEATURES])

    k_table = choose_k(Xs)
    best_k = int(k_table.sort_values("silhouette", ascending=False).iloc[0]["k"])
    km = KMeans(n_clusters=best_k, n_init=10, random_state=SEED).fit(Xs)
    df["segment"] = km.labels_

    # Profile = average of each feature per segment + its size; then name each segment
    profile = df.groupby("segment")[FEATURES].mean()
    profile["customers"] = df["segment"].value_counts().sort_index()
    overall = df[FEATURES].mean()
    profile["name"] = [name_segment(r, overall) for _, r in profile.iterrows()]

    # How well did we recover the hidden groups? (only possible because the data is synthetic)
    ari = adjusted_rand_score(df["hidden_segment"], df["segment"])

    # Charts: elbow, silhouette, PCA scatter
    out_dir.mkdir(parents=True, exist_ok=True)
    xy = PCA(n_components=2, random_state=SEED).fit_transform(Xs)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    axes[0].plot(k_table.k, k_table.inertia, "o-")
    axes[0].set(xlabel="k", ylabel="inertia", title="Elbow method")
    axes[1].plot(k_table.k, k_table.silhouette, "o-", color="tab:green")
    axes[1].axvline(best_k, ls="--", color="grey")
    axes[1].set(xlabel="k", ylabel="average silhouette", title=f"Silhouette (best k = {best_k})")
    for seg in sorted(df.segment.unique()):
        mask = df.segment == seg
        axes[2].scatter(xy[mask, 0], xy[mask, 1], s=12, label=f"{seg}: {profile.loc[seg, 'name']}")
    axes[2].set(xlabel="PCA 1", ylabel="PCA 2", title="Customers in 2-D (PCA)")
    axes[2].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "segmentation.png", dpi=110)
    plt.close(fig)

    df.drop(columns=["hidden_segment"]).to_csv(out_dir / "customers_with_segments.csv", index=False)
    return {"k_table": k_table, "best_k": best_k, "profile": profile, "ari": ari}
