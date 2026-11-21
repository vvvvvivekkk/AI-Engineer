# P1 - Classic classifiers in a proper scikit-learn Pipeline

**Level:** Beginner · **Modules used:** 02 (pandas), 03 (math intuition), 04 (machine learning) · **Runs on:** any laptop CPU or free Colab, about 20 seconds

## What it does

This project teaches a computer to **sort things into groups** from measurements:

- **wine** - which of 3 grape cultivars a wine came from, using 13 chemical measurements;
- **iris** - which of 3 flower species, using 4 petal/sepal sizes;
- **breast_cancer** - whether a tumour is malignant or benign, using 30 cell measurements.

Sorting into groups is called **classification** (a model that predicts a category, not a number). For each dataset the project:

1. splits the data into a **training set** (the part the model learns from) and a **test set** (kept hidden until the very end, like a final exam the student has never seen);
2. builds four models, each inside a **Pipeline** (a chain of steps - here "rescale the numbers" then "fit the model" - that acts as one model);
3. compares them with **5-fold cross-validation** (split the training set into 5 slices, train on 4, score on the 5th, rotate, and average the 5 scores);
4. tunes the winner's **hyperparameters** (settings you pick before training, such as how many neighbours k-NN looks at) with `GridSearchCV` (try every combination in a small grid, keep the best);
5. scores the tuned model **once** on the hidden test set, and writes a report with a **confusion matrix** (a table of "true class vs predicted class", where the diagonal counts correct answers).

For breast cancer it also counts **false negatives** (cancers the model missed) and **false positives** (false alarms), and explains why those two mistakes are not equally bad.

Typical result (your numbers will match because everything is seeded):

| dataset | best model | test accuracy | test F1-macro |
|---|---|---|---|
| wine | logistic_regression | 0.972 | 0.971 |
| iris | logistic_regression | 1.000 | 1.000 |
| breast_cancer | logistic_regression | 0.974 | 0.972 |

## Architecture

![P1 architecture](images/architecture.png)

