# Module 03 — Math for AI (intuition only)

**Week 6 of the course · about 6–8 hours of study for a learner · one 2-hour teaching session (or two shorter ones)**

## Goals
Understand, with pictures and NumPy rather than proofs:
- **vectors** and the **dot product**, and **cosine similarity** (the maths behind embeddings, semantic search and RAG)
- **matrices** as data tables and as transformations; **matrix multiplication** and the shape rule; one neural-network layer `X @ W + b`
- **probability**, **distributions**, **mean / variance / standard deviation**
- **softmax** and **temperature** (how a language model turns scores into word probabilities)
- **derivatives** as slope, **gradients**, **gradient descent**, the **learning rate**, and **loss functions** (MSE, cross-entropy)

## Prerequisites
- Module 02 (NumPy arrays: creating them, `shape`, `.sum()`, `.mean()`).
- School arithmetic. No calculus or linear algebra background is needed.
- Libraries: `numpy`, `matplotlib` (pre-installed in Colab). Everything runs offline, with no API keys.

## Which tool to use, and why
- **Google Colab** — easiest for students: click the badge at the top of each notebook. The notebooks need no data files.
- **Jupyter / VS Code** — good for trainers, because you can edit and rerun a single plot quickly while presenting.
- **Excel / LibreOffice / Google Sheets** — open `excel/math-in-a-spreadsheet.xlsx` to show the same maths as live formulas. Many students understand a formula better when they can click on the cell and see it.

## Suggested order
1. Read `concepts.md` §1–5 and run `notebooks/01-vectors-and-similarity.ipynb` and `notebooks/02-matrices.ipynb`.
2. Read §6–7 and run `notebooks/03-probability-and-softmax.ipynb`.
3. Read §8–10 and run `notebooks/04-derivatives-and-gradient-descent.ipynb`.
4. Play with every sheet of the spreadsheet; then do `exercises.md`.

## File map
| Path | What it is |
|---|---|
| `concepts.md` | The main lesson with analogies and 15+ pictures |
| `pdf/03-math-for-ai-handout.pdf` | `concepts.md` as a printable handout |
| `notebooks/01-vectors-and-similarity.ipynb` | Vectors as arrows, dot product, cosine similarity, toy embeddings, tiny semantic search |
| `notebooks/02-matrices.ipynb` | Matrices as tables, matrix × vector, matrix × matrix, shape rule, transformations, `X @ W + b` |
| `notebooks/03-probability-and-softmax.ipynb` | Simulation, law of large numbers, distributions, mean/variance, softmax, temperature, sampling, cross-entropy |
| `notebooks/04-derivatives-and-gradient-descent.ipynb` | Slopes, numerical derivatives, gradient descent frames, learning rates, 2-D descent, loss functions, fitting a line |
| `excel/math-in-a-spreadsheet.xlsx` | Live formulas: dot product & cosine, softmax with temperature, gradient descent (change the learning rate!), gradient descent fitting a line, matrix multiplication, mean & variance |
| `code/vectors_and_similarity.py` | Commented script: vectors, dot product, cosine, toy search |
| `code/matrices.py` | Commented script: matrix multiplication by hand vs `@`, one network layer |
| `code/probability_and_softmax.py` | Commented script: simulation, softmax, sampling, cross-entropy |
| `code/gradient_descent.py` | Commented script: gradient descent with saved frames, line fitting |
| `images/` | All diagrams; `images/gd_frames/` holds the 8 gradient-descent frames for flip-book slides |
| `slides/03-math-for-ai.pptx` | 19-slide teaching deck with speaker notes |
| `exercises.md` / `solutions/` | 12 exercises (easy → hard) with worked answers and runnable code |
| `trainer-notes.md` | Outcomes, timing table, common mistakes, check questions, adapting |
| `resources.md` | Curated links (videos and interactive explainers) |
| `build.py`, `figures.py`, `nb_cells.py` | Regenerate images, notebooks, slides, spreadsheet and PDF |

Scripts and notebooks save extra output (for example the frames they draw) into an `outputs/` folder, which git ignores.

## Rebuild everything
```bash
python 03-math-for-ai/build.py
python tools/check_module.py 03-math-for-ai --run
```
