"""
build.py for module 05-deep-learning.

Regenerates: images/ (Mermaid + matplotlib), notebooks/, slides/, excel/, pdf/.
Run from the repo root:  python 05-deep-learning/build.py
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

IMG = HERE / "images"
NB = HERE / "notebooks"
IMG.mkdir(exist_ok=True)
TEAL, NAVY, ORANGE = "#0F9D9A", "#1B263B", "#E07A1F"


# ---------------------------------------------------------------------------
# 1. Mermaid diagrams
# ---------------------------------------------------------------------------
def build_mermaid():
    mermaid("""
flowchart LR
    x1[x1 input] -->|w1| S((sum + bias))
    x2[x2 input] -->|w2| S
    x3[x3 input] -->|w3| S
    S --> A[activation e.g. ReLU]
    A --> O[output]
""", IMG / "neuron.png")

    mermaid("""
flowchart LR
    I[Input: 64 pixels] --> H1[Linear 64 to 64]
    H1 --> R1[ReLU]
    R1 --> H2[Linear 64 to 10]
    H2 --> L[10 logits]
    L --> SM[softmax]
    SM --> P[10 probabilities, pick the biggest]
""", IMG / "mlp.png")

    mermaid("""
flowchart LR
    X[Inputs] -->|forward pass| M[Model]
    M --> P[Predictions]
    P --> L[Loss vs true labels]
    L -.->|backward pass: gradients| M
    M -.-> W[Optimizer updates weights]
""", IMG / "forward-backward.png")

    mermaid("""
flowchart TD
    A[Take next batch xb, yb] --> B[logits = model xb]
    B --> C[loss = loss_fn logits, yb]
    C --> D[optimizer.zero_grad]
    D --> E[loss.backward]
    E --> F[optimizer.step]
    F -->|more batches| A
    F -->|end of epoch| G[Evaluate on validation set]
    G -->|next epoch| A
""", IMG / "training-loop.png")

    mermaid("""
flowchart LR
    I[Image 1x8x8] --> C1[Conv 3x3, 16 filters + ReLU: 16x8x8]
    C1 --> P1[MaxPool 2x2: 16x4x4]
    P1 --> C2[Conv 3x3, 32 filters + ReLU: 32x4x4]
    C2 --> P2[MaxPool 2x2: 32x2x2]
    P2 --> F[Flatten: 128]
    F --> D[Dropout]
    D --> O[Linear 128 to 10 logits]
""", IMG / "cnn.png")

    mermaid("""
flowchart TD
    A[Data to tensors, scale inputs] --> B[Split train / val / test]
    B --> C[DataLoader makes batches]
    C --> D[Define nn.Module]
    D --> E[Loss + optimizer]
    E --> F[Training loop]
    F --> G[Plot train and val loss]
    G -->|overfitting| H[Dropout, weight decay, early stopping]
    H --> F
    G -->|good| I[Test once in eval mode]
    I --> J[torch.save state_dict]
""", IMG / "dl-workflow.png")


# ---------------------------------------------------------------------------
# 2. matplotlib diagrams
# ---------------------------------------------------------------------------
def build_plots():
    # Activations
    x = np.linspace(-5, 5, 300)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.4))
    for ax, (name, yv) in zip(axes, [("ReLU: max(0, x)", np.maximum(0, x)),
                                      ("Sigmoid: squashes to 0..1", 1 / (1 + np.exp(-x))),
                                      ("Tanh: squashes to -1..1", np.tanh(x))]):
        ax.plot(x, yv, color=TEAL, lw=3)
        ax.axhline(0, color="grey", lw=0.8); ax.axvline(0, color="grey", lw=0.8)
        ax.set_title(name); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(IMG / "activations.png", dpi=130); plt.close(fig)

    # Gradient descent on a parabola
    f = lambda w: (w - 3) ** 2 + 1
    w, lr, path = -2.0, 0.15, []
    for _ in range(10):
        path.append(w); w = w - lr * 2 * (w - 3)
    ws = np.linspace(-3, 8, 200)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(ws, f(ws), color=NAVY, lw=2, label="loss for each weight value")
    ax.plot(path, [f(p) for p in path], "o--", color=ORANGE, label="gradient descent steps")
    ax.annotate("start", (path[0], f(path[0])), textcoords="offset points", xytext=(10, 5))
    ax.annotate("minimum", (3, 1), textcoords="offset points", xytext=(-20, -18))
    ax.set_xlabel("weight w"); ax.set_ylabel("loss")
    ax.set_title("Each step moves downhill: w = w - lr x slope"); ax.legend()
    fig.tight_layout(); fig.savefig(IMG / "gradient-descent.png", dpi=130); plt.close(fig)

    # Loss curves: healthy vs overfitting (illustrative shapes)
    ep = np.arange(1, 61)
    tr = 2.2 * np.exp(-ep / 8) + 0.05
    va_good = 2.2 * np.exp(-ep / 8) + 0.12
    va_bad = 2.2 * np.exp(-ep / 8) + 0.15 + 0.0009 * np.maximum(0, ep - 15) ** 1.6
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    axes[0].plot(ep, tr, color=NAVY, lw=2, label="training loss")
    axes[0].plot(ep, va_good, color=TEAL, lw=2, label="validation loss")
    axes[0].set_title("Healthy: both fall and level off")
    axes[1].plot(ep, tr, color=NAVY, lw=2, label="training loss")
    axes[1].plot(ep, va_bad, color=ORANGE, lw=2, label="validation loss")
    best = int(np.argmin(va_bad))
    axes[1].axvline(ep[best], color="grey", ls="--")
    axes[1].annotate("early stopping\nwould stop here", (ep[best], va_bad[best]), xytext=(ep[best] + 4, 1.2),
                     arrowprops=dict(arrowstyle="->"))
    axes[1].set_title("Overfitting: validation loss turns up")
    for ax in axes:
        ax.set_xlabel("epoch"); ax.legend(); ax.grid(alpha=0.3)
    axes[0].set_ylabel("loss")
    fig.tight_layout(); fig.savefig(IMG / "loss-curves.png", dpi=130); plt.close(fig)

    # Convolution illustration on a real digit
    from sklearn.datasets import load_digits
    d = load_digits()
    img = d.images[0] / 16.0       # a zero
    kernel = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=float)   # vertical-edge detector
    padded = np.pad(img, 1)
    fmap = np.zeros_like(img)
    for i in range(8):
        for j in range(8):
            fmap[i, j] = (padded[i:i + 3, j:j + 3] * kernel).sum()
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.4))
    axes[0].imshow(img, cmap="gray_r"); axes[0].set_title("Input: 8x8 digit")
    axes[0].add_patch(plt.Rectangle((1.5, 1.5), 3, 3, fill=False, ec=ORANGE, lw=3))
    axes[1].imshow(kernel, cmap="coolwarm", vmin=-1, vmax=1); axes[1].set_title("3x3 filter (vertical edges)")
    for (i, j), v in np.ndenumerate(kernel):
        axes[1].text(j, i, f"{v:+.0f}", ha="center", va="center", fontsize=14)
    axes[2].imshow(fmap, cmap="coolwarm"); axes[2].set_title("Feature map: strong where edges are")
    for ax in axes:
        ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout(pad=2.0); fig.savefig(IMG / "convolution.png", dpi=130, bbox_inches="tight"); plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Notebooks
# ---------------------------------------------------------------------------
SETUP_MD = """## Setup: device and reproducibility

