"""
04_pipeline_gridsearch_save.py
A complete, professional workflow: split -> pipeline -> cross-validated grid search -> test once -> save.
Run:  python 04_pipeline_gridsearch_save.py         (creates digits_model.joblib next to this script)
"""
# Path helps build file paths that work on Windows, Mac and Linux
from pathlib import Path
# joblib saves and loads Python objects (our trained model) to/from disk
import joblib
# scikit-learn itself, so we can record its version
import sklearn
# 1,797 tiny 8x8 images of handwritten digits, already flattened to 64 numbers each
from sklearn.datasets import load_digits
# splitter and the automatic settings-search tool
from sklearn.model_selection import train_test_split, GridSearchCV
# Pipeline chains named steps
from sklearn.pipeline import Pipeline
# feature scaler
from sklearn.preprocessing import StandardScaler
# the classifier
from sklearn.linear_model import LogisticRegression

# load features and labels
X, y = load_digits(return_X_y=True)
# lock away 20% as the final test set BEFORE doing anything else
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)

# the pipeline: each step has a name we can refer to later
pipe = Pipeline([
    ("scale", StandardScaler()),                       # step 1: rescale pixels
    ("model", LogisticRegression(max_iter=2000)),      # step 2: classify
])

# settings to try; "model__C" means "the C setting of the step named model"
param_grid = {"model__C": [0.01, 0.1, 1.0, 10.0]}
# try every setting with 3-fold cross-validation on the TRAINING data only
search = GridSearchCV(pipe, param_grid, cv=3, n_jobs=1)
# run the search (fits 4 settings x 3 folds = 12 models, then refits the best on all training data)
search.fit(X_train, y_train)
# report the winner
print("best C:", search.best_params_["model__C"], " CV accuracy:", round(search.best_score_, 3))

# use the untouched test set exactly once
best = search.best_estimator_
print("test accuracy:", round(best.score(X_test, y_test), 3))

# save the whole pipeline (scaler + model) next to this script
out = Path(__file__).with_name("digits_model.joblib")
joblib.dump(best, out)
print("saved to", out, "with scikit-learn", sklearn.__version__)

# load it back as if we were a different program, and use it
loaded = joblib.load(out)
print("loaded model predictions:", loaded.predict(X_test[:10]))
print("true labels:             ", y_test[:10])
