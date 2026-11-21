<!-- nav:start -->
> [🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 03 Math for AI](../03-math-for-ai/README.md) · [05 Deep Learning ➡️](../05-deep-learning/README.md)  
> **🎯 Module 04 · Machine Learning**  
> [📖 Lesson](concepts.md) · [📄 PDF handout](pdf/04-machine-learning-handout.pdf) · [🎞️ Slides](slides/04-machine-learning.pptx) · [📓 Notebooks](notebooks/) · [✍️ Exercises](exercises.md) · [✅ Solutions](solutions/) · [🧑‍🏫 Trainer notes](trainer-notes.md) · [🔗 Resources](resources.md)
<!-- nav:end -->

# Module 04 — Machine Learning (weeks 7–8)

Classic machine learning with **scikit-learn**: teaching computers to learn patterns from examples. This is the foundation that deep learning, NLP and LLM work all build on.

## Goals — after this module you can

- Explain what machine learning is, and the difference between **supervised** (data with answers) and **unsupervised** (data without answers) learning.
- Tell a **regression** task (predict a number) from a **classification** task (predict a category).
- Split data into training and test sets, and explain why that matters.
- Train linear regression, logistic regression, decision trees, random forests and k-means with scikit-learn.
- Spot **overfitting** (memorising instead of learning) from a training-vs-test comparison and a plot.
- Read a **confusion matrix** and calculate accuracy, precision, recall and F1 by hand; choose the right metric for a real problem.
- Use **cross-validation**, **pipelines** and `GridSearchCV`, and avoid **data leakage**.
- Save and load a trained model with **joblib**.

## Prerequisites

- Module 01 (Python basics): functions, lists, dictionaries, loops.
- Module 02 (Python for data): NumPy arrays, pandas DataFrames, matplotlib charts.
- Module 03 (Math for AI): the idea of a slope and of an average. No other maths needed.

## Time estimate

| Activity | Time |
|---|---|
| Read `concepts.md` | 2–3 hours |
| Work through the 4 notebooks | 4–5 hours |
| Exercises | 4–6 hours |
| Trainer: prepare to teach one session | 3–4 hours after self-study |

Total for a learner: about 12–16 hours over two weeks.

## Which tool, and why

**Google Colab or local Jupyter — both work.** Every notebook uses only datasets that ship inside scikit-learn (`load_diabetes`, `load_breast_cancer`, `load_iris`, `load_wine`, `load_digits`) or data we generate (`make_classification`, `make_blobs`), so there is **nothing to download and no API key**. Each notebook runs in under 30 seconds on a normal laptop CPU. No GPU is needed.

- New learners: click the **Open in Colab** badge at the top of each notebook — zero setup.
- If you have finished module 00 setup: open the notebooks in VS Code or Jupyter locally; you can then also run the scripts in `code/` from the terminal.

## File map

| Path | What it is |
|---|---|
| `concepts.md` | The main lesson. Read it first. |
| `notebooks/01-first-model-regression.ipynb` | Full workflow once: explore → split → baseline → linear regression → MAE/RMSE/R² by hand |
| `notebooks/02-classification-and-metrics.ipynb` | Logistic regression; confusion matrix walk-through; precision, recall, F1; threshold; ROC-AUC; the accuracy trap |
| `notebooks/03-trees-forests-kmeans.ipynb` | Decision trees, random forests, feature importance; k-means and the elbow plot |
| `notebooks/04-overfitting-cv-pipelines.ipynb` | Overfitting plot; cross-validation; data-leakage demo; Pipeline + GridSearchCV; joblib save/load |
| `code/01_regression_diabetes.py` … `04_pipeline_gridsearch_save.py` | The same ideas as plain scripts, commented line by line |
| `images/` | Diagrams used in concepts and slides (`.mmd` files are editable Mermaid sources) |
| `slides/04-machine-learning.pptx` | 20-slide teaching deck with speaker notes |
| `pdf/04-machine-learning-handout.pdf` | Printable handout made from `concepts.md` |
| `excel/04-ml-metrics.xlsx` | Metrics cheat sheet, a live **confusion-matrix calculator**, practice scenarios |
| `exercises.md` | 12 exercises, easy → hard |
| `solutions/` | Worked solutions (`solutions.md` + runnable `solutions.py`) |
| `trainer-notes.md` | How to teach it: session plan, common mistakes, check questions |
| `resources.md` | The best external links, each with a reason |
| `build.py` | Regenerates images, notebooks, slides, PDF and Excel |

## Run the scripts locally

```bash
cd 04-machine-learning/code
python 01_regression_diabetes.py
python 02_classify_breast_cancer.py
python 03_trees_and_kmeans.py
python 04_pipeline_gridsearch_save.py
```

Tested with Python 3.13 and scikit-learn 1.9 (as of late 2026). Older scikit-learn versions (1.4+) should also work.

<!-- nav:start -->
---
[🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 03 Math for AI](../03-math-for-ai/README.md) · [05 Deep Learning ➡️](../05-deep-learning/README.md)
<!-- nav:end -->