- `device` is `"cuda"` if a GPU is available (e.g. Colab with a T4 GPU), otherwise `"cpu"`. All later code uses this variable, so the same notebook runs anywhere.
- `torch.manual_seed(0)` fixes the random starting weights so you get the same results each run.
- On CPU we use one thread: these models are tiny, and many threads fighting over tiny jobs is slower (especially on shared or busy machines)."""

SETUP_CODE = """import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cpu":
    torch.set_num_threads(1)
torch.manual_seed(0)
print("PyTorch", torch.__version__, "| running on:", device)"""

DATA_MD = """## Load the digits and make tensors

`load_digits` ships inside scikit-learn: 1,797 greyscale images of handwritten digits, each 8×8 pixels with values 0–16.

1. Divide by 16 so pixels are between 0 and 1 (neural networks train best on small, similar-sized inputs).
2. Split into **train** (60%), **validation** (20%, for watching overfitting) and **test** (20%, locked away until the end).
3. Convert to tensors: inputs as `float32`, labels as `long` (whole numbers), which `CrossEntropyLoss` requires."""

DATA_CODE = """import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

digits = load_digits()
X = digits.data.astype("float32") / 16.0          # shape (1797, 64), values 0..1
y = digits.target                                 # shape (1797,), values 0..9

X_trainval, X_test, y_trainval, y_test = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_trainval, y_trainval, test_size=0.25,
                                                  random_state=0, stratify=y_trainval)

X_train_t, X_val_t, X_test_t = (torch.tensor(a) for a in (X_train, X_val, X_test))
y_train_t, y_val_t, y_test_t = (torch.tensor(a, dtype=torch.long) for a in (y_train, y_val, y_test))
print("train", tuple(X_train_t.shape), "val", tuple(X_val_t.shape), "test", tuple(X_test_t.shape))"""

NB1 = [
("md", """# 05-01 · Tensors and autograd: PyTorch from zero

**Goal:** learn the two building blocks of PyTorch.
1. **Tensors** — PyTorch's arrays of numbers.
2. **Autograd** — PyTorch's automatic gradient calculator, the engine behind all neural-network training.

We finish by training a one-neuron "network" with gradient descent, first by hand and then the PyTorch way. Runs in seconds on CPU."""),
("md", SETUP_MD),
("code", SETUP_CODE),
("md", """## Part 1 · Tensors

A **tensor** is a grid of numbers with a **shape** (its size in each direction) and a **dtype** (the number type). It is like a NumPy array, but it can live on a GPU and can track gradients."""),
("code", """scalar = torch.tensor(3.5)                       # 0-D: a single number
vector = torch.tensor([1.0, 2.0, 3.0])           # 1-D: a list
matrix = torch.tensor([[1.0, 2.0], [3.0, 4.0]])  # 2-D: a table
for name, t in [("scalar", scalar), ("vector", vector), ("matrix", matrix)]:
    print(f"{name:6s} shape={tuple(t.shape)}  dims={t.ndim}  dtype={t.dtype}")"""),
("md", """Ways to create tensors you will see constantly. `torch.rand` gives random numbers between 0 and 1; `torch.randn` gives random numbers from a bell curve centred on 0."""),
("code", """print(torch.zeros(2, 3))
print(torch.ones(2, 3))
print(torch.arange(6))           # 0,1,2,3,4,5
print(torch.rand(2, 2))
print(torch.randn(2, 2))"""),
("md", """### Maths on tensors

Operations work **element by element** (each position separately), just like NumPy. `@` is **matrix multiplication** — the core operation inside every neural-network layer."""),
("code", """a = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
b = torch.tensor([[10.0, 20.0], [30.0, 40.0]])
print("a + b =\\n", a + b)
print("a * b (element-wise) =\\n", a * b)
print("a @ b (matrix multiply) =\\n", a @ b)
print("sum:", a.sum().item(), " mean:", a.mean().item(), " max:", a.max().item())"""),
("md", """`.item()` turns a one-number tensor into a normal Python number.

### Reshaping

`reshape` (or `view`) changes the shape without changing the numbers. We will do this to turn a flat list of 64 pixels into an 8×8 image for the CNN. `-1` means "work this size out for me"."""),
("code", """t = torch.arange(12)
print(t.reshape(3, 4))
print(t.reshape(2, -1).shape)        # -1 -> PyTorch works out 6
img_batch = torch.rand(5, 64).reshape(-1, 1, 8, 8)
print("batch of images:", tuple(img_batch.shape), "-> (batch, channels, height, width)")"""),
("md", """### dtype and the NumPy bridge

Neural-network inputs are usually `float32`. Class labels must be `long` (64-bit whole numbers). `torch.from_numpy` and `.numpy()` convert between PyTorch and NumPy."""),
("code", """import numpy as np
arr = np.array([1, 2, 3])
t = torch.from_numpy(arr)
print(t, t.dtype)
print(t.float(), t.float().dtype)
print(t.long().dtype)
print("back to numpy:", t.float().numpy())"""),
("md", """### Devices

Every tensor lives on a **device**. `.to(device)` moves it. Tensors that are combined must be on the same device; mixing CPU and GPU tensors raises an error. On Colab with a GPU this prints `cuda:0`."""),
("code", """x = torch.rand(3).to(device)
print("x lives on:", x.device)
print("back on cpu for numpy:", x.cpu().numpy())"""),
("md", """## Part 2 · Autograd: automatic gradients

A **gradient** tells us how much a result changes when we nudge an input. If we create a tensor with `requires_grad=True`, PyTorch records every operation on it. Calling `.backward()` on the final result computes the gradient and stores it in `.grad`.

Example: `loss = (w − 5)²`. By hand, the slope is `2 × (w − 5)`. At `w = 3` that is `−4`."""),
("code", """w = torch.tensor(3.0, requires_grad=True)
loss = (w - 5) ** 2
loss.backward()
print("loss:", loss.item())
print("gradient d(loss)/dw:", w.grad.item(), " (by hand: 2*(3-5) = -4)")"""),
("md", """The gradient is negative, which means "increase `w` to make the loss smaller". That is exactly the information gradient descent needs.

Autograd works through any chain of operations, however long. Here `y` depends on `a` and `b` through several steps:"""),
("code", """a = torch.tensor(2.0, requires_grad=True)
b = torch.tensor(4.0, requires_grad=True)
y = a * b + a ** 3       # dy/da = b + 3a^2 = 4 + 12 = 16 ; dy/db = a = 2
y.backward()
print("dy/da =", a.grad.item(), "  dy/db =", b.grad.item())"""),
("md", """### Gradients add up — the reason for `zero_grad()`

If you call `.backward()` twice without resetting, PyTorch **adds** the new gradient to the old one. In a training loop this would be a bug, which is why every loop calls `optimizer.zero_grad()`."""),
("code", """w = torch.tensor(3.0, requires_grad=True)
for i in range(3):
    loss = (w - 5) ** 2
    loss.backward()
    print(f"after backward #{i+1}: w.grad = {w.grad.item()}")
w.grad.zero_()
print("after zero_():", w.grad.item())"""),
("md", """## Part 3 · Gradient descent by hand

Let us fit a straight line `y = w·x + b` to noisy data whose true rule is `y = 2x + 1`. We start with random `w` and `b`, and repeat:

1. **forward:** predict and compute the MSE loss,
2. **backward:** get gradients,
3. **update:** `w = w − lr × w.grad` (inside `torch.no_grad()` so the update itself is not recorded),
4. reset the gradients."""),
("code", """torch.manual_seed(0)
x = torch.linspace(-1, 1, 50)
y_true = 2 * x + 1 + 0.2 * torch.randn(50)

