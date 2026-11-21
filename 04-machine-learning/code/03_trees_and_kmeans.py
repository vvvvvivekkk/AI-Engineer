"""
03_trees_and_kmeans.py
Compare a decision tree with a random forest on the wine data, then cluster synthetic blobs with k-means.
Run:  python 03_trees_and_kmeans.py
"""
# numpy for arrays
import numpy as np
# two built-in data sources: real wine data and a fake-blob generator
from sklearn.datasets import load_wine, make_blobs
# splitter
from sklearn.model_selection import train_test_split
# a single tree of yes/no questions
from sklearn.tree import DecisionTreeClassifier
# many trees voting together
from sklearn.ensemble import RandomForestClassifier
# the k-means clustering algorithm
from sklearn.cluster import KMeans
# score that compares two groupings (1 = identical, ~0 = random)
from sklearn.metrics import adjusted_rand_score

# ---- Part 1: supervised trees ----
# load 178 wines with 13 chemical features and 3 grape-type labels
wine = load_wine()
# 30% test set, keeping the class mix equal in both parts
X_train, X_test, y_train, y_test = train_test_split(
    wine.data, wine.target, test_size=0.3, random_state=0, stratify=wine.target)

# try several depths to see under- and overfitting
for depth in (1, 2, 3, None):
    # None means "keep splitting until every leaf is pure"
    tree = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X_train, y_train)
    # compare accuracy on the data it studied vs data it never saw
    print(f"tree depth={depth}: train={tree.score(X_train, y_train):.3f} test={tree.score(X_test, y_test):.3f}")

# 200 trees; n_jobs=1 uses a single CPU core
forest = RandomForestClassifier(n_estimators=200, random_state=0, n_jobs=1).fit(X_train, y_train)
print(f"random forest: train={forest.score(X_train, y_train):.3f} test={forest.score(X_test, y_test):.3f}")

# list the three features the forest relied on most
top = np.argsort(forest.feature_importances_)[::-1][:3]
print("top features:", [wine.feature_names[i] for i in top])

# ---- Part 2: unsupervised k-means ----
# 300 points around 3 hidden centres; we keep the true groups only to check the result
X_blobs, true_groups = make_blobs(n_samples=300, centers=3, random_state=42)
# ask k-means for 3 clusters; n_init=10 tries 10 random starts and keeps the best
km = KMeans(n_clusters=3, n_init=10, random_state=42)
# fit_predict trains and returns a cluster number for every point
found = km.fit_predict(X_blobs)
# compare found clusters with the hidden truth
print(f"k-means ARI vs hidden groups: {adjusted_rand_score(true_groups, found):.3f}")
# show the elbow numbers: inertia for k = 1..6
for k in range(1, 7):
    inertia = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_blobs).inertia_
    print(f"k={k}: inertia={inertia:9.1f}")
