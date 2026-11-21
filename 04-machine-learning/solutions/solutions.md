# Module 04 — Worked Solutions

Runnable code for exercises 2–12 is in `solutions.py` (`python solutions.py`). Numbers below were produced with scikit-learn 1.9.1; other versions may differ in the last decimal place.

---

## Exercise 1 — Regression or classification?

1. **Regression.** Label: maximum temperature (a number like 34.6 °C).
2. **Binary classification.** Label: repay / default (two classes).
3. **Clustering** (unsupervised). No label — the groups are discovered.
4. **Multi-class classification.** Label: one of 26 letters.
5. **Regression.** Label: minutes (a number).

Tip for students: "Could the answer be 3.7?" → regression.

## Exercise 2 — Confusion matrix by hand

- TP = 35 (said positive, really had COVID)
- FP = 50 − 35 = 15 (said positive, but healthy)
- FN = 40 − 35 = 5 (had COVID, test said negative)
- TN = 200 − 35 − 15 − 5 = 145

| Metric | Working | Result |
|---|---|---|
| Accuracy | (35 + 145) / 200 | **0.900** |
| Precision | 35 / (35 + 15) | **0.700** |
| Recall | 35 / (35 + 5) | **0.875** |
| F1 | 2 × 0.7 × 0.875 / (0.7 + 0.875) | **0.778** |

Meaning: the test finds 87.5% of infected people, but 30% of its positive results are false alarms.

## Exercise 3 — Regression metrics by hand

Errors (true − predicted): −5, 2, 10, −10.

- MAE = (5 + 2 + 10 + 10) / 4 = **6.75 lakh**
- MSE = (25 + 4 + 100 + 100) / 4 = **57.25**
- RMSE = √57.25 ≈ **7.57 lakh**

RMSE > MAE because the two 10-lakh misses are squared.

## Exercise 4 — First classifier on iris

Test accuracy = **1.0** with this split; the confusion matrix is fully diagonal (no confusion). With other `random_state` values you will usually see one or two *versicolor*/*virginica* mix-ups — those two species overlap; *setosa* is always easy.

## Exercise 5 — Beat the baseline

| Model | MAE | R² |
|---|---|---|
| DummyRegressor | 62.6 | −0.007 |
| LinearRegression | **42.0** | **0.438** |
| RandomForestRegressor | 46.6 | 0.280 |

Linear regression wins. Lesson: a fancier model is not automatically better, especially on a small (442-row) noisy dataset. Both real models clearly beat the baseline.

## Exercise 6 — Find the overfitting point

Training accuracy reaches **1.0 at depth 4**. Test accuracy peaks at depth 3 (0.963) and then drops to 0.944 and stays flat. After depth 3 the tree is memorising details of the training rows that do not help on new wines. A sensible choice: `max_depth=3`.

## Exercise 7 — Choose a threshold for a hospital

The highest threshold with recall ≥ 0.98 is **0.15**: recall 0.981 (52 of 53 cancers caught, 1 missed), precision 0.929, **4 false alarms**. Compare with the default 0.5 threshold (4 cancers missed, 1 false alarm). The hospital trades 3 extra false alarms for 3 fewer missed cancers — the right trade in screening.

Key idea: the threshold is a business decision, made after training.

## Exercise 8 — Cross-validation and scaling

| Model | 5-fold accuracy |
|---|---|
| Logistic + scaling | 0.979 ± 0.014 |
| KNN + scaling | 0.965 ± 0.021 |
| KNN, no scaling | 0.932 ± 0.019 |

KNN measures distances. Without scaling, the features with large numbers (like *worst area*, in the hundreds or thousands) dominate the distance and the small-number features are ignored. Scaling lifts KNN by about 3 points. **Distance-based models need scaling.**

## Exercise 9 — k-means on digits

ARI ≈ **0.47** (far above random, far below perfect). Clusters for **0, 4 and 6** are almost pure (purity 0.96–0.99). Others are mixed: one large cluster is only 36% "3" (it also holds 5s, 8s and 9s), and the digit 1 is split across two impure clusters. k-means groups by overall pixel similarity, and digits like 3/5/8/9 share many strokes. This is why we use supervised learning when labels exist.

## Exercise 10 — Spot and fix the leak

**The leak:** `StandardScaler` is fitted on *all* rows, so inside cross-validation each validation fold has already influenced the mean and spread used to scale the training folds.

**Fix:**

```python
from sklearn.pipeline import make_pipeline
pipe = make_pipeline(StandardScaler(), SVC())
print(cross_val_score(pipe, X, y, cv=5).mean())
```

On this dataset the two numbers happen to be the same (0.974) — scaling leaks very little information. That is exactly why leakage is dangerous: it is usually invisible. With steps that learn more from the data (feature selection, filling missing values with target information), the leak can create huge fake skill — notebook 04 shows 92% "accuracy" on pure random noise. Always use the pipeline habit, even when the leak looks harmless.

## Exercise 11 — Grid search on a random forest

Best: `max_depth=2`, `n_estimators=200`, CV accuracy **0.963**, test accuracy **1.0**.

We report the test score once because if we used it to choose settings, it would stop being an unseen exam — we would be tuning to the test set and the number would be over-optimistic. (A perfect 1.0 on 45 test wines is partly luck; the CV score of 0.963 is the more reliable estimate.)

## Exercise 12 — Saved, reusable model

`solutions.py → ex12()` does both parts in one file for convenience; in a real project split it into `train_and_save.py` and `predict.py`. Result: CV chose the random forest (0.975 vs 0.966 for logistic regression); test accuracy 0.978; the loaded model got 20/20 correct without retraining.

`predict.py` would contain only:

```python
import joblib
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
X, y = load_digits(return_X_y=True)
_, X_te, _, y_te = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
model = joblib.load("digits.joblib")
print((model.predict(X_te[:20]) == y_te[:20]).sum(), "/ 20 correct")
```

**Why never load untrusted joblib files:** joblib uses Python's pickle format, which can contain instructions that run arbitrary code the moment the file is loaded. A malicious "model" file could delete files or steal secrets from your computer.