w = torch.randn(1, requires_grad=True)
b = torch.randn(1, requires_grad=True)
lr = 0.1
history = []
for step in range(100):
    pred = w * x + b                          # forward
    loss = ((pred - y_true) ** 2).mean()      # MSE loss
    loss.backward()                           # gradients for w and b
    with torch.no_grad():                     # update without recording
        w -= lr * w.grad
        b -= lr * b.grad
    w.grad.zero_(); b.grad.zero_()            # reset for next step
    history.append(loss.item())
    if step % 20 == 0:
        print(f"step {step:3d}  loss={loss.item():.4f}  w={w.item():.3f}  b={b.item():.3f}")
print(f"final: w={w.item():.3f} (true 2), b={b.item():.3f} (true 1)")"""),
("md", """The loss falls quickly and `w`, `b` approach the true values 2 and 1. Here is the loss curve:"""),
("code", """import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
axes[0].plot(history); axes[0].set_xlabel("step"); axes[0].set_ylabel("MSE loss"); axes[0].set_title("Loss goes down")
axes[1].scatter(x, y_true, s=12, label="data")
axes[1].plot(x, (w * x + b).detach(), color="red", label="learned line")
axes[1].legend(); axes[1].set_title("The fitted line")
plt.show()"""),
("md", """`.detach()` gives a copy of a tensor that is no longer tracked by autograd — needed before plotting or converting to NumPy.

## Part 4 · The same thing, the PyTorch way

In real code we do not write the update by hand. We use:
- `nn.Linear(1, 1)` — a layer holding `w` and `b` for us,
- `nn.MSELoss()` — the loss,
- `torch.optim.SGD` — an **optimizer** that performs `w = w − lr × grad` for every weight.

The loop now has the exact shape of every training loop you will ever write: forward → loss → zero_grad → backward → step."""),
("code", """import torch.nn as nn
torch.manual_seed(0)
model = nn.Linear(1, 1).to(device)
loss_fn = nn.MSELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
X_col = x.reshape(-1, 1).to(device)          # nn.Linear expects (rows, features)
Y_col = y_true.reshape(-1, 1).to(device)

for step in range(100):
    pred = model(X_col)                       # forward
    loss = loss_fn(pred, Y_col)               # how wrong?
    optimizer.zero_grad()                     # clear old gradients
    loss.backward()                           # compute new gradients
    optimizer.step()                          # update weights
print("learned weight:", model.weight.item(), " bias:", model.bias.item())"""),
("md", """## Recap

- Tensors: shape, dtype, device; `@` for matrix multiply; `reshape`; `.item()`, `.numpy()`, `.detach()`, `.cpu()`.
- Autograd: `requires_grad=True` → `.backward()` → `.grad`.
- Gradients accumulate → always zero them.
- Training = forward → loss → zero_grad → backward → step, repeated.

**Try it:** set `lr = 1.5` in Part 3. What happens to the loss? (Too big a step overshoots the valley.)"""),
]

NB2 = [
("md", """# 05-02 · Your first neural network: an MLP on handwritten digits

**Goal:** build, train and evaluate a **multi-layer perceptron (MLP)** — a stack of fully connected layers — on 8×8 handwritten digits. Along the way we write the full training loop, plot **loss curves**, and **save and load** the trained weights.

Takes well under a minute on a laptop CPU. Works unchanged on a Colab GPU."""),
("md", SETUP_MD),
("code", SETUP_CODE),
("md", DATA_MD),
("code", DATA_CODE),
("md", """## Look at some digits

Each row of `X` is 64 numbers; reshaped to 8×8 it is a tiny picture. These are low-resolution — even humans find some hard."""),
("code", """import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 8, figsize=(10, 1.8))
for ax, img, label in zip(axes, X_train[:8], y_train[:8]):
    ax.imshow(img.reshape(8, 8), cmap="gray_r"); ax.set_title(str(label)); ax.axis("off")
plt.show()"""),
("md", """## Batches with DataLoader

A `TensorDataset` pairs each input with its label. A `DataLoader` serves them in **batches** (groups of 64 here) and shuffles the order every **epoch** (full pass over the data). Shuffling stops the network from learning anything about the order of examples."""),
("code", """from torch.utils.data import TensorDataset, DataLoader
train_loader = DataLoader(TensorDataset(X_train_t, y_train_t), batch_size=64, shuffle=True)
xb, yb = next(iter(train_loader))
print("one batch:", tuple(xb.shape), tuple(yb.shape), "| batches per epoch:", len(train_loader))"""),
("md", """## Define the model with nn.Module

- `__init__` creates the layers (where the weights live).
- `forward` says how data flows: 64 pixels → 128 hidden neurons → ReLU → 10 **logits** (raw scores, one per digit).

No softmax at the end: `CrossEntropyLoss` applies it internally."""),
("code", """import torch.nn as nn

class DigitMLP(nn.Module):
    def __init__(self, hidden=128):
        super().__init__()
        self.layer1 = nn.Linear(64, hidden)
        self.layer2 = nn.Linear(hidden, 10)

    def forward(self, x):
        x = torch.relu(self.layer1(x))
        return self.layer2(x)

model = DigitMLP().to(device)
print(model)
n_params = sum(p.numel() for p in model.parameters())
print("trainable parameters:", n_params, " (= 64*128 + 128 + 128*10 + 10)")"""),
("md", """Before training, the weights are random, so predictions are random guesses (about 10% accuracy). Let us confirm, and look at what the untrained model outputs for one image."""),
("code", """with torch.no_grad():
    logits = model(X_val_t[:1].to(device))
print("logits:", logits.cpu().numpy().round(2))
print("softmax probabilities:", torch.softmax(logits, dim=1).cpu().numpy().round(2))

def accuracy(model, X, y):
    model.eval()
    with torch.no_grad():
        preds = model(X.to(device)).argmax(dim=1)
    return (preds == y.to(device)).float().mean().item()

print("untrained validation accuracy:", round(accuracy(model, X_val_t, y_val_t), 3))"""),
("md", """## The training loop, line by line

Read every comment. This exact structure trains every PyTorch model, up to and including LLMs.

Each epoch we also compute the **validation loss** in `eval()` mode under `torch.no_grad()` (no gradient bookkeeping, so it is faster and uses less memory). We keep a history to plot."""),
("code", """loss_fn = nn.CrossEntropyLoss()                               # classification loss (takes logits)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)     # Adam: a good default optimizer
history = {"train_loss": [], "val_loss": [], "val_acc": []}

for epoch in range(40):                                       # 40 passes over the training data
    model.train()                                             # training mode
    running = 0.0
    for xb, yb in train_loader:                               # one batch at a time
        xb, yb = xb.to(device), yb.to(device)                 # same device as the model
        logits = model(xb)                                    # 1. forward pass
        loss = loss_fn(logits, yb)                            # 2. how wrong?
        optimizer.zero_grad()                                 # 3. clear old gradients
        loss.backward()                                       # 4. backprop
        optimizer.step()                                      # 5. update weights
        running += loss.item() * len(xb)                      # add up loss for the epoch average
    history["train_loss"].append(running / len(X_train_t))

    model.eval()                                              # evaluation mode
    with torch.no_grad():                                     # no gradients needed
        val_logits = model(X_val_t.to(device))
        history["val_loss"].append(loss_fn(val_logits, y_val_t.to(device)).item())
        history["val_acc"].append((val_logits.argmax(1) == y_val_t.to(device)).float().mean().item())
    if epoch % 5 == 0 or epoch == 39:
        print(f"epoch {epoch:2d}  train_loss={history['train_loss'][-1]:.3f}  "
              f"val_loss={history['val_loss'][-1]:.3f}  val_acc={history['val_acc'][-1]:.3f}")"""),
("md", """## Plot the loss curves

