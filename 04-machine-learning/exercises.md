# Module 04 — Exercises

Work through these in order. They start easy and get harder. Use a new notebook (Colab or Jupyter). Only scikit-learn's built-in datasets are needed — no downloads.

Solutions: `solutions/solutions.md` (explanations) and `solutions/solutions.py` (runnable code). Try each one properly before looking.

---

## Easy

### Exercise 1 — Regression or classification?
For each task, say whether it is **regression**, **binary classification**, **multi-class classification** or **clustering**, and name the label (if there is one).

1. Predict tomorrow's maximum temperature in Hyderabad.
2. Decide whether a loan applicant will repay or default.
3. Group 10,000 online shoppers into types, with no labels.
4. Recognise which of 26 letters a handwritten character is.
5. Estimate how many minutes a food delivery will take.

### Exercise 2 — Confusion matrix by hand
A COVID test is used on 200 people. 40 really have COVID. The test says "positive" for 50 people, and 35 of those really have COVID.

Fill in TP, FN, FP, TN. Then calculate accuracy, precision, recall and F1 (to 3 decimal places). Check your answer with the calculator in `excel/04-ml-metrics.xlsx`.

### Exercise 3 — Regression metrics by hand
True house prices (lakh): `[50, 60, 80, 100]`. Predicted: `[55, 58, 70, 110]`.
Calculate MAE, MSE and RMSE by hand. Then check with `sklearn.metrics`.

### Exercise 4 — Your first classifier on iris
Load `load_iris`. Split 75/25 with `stratify=y` and `random_state=0`. Train `LogisticRegression(max_iter=1000)`. Print the test accuracy and the confusion matrix. Which two species get confused (if any)?

---

## Medium

### Exercise 5 — Beat the baseline
On `load_diabetes`, compare these three models on the same 80/20 split (`random_state=1`): `DummyRegressor()`, `LinearRegression()`, `RandomForestRegressor(n_estimators=200, random_state=0)`. Print MAE and R² for each. Which wins? Is the difference big?

### Exercise 6 — Find the overfitting point
On `load_wine`, train `DecisionTreeClassifier` with `max_depth` from 1 to 10. For each depth record training and test accuracy. Plot both lines on one chart. At what depth does the training accuracy reach 1.0? What does the test accuracy do after that?

### Exercise 7 — Choose a threshold for a hospital
Using the breast-cancer data with **malignant = 1** (see notebook 02), train a scaled logistic regression. The hospital says: "We must catch at least 98% of cancers (recall ≥ 0.98). Among models that do, we want the fewest false alarms." Find the **highest** threshold (try 0.05, 0.10, …, 0.95) that meets the rule, and report precision, recall and number of false alarms at that threshold.

### Exercise 8 — Cross-validation instead of one split
On `load_breast_cancer`, compute 5-fold cross-validated accuracy (`StratifiedKFold(5, shuffle=True, random_state=0)`) for: a scaled logistic regression, a `KNeighborsClassifier()` **with** scaling, and a `KNeighborsClassifier()` **without** scaling. (**k-nearest neighbours** — predicts the label most common among the k closest training rows.) What does the result tell you about scaling for distance-based models?

---

## Hard

### Exercise 9 — k-means on digits
Load `load_digits`. Scale the data and run `KMeans(n_clusters=10, n_init=10, random_state=0)`. Compute the adjusted Rand index against the real digit labels. Then, for each cluster, find the most common real digit in it and report what fraction of the cluster that digit makes up ("purity"). Which digits does k-means find easily, and which get mixed?

### Exercise 10 — Spot and fix the leak
This code is meant to estimate how well a model does. It contains **data leakage**. Explain the leak in one sentence, then rewrite it with a `Pipeline` so the estimate is honest.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
X, y = load_breast_cancer(return_X_y=True)
X_scaled = StandardScaler().fit_transform(X)
print(cross_val_score(SVC(), X_scaled, y, cv=5).mean())
```

### Exercise 11 — Full grid search on a random forest
On `load_wine`, split off a 25% test set. Build a `Pipeline` with just a `RandomForestClassifier(random_state=0, n_jobs=1)`. Use `GridSearchCV` (cv=5) over `n_estimators` in `[50, 200]` and `max_depth` in `[2, 4, None]`. Report the best settings, the best CV score, and the final test score. Explain why we report the test score only once.

### Exercise 12 — Mini project: a saved, reusable model
Write a script `train_and_save.py` that:
1. Trains the best model you can find on `load_digits` (use cross-validation to choose between at least two model types).
2. Saves the full pipeline to `digits.joblib`, plus a small text file `model_info.txt` with the scikit-learn version, the chosen model and its test accuracy.

Then write a second script `predict.py` that loads `digits.joblib`, predicts the first 20 test images and prints how many are correct — without retraining. Finally, write two sentences on why you must never `joblib.load` a file from an untrusted source.
