# Module 05 — Worked Solutions

Runnable code: `solutions.py` (`python solutions.py`, about 1–2 minutes on CPU). Numbers below came from PyTorch 2.15 on CPU; on other machines or a GPU, accuracies can differ by a percent or two — the conclusions should not change.

---

## Exercise 1 — Predict the shape

| Expression | Shape | Why |
|---|---|---|
| `zeros(3,4) @ ones(4,2)` | (3, 2) | (rows of first) × (columns of second) |
| `rand(10,64).reshape(-1,1,8,8)` | (10, 1, 8, 8) | −1 is worked out as 10 |
| `rand(5,3).sum(dim=0)` | (3,) | summing *down* the rows removes dimension 0 |
| `rand(5,3).sum(dim=1)` | (5,) | summing *across* columns removes dimension 1 |
| `rand(32,16,8,8).flatten(1)` | (32, 1024) | keeps the batch, flattens 16×8×8 = 1024 |

## Exercise 2 — Autograd vs pencil

f′(x) = 3x² + 2 → f′(2) = 12 + 2 = **14**. Autograd prints 14.0.

## Exercise 3 — Count parameters

1. Linear(64, 32): 64×32 + 32 = 2,080. Linear(32, 10): 32×10 + 10 = 330. ReLU has none. **Total 2,410.**
2. Conv2d(1, 8, 3): 1×8×3×3 + 8 = **80**. Note how few parameters a conv layer needs — the same 8 small filters are reused at every position.

## Exercise 4 — Cross-entropy by hand

1. −log(0.5) ≈ **0.693**.
2. e² = 7.389, e¹ = 2.718, e⁰ = 1; sum = 11.107. Softmax = [0.665, 0.245, 0.090]. Loss = −log(0.665) ≈ **0.408**. `nn.CrossEntropyLoss` gives the same 0.408 — confirming it applies softmax internally to the logits.

## Exercise 5 — Learning-rate sweep

| lr | val accuracy (20 epochs) |
|---|---|
| 1e-4 | 0.867 — too slow: tiny steps, not yet at the bottom of the hill |
| 1e-3 | 0.953 |
| 1e-2 | **0.975** |
| 1e-1 | 0.964 — starting to be jumpy |
| 1.0 | 0.203 — unstable: steps so big it leaps over the valley and never settles |

On this small problem 1e-2 happens to be best within 20 epochs; 1e-3 is the common safe default and would catch up with more epochs. Always try a few learning rates spaced by factors of 10.

## Exercise 6 — Hidden size

| hidden | params | test acc |
|---|---|---|
| 8 | 610 | 0.786 |
| 32 | 2,410 | 0.925 |
| 128 | 9,610 | 0.956 |
| 512 | 38,410 | 0.969 |

Bigger helped here because 1,077 training images are enough for these sizes. Gains shrink as size grows (diminishing returns), and costs grow. With a tiny training set, a big network would overfit (see notebook 04 and Exercise 9).

## Exercise 7 — The four bugs

1. **No `opt.zero_grad()`** — gradients pile up from every batch, so each step uses a wrong, ever-growing gradient. Add `opt.zero_grad()` before `loss.backward()`.
2. **`nn.Softmax` at the end of the model** — `CrossEntropyLoss` already applies softmax; applying it twice squashes the gradients and slows learning badly. Remove the Softmax layer and output logits.
3. **Labels as `float32`** — with class-index targets, `CrossEntropyLoss` needs `torch.long`; float labels raise an error (or are interpreted as probabilities if shaped like the output). Use `dtype=torch.long`.
4. **No `model.eval()` before evaluating** (and no `model.train()` in the loop) — harmless for this exact model, but with dropout or batch-norm the evaluation would be noisy and wrong. Always switch modes.

Fixed version: `solutions.py → ex7()` (validation accuracy ≈ 0.94 after 20 epochs). On a GPU you would also need `.to(device)` on the model and every batch.

## Exercise 8 — Neural network for regression

MLP test MAE ≈ **40.5** vs LinearRegression ≈ **42.8**. The network is slightly better, but the gain is small, the result moves around with the random seed, and it needed target scaling, a learning rate and an epoch count to be tuned. On small tabular datasets, classic models from module 04 are often just as good and much simpler. Neural networks earn their keep on images, audio, text and very large datasets.

Why standardise the target? Raw targets are around 25–346. Starting from random weights, outputs are near 0, so early losses and gradients are huge and training is unstable. Scaling to mean 0 / spread 1 makes it smooth.

## Exercise 9 — More data beats tricks

| training images | final val loss | test acc |
|---|---|---|
| 200 | 0.263 | 0.925 |
| 1,077 | **0.176** | **0.969** |

Same model, same epochs — only more data. With 85,000 parameters and 200 images the network memorises; with 5× more images there is far less room to memorise and much more real pattern to learn. This is usually a bigger win than dropout or early stopping.

## Exercise 10 — Early-stopping class

See `EarlyStopper` in `solutions.py`. Key points:
- Compare against `best - min_delta` so tiny noise-level improvements do not reset the counter.
- Save a `copy.deepcopy(model.state_dict())` — without `deepcopy` you would store references that keep changing as training continues.
- Call `restore(model)` after the loop.

Result: stopped at epoch 42, best validation loss 0.224, test accuracy 0.928 (vs 0.922 for training the full 150 epochs without protection in notebook 04).

## Exercise 11 — Data augmentation

| CNN | test acc |
|---|---|
| no augmentation | **0.972** |
| random 1-pixel shifts | 0.936 |

It **hurt**. On an 8×8 image, one pixel is 12.5% of the width, and `torch.roll` wraps the column that falls off one side onto the other side, putting stray ink at the far edge. That changes what the digit looks like, so the network is trained on partly misleading examples. The lesson: augmentation must keep the meaning of the example. Ideas that fit tiny images better: shifting with zero-padding instead of wrap-around, shifting only some batches, or adding a little random noise to pixel values. On large photos (224×224), small shifts, flips and crops are standard and help a lot. (Never flip digits horizontally — a flipped 2 is not a 2!)

## Exercise 12 — Checkpoint and resume

Validation loss 0.902 after 5 epochs → 0.380 after resuming for 5 more: training clearly continued from the saved point rather than starting again (a fresh model would be back near 2.3).

Why the optimizer state matters: Adam keeps running averages of each weight's past gradients (its "momentum" and step-size memory). If you reload only the model weights with a fresh Adam, those averages restart from zero, causing a bumpy restart. Saving `opt.state_dict()` resumes smoothly.