Both losses should fall and then level off. If validation loss started rising while training loss kept falling, that would be **overfitting** (notebook 04 deals with it)."""),
("code", """fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
axes[0].plot(history["train_loss"], label="train"); axes[0].plot(history["val_loss"], label="validation")
axes[0].set_xlabel("epoch"); axes[0].set_ylabel("cross-entropy loss"); axes[0].legend(); axes[0].set_title("Loss")
axes[1].plot(history["val_acc"], color="green"); axes[1].set_xlabel("epoch"); axes[1].set_title("Validation accuracy")
plt.show()"""),
("md", """## Final test — once

Only now do we use the locked-away test set. We also print a **confusion matrix** (from module 04): rows are true digits, columns predicted digits, the diagonal holds the correct answers."""),
("code", """from sklearn.metrics import confusion_matrix
print("test accuracy:", round(accuracy(model, X_test_t, y_test_t), 3))
model.eval()
with torch.no_grad():
    test_preds = model(X_test_t.to(device)).argmax(1).cpu().numpy()
print(confusion_matrix(y_test, test_preds))"""),
("md", """Let us look at some mistakes. Often they are digits a human would also hesitate over."""),
("code", """wrong = np.where(test_preds != y_test)[0][:8]
fig, axes = plt.subplots(1, max(len(wrong), 1), figsize=(10, 1.9))
axes = np.atleast_1d(axes)
for ax, i in zip(axes, wrong):
    ax.imshow(X_test[i].reshape(8, 8), cmap="gray_r"); ax.axis("off")
    ax.set_title(f"true {y_test[i]}\\npred {test_preds[i]}", fontsize=9)
plt.show()"""),
("md", """## Save and load the weights

`model.state_dict()` is a dictionary of all learned weights. We save it with `torch.save`, then build a **fresh** model from the class and load the weights into it. `map_location="cpu"` makes GPU-trained weights load on any machine.

We save into a temporary folder so the course repository stays clean; in your own project choose a real path like `models/digit_mlp.pt`."""),
("code", """import os, tempfile
print("weights stored:", {k: tuple(v.shape) for k, v in model.state_dict().items()})

path = os.path.join(tempfile.gettempdir(), "digit_mlp.pt")
torch.save(model.state_dict(), path)
print("saved", path, round(os.path.getsize(path) / 1024, 1), "KB")

fresh = DigitMLP().to(device)                                  # random weights
print("fresh model accuracy:", round(accuracy(fresh, X_test_t, y_test_t), 3))
fresh.load_state_dict(torch.load(path, map_location=device))   # trained weights
print("after loading:      ", round(accuracy(fresh, X_test_t, y_test_t), 3))"""),
("md", """## Recap

- `nn.Module` with `__init__` (layers) and `forward` (data flow).
- `DataLoader` gives shuffled batches.
- Loop: forward → loss → `zero_grad` → `backward` → `step`; validate with `eval()` + `no_grad()`.
- Plot train vs validation loss every time you train.
- `torch.save(model.state_dict())` / `load_state_dict(torch.load(...))`.

**Try it:** change `hidden=128` to `hidden=16` and to `hidden=512`. How do accuracy and parameter count change? Try `lr=1e-1` and `lr=1e-5`."""),
]

NB3 = [
("md", """# 05-03 · Convolutional neural network (CNN) on 8×8 digits

**Goal:** see what a **convolution** does to an image, understand **pooling**, then build and train a small CNN and compare it with the MLP from notebook 02.

A **CNN** slides small learnable pattern detectors (**filters**) across the image, so it understands that nearby pixels belong together. Takes under a minute on CPU."""),
("md", SETUP_MD),
("code", SETUP_CODE),
("md", DATA_MD),
("code", DATA_CODE),
("md", """## Images need a channel dimension

Convolution layers expect input shaped **(batch, channels, height, width)**. Our digits are greyscale, so there is 1 channel. We reshape each 64-number row into 1×8×8."""),
("code", """to_img = lambda t: t.reshape(-1, 1, 8, 8)
Xtr_img, Xval_img, Xte_img = to_img(X_train_t), to_img(X_val_t), to_img(X_test_t)
print("train images:", tuple(Xtr_img.shape))"""),
("md", """## Part 1 · Convolution by hand

Before letting a network learn its own filters, we apply two **hand-made** 3×3 filters to one digit using `torch.nn.functional.conv2d`:
- a **vertical-edge** filter (left column +1, right column −1),
- a **horizontal-edge** filter (top row +1, bottom row −1).

The output, a **feature map**, is large (bright or dark) wherever the filter's pattern appears. `padding=1` adds a zero border so the output stays 8×8."""),
("code", """import torch.nn.functional as F
import matplotlib.pyplot as plt

vertical = torch.tensor([[1., 0., -1.], [1., 0., -1.], [1., 0., -1.]])
horizontal = vertical.T
filters = torch.stack([vertical, horizontal]).unsqueeze(1)    # shape (2 filters, 1 channel, 3, 3)

img = Xtr_img[:1]                                             # one image, shape (1, 1, 8, 8)
fmap = F.conv2d(img, filters, padding=1)                      # shape (1, 2, 8, 8)
print("input", tuple(img.shape), "-> feature maps", tuple(fmap.shape))

fig, axes = plt.subplots(1, 3, figsize=(9, 3))
axes[0].imshow(img[0, 0], cmap="gray_r"); axes[0].set_title(f"digit {y_train[0]}")
axes[1].imshow(fmap[0, 0], cmap="coolwarm"); axes[1].set_title("vertical edges")
axes[2].imshow(fmap[0, 1], cmap="coolwarm"); axes[2].set_title("horizontal edges")
for ax in axes: ax.axis("off")
plt.show()"""),
("md", """## Part 2 · Max pooling

**Max pooling** with a 2×2 window keeps the largest value in each 2×2 block. Height and width halve: 8×8 → 4×4. The network becomes cheaper and cares less about tiny shifts."""),
("code", """pooled = F.max_pool2d(fmap, kernel_size=2)
print("before pooling", tuple(fmap.shape), "-> after", tuple(pooled.shape))
small = torch.tensor([[1., 3., 2., 0.], [4., 2., 1., 1.], [0., 1., 5., 6.], [2., 2., 7., 1.]])
print("4x4 example:\\n", small)
print("after 2x2 max pool:\\n", F.max_pool2d(small.reshape(1, 1, 4, 4), 2)[0, 0])"""),
("md", """## Part 3 · Build the CNN

Architecture (shapes for one image):

| Layer | Output shape |
|---|---|
| input | 1×8×8 |
| `Conv2d(1, 16, 3, padding=1)` + ReLU | 16×8×8 |
| `MaxPool2d(2)` | 16×4×4 |
| `Conv2d(16, 32, 3, padding=1)` + ReLU | 32×4×4 |
| `MaxPool2d(2)` | 32×2×2 |
| flatten | 128 |
| `Dropout(0.25)` then `Linear(128, 10)` | 10 logits |

**Dropout** randomly switches off 25% of the values during training to reduce overfitting (more in notebook 04)."""),
("code", """import torch.nn as nn

class DigitCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2)
        self.dropout = nn.Dropout(0.25)
        self.fc = nn.Linear(32 * 2 * 2, 10)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))   # (N, 16, 4, 4)
        x = self.pool(torch.relu(self.conv2(x)))   # (N, 32, 2, 2)
        x = x.flatten(start_dim=1)                 # (N, 128)
        return self.fc(self.dropout(x))            # (N, 10)

cnn = DigitCNN().to(device)
print(cnn)
print("parameters:", sum(p.numel() for p in cnn.parameters()))"""),
("md", """A habit that saves hours: push a fake batch through the layers and print the shape after each one. Shape mismatches are the most common CNN error."""),
("code", """x = torch.zeros(4, 1, 8, 8, device=device)
print("input      ", tuple(x.shape))
x = cnn.pool(torch.relu(cnn.conv1(x))); print("after block1", tuple(x.shape))
x = cnn.pool(torch.relu(cnn.conv2(x))); print("after block2", tuple(x.shape))
x = x.flatten(1);                       print("flattened   ", tuple(x.shape))
print("logits      ", tuple(cnn.fc(x).shape))"""),
("md", """## Part 4 · A reusable training function

Same loop as notebook 02, wrapped in a function so we can train both an MLP and the CNN with identical settings for a fair comparison."""),
("code", """from torch.utils.data import TensorDataset, DataLoader

def train_model(model, X_tr, y_tr, X_va, y_va, epochs=30, lr=1e-3, batch_size=64):
    loader = DataLoader(TensorDataset(X_tr, y_tr), batch_size=batch_size, shuffle=True)
    loss_fn = nn.CrossEntropyLoss()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    hist = {"train_loss": [], "val_loss": [], "val_acc": []}
    for epoch in range(epochs):
        model.train(); total = 0.0
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            loss = loss_fn(model(xb), yb)
            opt.zero_grad(); loss.backward(); opt.step()
            total += loss.item() * len(xb)
        hist["train_loss"].append(total / len(X_tr))
        model.eval()
        with torch.no_grad():
            out = model(X_va.to(device))
            hist["val_loss"].append(loss_fn(out, y_va.to(device)).item())
            hist["val_acc"].append((out.argmax(1) == y_va.to(device)).float().mean().item())
    return hist

def test_accuracy(model, X, y):
    model.eval()
    with torch.no_grad():
        return (model(X.to(device)).argmax(1) == y.to(device)).float().mean().item()"""),
