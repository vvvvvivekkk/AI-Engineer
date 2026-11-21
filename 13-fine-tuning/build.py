"""
build.py - regenerate every generated file in module 13 (diagrams, notebooks, slides, PDF, Excel).

Run from the repo root:   python 13-fine-tuning/build.py
Optional flags:           --no-pdf   --no-images   --no-notebooks   (skip steps while editing)
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook

MOD = HERE.name
IMG = HERE / "images"
NB = HERE / "notebooks"
ARGS = set(sys.argv[1:])
RAW = "https://raw.githubusercontent.com/vvvvvivekkk/AI-Engineer/main/13-fine-tuning/data"

# ---------------------------------------------------------------------------
# 1. Diagrams
# ---------------------------------------------------------------------------
DIAGRAMS = {
    "decision-prompt-rag-finetune": """
flowchart TD
    S[Model not doing what you want] --> P[Write a better prompt<br/>add a few examples]
    P --> Q1{Good enough?}
    Q1 -- yes --> D[Ship it, keep evaluating]
    Q1 -- no --> Q2{Missing facts or<br/>private / fresh data?}
    Q2 -- yes --> R[Add RAG]
    R --> Q1
    Q2 -- no --> Q3{Have hundreds of good<br/>examples and an eval?}
    Q3 -- no --> C[Collect data first]
    Q3 -- yes --> F[Fine-tune with LoRA / QLoRA]
    F --> Q1
""",
    "full-vs-peft": """
flowchart LR
    subgraph FULL[Full fine-tuning]
      A1[All weights<br/>trainable] --> A2[Gradients + optimizer<br/>for every weight]
      A2 --> A3[New full model<br/>GBs]
    end
    subgraph PEFT[PEFT / LoRA]
      B1[Base weights<br/>frozen] --> B2[Small adapter<br/>trainable]
      B2 --> B3[Adapter file<br/>MBs]
    end
""",
    "qlora": """
flowchart LR
    X[Input tokens] --> L
    subgraph L[One layer during QLoRA training]
      W[Frozen base weights<br/>stored in 4-bit NF4] --> DQ[Dequantise to 16-bit<br/>on the fly]
      AD[LoRA adapter A, B<br/>16-bit, trainable]
      DQ --> SUM((+))
      AD --> SUM
    end
    SUM --> Y[Output]
    Y -. gradients flow only to .-> AD
""",
    "finetune-workflow": """
flowchart LR
    A[Define task<br/>and eval] --> B[Build chat-format<br/>JSONL data]
    B --> C[Baseline: measure<br/>base model]
    C --> D[Train LoRA or<br/>QLoRA adapter]
    D --> E[Evaluate on<br/>held-out set]
    E --> F{Better?}
    F -- no --> B
    F -- yes --> G[Save / merge adapter]
    G --> H[Push to Hub<br/>with model card]
""",
}


def build_images():
    for name, src in DIAGRAMS.items():
        mermaid(src, IMG / f"{name}.png")
        print("image", name)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    import numpy as np

    # LoRA matrices picture: W (d x k) + B (d x r) x A (r x k)
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.set_xlim(0, 22); ax.set_ylim(-0.8, 6.9); ax.axis("off")
    ax.add_patch(Rectangle((0.5, 0.5), 5, 5, color="#B8BEC6"))
    ax.text(3, 3, "W\nd x k\nfrozen\n16.8M numbers", ha="center", va="center", fontsize=12)
    ax.text(6.4, 3, "+", fontsize=28, ha="center", va="center")
    ax.text(8.3, 3, "alpha / r", fontsize=12, ha="center", va="center")
    ax.add_patch(Rectangle((10, 0.5), 0.8, 5, color="#0F9D9A"))
    ax.text(10.4, 5.6, "B  d x r", ha="center", va="bottom", fontsize=11)
    ax.text(11.6, 3, "x", fontsize=24, ha="center", va="center")
    ax.add_patch(Rectangle((12.4, 2.6), 5, 0.8, color="#1B263B"))
    ax.text(14.9, 2.3, "A   r x k", ha="center", va="top", fontsize=11)
    ax.text(18.3, 3, "=", fontsize=24, ha="center", va="center")
    ax.add_patch(Rectangle((19, 1.5), 2.6, 3, fill=False, lw=2, ls="--", color="#0F9D9A"))
    ax.text(20.3, 3, "dW\n(d x k)\nlow rank", ha="center", va="center", fontsize=11)
    ax.text(11, 6.5, "d = k = 4096, r = 8:  A and B hold 65,536 trainable numbers = 0.39% of W",
            ha="center", fontsize=12, color="#1B263B")
    ax.text(11, -0.5, "B starts at zero, so dW = 0 and the model is unchanged before training",
            ha="center", fontsize=11, color="#5A6370")
    fig.tight_layout(); fig.savefig(IMG / "lora-matrices.png", dpi=150); plt.close(fig)
    print("image lora-matrices")

    # Quantisation levels: uniform 4-bit vs normal-quantile (NF4-style) levels on a bell-shaped weight histogram
    from statistics import NormalDist
    rng = np.random.default_rng(0)
    w = rng.normal(0, 1, 20000)
    w = w / np.abs(w).max()
    uniform = np.linspace(-1, 1, 15)
    probs = np.linspace(0.02, 0.98, 16)
    q = np.array([NormalDist().inv_cdf(p) for p in probs]); q = q / np.abs(q).max()
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.hist(w, bins=120, color="#B8BEC6", density=True)
    for v in uniform:
        ax.axvline(v, ymin=0.0, ymax=0.45, color="#1B263B", lw=1.4)
    for v in q:
        ax.axvline(v, ymin=0.55, ymax=1.0, color="#0F9D9A", lw=1.4)
    ax.set_title("Bell-shaped weights: uniform 4-bit levels (navy, bottom) vs NF4-style levels (teal, top)")
    ax.set_xlabel("weight value (scaled to -1..1)"); ax.set_yticks([])
    fig.tight_layout(); fig.savefig(IMG / "quant-levels.png", dpi=150); plt.close(fig)
    print("image quant-levels")


# ---------------------------------------------------------------------------
# 2. Notebooks
# ---------------------------------------------------------------------------
NB1 = [
("md", """# 01 - LoRA from scratch in PyTorch

**Goal:** understand LoRA (Low-Rank Adaptation) by building it yourself in about 20 lines, then compare it with the real `peft` library.

**Words you need**
- **Matrix** - a grid of numbers. A neural-network layer is mostly a weight matrix W.
- **Rank** - roughly, how many independent "directions" of information a matrix holds.
- **Low-rank update** - a change to W written as B x A, where B and A are thin matrices.
- **Frozen** - weights that are not changed by training.

Runs on any CPU in under a minute. No downloads, no keys."""),
("md", """## Step 1 - Imports"""),
("code", """import math
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
torch.manual_seed(0)
print("torch", torch.__version__)"""),
("md", """## Step 2 - What "low rank" means, with a picture

We build a 64 x 64 matrix that is secretly made of only 3 "ingredients" (3 outer products) plus a little noise. **SVD** (singular value decomposition) is a tool that measures how much each independent direction contributes; the contributions are called **singular values**. A low-rank matrix has only a few large ones."""),
("code", """d = 64
M = sum(torch.randn(d, 1) @ torch.randn(1, d) for _ in range(3))   # 3 ingredients
M = M + 0.05 * torch.randn(d, d)                                      # a little noise
S = torch.linalg.svdvals(M)
plt.bar(range(20), S[:20]); plt.title("Singular values: only 3 are big"); plt.xlabel("direction"); plt.show()
print("first 5 singular values:", [round(s, 1) for s in S[:5].tolist()])"""),
("md", """## Step 3 - Rebuild the matrix from thin pieces

If only 3 directions matter, we can write M ≈ B x A with B of shape 64 x 3 and A of shape 3 x 64. That is 384 numbers instead of 4,096 - and the error is tiny. LoRA bets that the *change* needed for fine-tuning is also low rank."""),
("code", """U, S_full, Vh = torch.linalg.svd(M)
for r in [1, 2, 3, 8]:
    B = U[:, :r] * S_full[:r]          # 64 x r
    A = Vh[:r, :]                      # r x 64
    err = (M - B @ A).norm() / M.norm()
    print(f"rank {r}: B {tuple(B.shape)} x A {tuple(A.shape)} -> {B.numel() + A.numel():5d} numbers, relative error {err:.3f}")"""),
