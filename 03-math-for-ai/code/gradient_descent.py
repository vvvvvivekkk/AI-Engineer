"""
gradient_descent.py - gradient descent from scratch:
  1. on a one-weight loss, printing every step and saving one PNG frame per step;
  2. fitting a straight line y = w*x + b to noisy data.

Run:   python 03-math-for-ai/code/gradient_descent.py
Frames are written to 03-math-for-ai/outputs/gd_frames/ (ignored by git).
"""
from pathlib import Path                                   # file paths

import matplotlib                                          # plotting
matplotlib.use("Agg")                                      # draw to files, no window
import matplotlib.pyplot as plt
import numpy as np                                         # arrays

OUT = Path(__file__).resolve().parent.parent / "outputs" / "gd_frames"   # where frames go
OUT.mkdir(parents=True, exist_ok=True)                     # create the folder if needed


def loss(w):
    """A simple bowl-shaped loss with its lowest point at w = 3."""
    return (w - 3) ** 2 + 1


def slope(w, h=1e-5):
    """Numerical derivative: how much the loss changes for a tiny step h."""
    return (loss(w + h) - loss(w - h)) / (2 * h)           # centred version: a bit more accurate


# --- Part 1: one weight -------------------------------------------------------------------
w, lr = -1.0, 0.2                                          # starting weight and learning rate (step size)
xs = np.linspace(-2, 7, 200)                               # x values for drawing the curve
for step in range(8):
    s = slope(w)                                           # which way is uphill, and how steep
    new_w = w - lr * s                                     # step the OTHER way (downhill)
    print(f"step {step}: w={w:6.3f} loss={loss(w):6.3f} slope={s:6.3f} -> new w={new_w:6.3f}")
    fig, ax = plt.subplots(figsize=(6, 3.5))               # one frame per step
    ax.plot(xs, loss(xs), color="#1B263B")                 # the loss curve
    ax.plot(w, loss(w), "o", color="#D1495B", ms=10)       # where we are now
    ax.annotate("", xy=(new_w, loss(new_w)), xytext=(w, loss(w)),
                arrowprops=dict(arrowstyle="-|>", color="#0F9D9A", lw=2))   # where we go next
    ax.set_ylim(0, 20)
    ax.set_title(f"step {step}: w = {w:.2f}")
    fig.savefig(OUT / f"frame_{step + 1:02d}.png", dpi=90, bbox_inches="tight")
    plt.close(fig)                                         # free memory before the next frame
    w = new_w                                              # move to the new position
print("frames saved in", OUT)

# --- Part 2: fit a line ---------------------------------------------------------------------
rng = np.random.default_rng(42)                            # repeatable noise
x = np.linspace(0, 5, 20)                                  # 20 x values
y = 2 * x + 1 + rng.normal(0, 0.8, x.size)                 # true line y = 2x + 1, plus noise

w, b, lr = 0.0, 0.0, 0.05                                  # start with a flat line
for step in range(201):
    pred = w * x + b                                       # 1. predict
    err = pred - y                                         # 2. how far off each prediction is
    mse = np.mean(err ** 2)                                # 3. loss = mean squared error
    dw = 2 * np.mean(err * x)                              # 4. slope of the loss with respect to w
    db = 2 * np.mean(err)                                  #    slope of the loss with respect to b
    w, b = w - lr * dw, b - lr * db                        # 5. step downhill for both
    if step % 50 == 0:
        print(f"step {step:3d}: MSE={mse:7.3f}  w={w:.3f}  b={b:.3f}")
print(f"learned y = {w:.2f}x + {b:.2f}  (data was made from y = 2x + 1)")