("md", """## Part 5 · Train the MLP and the CNN

We use the same number of epochs and learning rate for both. The MLP gets flat inputs; the CNN gets 1×8×8 images."""),
("code", """import time
torch.manual_seed(0)
mlp = nn.Sequential(nn.Linear(64, 128), nn.ReLU(), nn.Linear(128, 10)).to(device)
t0 = time.time(); mlp_hist = train_model(mlp, X_train_t, y_train_t, X_val_t, y_val_t); t_mlp = time.time() - t0

torch.manual_seed(0)
cnn = DigitCNN().to(device)
t0 = time.time(); cnn_hist = train_model(cnn, Xtr_img, y_train_t, Xval_img, y_val_t); t_cnn = time.time() - t0

print(f"MLP: test accuracy {test_accuracy(mlp, X_test_t, y_test_t):.3f}  "
      f"params {sum(p.numel() for p in mlp.parameters())}  time {t_mlp:.1f}s")
print(f"CNN: test accuracy {test_accuracy(cnn, Xte_img, y_test_t):.3f}  "
      f"params {sum(p.numel() for p in cnn.parameters())}  time {t_cnn:.1f}s")"""),
("md", """Plot the validation curves side by side. On these tiny 8×8 images the difference is modest; on real photos (say 224×224 colour) CNNs win by a huge margin, because their filters re-use the same weights everywhere in the image."""),
("code", """fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
axes[0].plot(mlp_hist["val_loss"], label="MLP"); axes[0].plot(cnn_hist["val_loss"], label="CNN")
axes[0].set_title("validation loss"); axes[0].set_xlabel("epoch"); axes[0].legend()
axes[1].plot(mlp_hist["val_acc"], label="MLP"); axes[1].plot(cnn_hist["val_acc"], label="CNN")
axes[1].set_title("validation accuracy"); axes[1].set_xlabel("epoch"); axes[1].legend()
plt.show()"""),
("md", """## Part 6 · What did the CNN learn?

The first conv layer has 16 learned 3×3 filters. They start random; after training many look like small edge or corner detectors. Below: the filters, then the 16 feature maps they produce for one test digit."""),
("code", """w = cnn.conv1.weight.detach().cpu()           # (16, 1, 3, 3)
fig, axes = plt.subplots(2, 16, figsize=(14, 2.2))
with torch.no_grad():
    maps = torch.relu(cnn.conv1(Xte_img[:1].to(device))).cpu()[0]   # (16, 8, 8)
for i in range(16):
    axes[0, i].imshow(w[i, 0], cmap="coolwarm"); axes[0, i].axis("off")
    axes[1, i].imshow(maps[i], cmap="viridis"); axes[1, i].axis("off")
axes[0, 0].set_title("filters", loc="left", fontsize=9)
axes[1, 0].set_title(f"maps for a {y_test[0]}", loc="left", fontsize=9)
plt.show()"""),
("md", """## Recap

- Convolution slides a small filter over the image → feature map; filters are **learned**.
- Pooling shrinks feature maps (8×8 → 4×4).
- Shapes are (batch, channels, height, width); print shapes layer by layer when building a CNN.
- The training loop is unchanged — only the model changed.

**Try it:** add a third conv layer, or change 16/32 filters to 8/16. How do parameters and accuracy change?"""),
]