("md", """## Step 4 - Count LoRA's savings on a real-size layer

A typical attention matrix in a 7B-parameter model is 4096 x 4096. With rank r = 8, LoRA trains r x (d + k) numbers instead of d x k."""),
("code", """def lora_params(d, k, r):
    return r * (d + k)

d = k = 4096
for r in [4, 8, 16, 64]:
    full, lora = d * k, lora_params(d, k, r)
    print(f"r={r:3d}: full {full:,}  LoRA {lora:,}  ({100 * lora / full:.2f}% of the layer)")"""),
("md", """## Step 5 - A LoRA linear layer, written by hand

`LoRALinear` wraps an existing `nn.Linear`:
1. It **freezes** the original layer (`requires_grad = False`).
2. It creates **A** (r x k, small random numbers) and **B** (d x r, all zeros).
3. Output = original output + (alpha / r) x B A x.

Because B starts at zero, the wrapped layer gives *exactly* the same output as the original before training. (`peft` uses the same initialisation idea.)"""),
("code", """class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, r: int = 4, alpha: float = 8, dropout: float = 0.0):
        super().__init__()
        self.base = base
        for p in self.base.parameters():
            p.requires_grad = False                      # freeze W and bias
        d, k = base.out_features, base.in_features
        self.A = nn.Parameter(torch.empty(r, k))
        nn.init.kaiming_uniform_(self.A, a=math.sqrt(5))  # small random start
        self.B = nn.Parameter(torch.zeros(d, r))          # zeros -> no change at start
        self.scaling = alpha / r
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        return self.base(x) + (self.dropout(x) @ self.A.T @ self.B.T) * self.scaling

    def merged_weight(self):
        return self.base.weight + self.scaling * (self.B @ self.A)

base = nn.Linear(64, 64)
lora = LoRALinear(base, r=2, alpha=4)
x = torch.randn(5, 64)
print("same output before training:", torch.allclose(base(x), lora(x)))
trainable = sum(p.numel() for p in lora.parameters() if p.requires_grad)
total = sum(p.numel() for p in lora.parameters())
print(f"trainable {trainable} of {total} parameters ({100 * trainable / total:.1f}%)")"""),
("md", """## Step 6 - Train it on a toy "new task"

We pretend `base` is a pre-trained layer. The new task needs the layer to behave like W + dW, where dW is a hidden **rank-2** change. We train only A and B with the **mean squared error** loss (average squared difference between prediction and target) and see whether LoRA can discover dW. We try ranks 1, 2 and 8."""),
("code", """dW_true = 0.1 * torch.randn(64, 2) @ torch.randn(2, 64)          # hidden rank-2 change
X = torch.randn(2000, 64)
Y = (X @ (base.weight + dW_true).T + base.bias).detach()            # targets for the new task

results = {}
for r in [1, 2, 8]:
    torch.manual_seed(0)
    layer = LoRALinear(base, r=r, alpha=2 * r)
    opt = torch.optim.Adam([layer.A, layer.B], lr=1e-2)
    losses = []
    for step in range(600):
        loss = ((layer(X) - Y) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
        losses.append(loss.item())
    learned = layer.scaling * (layer.B @ layer.A)
    rel = ((learned - dW_true).norm() / dW_true.norm()).item()
    results[r] = layer
    plt.plot(losses, label=f"r={r}")
    print(f"r={r}: final loss {losses[-1]:.2e}, error in recovered dW {rel:.3f}")
plt.yscale("log"); plt.xlabel("step"); plt.ylabel("MSE (log scale)"); plt.legend(); plt.title("Rank 1 is too small; rank 2+ fits"); plt.show()
print("base weights unchanged:", base.weight.requires_grad is False)"""),
("md", """## Step 7 - Merge the adapter into the weights

**Merging** computes W' = W + (alpha/r) B A once. A plain `nn.Linear` with W' gives the same outputs as base + adapter, with no extra cost at inference time."""),
("code", """layer = results[2]
merged = nn.Linear(64, 64)
with torch.no_grad():
    merged.weight.copy_(layer.merged_weight())
    merged.bias.copy_(base.bias)
x = torch.randn(3, 64)
print("merged == base + adapter:", torch.allclose(merged(x), layer(x), atol=1e-5))"""),
("md", """## Step 8 - The same idea with the `peft` library

`peft` does all of this for any model. We give it a tiny two-layer network and say which layers to adapt with `target_modules`. Look at the printed structure: each targeted `Linear` now has a `base_layer` plus `lora_A` and `lora_B` - exactly our design."""),
("code", """from peft import LoraConfig, get_peft_model

class TinyMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(16, 32)
        self.fc2 = nn.Linear(32, 4)
    def forward(self, x):
        return self.fc2(torch.relu(self.fc1(x)))

peft_model = get_peft_model(TinyMLP(), LoraConfig(r=4, lora_alpha=8, target_modules=["fc1", "fc2"]))
peft_model.print_trainable_parameters()
print(peft_model.base_model.model.fc1)"""),
("md", """## Step 9 - peft merging

`merge_and_unload()` folds the adapters into the weights and returns the plain model - the same as our Step 7."""),
("code", """with torch.no_grad():                                   # give B some non-zero values so merging matters
    for name, p in peft_model.named_parameters():
        if "lora_B" in name:
            p.add_(0.1 * torch.randn_like(p))
x = torch.randn(2, 16)
before = peft_model(x)
plain = peft_model.merge_and_unload()
print(type(plain).__name__, "| outputs match:", torch.allclose(before, plain(x), atol=1e-5))"""),
("md", """## What you learned

- A low-rank matrix can be stored as two thin matrices B (d x r) and A (r x k).
- LoRA: output = W x + (alpha/r) B A x, with W frozen and B starting at zero.
- r = 8 on a 4096 x 4096 layer trains only 0.39% of it.
- If r is too small for the change you need, LoRA underfits (r = 1 above).
- Merging folds the adapter into W; `peft` implements the same design.
- Next: `02-quantisation-explained.ipynb`, the other half of QLoRA."""),
]

