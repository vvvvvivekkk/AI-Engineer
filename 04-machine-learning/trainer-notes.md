# Module 04 — Trainer Notes

These notes assume you have read `concepts.md` and run all four notebooks yourself at least once. Plan on two sessions of about 2 hours (weeks 7 and 8). The timing table below is for **session 1**; session 2 is listed after it.

---

## 1. What students should be able to do after the sessions

- Say in one sentence what machine learning is, and give one example each of regression, classification and clustering.
- Explain why we split data into training and test sets, using the exam analogy.
- Write the create → `fit` → `predict` pattern from memory.
- Draw a confusion matrix for a given scenario and calculate accuracy, precision, recall and F1 with a calculator.
- Choose precision or recall for a real situation and justify it by the cost of each mistake.
- Recognise overfitting from training vs test scores, and name two ways to reduce it.
- Build a `Pipeline`, run `cross_val_score`, and save the result with `joblib`.

## 2. Teaching sequence and timing

### Session 1 (2 hours) — "What ML is, and how we measure it"

| Time | Activity | Materials | Notes |
|---|---|---|---|
| 0:00–0:10 | Hook: "How would you write rules to recognise a handwritten 7?" Let students try; show how hard it is. | Whiteboard | Leads into "let the computer learn the rules from examples". |
| 0:10–0:25 | Used-car analogy; map features, label, model, training, prediction | Slides 1–3 | Leave the mapping table on the board all session. |
| 0:25–0:35 | Supervised vs unsupervised; regression vs classification quiz (Exercise 1, out loud) | Slide 4 | Use the "could it be 3.7?" test. |
| 0:35–0:45 | Train/test split + exam analogy | Slide 5 | Ask: "What if the exam questions were the homework questions?" |
| 0:45–1:10 | Live-code notebook 01 together (Colab) | Notebook 01 | Type, do not paste. Pause at the baseline and ask what "good" means. |
| 1:10–1:15 | Break | | |
| 1:15–1:35 | Confusion matrix with the 100-email example; students calculate metrics on paper | Slides 10–11, Excel calculator | Reveal answers in the Excel calculator, then change numbers live. |
| 1:35–1:50 | Notebook 02 steps 5–9 (real confusion matrix, threshold, accuracy trap) | Notebook 02 | The "missed 4 cancers at 96.5% accuracy" moment is the key lesson. |
| 1:50–2:00 | Recap + set Exercises 2–5 | Slide 20 | Exit question: "When is accuracy misleading?" |

### Session 2 (2 hours) — "Better models, honest evaluation"

| Time | Activity | Materials |
|---|---|---|
| 0:00–0:10 | Recap quiz on metrics (Section 4 questions 1–4) | — |
| 0:10–0:35 | Trees and forests: 20 Questions, then notebook 03 steps 2–4 | Slide 12, Notebook 03 |
| 0:35–0:55 | k-means: ice-cream vans role-play (3 students as vans, rest as sunbathers), then notebook 03 steps 5–7 | Slide 13 |
| 0:55–1:00 | Break | — |
| 1:00–1:20 | Overfitting: polynomial plot and tree-depth curve | Slides 14–15, Notebook 04 steps 2–3 |
| 1:20–1:40 | Cross-validation and the data-leakage demo | Slides 16–17, Notebook 04 steps 4–7 |
| 1:40–1:52 | Pipeline + GridSearchCV + joblib | Slide 18, Notebook 04 steps 8–9 |
| 1:52–2:00 | Common mistakes slide; set Exercises 6–12 | Slides 19–20 |

## 3. Common student mistakes and how to fix them