NB4 = [
("md", """# 05-04 · Overfitting, dropout and early stopping

**Goal:** make a network **overfit** on purpose, see it in the loss curves, then fix it with two tools:
- **dropout** — randomly switching off neurons during training,
- **early stopping** — stopping when validation loss stops improving and keeping the best weights.

To make overfitting obvious we deliberately train a large MLP on only **200** training images for many epochs. Runs in under a minute on CPU."""),
("md", SETUP_MD),
("code", SETUP_CODE),
("md", DATA_MD),
("code", DATA_CODE),
("md", """## A small training set and a big model

We keep only the first 200 training images. With ~100,000 parameters and 200 examples, the network can memorise every training image — a recipe for overfitting."""),
("code", """import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import matplotlib.pyplot as plt
import copy

X_small, y_small = X_train_t[:200], y_train_t[:200]

def make_mlp(dropout=0.0):
    return nn.Sequential(
        nn.Linear(64, 256), nn.ReLU(), nn.Dropout(dropout),
        nn.Linear(256, 256), nn.ReLU(), nn.Dropout(dropout),
        nn.Linear(256, 10),
    )
print("parameters:", sum(p.numel() for p in make_mlp().parameters()), "for", len(X_small), "training images")"""),
("md", """## A training function that records both losses

Same loop as before. It optionally does **early stopping**: if validation loss has not improved for `patience` epochs, stop, and restore the best weights we saw. `copy.deepcopy(model.state_dict())` takes a snapshot of the weights."""),
("code", """def train(model, epochs=150, lr=1e-3, patience=None, weight_decay=0.0):
    loader = DataLoader(TensorDataset(X_small, y_small), batch_size=32, shuffle=True)
    loss_fn = nn.CrossEntropyLoss()
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    hist = {"train": [], "val": []}
    best_val, best_state, best_epoch, waited = float("inf"), None, 0, 0
    for epoch in range(epochs):
        model.train(); total = 0.0
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            loss = loss_fn(model(xb), yb)
            opt.zero_grad(); loss.backward(); opt.step()
            total += loss.item() * len(xb)
        hist["train"].append(total / len(X_small))
        model.eval()
        with torch.no_grad():
            val_loss = loss_fn(model(X_val_t.to(device)), y_val_t.to(device)).item()
        hist["val"].append(val_loss)
        if val_loss < best_val:                                   # new best: remember it
            best_val, best_epoch, waited = val_loss, epoch, 0
            best_state = copy.deepcopy(model.state_dict())
        else:
            waited += 1
            if patience is not None and waited >= patience:       # no improvement for a while: stop
                print(f"early stop at epoch {epoch}, best epoch was {best_epoch}")
                break
    if patience is not None:
        model.load_state_dict(best_state)                         # roll back to the best weights
    return hist, best_epoch

def test_acc(model):
    model.eval()
    with torch.no_grad():
        return (model(X_test_t.to(device)).argmax(1) == y_test_t.to(device)).float().mean().item()"""),
("md", """## Experiment 1 · No protection

Watch the two curves: training loss goes almost to zero (memorised), while validation loss bottoms out early and then **climbs**."""),
("code", """torch.manual_seed(0)
plain = make_mlp(dropout=0.0).to(device)
plain_hist, plain_best = train(plain)
print(f"lowest val loss at epoch {plain_best}; final train loss {plain_hist['train'][-1]:.4f}, "
      f"final val loss {plain_hist['val'][-1]:.3f}")
print("test accuracy (weights from the last epoch):", round(test_acc(plain), 3))

plt.plot(plain_hist["train"], label="train"); plt.plot(plain_hist["val"], label="validation")
plt.axvline(plain_best, color="grey", ls="--", label="best validation epoch")
plt.xlabel("epoch"); plt.ylabel("loss"); plt.title("No dropout: overfitting"); plt.legend(); plt.show()"""),
("md", """## Experiment 2 · Dropout

Same model with `Dropout(0.5)` after each hidden layer: half of the hidden values are switched off at random on every batch during training. Remember: dropout is only active in `model.train()` mode; `model.eval()` turns it off."""),
("code", """torch.manual_seed(0)
drop = make_mlp(dropout=0.5).to(device)
drop_hist, drop_best = train(drop)
print(f"final val loss {drop_hist['val'][-1]:.3f} (no dropout: {plain_hist['val'][-1]:.3f})")
print("test accuracy:", round(test_acc(drop), 3))"""),
("md", """Dropout in action: in training mode, the same input gives **different** outputs each time (different neurons are dropped). In eval mode, outputs are stable."""),
("code", """x1 = X_val_t[:1].to(device)
drop.train()
print("train mode:", [drop(x1).argmax(1).item() for _ in range(5)], [round(drop(x1).max().item(), 2) for _ in range(5)])
drop.eval()
print("eval mode: ", [drop(x1).argmax(1).item() for _ in range(5)], [round(drop(x1).max().item(), 2) for _ in range(5)])"""),
("md", """## Experiment 3 · Early stopping (+ a little weight decay)

No dropout this time. Instead we stop when validation loss has not improved for 10 epochs (`patience=10`), and roll back to the best weights. We also add `weight_decay=0.01` — a penalty that keeps weights small."""),
("code", """torch.manual_seed(0)
early = make_mlp(dropout=0.0).to(device)
early_hist, early_best = train(early, patience=10, weight_decay=0.01)
print("test accuracy (best weights restored):", round(test_acc(early), 3))"""),
("md", """## Compare all three"""),
("code", """fig, axes = plt.subplots(1, 3, figsize=(14, 3.8), sharey=True)
for ax, (name, h, b) in zip(axes, [("no protection", plain_hist, plain_best),
                                   ("dropout 0.5", drop_hist, drop_best),
                                   ("early stopping", early_hist, early_best)]):
    ax.plot(h["train"], label="train"); ax.plot(h["val"], label="validation")
    ax.axvline(b, color="grey", ls="--"); ax.set_title(name); ax.set_xlabel("epoch")
axes[0].set_ylabel("loss"); axes[0].legend(); axes[0].set_ylim(0, 1.5)
plt.show()

print(f"{'no protection':15s} test acc {test_acc(plain):.3f}")
print(f"{'dropout 0.5':15s} test acc {test_acc(drop):.3f}")
print(f"{'early stopping':15s} test acc {test_acc(early):.3f}")"""),
("md", """**How to read this.** Without protection, validation loss rises after its best epoch — the network grows over-confident on wrong answers. Dropout keeps the validation loss lower and flatter. Early stopping simply stops near the best point and keeps those weights, and it saves training time too. Exact accuracies will vary a little between machines, but the *shape* of the curves is the lesson.

The biggest fix of all is usually **more data**: train on all ~1,000 training images instead of 200 and the overfitting gap shrinks a lot (try it in the exercises).

## Saving a checkpoint

A **checkpoint** stores everything needed to resume training later: model weights, optimizer state and the epoch. Here we save the early-stopped model's weights plus some notes to a temp folder."""),
("code", """import os, tempfile
ckpt = {"model_state": early.state_dict(), "best_epoch": early_best, "note": "MLP 64-256-256-10, 200 train images"}
path = os.path.join(tempfile.gettempdir(), "early_stopped.pt")
torch.save(ckpt, path)
loaded = torch.load(path, map_location=device)
restored = make_mlp().to(device); restored.load_state_dict(loaded["model_state"])
print("restored test accuracy:", round(test_acc(restored), 3), "| best epoch:", loaded["best_epoch"])"""),
("md", """## Recap

- Overfitting shows up as validation loss rising while training loss keeps falling.
- **Dropout** randomly disables neurons in training → more robust network. Always call `model.eval()` before evaluating.
- **Early stopping** with patience → stop at the best epoch and restore its weights.
- **Weight decay** (via `AdamW`) keeps weights small.
- More data beats every trick."""),
]


def build_notebooks():
    notebook(NB1, NB / "01-tensors-and-autograd.ipynb")
    notebook(NB2, NB / "02-mlp-on-digits.ipynb")
    notebook(NB3, NB / "03-cnn-on-digits.ipynb")
    notebook(NB4, NB / "04-overfitting-dropout-early-stopping.ipynb")