NB2 = [
("md", """# 02 - Quantisation explained (the "Q" in QLoRA)

**Goal:** see how 4-bit quantisation works on real numbers, measure the error it adds, understand why NF4 places its levels the way it does, and estimate GPU memory for different fine-tuning methods.

**Words you need**
- **Quantisation** - storing numbers with fewer bits by rounding them to a small set of allowed values.
- **Bit** - a 0 or 1. With 4 bits you can label 2^4 = 16 different values.
- **Scale** - the number we divide by before rounding and multiply by afterwards.
- **Block-wise** - quantising small groups of numbers separately, each with its own scale.

The real 4-bit library (`bitsandbytes`) needs an NVIDIA GPU, so here we write the maths ourselves on a CPU."""),
("md", """## Step 1 - Imports and some fake weights

Neural-network weights are roughly bell-shaped (a **normal distribution**): many values near zero, few large. We also plant a few **outliers** (unusually large values), because real models have them."""),
("code", """import torch
import matplotlib.pyplot as plt
torch.manual_seed(0)
w = torch.randn(4096) * 0.02             # typical small weights
w[torch.randint(0, 4096, (5,))] = 0.4    # a few outliers
print("min", w.min().item(), "max", w.max().item())
plt.hist(w, bins=100); plt.title("Our fake weights"); plt.show()"""),
("md", """## Step 2 - Bytes per weight

The same model takes very different amounts of memory depending on the format."""),
("code", """formats = {"float32": 4, "bfloat16 / float16": 2, "int8": 1, "4-bit": 0.5}
for params_b in [0.5, 7, 70]:
    row = ", ".join(f"{name}: {params_b * b:.1f} GB" for name, b in formats.items())
    print(f"{params_b:>4}B params -> {row}")"""),
("md", """## Step 3 - Absmax quantisation of the whole tensor

Recipe for symmetric 4-bit (integers -7..7):
1. scale = max(|w|) / 7
2. q = round(w / scale), clipped to -7..7 - these small integers are what we store
3. dequantise: w_hat = q x scale

Because of the outliers, the scale is large, so most small weights round to 0. Look at the error."""),
("code", """def absmax_quant(x, bits=4):
    qmax = 2 ** (bits - 1) - 1                    # 7 for 4-bit, 127 for 8-bit
    scale = x.abs().max() / qmax
    q = torch.clamp(torch.round(x / scale), -qmax, qmax)
    return q, scale

def dequant(q, scale):
    return q * scale

for bits in [8, 4]:
    q, s = absmax_quant(w, bits)
    err = (w - dequant(q, s)).abs().mean().item()
    zeros = (q == 0).float().mean().item()
    print(f"{bits}-bit whole tensor: mean abs error {err:.5f}, {zeros:.0%} of weights became 0")"""),
("md", """## Step 4 - Block-wise quantisation

Split the tensor into blocks of 64 and give each block its own scale. An outlier now only hurts its own block. Storing one extra scale per 64 weights costs a little memory, which is why real 4-bit formats use slightly more than 0.5 bytes per weight (and why QLoRA's **double quantisation** compresses the scales too)."""),
("code", """def blockwise(x, bits=4, block=64):
    blocks = x.view(-1, block)
    out = torch.empty_like(blocks)
    for i, b in enumerate(blocks):
        q, s = absmax_quant(b, bits)
        out[i] = dequant(q, s)
    return out.view(-1)

w4_block = blockwise(w, 4, 64)
print("4-bit block-wise mean abs error:", round((w - w4_block).abs().mean().item(), 5))"""),
("md", """## Step 5 - NF4-style levels: put more levels where the weights are

Uniform levels waste values on the rare large numbers. **NF4 (4-bit NormalFloat)** chooses its 16 levels from the **quantiles** of a normal distribution - points that split the bell curve into equal-probability slices - so levels are dense near zero. The real NF4 table is built this way with an extra trick so that 0 is exactly representable; here we build a simple version."""),
("code", """normal = torch.distributions.Normal(0, 1)
probs = torch.linspace(0.02, 0.98, 16)
nf_levels = normal.icdf(probs)
nf_levels = nf_levels / nf_levels.abs().max()          # scale to -1..1
uniform_levels = torch.linspace(-1, 1, 16)
print("NF4-style levels:", [round(v, 2) for v in nf_levels.tolist()])

def quant_to_levels(x, levels, block=64):
    blocks = x.view(-1, block)
    out = torch.empty_like(blocks)
    for i, b in enumerate(blocks):
        s = b.abs().max()
        idx = torch.argmin((b[:, None] / s - levels[None, :]).abs(), dim=1)  # nearest level
        out[i] = levels[idx] * s
    return out.view(-1)

for name, lv in [("uniform 16 levels", uniform_levels), ("NF4-style levels", nf_levels)]:
    err = (w - quant_to_levels(w, lv)).abs().mean().item()
    print(f"{name:18s}: mean abs error {err:.5f}")"""),
("md", """## Step 6 - See the levels against the weights"""),
("code", """b = w.view(-1, 64)[0]
b = b / b.abs().max()
plt.hist(b, bins=30, color="lightgrey")
for v in uniform_levels: plt.axvline(v, color="navy", ymax=0.4)
for v in nf_levels: plt.axvline(v, color="teal", ymin=0.6)
plt.title("One block: uniform levels (navy) vs NF4-style (teal)"); plt.show()"""),
("md", """## Step 7 - A GPU memory estimator

Rough rule-of-thumb formulas (the same ones used in `excel/gpu-memory-estimator.xlsx`):
- **weights** = parameters x bytes per weight (2 for 16-bit, ~0.55 for 4-bit including scales)
- **training state** = trainable parameters x bytes for gradient + optimizer (about 14 extra for full fine-tuning with Adam in mixed precision; about 16 for LoRA adapters kept in 32-bit)
- **activations** = depends on batch size and sequence length; we use a rough fixed guess

These are planning numbers, not guarantees."""),
("code", """def estimate_gb(params_b, method, activations_gb=2.0, lora_fraction=0.005):
    p = params_b * 1e9
    if method == "inference-16bit":
        weights, state, act = 2 * p, 0, 0.5
    elif method == "full":
        weights, state, act = 2 * p, 14 * p, activations_gb
    elif method == "lora":
        weights, state, act = 2 * p, 16 * p * lora_fraction, activations_gb
    elif method == "qlora":
        weights, state, act = 0.55 * p, 16 * p * lora_fraction, activations_gb
    return (weights + state) / 1e9 + act

print(f"{'model':>6} | {'inference':>9} | {'full FT':>8} | {'LoRA':>6} | {'QLoRA':>6}   (GB, rough)")
for size in [0.5, 1.5, 7, 13]:
    vals = [estimate_gb(size, m) for m in ["inference-16bit", "full", "lora", "qlora"]]
    print(f"{size:>5}B | " + " | ".join(f"{v:>8.1f}" for v in vals))
print("A free Colab T4 has 16 GB (about 15 usable).")"""),
("md", """## Step 8 - How you load a model in 4-bit (GPU only, not run here)

On a GPU with `bitsandbytes` installed, this is all it takes. Notebook `04-qlora-colab-only.ipynb` runs it for real.

```python
import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                         bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct",
                                             quantization_config=bnb, device_map="auto")
```"""),
("md", """## What you learned

- 4-bit storage = one quarter of 16-bit memory, at the cost of rounding error.
- Block-wise scales stop outliers from ruining everything.
- NF4 puts more levels near zero because weights are bell-shaped.
- QLoRA = 4-bit frozen base + 16-bit LoRA adapters; full fine-tuning needs roughly 16 bytes per parameter."""),
]