Analogy: think of a cooking contest. Four cooks (models) each follow the same prep routine (the Pipeline's scaling step). Cross-validation is five rounds of tasting by different judges. The winner gets to fine-tune their recipe (grid search). Then a brand-new judge tastes the final dish once (the test set). That last score is the one you report.

## Setup

### Option A - Google Colab (nothing to install)

1. Open `colab_quickstart.ipynb` from this folder on GitHub and click the **Open in Colab** badge at the top.
2. Click **Runtime → Run all**. The notebook clones the repo, installs the packages from `requirements.txt` (except PyTorch, which Colab already has and this project does not need), runs `main.py`, shows a report and runs the tests.

### Option B - your own computer

```bash
# 1. get the code and move into this project
git clone https://github.com/vvvvvivekkk/AI-Engineer.git
cd AI-Engineer/15-projects/p01-ml-classifier-pipeline

# 2. make a virtual environment (a private box of packages just for this project)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. install the exact package versions
pip install -r requirements.txt

# 4. settings file (this project needs no API keys; the file is here for consistency)
cp .env.example .env               # Windows: copy .env.example .env

# 5. run it
python make_data.py                # optional: rewrites data/*.csv (already committed)
python main.py                     # all three datasets
python main.py --dataset wine      # just one
python -m pytest -q                # run the tests
```

Results appear in `reports/` (`report_<dataset>.md` and `confusion_<dataset>.png`).

## How each file works

### `make_data.py`
Loads the three datasets that ship inside scikit-learn (`load_wine`, `load_iris`, `load_breast_cancer` - no internet needed) and saves each as a CSV in `data/`. It adds a readable `target_name` column next to the numeric `target`, so you can open the file in Excel and understand it.

### `data/`
`wine.csv` (178 rows), `iris.csv` (150 rows), `breast_cancer.csv` (569 rows). Each row is one example; every column except `target` / `target_name` is a **feature** (an input measurement).

### `src/pipeline.py`
All the machine-learning logic, in small functions:
- `load_dataset(name)` - reads the CSV into a pandas table `X` (features) and a column `y` (labels). If the CSV is missing it falls back to scikit-learn's copy.
- `split(X, y)` - 80/20 train/test split with `stratify=y`, which keeps the share of each class the same in both parts.
- `build_candidates()` - four Pipelines: `StandardScaler` (rescales each column to mean 0, spread 1) plus Logistic Regression, k-Nearest Neighbours, Decision Tree or Random Forest.
- `compare_models(...)` - runs `cross_validate` for each Pipeline and returns a table of mean accuracy, its spread (standard deviation) and mean F1-macro.
- `tune(...)` + `PARAM_GRIDS` - `GridSearchCV` over a small grid for the winning model.
- `evaluate(...)` - accuracy, F1-macro, the per-class report (precision, recall, F1) and the confusion matrix on the test set.
- `plot_confusion(...)` - saves the confusion matrix as a PNG with matplotlib.
- `medical_note(...)` - for breast cancer, counts missed cancers vs false alarms.
- `run_experiment(name, out_dir)` - glues steps 1-5 together and writes the markdown report.

### `main.py`
The command-line entry point. `--dataset` picks one dataset or `all`; `--out` changes the output folder. Prints the comparison table and the final test scores.

### `tests/test_pipeline.py`
Five quick **pytest** tests (pytest is a tool that runs functions named `test_*` and reports which fail): data shapes, stratified split, Pipeline structure, "better than chance" on iris, and that a report file is written.

### `build.py`
Regenerates `images/architecture.png` (from Mermaid text, using `tools/build_kit.py`) and `colab_quickstart.ipynb`.

### `requirements.txt` and `.env.example`
Exact versions of every package (`==` pins, so the code behaves the same on every machine). `.env.example` is a template for settings; this project has none that matter.

## Key ideas in plain English

- **Why a Pipeline?** If you scale the whole dataset before splitting, the scaler has "seen" the test rows. That is **data leakage** (information from the exam sneaking into the study notes), and it makes scores look better than they really are. Inside a Pipeline, the scaler is refit on the training folds only, every time.
- **Accuracy vs F1-macro.** **Accuracy** is "fraction correct". **Precision** for a class is "of everything I called class A, how much really was A?". **Recall** is "of all the real A's, how many did I find?". **F1** combines the two. **Macro** means "average over classes equally", so a small class counts as much as a big one.
- **Why test only once?** Every time you peek at the test score and change something, the test set leaks into your decisions. Choose with cross-validation; confirm with the test set.

## How to explain it in an interview

**60-second pitch.** "I built a reusable classification pipeline in scikit-learn and ran it on three datasets: wine, iris and breast cancer. Each model is a Pipeline of scaling plus a classifier, so there's no data leakage. I compared logistic regression, k-NN, a decision tree and a random forest with stratified 5-fold cross-validation, tuned the winner with grid search, and only then scored it once on a held-out test set. Logistic regression won on all three, around 97% test accuracy. For breast cancer I went beyond accuracy and looked at false negatives, because a missed cancer costs far more than a false alarm, and I explained how I'd move the decision threshold to trade one for the other. Everything is seeded and tested with pytest, so the results reproduce exactly."

**Design decisions and trade-offs**
- *Pipeline everywhere* - a tiny bit more code, but it removes the most common beginner bug (leakage) and makes the model a single object you can save and deploy.
- *F1-macro as the selection metric* - it treats every class equally; accuracy alone can hide a weak class.
- *Small grids* - fast and readable; a bigger search could squeeze out a little more but risks overfitting to the cross-validation folds.
- *Logistic regression won* - these datasets are small and close to linearly separable; a simple model with fewer knobs generalises well. A random forest is a close second and needs no scaling.

**Five likely questions**
1. *What is data leakage and how did you avoid it?* - Test information influencing training. The scaler lives inside the Pipeline, so cross-validation refits it on each training fold, and the test set is touched once.
2. *Why cross-validation instead of one validation split?* - With 150-569 rows, one split is noisy. Averaging 5 folds gives a steadier estimate and a spread (std) that shows stability.
3. *Why stratify?* - So each split keeps the same class proportions; otherwise a fold might have very few examples of one class.
4. *For cancer, would you optimise accuracy?* - No. I'd optimise recall on the malignant class (or a cost-weighted metric) and pick a probability threshold that keeps false negatives near zero, accepting more false alarms.
5. *Why did the decision tree score lowest?* - A single tree has high **variance** (small data changes give very different trees), so it overfits. A random forest averages many trees, which reduces variance.

## Credits (original idea)

- "10 Machine Learning Projects for Classification with Python" - Aman Kharwal, listed in ashishpatel26's project index (source 6): https://medium.datadriveninvestor.com/10-machine-learning-projects-on-classification-with-python-9261add2e8a7
- Iris as a beginner practice dataset - source 8's `Projects/Projects.md`.
- Datasets: scikit-learn's bundled copies of the UCI Wine, Iris and Breast Cancer Wisconsin (Diagnostic) datasets - https://scikit-learn.org/stable/datasets/toy_dataset.html

This code is our own reimplementation on bundled offline data.

## What to try next

1. Add a fifth model (e.g. `SVC` with an RBF kernel or `GradientBoostingClassifier`) to `build_candidates()` and `PARAM_GRIDS`.
2. For breast cancer, use `predict_proba` and plot precision and recall against the threshold; pick the threshold that gives recall ≥ 0.99 on malignant.
3. Save the tuned pipeline with `joblib.dump` and write a tiny `predict.py` that loads it and classifies one new row.
4. Add `RepeatedStratifiedKFold` and compare how much the scores move.
5. Plot random-forest feature importances for wine and explain the top three features.