# ---------------------------------------------------------------------------
# 4. Slides
# ---------------------------------------------------------------------------
def build_slides():
    I = lambda n: str(IMG / n)
    deck = {
        "title": "Module 05 - Deep Learning with PyTorch",
        "subtitle": "Python to Pro AI Engineer curriculum - weeks 9-10",
        "slides": [
            {"title": "What is deep learning?",
             "bullets": ["Neural networks with many layers", "Learn their own features from raw data",
                         "Images, sound, text", "LLMs are giant neural networks"],
             "notes": "Deep just means many layers. In module 04 we hand-picked features. Deep networks learn features themselves, which is why they dominate images, audio and text. Everything in later modules, including large language models, is built on what we learn today."},
            {"title": "Analogy: the assembly line",
             "bullets": ["Pixels go in one end", "Early stations spot edges", "Middle stations spot shapes", "Last station names the digit",
                         "Nobody tells stations what to look for"],
             "notes": "Each layer is a station on an assembly line. Training adjusts every station so the final answer comes out right. Keep returning to this picture when you explain CNNs later."},
            {"title": "One neuron", "image": I("neuron.png"),
             "bullets": ["Weighted sum of inputs + bias", "Then an activation function", "No activation = linear regression"],
             "notes": "Use the party decision example: is it raining, are friends going, is there an exam tomorrow. Each input gets a weight, add them up, and if the total passes your threshold you go. Point out the link to linear and logistic regression from module 04."},
            {"title": "Activation functions", "image": I("activations.png"),
             "bullets": ["Add bends (non-linearity)", "ReLU = max(0, x): default", "Sigmoid / softmax at the output",
                         "Without them, 100 layers = 1 straight line"],
             "notes": "Stacking multiply-and-add layers without activations collapses into one multiply-and-add. The activation is what allows curves. ReLU is the default for hidden layers. Softmax turns the final scores into probabilities that add to one."},
            {"title": "An MLP for 8x8 digits", "image": I("mlp.png"),
             "bullets": ["64 inputs (pixels)", "Hidden layer + ReLU", "10 outputs = logits, one per digit", "Thousands of learnable parameters"],
             "notes": "An MLP is fully connected layers with activations between them. Count parameters with the class: 64 times 128 weights plus 128 biases for the first layer. Logits are the raw scores; the biggest wins."},
            {"title": "Loss: one number for how wrong",
             "bullets": ["Regression: MSE", "Classification: cross-entropy", "p(correct)=0.9 -> loss 0.11", "p(correct)=0.01 -> loss 4.6",
                         "CrossEntropyLoss takes logits (no softmax!)"],
             "notes": "Cross entropy punishes low probability on the correct class. Work through the two examples: minus log of 0.9 is about 0.11, minus log of 0.01 is about 4.6. Warn students not to add a softmax layer before CrossEntropyLoss because PyTorch applies it internally."},
            {"title": "Gradient descent", "image": I("gradient-descent.png"),
             "bullets": ["Gradient = slope of loss per weight", "w = w - lr x gradient", "Learning rate = stride length",
                         "Too big: bounce. Too small: crawl."],
             "notes": "The foggy hill analogy. You cannot see the valley but you can feel the slope. Each step goes a little downhill. Demonstrate by changing the learning rate in notebook one, part three."},
            {"title": "Backpropagation", "image": I("forward-backward.png"),
             "bullets": ["Forward: inputs -> predictions -> loss", "Backward: blame flows back to every weight", "Chain rule does the maths",
                         "PyTorch autograd does it for you"],
             "notes": "The football replay analogy: watch the goal backwards and hand out blame to each player. Backprop hands out gradients to every weight. Students never compute these by hand; loss.backward does it."},
            {"title": "Tensors and autograd",
             "bullets": ["Tensor = array that can live on GPU", "requires_grad=True records operations", ".backward() fills .grad",
                         "Gradients add up -> zero them"],
             "code": "w = torch.tensor(3.0, requires_grad=True)\nloss = (w - 5) ** 2\nloss.backward()\nprint(w.grad)   # tensor(-4.)",
             "notes": "Run this live. The slope of w minus 5 squared at 3 is minus 4. Negative gradient means increase w to lower the loss. Then call backward again without zeroing and show the gradient doubling."},
            {"title": "nn.Module",
             "bullets": ["__init__: create layers", "forward: how data flows", "Call model(x), never forward(x)"],
             "code": "class DigitMLP(nn.Module):\n    def __init__(self):\n        super().__init__()\n        self.l1 = nn.Linear(64, 128)\n        self.l2 = nn.Linear(128, 10)\n    def forward(self, x):\n        return self.l2(torch.relu(self.l1(x)))",
             "notes": "Every PyTorch model is a class like this. The layers in init hold the weights. Forward describes the path. Forgetting super().__init__() is a common error; read the error message together."},
            {"title": "The training loop", "image": I("training-loop.png"),
             "bullets": ["forward -> loss", "zero_grad -> backward -> step", "Repeat for every batch, every epoch", "Same loop trains LLMs"],
             "notes": "This is the most important slide. Have students say the five steps out loud: forward, loss, zero grad, backward, step. Use the free throw analogy: shoot, see the miss, forget the last shot, work out the fix, adjust."},
            {"title": "The loop in code",
             "bullets": ["model.train() before training", "model.eval() + torch.no_grad() to evaluate", "Batch and model on the same device"],
             "code": "for xb, yb in loader:\n    xb, yb = xb.to(device), yb.to(device)\n    loss = loss_fn(model(xb), yb)\n    optimizer.zero_grad()\n    loss.backward()\n    optimizer.step()",
             "notes": "Walk through each line. Ask what happens if we remove zero_grad: gradients pile up and training goes wrong. Ask what happens if xb is on the CPU and the model on the GPU: an error about devices."},
            {"title": "Reading loss curves", "image": I("loss-curves.png"),
             "bullets": ["Always plot train AND validation", "Both fall together: healthy", "Validation turns up: overfitting", "Both high: underfitting"],
             "notes": "Show the two pictures. The dashed line on the right marks where early stopping would stop. Make plotting both curves a habit every single time students train a model."},
            {"title": "Convolution", "image": I("convolution.png"),
             "bullets": ["Small filter slides over the image", "Output = feature map", "Same filter everywhere (weight sharing)", "Filters are learned"],
             "notes": "The torch on a dark wall analogy. The filter here detects vertical edges; the feature map lights up on the left and right sides of the zero. A CNN learns dozens of such filters on its own."},
            {"title": "A small CNN", "image": I("cnn.png"),
             "bullets": ["Conv + ReLU + pool, twice", "Shapes: (batch, channels, H, W)", "Flatten then Linear to 10", "Print shapes layer by layer"],
             "notes": "Trace the shapes: 1 by 8 by 8, then 16 by 8 by 8, pooled to 4 by 4, then 32 by 4 by 4, pooled to 2 by 2, flatten to 128, then 10 logits. Most CNN bugs are shape bugs, so print shapes with a fake batch."},
            {"title": "Dropout and early stopping",
             "bullets": ["Dropout: randomly switch off neurons in training", "Team practising with random players missing",
                         "Early stopping: stop when val loss stops improving", "Restore the best weights", "Weight decay keeps weights small"],
             "notes": "Notebook four makes a big network overfit 200 images, then fixes it. Stress that dropout is only active in train mode, so model.eval matters. Early stopping is like taking the cake out when it is golden."},
            {"title": "Save and load weights",
             "bullets": ["state_dict = dictionary of weights", "Need the class code to rebuild", "map_location for GPU -> CPU"],
             "code": "torch.save(model.state_dict(), 'mlp.pt')\nm = DigitMLP()\nm.load_state_dict(torch.load('mlp.pt',\n                  map_location='cpu'))\nm.eval()",
             "notes": "Save the state dict, not the whole object. To load, rebuild the model from its class and load the numbers in. Only load files you trust."},
            {"title": "GPUs and Colab",
             "bullets": ["GPU = thousands of small cores", "device = 'cuda' if available else 'cpu'", "Colab: Runtime > Change runtime type > GPU",
                         "Tiny models: GPU not faster"],
             "notes": "Master chef versus a hundred line cooks chopping onions. Our notebooks pick the device automatically, so they run on a laptop or on Colab. For 8 by 8 digits the GPU is not faster because the data is tiny; GPUs shine on big models and images."},
            {"title": "Common mistakes",
             "bullets": ["Forgetting optimizer.zero_grad()", "Softmax before CrossEntropyLoss", "Labels as float instead of long",
                         "Model and data on different devices", "Forgetting model.eval()", "Wrong image shape for Conv2d"],
             "notes": "For each mistake ask the class what symptom it causes. Fixes: zero grads every batch, feed logits, use dtype long for labels, move both to device, switch modes, reshape to batch, channels, height, width."},
            {"title": "Recap and exercises",
             "bullets": ["Neuron -> layer -> network", "Loss + gradients + optimizer = learning", "forward, loss, zero_grad, backward, step",
                         "CNNs for images; dropout and early stopping for overfitting", "Exercises: exercises.md"],
             "notes": "Recap the five-step loop one more time. Set exercises one to four in class, the rest as homework. The Excel cheat sheet in the excel folder lists every PyTorch call from today."},
        ],
    }
    slides(deck, HERE / "slides" / "05-deep-learning.pptx")