NB3 = [
("md", """# 03 - LoRA fine-tune a real chat model on your CPU

**Goal:** fine-tune `HuggingFaceTB/SmolLM2-135M-Instruct` (a 135-million-parameter chat model, ~270 MB download) with LoRA using the `peft` library, on 48 examples, in a few minutes on a laptop CPU. We measure the model **before and after**, save the adapter, reload it, merge it, and (optionally) push it to the Hugging Face Hub.

**The task:** answer questions for *Chai Corner*, a made-up tea shop, in its house style: start with "Chai Corner here!" and end with "Have a warm day!". The style is easy to measure, so we can prove whether training worked.

**Words you need**
- **SFT (supervised fine-tuning)** - training on example input-output pairs.
- **Chat template** - the recipe that turns a list of messages into the exact text the model reads.
- **Adapter** - the small set of LoRA weights we train; the base model stays frozen.

This notebook takes roughly 3-8 minutes on a 2-core CPU. A GPU makes it much faster but is not needed."""),
("md", """## Step 1 - Install / import

Colab already has `torch` and `transformers`; `peft` may need installing. Locally, install from the repo's `requirements.txt`. We also limit PyTorch to the available CPU cores."""),
("code", """import importlib.util, subprocess, sys
if importlib.util.find_spec("peft") is None:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "peft"], check=True)

import json, os, pathlib, random, time, urllib.request
import torch
import matplotlib.pyplot as plt
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, PeftModel
import peft, transformers
torch.manual_seed(0); random.seed(0)
torch.set_num_threads(min(4, os.cpu_count() or 1))
print("transformers", transformers.__version__, "| peft", peft.__version__, "| torch", torch.__version__)"""),
("md", f"""## Step 2 - Load the dataset

The data lives in `13-fine-tuning/data/` as **JSONL** (one JSON object per line) in the chat format. If you opened this notebook in Colab, the files are downloaded from the course GitHub repo."""),
("code", f"""RAW = "{RAW}"
def get_jsonl(name):
    local = pathlib.Path("../data") / name
    if not local.exists():                       # e.g. running in Colab
        local = pathlib.Path(name)
        if not local.exists():
            urllib.request.urlretrieve(f"{{RAW}}/{{name}}", local)
    return [json.loads(l) for l in local.read_text(encoding="utf-8").splitlines() if l.strip()]

train = get_jsonl("chai_corner_train.jsonl")
test = get_jsonl("chai_corner_test.jsonl")
print(len(train), "train examples,", len(test), "test examples")
print(json.dumps(train[0], indent=1))"""),
("md", """## Step 3 - Load the model and tokenizer

The **tokenizer** splits text into tokens and holds the chat template. A **pad token** is a filler used to make sequences in a batch the same length; if a model has none, we reuse the end-of-sequence token."""),
("code", """MODEL_ID = "HuggingFaceTB/SmolLM2-135M-Instruct"
tok = AutoTokenizer.from_pretrained(MODEL_ID)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32)
n_params = sum(p.numel() for p in model.parameters())
print(f"{n_params / 1e6:.0f}M parameters")"""),
("md", """## Step 4 - Look at the chat template

This is what the model *actually* reads. Notice the special tokens `<|im_start|>` and `<|im_end|>` around each message. `add_generation_prompt=True` adds the opening of an assistant turn so the model knows it should reply."""),
("code", """print(tok.apply_chat_template(train[0]["messages"], tokenize=False))
print("---- prompt only, ready for the model to answer ----")
print(tok.apply_chat_template(train[0]["messages"][:-1], tokenize=False, add_generation_prompt=True))"""),
("md", """## Step 5 - Turn examples into training tensors with loss masking

For each example we build:
- `input_ids` - the token numbers of the whole conversation;
- `labels` - a copy, except the prompt tokens are set to **-100**, which tells PyTorch to ignore them in the loss. So the model learns to write the *answer*, not to repeat the question.

In recent `transformers` versions `apply_chat_template(..., tokenize=True)` returns a dictionary-like object, so we take its `input_ids`."""),
("code", """def ids_of(x):
    return x if isinstance(x, list) else list(x["input_ids"])

def encode(example, max_len=128):
    msgs = example["messages"]
    prompt_ids = ids_of(tok.apply_chat_template(msgs[:-1], add_generation_prompt=True, tokenize=True))
    full_ids = ids_of(tok.apply_chat_template(msgs, tokenize=True))[:max_len]
    labels = ([-100] * len(prompt_ids) + full_ids[len(prompt_ids):])[:len(full_ids)]
    return full_ids, labels

def collate(batch):
    width = max(len(i) for i, _ in batch)
    ids = torch.full((len(batch), width), tok.pad_token_id)
    lab = torch.full((len(batch), width), -100)
    att = torch.zeros((len(batch), width), dtype=torch.long)
    for r, (i, l) in enumerate(batch):
        ids[r, :len(i)] = torch.tensor(i); lab[r, :len(l)] = torch.tensor(l); att[r, :len(i)] = 1
    return ids, att, lab

enc_train = [encode(r) for r in train]
enc_test = [encode(r) for r in test]
ids, labels = enc_train[0]
trained_on = tok.decode([t for t, l in zip(ids, labels) if l != -100])
print(f"{len(ids)} tokens, of which {sum(l != -100 for l in labels)} are trained on:")
print(repr(trained_on))"""),
("md", """## Step 6 - Measure the model BEFORE training

Two measurements on the 12 **held-out** test examples (never used for training):
1. **Test loss** - how surprised the model is by the correct answers (lower is better).
2. **Style score** - generate answers for 6 test questions and count how many start with "Chai Corner here!" and contain "Have a warm day!". **Greedy decoding** (`do_sample=False`) always picks the most likely next token, so results are repeatable."""),
("code", """PREFIX, SUFFIX = "Chai Corner here!", "Have a warm day!"

@torch.no_grad()
def test_loss(m):
    m.eval()
    ids, att, lab = collate(enc_test)
    return m(input_ids=ids, attention_mask=att, labels=lab).loss.item()

@torch.no_grad()
def reply(m, msgs):
    enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    out = m.generate(**enc, max_new_tokens=32, do_sample=False, pad_token_id=tok.pad_token_id)
    return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()

def style_score(m, rows):
    m.eval()
    answers = [reply(m, r["messages"][:-1]) for r in rows]
    ok = [a.startswith(PREFIX) and SUFFIX in a for a in answers]
    return sum(ok) / len(ok), answers

GEN_ROWS = test[:6]
t0 = time.time()
before_loss = test_loss(model)
before_style, before_answers = style_score(model, GEN_ROWS)
print(f"BEFORE: test loss {before_loss:.3f}, style {before_style:.0%}  ({time.time() - t0:.0f}s)")
for r, a in list(zip(GEN_ROWS, before_answers))[:2]:
    print("Q:", r["messages"][1]["content"], "\\nA:", a, "\\n")"""),
("md", """## Step 7 - Add LoRA adapters with `peft`

`LoraConfig` settings (see `concepts.md` section 5.5):
- `r=8`, `lora_alpha=16` - rank 8, scaling alpha/r = 2;
- `target_modules` - the four attention projections in every layer;
- `task_type="CAUSAL_LM"` - a text-generation model.

`print_trainable_parameters()` shows how few weights we will train."""),
("code", """lora_cfg = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05,
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], task_type="CAUSAL_LM")
model = get_peft_model(model, lora_cfg)
model.print_trainable_parameters()"""),
("md", """## Step 8 - Train

A plain PyTorch training loop, so every step is visible:
1. pick a random **batch** of 4 examples;
2. forward pass → loss (the model computes it from `labels`);
3. `loss.backward()` computes gradients - only for the LoRA weights;
4. the **AdamW** optimizer updates them. The **learning rate** 2e-3 is higher than usual because we train very few steps on a tiny model.

30 steps x 4 examples ≈ 2.5 passes (**epochs**) over the 48 examples."""),
("code", """opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=2e-3)
STEPS, BATCH = 30, 4
losses, t0 = [], time.time()
model.train()
for step in range(1, STEPS + 1):
    ids, att, lab = collate(random.sample(enc_train, BATCH))
    loss = model(input_ids=ids, attention_mask=att, labels=lab).loss
    loss.backward()
    opt.step(); opt.zero_grad()
    losses.append(loss.item())
    if step % 5 == 0:
        print(f"step {step:2d}  loss {loss.item():.3f}  ({time.time() - t0:.0f}s)")
plt.plot(losses); plt.xlabel("step"); plt.ylabel("training loss"); plt.title("LoRA training on CPU"); plt.show()"""),
("md", """## Step 9 - Measure AFTER training

Same test loss and the same 6 questions. Compare with Step 6."""),
("code", """after_loss = test_loss(model)
after_style, after_answers = style_score(model, GEN_ROWS)
print(f"test loss : {before_loss:.3f} -> {after_loss:.3f}")
print(f"style     : {before_style:.0%} -> {after_style:.0%}")
for r, a in zip(GEN_ROWS, after_answers):
    print("\\nQ:", r["messages"][1]["content"])
    print("A:", a)
    print("reference:", r["messages"][2]["content"])"""),
("md", """## Step 10 - Read the answers critically

Compare the answers with the reference answers. The **style** is learned quickly. But a 135M model trained for 30 steps will often **invent facts** (wrong prices, made-up features). That is the lesson from `concepts.md` section 1: fine-tuning teaches *behaviour*; for reliable *facts*, use RAG - or combine both.

## Step 11 - Save the adapter

`save_pretrained` on a `PeftModel` writes only the adapter - a few MB - not the 270 MB base model."""),
("code", """out_dir = pathlib.Path("outputs/chai-corner-lora")
model.save_pretrained(out_dir)
tok.save_pretrained(out_dir)
for f in sorted(out_dir.iterdir()):
    print(f"{f.name:32s} {f.stat().st_size / 1e6:6.2f} MB")"""),
("md", """## Step 12 - Reload the adapter on a fresh base model

This is how someone else would use your adapter: load the original base model, then attach the adapter with `PeftModel.from_pretrained`. The answer should match the trained model's answer. We delete the training copy first to keep memory low on small machines."""),
("code", """import gc
q = GEN_ROWS[0]["messages"][:-1]
trained_answer = reply(model, q)
del model, opt; gc.collect()                      # free memory: we only need the saved adapter now

fresh_base = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32)
reloaded = PeftModel.from_pretrained(fresh_base, out_dir)
reloaded.eval()
print("trained :", trained_answer)
print("reloaded:", reply(reloaded, q))"""),
("md", """## Step 13 - Merge into a standalone model

`merge_and_unload()` folds B A into the base weights (W' = W + (alpha/r) B A) and returns a normal `transformers` model that does not need `peft`. We check it gives the same answer, then save it."""),
("code", """merged = reloaded.merge_and_unload()
print(type(merged).__name__)
print("merged  :", reply(merged, q))
merged.save_pretrained("outputs/chai-corner-merged")
print("saved merged model to outputs/chai-corner-merged")"""),
("md", """## Step 14 - Push to the Hugging Face Hub (optional, guarded)

To share your adapter you need a free Hugging Face account and an **access token** with write permission. Put it in the environment variable `HF_TOKEN` (or a Colab secret) - **never** type it into a notebook. This cell does nothing unless the token exists *and* you set `PUSH = True`."""),
("code", """PUSH = False                                   # change to True when you really want to upload
REPO_ID = "your-username/chai-corner-smollm2-lora"   # change to your own username
token = os.getenv("HF_TOKEN")
if PUSH and token:
    from huggingface_hub import HfApi
    api = HfApi(token=token)
    api.create_repo(REPO_ID, private=True, exist_ok=True)       # private until you are happy with it
    api.upload_folder(folder_path=str(out_dir), repo_id=REPO_ID)  # uploads only the small adapter files
    print("pushed to https://huggingface.co/" + REPO_ID)
else:
    print("Skipping upload (set HF_TOKEN in your environment and PUSH = True to enable).")"""),
("md", """## The same training with TRL (for reference)

Libraries like **TRL** wrap Steps 5-8 in a few lines (`SFTTrainer` builds the chat template, masks the prompt, batches and trains). Notebook 04 uses it on a GPU. On CPU it looks like:

```python
from trl import SFTConfig, SFTTrainer
from datasets import load_dataset
ds = load_dataset("json", data_files="../data/chai_corner_train.jsonl")["train"]
ds = ds.map(lambda ex: {"prompt": ex["messages"][:-1], "completion": ex["messages"][-1:]},
            remove_columns=["messages"])   # prompt/completion format -> loss only on the completion
trainer = SFTTrainer(model=MODEL_ID, train_dataset=ds,
                     args=SFTConfig(output_dir="trl-out", max_steps=30, learning_rate=2e-3,
                                    per_device_train_batch_size=4, report_to="none"),
                     peft_config=lora_cfg)
trainer.train()
```

## What you learned
- Chat-format data + the model's chat template + loss masking = SFT.
- LoRA trained under 1% of the weights and changed the style from 0% to most answers.
- Always measure before and after on held-out data - and read the outputs.
- Adapters are small files; they can be reloaded, merged, and shared."""),
]