1. **Evaluating on the training data.** Symptom: "my model is 100% accurate!" Fix: ask "accurate on what data?" Always report the test score (or CV score). Show the decision-tree depth table.
2. **Unpacking `train_test_split` in the wrong order** (e.g. `X_train, y_train, X_test, y_test`). Symptom: shape errors or nonsense scores. Fix: the order is *X_train, X_test, y_train, y_test* — "both X's first, then both y's". Have students print `.shape` of all four.
3. **Scaling or selecting features before the split / outside the pipeline** (data leakage). Fix: put every step that "learns" from data inside a `Pipeline`. Show the leakage demo in notebook 04 (92% on random noise).
4. **Passing a 1-D array as X.** Symptom: `ValueError: Expected 2D array, got 1D array`. Fix: X must be a table. Use `df[["bmi"]]` (double brackets) or `x.reshape(-1, 1)`.
5. **Mixing up precision and recall.** Fix: the fishing-net analogy; recall's denominator is "everything that was really there" (TP + FN), precision's is "everything I flagged" (TP + FP). Make them write both formulas from the confusion-matrix picture.
6. **Forgetting which class is positive in scikit-learn.** In `load_breast_cancer`, 1 = *benign*. Symptom: "recall" numbers that describe the wrong class. Fix: check `data.target_names`, and flip labels or use `pos_label=` when needed.
7. **Reading TP from the wrong corner of `confusion_matrix`.** scikit-learn puts the negative class first, so TP is bottom-right. Fix: always use `tn, fp, fn, tp = cm.ravel()`.
8. **Ignoring `ConvergenceWarning`.** Fix: scale features (pipeline with `StandardScaler`) and/or raise `max_iter`.
9. **Tuning on the test set** (trying settings until the test score is high). Fix: tune with CV/`GridSearchCV` on training data; touch the test set once.
10. **Thinking k-means cluster numbers mean something.** Cluster "0" is not species "0". Fix: use `pd.crosstab` or adjusted Rand index to compare with known labels.

## 4. Questions to check understanding (with answers)

1. **Q:** A model scores 99% on training data and 70% on test data. What is happening and what would you try?
   **A:** Overfitting. Try a simpler model (e.g. smaller `max_depth`), regularisation, more data, or an ensemble; compare options with cross-validation.
2. **Q:** 1% of transactions are fraud. Your model is 99% accurate. Is it good?
   **A:** Not necessarily — always predicting "not fraud" also gets 99%. Look at recall and precision for the fraud class.
3. **Q:** For a cancer screening test, which matters more: precision or recall? Why?
   **A:** Recall — missing a cancer (FN) is far worse than a false alarm, which a follow-up test can clear.
4. **Q:** TP=8, FP=2, FN=8, TN=82. Precision? Recall?
   **A:** Precision 8/10 = 0.8. Recall 8/16 = 0.5.
5. **Q:** What is the difference between a parameter and a hyperparameter?
   **A:** Parameters are learned during training (weights); hyperparameters are chosen by you before training (`max_depth`, `C`, `n_clusters`).
6. **Q:** Why do we put `StandardScaler` inside a pipeline rather than scaling first?
   **A:** So the scaler learns its mean/spread only from training data (each training fold in CV). Otherwise test information leaks into training.
7. **Q:** Why does k-means need you to choose k? How can you pick it?
   **A:** It has no labels to tell it how many groups exist. Use the elbow plot of inertia, plus domain knowledge.
8. **Q:** Why might a random forest beat a single decision tree?
   **A:** Each tree makes different mistakes on different random samples; voting cancels many of them out (wisdom of the crowd), so it overfits less.
9. **Q:** What is the danger of `joblib.load` on a file someone emailed you?
   **A:** It can run arbitrary code on your machine.

## 5. Adapting for faster or slower groups

**Slower groups**
- Spend session 1 entirely on notebook 01 and the confusion matrix; move ROC-AUC to session 2 or skip it.
- Do metrics with paper and calculators before any code. Use the Excel calculator's "Practice Scenarios" sheet as a group activity.
- Skip `GridSearchCV`; teach `cross_val_score` and `Pipeline` only.
- Pair students: one types, one reads the markdown explanation aloud; swap every notebook step.

**Faster groups**
- Add `Ridge` / `Lasso` regularisation and show weights shrinking as `alpha` grows.
- Try `GradientBoostingClassifier` or `HistGradientBoostingClassifier` and compare with random forests via CV.
- Introduce `ColumnTransformer` for mixed numeric + text-category columns (make a small DataFrame with a "city" column).
- Exercise 12 as a timed mini-hackathon: best CV accuracy on digits in 30 minutes.
- Discuss `class_weight="balanced"` for imbalanced data and compare recall with the default.

## Practical tips

- Run every notebook once before class (Colab first run is slower while it starts).
- Use `n_jobs=1` in shared/classroom environments; on personal laptops `n_jobs=-1` is fine.
- Keep the confusion-matrix picture on screen whenever you discuss metrics.