# ---------------------------------------------------------------------------
# 5. Excel: PyTorch cheat sheet + shape calculator + experiment log
# ---------------------------------------------------------------------------
def build_excel():
    cheat = [
        ["Task", "PyTorch code", "What it does", "Common mistake"],
        ["Pick device", 'device = "cuda" if torch.cuda.is_available() else "cpu"', "Use GPU when present", "Hard-coding 'cuda' breaks on laptops"],
        ["Make a tensor", "torch.tensor(data, dtype=torch.float32)", "Array of numbers", "Labels need dtype=torch.long"],
        ["Shape", "t.shape / t.reshape(-1, 1, 8, 8)", "Size / change shape", "Conv2d needs (N, C, H, W)"],
        ["Move to device", "t.to(device), model.to(device)", "CPU <-> GPU", "Model and data on different devices"],
        ["To NumPy", "t.detach().cpu().numpy()", "For plotting", "Forgetting .cpu() on GPU tensors"],
        ["Track gradients", "torch.tensor(3.0, requires_grad=True)", "Record ops for backprop", "Only floats can require grad"],
        ["Backprop", "loss.backward()", "Fill .grad for every weight", "Calling twice without zeroing"],
        ["Fully connected layer", "nn.Linear(in_features, out_features)", "Weighted sums", "in_features must match previous output"],
        ["Conv layer", "nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1)", "Sliding filters", "Wrong in_ch (1 for greyscale)"],
        ["Pooling", "nn.MaxPool2d(2)", "Halve height and width", "Pooling too much on small images"],
        ["Activation", "nn.ReLU() / torch.relu(x)", "Add non-linearity", "Forgetting it between Linear layers"],
        ["Dropout", "nn.Dropout(0.3)", "Randomly zero 30% in training", "Forgetting model.eval() at test time"],
        ["Classification loss", "nn.CrossEntropyLoss()", "Softmax + log loss on logits", "Applying softmax first"],
        ["Regression loss", "nn.MSELoss()", "Mean squared error", "Shape (N,) vs (N,1) mismatch"],
        ["Optimizer", "torch.optim.Adam(model.parameters(), lr=1e-3)", "Updates weights", "Learning rate far too high/low"],
        ["Weight decay", "torch.optim.AdamW(params, lr=1e-3, weight_decay=1e-2)", "Keep weights small", "Huge values hurt learning"],
        ["Batches", "DataLoader(TensorDataset(X, y), batch_size=64, shuffle=True)", "Shuffled mini-batches", "shuffle=True on the test loader is pointless"],
        ["Train step", "opt.zero_grad(); loss.backward(); opt.step()", "One update", "Wrong order or missing zero_grad"],
        ["Evaluate", "model.eval(); with torch.no_grad(): ...", "No dropout, no grad tracking", "Leaving model in train mode"],
        ["Predicted class", "logits.argmax(dim=1)", "Index of biggest score", "argmax over wrong dim"],
        ["Save weights", 'torch.save(model.state_dict(), "m.pt")', "Write weights to file", "Saving whole model object"],
        ["Load weights", 'model.load_state_dict(torch.load("m.pt", map_location=device))', "Restore weights", "Architecture must match exactly"],
        ["Count parameters", "sum(p.numel() for p in model.parameters())", "Model size", ""],
        ["Reproducibility", "torch.manual_seed(0)", "Same random start", "GPU runs can still differ slightly"],
    ]
    shapes = [
        ["Layer", "Input size (H=W)", "Kernel", "Padding", "Stride", "Output size", "Formula"],
        ["Conv 3x3 pad 1 (8x8)", 8, 3, 1, 1, "=FLOOR((B2+2*D2-C2)/E2,1)+1", "out = floor((in + 2*pad - kernel)/stride) + 1"],
        ["MaxPool 2x2 (8x8)", 8, 2, 0, 2, "=FLOOR((B3+2*D3-C3)/E3,1)+1", "pooling uses the same formula"],
        ["Conv 3x3 pad 1 (4x4)", 4, 3, 1, 1, "=FLOOR((B4+2*D4-C4)/E4,1)+1", ""],
        ["MaxPool 2x2 (4x4)", 4, 2, 0, 2, "=FLOOR((B5+2*D5-C5)/E5,1)+1", ""],
        ["Conv 3x3 no pad (28x28)", 28, 3, 0, 1, "=FLOOR((B6+2*D6-C6)/E6,1)+1", "e.g. MNIST-size images"],
        ["Conv 5x5 stride 2 (32x32)", 32, 5, 2, 2, "=FLOOR((B7+2*D7-C7)/E7,1)+1", "try your own numbers"],
    ]
    params = [
        ["Layer", "Inputs (or in_channels)", "Outputs (or out_channels)", "Kernel size (conv only, else 1)", "Parameters", "Formula"],
        ["Linear 64 -> 128", 64, 128, 1, "=B2*C2*D2*D2+C2", "in*out + out (bias)"],
        ["Linear 128 -> 10", 128, 10, 1, "=B3*C3*D3*D3+C3", ""],
        ["Conv2d 1 -> 16, 3x3", 1, 16, 3, "=B4*C4*D4*D4+C4", "in*out*k*k + out"],
        ["Conv2d 16 -> 32, 3x3", 16, 32, 3, "=B5*C5*D5*D5+C5", ""],
        ["Linear 128 -> 10 (CNN head)", 128, 10, 1, "=B6*C6*D6*D6+C6", ""],
        ["CNN total", "", "", "", "=E4+E5+E6", "matches notebook 03"],
        ["MLP total", "", "", "", "=E2+E3", "matches notebook 02"],
    ]
    log = [
        ["Run #", "Model", "Hidden size / filters", "Dropout", "Learning rate", "Epochs", "Batch size", "Train loss", "Val loss", "Test accuracy", "Notes"],
        [1, "MLP", 128, 0, 0.001, 40, 64, "", "", "", "baseline from notebook 02"],
        [2, "CNN", "16/32", 0.25, 0.001, 30, 64, "", "", "", "notebook 03"],
        [3, "", "", "", "", "", "", "", "", "", ""],
    ]
    workbook({"PyTorch Cheat Sheet": cheat, "Conv Shape Calculator": shapes,
              "Parameter Counter": params, "Experiment Log": log},
             HERE / "excel" / "05-pytorch-cheatsheet.xlsx",
             col_widths={"PyTorch Cheat Sheet": [22, 58, 30, 40],
                         "Conv Shape Calculator": [28, 16, 10, 10, 10, 14, 46],
                         "Parameter Counter": [28, 22, 24, 26, 14, 24]})


if __name__ == "__main__":
    build_mermaid()
    build_plots()
    build_notebooks()
    build_slides()
    build_excel()
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / "05-deep-learning-handout.pdf",
                      title="Module 05 - Deep Learning with PyTorch (handout)")
    print("05-deep-learning built.")