NB4 = [
("md", """# 04 - QLoRA on a small instruct model (Colab T4 GPU only)

**Before you start: Runtime → Change runtime type → T4 GPU.** This notebook needs an NVIDIA GPU because 4-bit layers come from `bitsandbytes`. It is *not* run by the course's automatic checks.

**Goal:** fine-tune `Qwen/Qwen2.5-0.5B-Instruct` with **QLoRA** (frozen base weights in 4-bit NF4 + trainable LoRA adapters) using `transformers`, `peft`, `trl` and `bitsandbytes`, on the Chai Corner dataset. Then evaluate before/after, save, merge, and optionally push to the Hub.

Expected time on a T4: about 5-10 minutes including downloads.

Versions: this notebook was written and API-checked against **transformers 5.23.0, peft 0.22.0, trl 1.18.2** (late 2026) and pins them. If you change versions, check argument names in the official docs."""),
("md", """## Step 1 - Install the libraries

`bitsandbytes` provides the 4-bit layers. We pin the versions the notebook was checked with. After installing, if Colab asks you to restart the session, do so and continue from Step 2."""),
("code", """!pip install -q "transformers==5.23.0" "peft==0.22.0" "trl==1.18.2" bitsandbytes accelerate datasets"""),
("md", """## Step 2 - Check the GPU

`torch.cuda.is_available()` must be `True`. The T4 does not support fast bfloat16, so we use **float16** for computation."""),
("code", """import os, json, pathlib, urllib.request, time
import torch
assert torch.cuda.is_available(), "No GPU found: Runtime -> Change runtime type -> T4 GPU, then rerun."
print(torch.cuda.get_device_name(0), f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
import transformers, peft, trl
print("transformers", transformers.__version__, "| peft", peft.__version__, "| trl", trl.__version__)"""),
("md", f"""## Step 3 - Get the dataset

The same 48 training and 12 test examples as notebook 03, downloaded from the course repo."""),
("code", f"""RAW = "{RAW}"
for name in ["chai_corner_train.jsonl", "chai_corner_test.jsonl"]:
    if not pathlib.Path(name).exists():
        urllib.request.urlretrieve(f"{{RAW}}/{{name}}", name)

from datasets import load_dataset
ds = load_dataset("json", data_files={{"train": "chai_corner_train.jsonl", "test": "chai_corner_test.jsonl"}})
print(ds)"""),
("md", """## Step 4 - Convert to prompt / completion format

TRL understands several dataset formats. In the **conversational prompt-completion** format, `prompt` is the list of messages before the answer and `completion` is the assistant message. With this format `SFTTrainer` computes the loss **only on the completion** (`completion_only_loss` defaults to on), which is the loss masking we did by hand in notebook 03."""),
("code", """def to_prompt_completion(ex):
    return {"prompt": ex["messages"][:-1], "completion": ex["messages"][-1:]}

ds = ds.map(to_prompt_completion, remove_columns=["messages"])
print(ds["train"][0])"""),
("md", """## Step 5 - Load the model in 4-bit

`BitsAndBytesConfig`:
- `load_in_4bit=True` - store the frozen weights in 4 bits;
- `bnb_4bit_quant_type="nf4"` - the NormalFloat levels from notebook 02;
- `bnb_4bit_use_double_quant=True` - also compress the scale numbers;
- `bnb_4bit_compute_dtype=torch.float16` - dequantise to float16 for the maths (T4-friendly).

`device_map="auto"` places the model on the GPU."""),
("code", """from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"     # try Qwen/Qwen2.5-1.5B-Instruct for a bigger model
bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)
tok = AutoTokenizer.from_pretrained(MODEL_ID)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, quantization_config=bnb_config,
                                             device_map="auto", dtype=torch.float16)
print(f"GPU memory used by the 4-bit model: {torch.cuda.memory_allocated() / 1e9:.2f} GB")"""),
("md", """## Step 6 - Measure BEFORE training

The same style score as notebook 03: does the answer start with "Chai Corner here!" and contain "Have a warm day!"? We use all 12 test questions and greedy decoding."""),
("code", """PREFIX, SUFFIX = "Chai Corner here!", "Have a warm day!"
test_rows = list(ds["test"])

@torch.no_grad()
def reply(m, prompt_msgs, max_new_tokens=48):
    enc = tok.apply_chat_template(prompt_msgs, add_generation_prompt=True,
                                  return_tensors="pt", return_dict=True).to(m.device)
    out = m.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=tok.pad_token_id)
    return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()

def style_score(m):
    m.eval()
    answers = [reply(m, r["prompt"]) for r in test_rows]
    return sum(a.startswith(PREFIX) and SUFFIX in a for a in answers) / len(answers), answers

before_style, before_answers = style_score(model)
print(f"BEFORE style score: {before_style:.0%}")
print("Example:", before_answers[0])"""),
("md", """## Step 7 - Prepare for k-bit training and define LoRA

`prepare_model_for_kbit_training` (from `peft`) gets a quantised model ready: it freezes the base, keeps small layers such as layer norms in higher precision, and turns on **gradient checkpointing** (saves memory by recomputing activations).

`target_modules="all-linear"` puts adapters on every linear layer (attention and MLP), a common QLoRA choice."""),
("code", """from peft import LoraConfig, prepare_model_for_kbit_training
model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
peft_config = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
                         target_modules="all-linear", task_type="CAUSAL_LM")
print(peft_config)"""),
("md", """## Step 8 - Configure and create the SFTTrainer

Key `SFTConfig` settings:
- `num_train_epochs=3`, `per_device_train_batch_size=4`, `gradient_accumulation_steps=2` → effective batch 8;
- `learning_rate=2e-4` - a typical LoRA learning rate;
- `max_length=256` - longer examples would be truncated (ours are short);
- `fp16=True` - mixed precision on the T4 (do **not** use `bf16` on a T4);
- `optim="paged_adamw_8bit"` - the memory-saving paged optimizer from QLoRA;
- `report_to="none"` - do not send logs to external services.

We pass `peft_config`, so the trainer wraps the model with LoRA for us."""),
("code", """from trl import SFTConfig, SFTTrainer
args = SFTConfig(
    output_dir="qlora-chai",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=2,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_steps=2,
    logging_steps=2,
    max_length=256,
    fp16=True,
    bf16=False,
    optim="paged_adamw_8bit",
    gradient_checkpointing=True,
    eval_strategy="epoch",
    save_strategy="no",
    report_to="none",
)
trainer = SFTTrainer(model=model, args=args, train_dataset=ds["train"], eval_dataset=ds["test"],
                     processing_class=tok, peft_config=peft_config)
trainer.model.print_trainable_parameters()"""),
("md", """## Step 9 - Train

Watch the training loss fall and the evaluation loss after each epoch. If the loss shows `nan`, restart and set `fp16=False` (slower but safer)."""),
("code", """t0 = time.time()
trainer.train()
print(f"training took {time.time() - t0:.0f}s; peak GPU memory {torch.cuda.max_memory_allocated() / 1e9:.2f} GB")"""),
("md", """## Step 10 - Measure AFTER training

Same 12 questions. Also read the answers against the references - check the facts, not only the style."""),
("code", """after_style, after_answers = style_score(trainer.model)
print(f"style score: {before_style:.0%} -> {after_style:.0%}")
print("eval loss:", trainer.evaluate()["eval_loss"])
for r, a in list(zip(test_rows, after_answers))[:5]:
    print("\\nQ:", r["prompt"][-1]["content"]); print("A:", a); print("ref:", r["completion"][0]["content"])"""),
("md", """## Step 11 - Save the adapter

Only the LoRA weights are saved (a few tens of MB at most), plus the tokenizer."""),
("code", """ADAPTER_DIR = "qlora-chai-adapter"
trainer.model.save_pretrained(ADAPTER_DIR)
tok.save_pretrained(ADAPTER_DIR)
!ls -lh {ADAPTER_DIR}"""),
("md", """## Step 12 - Merge into a 16-bit model

You cannot cleanly merge into 4-bit weights. Instead, load a fresh **float16** copy of the base model, attach the adapter, and merge. We free the training model first to make room on the GPU."""),
("code", """import gc
from peft import PeftModel
del trainer, model
gc.collect(); torch.cuda.empty_cache()
base16 = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float16, device_map="auto")
merged = PeftModel.from_pretrained(base16, ADAPTER_DIR).merge_and_unload()
print("merged answer:", reply(merged, test_rows[0]["prompt"]))
merged.save_pretrained("qlora-chai-merged")
tok.save_pretrained("qlora-chai-merged")"""),
("md", """## Step 13 - Push to the Hugging Face Hub (optional, guarded)

Add your write token as a Colab **secret** named `HF_TOKEN` (key icon in the left sidebar) or as an environment variable. Never paste it into a cell. Set `PUSH = True` and change `REPO_ID` to your username. Pushing the adapter is usually enough; others load it on top of the same base model. Remember: the base model's licence applies to your fine-tune too."""),
("code", """PUSH = False
REPO_ID = "your-username/chai-corner-qwen2.5-0.5b-qlora"
token = os.getenv("HF_TOKEN")
if token is None:
    try:
        from google.colab import userdata
        token = userdata.get("HF_TOKEN")
    except Exception:
        token = None
if PUSH and token:
    from huggingface_hub import HfApi
    HfApi(token=token).create_repo(REPO_ID, private=True, exist_ok=True)
    HfApi(token=token).upload_folder(folder_path=ADAPTER_DIR, repo_id=REPO_ID)
    print("uploaded adapter to https://huggingface.co/" + REPO_ID)
else:
    print("Skipping upload (needs HF_TOKEN and PUSH = True).")"""),
("md", """## What you learned
- QLoRA = load the base in 4-bit NF4 + train LoRA adapters; a T4 is enough for small models.
- TRL's `SFTTrainer` handles the chat template and completion-only loss for prompt/completion data.
- Evaluate before/after on held-out data and read the outputs.
- Merge into a 16-bit base, not the 4-bit one; share adapters with a token from a secret."""),
]


