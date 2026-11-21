# Module 05 — Deep Learning with PyTorch (weeks 9–10)

Neural networks from first principles, built and trained with **PyTorch**. You will write the training loop that every modern AI model — up to and including large language models — is trained with.

## Goals — after this module you can

- Explain what a neuron, a layer, an activation function and a loss are, in plain English.
- Describe gradient descent and backpropagation with an analogy (no calculus required).
- Use PyTorch **tensors** (arrays that can live on a GPU) and **autograd** (automatic gradients).
- Define a model as an `nn.Module` and write the training loop **line by line**: forward → loss → `zero_grad` → `backward` → `step`.
- Train an **MLP** (fully connected network) and a small **CNN** (convolutional network) on handwritten digits.
- Read **loss curves** and recognise overfitting; fix it with **dropout**, **weight decay** and **early stopping**.
- Save and load weights with `state_dict`, and write device-agnostic code that runs on CPU or a Colab GPU.

## Prerequisites

- Module 04 (machine learning): train/validation/test split, overfitting, accuracy, confusion matrix.
- Module 03 (math intuition): slope, gradient descent idea.
- Module 01–02: Python classes (light), NumPy arrays, matplotlib.

## Time estimate

| Activity | Time |
|---|---|
| Read `concepts.md` | 2–3 hours |
| Work through the 4 notebooks | 4–5 hours |
| Exercises | 5–7 hours |
| Trainer: prepare one session | 3–4 hours after self-study |

Total for a learner: about 12–16 hours over two weeks.

## Which tool, and why

**Google Colab is the recommended tool for this module**, with local Jupyter/VS Code as an equally good option.

- Every notebook trains on scikit-learn's built-in 8×8 digits (`load_digits`), so there is **no download and no API key**, and each notebook finishes in well under 2 minutes on a laptop CPU.
- Every notebook starts with `device = "cuda" if torch.cuda.is_available() else "cpu"`, so the **same notebook runs unchanged on a Colab GPU**. To try it: *Runtime → Change runtime type → T4 GPU* (free GPU availability changes often; check Colab's FAQ). For these tiny models a GPU is not faster — but practising the device pattern now prepares you for modules 06, 07 and 13, where it matters.
- PyTorch is pre-installed on Colab. Locally: follow the install selector on the official PyTorch site (link in `resources.md`); the CPU build is enough for this module.

## File map

| Path | What it is |
|---|---|
| `concepts.md` | The main lesson. Read it first. |
| `notebooks/01-tensors-and-autograd.ipynb` | Tensors, shapes, devices, autograd; gradient descent by hand, then with `nn.Linear` + optimizer |
| `notebooks/02-mlp-on-digits.ipynb` | `nn.Module`, `DataLoader`, the full training loop, loss curves, confusion matrix, save/load weights |
| `notebooks/03-cnn-on-digits.ipynb` | Convolution and pooling by hand; a small CNN; shape tracing; CNN vs MLP; learned filters |
| `notebooks/04-overfitting-dropout-early-stopping.ipynb` | Forcing overfitting; dropout; early stopping with best-weight restore; weight decay; checkpoints |
| `code/01_tensors_autograd.py` … `04_early_stopping.py` | Plain-script versions, commented line by line |
| `images/` | Diagrams (`.mmd` = editable Mermaid sources) |
| `slides/05-deep-learning.pptx` | 20-slide deck with speaker notes |
| `pdf/05-deep-learning-handout.pdf` | Printable handout made from `concepts.md` |
| `excel/05-pytorch-cheatsheet.xlsx` | PyTorch cheat sheet, conv **output-shape calculator**, **parameter counter** (live formulas), experiment log |
| `exercises.md` | 12 exercises, easy → hard |
| `solutions/` | `solutions.md` (explanations) + `solutions.py` (runnable) |
| `trainer-notes.md` | Session plan, common mistakes, check questions |
| `resources.md` | Curated external links |
| `build.py` | Regenerates images, notebooks, slides, PDF and Excel |

## Run the scripts locally

```bash
cd 05-deep-learning/code
python 01_tensors_autograd.py
python 02_train_mlp_digits.py      # writes digit_mlp.pt next to the script
python 03_train_cnn_digits.py
python 04_early_stopping.py
```

Tested with Python 3.13 and PyTorch 2.15 (CPU build) as of late 2026. Any PyTorch 2.x should work.