def build_notebooks():
    notebook(NB1, NB / "01-lora-from-scratch.ipynb")
    notebook(NB2, NB / "02-quantisation-explained.ipynb")
    notebook(NB3, NB / "03-lora-finetune-cpu.ipynb")
    notebook(NB4, NB / "04-qlora-colab-only.ipynb")
    print("notebooks built")


# ---------------------------------------------------------------------------
# 3. Slides
# ---------------------------------------------------------------------------
def build_slides():
    I = lambda n: str(IMG / f"{n}.png")
    deck = {
        "title": "Module 13 - Fine-tuning LLMs",
        "subtitle": "SFT, LoRA and QLoRA - Python to Pro AI Engineer, week 21",
        "slides": [
            {"title": "Today's goals", "bullets": [
                "Decide: prompt, RAG or fine-tune?", "Prepare chat-format SFT data",
                "Explain LoRA with matrices", "Explain 4-bit quantisation and QLoRA",
                "Fine-tune a real model on a CPU", "Evaluate, merge and share an adapter"],
             "notes": "Tell students that by the end of the session they will have fine-tuned a real language model on their own laptop. Fine-tuning sounds scary and expensive; LoRA makes it small and cheap."},
            {"title": "What fine-tuning is", "bullets": [
                "Extra training on a small, specific dataset", "Analogy: a graduate's on-the-job training",
                "Good for: style, format, narrow skills, smaller models",
                "Bad for: adding reliable facts (use RAG)"],
             "notes": "Pre-training is the degree, fine-tuning is two weeks of company training. Stress the last bullet: you will see the CPU model learn the greeting perfectly but invent facts. That is the most important practical lesson."},
            {"title": "Prompt, RAG or fine-tune?", "image": I("decision-prompt-rag-finetune"), "bullets": [
                "Always start with a better prompt", "Missing facts -> RAG",
                "Wrong behaviour + data + eval -> fine-tune", "Often RAG + fine-tune together"],
             "notes": "Walk the decision diagram top to bottom with one example: a support bot that must know return policies (RAG) and always answer in a fixed format (maybe fine-tune). Ask students to classify three scenarios."},
            {"title": "SFT data: the chat format", "bullets": [
                "JSONL: one example per line", "messages: system, user, assistant",
                "Train on the assistant reply", "Quality beats quantity", "Keep a held-out test set"],
             "code": '{"messages": [\n {"role": "system",\n  "content": "You are Chai Corner\'s assistant."},\n {"role": "user",\n  "content": "Do you have Wi-Fi?"},\n {"role": "assistant",\n  "content": "Chai Corner here! Yes ...\n   Have a warm day!"}]}',
             "notes": "Open data/chai_corner_train.jsonl and show a line. The assistant message is what the model learns to produce. Mention LIMA: about a thousand carefully chosen examples can be enough."},
            {"title": "Chat templates and loss masking", "bullets": [
                "Model reads one string with special tokens", "tokenizer.apply_chat_template()",
                "Wrong template = bad fine-tune", "Prompt labels = -100 (ignored)"],
             "code": "<|im_start|>user\nDo you have Wi-Fi?<|im_end|>\n<|im_start|>assistant\nChai Corner here! ...<|im_end|>",
             "notes": "Show notebook 03 step 4 and 5 output. The -100 label tells PyTorch to skip those positions in the loss, so we only learn the answer. TRL does this automatically with prompt/completion data."},
            {"title": "Full fine-tuning vs PEFT", "image": I("full-vs-peft"), "bullets": [
                "Full: every weight + gradients + Adam states", "~16 bytes per parameter",
                "PEFT: freeze base, train a small adapter", "Adapter = MBs, swappable"],
             "notes": "Textbook analogy: reprinting the book versus adding sticky notes. Do the 7B arithmetic: 7 billion times 16 bytes is about 112 GB. No single consumer GPU has that."},
            {"title": "LoRA: the picture", "image": I("lora-matrices"), "bullets": [
                "Keep W frozen", "Learn dW = B x A", "r is small: 4-64", "B starts at zero"],
             "notes": "Recipe-card analogy: every dish is a mix of 8 base sauces. Point at the shapes: B is d by r, A is r by k, so B times A is d by k like W. Because B starts at zero the model is unchanged before training."},
            {"title": "LoRA: the maths", "bullets": [
                "h = W x + (alpha / r) B A x", "Trainable: r(d + k) instead of d x k",
                "4096 x 4096, r = 8 -> 65,536 = 0.39%", "Merge: W' = W + (alpha/r) B A"],
             "code": "class LoRALinear(nn.Module):\n  def forward(self, x):\n    return self.base(x) + \\\n      (x @ self.A.T @ self.B.T) * self.scaling",
             "notes": "Do the parameter count on the board. Then show notebook 01: our 20-line LoRA recovers a hidden rank-2 change, rank 1 underfits, and merging gives identical outputs."},
            {"title": "LoRA settings", "bullets": [
                "r: 8 or 16 to start", "lora_alpha: r or 2r", "lora_dropout: 0.05",
                "target_modules: q,k,v,o_proj or all-linear", "task_type: CAUSAL_LM"],
             "notes": "These are starting points, not laws. Bigger r gives more capacity but more parameters. The learning rate for LoRA is usually around 1e-4 to 2e-4, higher than for full fine-tuning."},
            {"title": "Quantisation", "image": I("quant-levels"), "bullets": [
                "Store weights in fewer bits", "16-bit = 2 bytes, 4-bit = 0.5 bytes",
                "Absmax: scale, round, store integers", "Blocks of 64 tame outliers",
                "NF4: levels dense near zero"],
             "notes": "Rounding prices analogy. The chart shows why NF4 is smart: weights are bell-shaped, so NF4 puts more levels near zero. Notebook 02 measures that NF4-style levels give lower error than uniform ones."},
            {"title": "QLoRA", "image": I("qlora"), "bullets": [
                "Frozen base in 4-bit NF4", "LoRA adapters in 16-bit, trainable",
                "Dequantise on the fly", "Double quantisation + paged optimizers",
                "Fits small models on a free T4"],
             "notes": "QLoRA combines the two halves of today's lesson. Gradients only flow into the adapters. Mention that bitsandbytes needs an NVIDIA GPU, which is why notebook 04 is Colab-only."},
            {"title": "GPU memory, roughly", "bullets": [
                "Inference 16-bit: ~2 bytes/param", "Full FT: ~16 bytes/param",
                "LoRA: ~2 bytes/param + adapter", "QLoRA: ~0.5-0.6 bytes/param + adapter",
                "Plus activations - use the estimator sheet"],
             "notes": "Open excel/gpu-memory-estimator.xlsx and change the parameter count live. A 7B model: about 112 GB full, about 16 GB LoRA, about 5 GB QLoRA. These are planning numbers, not guarantees."},
            {"title": "The Hugging Face stack", "image": I("finetune-workflow"), "bullets": [
                "transformers: models + tokenizers", "peft: LoRA adapters", "trl: SFTTrainer, DPOTrainer",
                "bitsandbytes: 4-bit layers", "datasets: load JSONL"],
             "notes": "Follow the workflow left to right. Point out the loop back from evaluation to data: most improvements come from better data, not from tweaking settings. Libraries change fast; check versions."},
            {"title": "Code: LoRA with peft", "bullets": [
                "Wrap any model in 3 lines", "Only adapters train", "save_pretrained -> MBs"],
             "code": "from peft import LoraConfig, get_peft_model\ncfg = LoraConfig(r=8, lora_alpha=16,\n    target_modules=['q_proj','k_proj',\n                    'v_proj','o_proj'],\n    task_type='CAUSAL_LM')\nmodel = get_peft_model(model, cfg)\nmodel.print_trainable_parameters()",
             "notes": "Run notebook 03 live if the machine is fast enough; otherwise show the saved outputs. The trainable percentage is well under 1 percent for SmolLM2 with these settings."},
            {"title": "Evaluate honestly", "bullets": [
                "Held-out loss, not training loss", "Task metric before vs after",
                "Read 10-20 outputs", "Check general skills did not break", "Notebook 03: style 0% -> most; facts invented"],
             "notes": "Training loss going down proves nothing on its own. Show the before and after table from notebook 03, then read a few answers aloud and ask students to spot invented facts."},
            {"title": "Save, merge, share", "bullets": [
                "save_pretrained: adapter only", "PeftModel.from_pretrained: reload",
                "merge_and_unload: standalone model", "push_to_hub with HF_TOKEN from env",
                "Base model licence still applies"],
             "notes": "For QLoRA, merge into a 16-bit copy of the base, not the 4-bit one. Never put tokens in notebooks; use environment variables or Colab secrets. Add a model card describing data and limitations."},
            {"title": "Common mistakes", "bullets": [
                "Fine-tuning to add facts", "Wrong chat template", "No held-out test set",
                "Learning rate far too high or low", "bf16 on a T4; out-of-memory errors",
                "Leaking a token or private data"],
             "notes": "Go through each and ask who has seen it. For out-of-memory: smaller batch, gradient accumulation, shorter max length, gradient checkpointing, or QLoRA."},
            {"title": "Recap and exercises", "bullets": [
                "Prompt -> RAG -> fine-tune", "LoRA: h = Wx + (alpha/r)BAx", "QLoRA: 4-bit base + LoRA",
                "Measure before/after", "Now: exercises 1-4; homework 5-12"],
             "notes": "One sentence per bullet. Exercises 1 to 4 take about 25 minutes in class. Exercise 12, the Colab QLoRA run with your own dataset, is the capstone of the module."},
        ],
    }
    slides(deck, HERE / "slides" / f"{MOD}.pptx")
    print("slides built")


# ---------------------------------------------------------------------------
# 4. Excel
# ---------------------------------------------------------------------------
def build_excel():
    # GPU memory estimator ------------------------------------------------------
    hdr = ["Model", "Params (billions)", "Method", "Bytes per weight", "Trainable fraction",
           "Extra bytes per trainable param (grads + optimizer)", "Activations + buffer (GB, guess)",
           "Weights (GB)", "Training state (GB)", "Total (GB)", "Fits on 16 GB T4?", "Fits on 24 GB GPU?"]
    method_vals = {"Inference 16-bit": (2, 0, 0, 0.5), "Full fine-tune": (2, 1, 14, 2),
                   "LoRA": (2, 0.005, 16, 2), "QLoRA": (0.55, 0.005, 16, 2)}
    rows = [hdr]
    for model, size in [("Qwen2.5-0.5B (example)", 0.5), ("1.5B model", 1.5), ("7B model", 7), ("13B model", 13)]:
        for m, (bpw, frac, extra, act) in method_vals.items():
            r = len(rows) + 1
            rows.append([model, size, m, bpw, frac, extra, act,
                         f"=B{r}*D{r}", f"=B{r}*E{r}*F{r}", f"=H{r}+I{r}+G{r}",
                         f'=IF(J{r}<=15,"yes","no")', f'=IF(J{r}<=23,"yes","no")'])
    r = len(rows) + 1
    rows.append(["YOUR MODEL - edit B to G", 3, "QLoRA", 0.55, 0.005, 16, 3,
                 f"=B{r}*D{r}", f"=B{r}*E{r}*F{r}", f"=H{r}+I{r}+G{r}",
                 f'=IF(J{r}<=15,"yes","no")', f'=IF(J{r}<=23,"yes","no")'])
    notes = [["Assumption", "Value used", "Why"],
             ["Bytes per weight, 16-bit", "2", "bfloat16/float16 store each number in 2 bytes"],
             ["Bytes per weight, 4-bit (QLoRA)", "0.55", "0.5 for 4 bits plus a little for block scales"],
             ["Full fine-tune extra bytes", "14", "2 gradient + 4 fp32 master copy + 8 Adam states (2 x fp32)"],
             ["LoRA adapter extra bytes", "16", "adapters often kept in fp32: 4 weight + 4 grad + 8 Adam"],
             ["LoRA trainable fraction", "0.005", "typically 0.1%-1% of parameters; check print_trainable_parameters()"],
             ["Activations", "guess", "grow with batch size x sequence length; gradient checkpointing reduces them"],
             ["GB", "1e9 bytes", "decimal gigabytes, for simple mental maths"],
             ["Caveat", "", "Rough planning numbers only. Real usage depends on framework, kernels, sequence length and batch size."]]
    workbook({"Estimator": rows, "Assumptions": notes}, HERE / "excel" / "gpu-memory-estimator.xlsx",
             col_widths={"Estimator": [24, 10, 16, 10, 10, 18, 14, 11, 12, 10, 11, 11], "Assumptions": [32, 12, 80]})

    # Experiment tracker ----------------------------------------------------------
    th = ["Run ID", "Date", "Base model", "Method", "Dataset", "Train examples", "LoRA r", "LoRA alpha",
          "Target modules", "Learning rate", "Epochs", "Batch size", "Grad accumulation", "Effective batch",
          "Steps (approx)", "Max length", "Hardware", "Train time (min)", "Test loss before", "Test loss after",
          "Loss change", "Task metric before", "Task metric after", "Metric change", "Notes / what I learned"]
    def run_row(r, vals):
        v = list(vals)
        v[13] = f'=IF(OR(L{r}="",M{r}=""),"",L{r}*M{r})'                      # effective batch
        v[14] = f'=IFERROR(ROUNDUP(F{r}/N{r},0)*K{r},"")'                      # steps per epoch x epochs
        v[20] = f'=IF(OR(S{r}="",T{r}=""),"",T{r}-S{r})'                      # loss change
        v[23] = f'=IF(OR(V{r}="",W{r}=""),"",W{r}-V{r})'                      # metric change
        return v
    tr = [th]
    tr.append(run_row(2, ["cpu-01", "2026-11-21", "SmolLM2-135M-Instruct", "LoRA", "chai_corner", 48, 8, 16,
                          "q,k,v,o_proj", 0.002, 2.5, 4, 1, "", "", 128, "2-core CPU", 5, 3.28, 1.45, "",
                          0.0, 1.0, "", "Example values from our notebook 03 run (30 steps; style on 6 test questions). Style learned; facts often invented."]))
    tr.append(run_row(3, ["t4-01", "", "Qwen2.5-0.5B-Instruct", "QLoRA", "chai_corner", 48, 16, 32,
                          "all-linear", 0.0002, 3, 4, 2, "", "", 256, "Colab T4", "", "", "", "", "", "", "", ""]))
    for r in range(4, 12):
        tr.append(run_row(r, [""] * 25))
    guide = [["Column", "How to fill it"],
             ["Effective batch", "Formula: batch size x gradient accumulation"],
             ["Steps (approx)", "Formula: ceiling(train examples / effective batch) x epochs"],
             ["Test loss before/after", "Loss on held-out data only - never on training data"],
             ["Task metric", "The number you care about, e.g. style score, accuracy, judge pass rate (0-1)"],
             ["Notes", "One sentence: what changed and what you learned. Change one setting per run."]]
    workbook({"Runs": tr, "How to use": guide}, HERE / "excel" / "finetune-experiment-tracker.xlsx",
             col_widths={"Runs": [9, 11, 22, 8, 12, 9, 7, 7, 14, 9, 7, 7, 9, 9, 9, 8, 12, 9, 9, 9, 9, 9, 9, 9, 50]})
    print("excel built")


def build_pdf():
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / f"{MOD}-handout.pdf",
                      title="Module 13 - Fine-tuning LLMs: SFT, LoRA and QLoRA")
    print("pdf built")


if __name__ == "__main__":
    if "--no-images" not in ARGS:
        build_images()
    if "--no-notebooks" not in ARGS:
        build_notebooks()
    build_slides()
    build_excel()
    if "--no-pdf" not in ARGS:
        build_pdf()
