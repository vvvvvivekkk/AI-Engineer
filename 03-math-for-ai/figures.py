"""
figures.py - draws every matplotlib picture used in Module 03 (called by build.py).

Each function saves one PNG into images/. The gradient-descent "animation" is saved as a
sequence of still frames in images/gd_frames/ plus one combined strip image.
"""
from __future__ import annotations

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE / "images"
NAVY, TEAL, RED, GREY, ORANGE = "#1B263B", "#0F9D9A", "#D1495B", "#5A6370", "#F28C28"


def save(fig, name):
    IMG.mkdir(exist_ok=True)
    fig.savefig(IMG / name, dpi=150, bbox_inches="tight")
    plt.close(fig)


def arrow(ax, start, vec, color, label=None, lw=2.5):
    ax.annotate("", xy=(start[0] + vec[0], start[1] + vec[1]), xytext=start,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=18))
    if label:
        ax.text(start[0] + vec[0] * 1.05, start[1] + vec[1] * 1.05 + 0.15, label, color=color, fontsize=12, weight="bold")


def setup_plane(ax, lim=(-1, 6), ylim=None):
    ylim = ylim or lim
    ax.set_xlim(*lim); ax.set_ylim(*ylim); ax.set_aspect("equal")
    ax.axhline(0, color=GREY, lw=0.8); ax.axvline(0, color=GREY, lw=0.8)
    ax.grid(alpha=0.3)


def fig_vectors():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    ax = axes[0]; setup_plane(ax, (-1, 5), (-1, 4))
    arrow(ax, (0, 0), (3, 2), NAVY, "[3, 2]")
    arrow(ax, (0, 0), (1, 3), TEAL, "[1, 3]")
    ax.plot(3, 2, "o", color=NAVY)
    ax.set_title("A vector is an arrow from (0, 0)\nand also a list of numbers", color=NAVY)
    ax = axes[1]; setup_plane(ax, (-1, 6), (-1, 6))
    arrow(ax, (0, 0), (3, 2), NAVY, "a = [3, 2]")
    arrow(ax, (3, 2), (1, 3), TEAL, "b = [1, 3]")
    arrow(ax, (0, 0), (4, 5), RED, "a + b = [4, 5]")
    ax.set_title("Adding vectors: tip to tail", color=NAVY)
    save(fig, "vectors_arrows.png")


def fig_dot_angles():
    cases = [((3, 1), (2.5, 1.5), "same direction"), ((3, 1), (-1, 3), "right angle"), ((3, 1), (-2.5, -1.2), "opposite")]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
    for ax, (a, b, name) in zip(axes, cases):
        setup_plane(ax, (-3.5, 3.5))
        arrow(ax, (0, 0), a, NAVY, "a"); arrow(ax, (0, 0), b, TEAL, "b")
        dot = a[0] * b[0] + a[1] * b[1]
        cos = dot / (np.hypot(*a) * np.hypot(*b))
        ax.set_title(f"{name}\na · b = {dot:.1f}   cosine = {cos:.2f}", color=NAVY)
    save(fig, "dot_product_angles.png")


WORDS = {"lion": (0.35, 1.15), "puppy": (0.75, 1.05), "cat": (1.05, 0.85), "dog": (1.2, 0.5),
         "car": (0.25, -1.05), "truck": (0.7, -0.95), "bus": (1.1, -0.6)}


def fig_word_vectors():
    fig, ax = plt.subplots(figsize=(8.5, 6))
    setup_plane(ax, (-1.0, 1.6), (-1.3, 1.4))
    for w, v in WORDS.items():
        col = TEAL if v[1] > 0 else NAVY
        arrow(ax, (0, 0), v, col, None, lw=1.8)
        ax.text(v[0] + 0.03, v[1] + 0.03, w, fontsize=12, color=col, weight="bold")
    def cos(a, b):
        a, b = np.array(WORDS[a]), np.array(WORDS[b])
        return a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
    ax.text(-0.95, 0.15, f"cos(cat, dog) = {cos('cat', 'dog'):.2f}\ncos(car, truck) = {cos('car', 'truck'):.2f}\n"
                          f"cos(cat, truck) = {cos('cat', 'truck'):.2f}", fontsize=11, color=NAVY,
            bbox=dict(facecolor="white", edgecolor=GREY))
    ax.set_title("Toy 2-D 'embeddings': similar meaning -> similar direction", color=NAVY)
    ax.set_xlabel("made-up feature 1"); ax.set_ylabel("made-up feature 2 (animal +, vehicle -)")
    save(fig, "word_vectors_2d.png")


def fig_matrix_transform():
    mats = [("original", np.eye(2)), ("scale [[2,0],[0,1]]", np.array([[2, 0], [0, 1]])),
            ("rotate 90° [[0,-1],[1,0]]", np.array([[0, -1], [1, 0]])), ("shear [[1,1],[0,1]]", np.array([[1, 1], [0, 1]]))]
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.2))
    g = np.linspace(-1, 1, 5)
    for ax, (name, M) in zip(axes, mats):
        setup_plane(ax, (-2.6, 2.6))
        for v in g:
            line = np.array([[v, t] for t in np.linspace(-1, 1, 20)]) @ M.T
            ax.plot(line[:, 0], line[:, 1], color=TEAL, lw=1)
            line = np.array([[t, v] for t in np.linspace(-1, 1, 20)]) @ M.T
            ax.plot(line[:, 0], line[:, 1], color=TEAL, lw=1)
        sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1]]) @ M.T
        ax.add_patch(Polygon(sq, closed=True, facecolor=ORANGE, alpha=0.5, edgecolor=ORANGE))
        e1, e2 = M @ np.array([1, 0]), M @ np.array([0, 1])
        arrow(ax, (0, 0), e1, RED); arrow(ax, (0, 0), e2, NAVY)
        ax.set_title(name, color=NAVY)
    fig.suptitle("A 2x2 matrix moves every point of the grid (orange = the unit square)", color=GREY)
    save(fig, "matrix_transform.png")


def fig_matmul():
    A = np.array([[1, 2], [3, 4], [5, 6]])
    B = np.array([[7, 8, 9], [10, 11, 12]])
    C = A @ B
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.set_xlim(0, 15); ax.set_ylim(-0.5, 5); ax.axis("off")
    def grid(M, x0, y0, title, hl_row=None, hl_col=None, hl_cell=None):
        r, c = M.shape
        for i in range(r):
            for j in range(c):
                face = "#E8EEF2"
                if hl_row is not None and i == hl_row: face = "#BFE6E5"
                if hl_col is not None and j == hl_col: face = "#F9D9A6"
                if hl_cell == (i, j): face = ORANGE
                ax.add_patch(Rectangle((x0 + j, y0 - i), 1, 1, facecolor=face, edgecolor=NAVY))
                ax.text(x0 + j + 0.5, y0 - i + 0.5, str(M[i, j]), ha="center", va="center", fontsize=13, color=NAVY)
        ax.text(x0 + c / 2, y0 + 1.3, title, ha="center", fontsize=12, color=NAVY, weight="bold")
    grid(A, 0.5, 3, "A  (3 x 2)", hl_row=1)
    ax.text(3.0, 2.0, "@", fontsize=22, color=NAVY, ha="center", va="center")
    grid(B, 3.8, 3, "B  (2 x 3)", hl_col=2)
    ax.text(7.5, 2.0, "=", fontsize=22, color=NAVY, ha="center", va="center")
    grid(C, 8.3, 3, "C  (3 x 3)", hl_cell=(1, 2))
    ax.text(7.5, -0.3, f"C[1, 2] = row 1 of A · column 2 of B = 3×9 + 4×12 = {C[1, 2]}", ha="center", fontsize=13,
            color=NAVY, bbox=dict(facecolor="white", edgecolor=ORANGE))
    ax.text(13.0, 3.5, "shape rule:\n(3 x 2) @ (2 x 3)\ninner 2 = 2 ok\nresult (3 x 3)", fontsize=11, color=GREY, va="top")
    save(fig, "matmul_visual.png")


def fig_distributions():
    rng = np.random.default_rng(42)
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    axes[0].hist(rng.integers(1, 7, 6000), bins=np.arange(0.5, 7.5, 1), color=TEAL, edgecolor="white", rwidth=0.85)
    axes[0].set_title("Uniform: fair die, 6000 rolls"); axes[0].set_xlabel("face")
    axes[1].hist(rng.normal(165, 8, 6000), bins=40, color=NAVY, edgecolor="white")
    axes[1].set_title("Normal: heights (mean 165, std 8)"); axes[1].set_xlabel("cm")
    axes[2].hist(rng.binomial(10, 0.5, 6000), bins=np.arange(-0.5, 11.5, 1), color=ORANGE, edgecolor="white", rwidth=0.85)
    axes[2].set_title("Binomial: heads in 10 flips"); axes[2].set_xlabel("number of heads")
    for ax in axes: ax.set_ylabel("count")
    fig.tight_layout(); save(fig, "distributions.png")


def fig_mean_variance():
    x = np.linspace(130, 200, 400)
    pdf = lambda m, s: np.exp(-((x - m) ** 2) / (2 * s * s)) / (s * np.sqrt(2 * np.pi))
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(x, pdf(165, 4), color=TEAL, lw=2.5, label="std = 4 (tight)")
    ax.plot(x, pdf(165, 12), color=NAVY, lw=2.5, label="std = 12 (spread out)")
    ax.axvline(165, color=RED, ls="--", label="same mean = 165")
    ax.fill_between(x, pdf(165, 12), where=(x > 153) & (x < 177), color=NAVY, alpha=0.12, label="±1 std ≈ 68 % of values")
    ax.set_title("Same mean, different variance", color=NAVY); ax.set_xlabel("height (cm)"); ax.set_ylabel("how likely")
    ax.legend(); save(fig, "mean_variance.png")


def softmax(z, t=1.0):
    z = np.asarray(z, float) / t
    e = np.exp(z - z.max())
    return e / e.sum()


def fig_softmax_temperature():
    words = ["cat", "dog", "car", "tree", "sky"]
    logits = np.array([3.0, 2.2, 1.0, 0.4, -0.5])
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), sharey=True)
    for ax, t, col in zip(axes, [0.5, 1.0, 2.0], [NAVY, TEAL, ORANGE]):
        p = softmax(logits, t)
        ax.bar(words, p, color=col)
        for i, v in enumerate(p): ax.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=10)
        ax.set_title(f"temperature = {t}", color=NAVY); ax.set_ylim(0, 1.05)
    axes[0].set_ylabel("probability")
    fig.suptitle("Same logits [3.0, 2.2, 1.0, 0.4, -0.5] -> softmax at three temperatures", color=GREY)
    fig.tight_layout(); save(fig, "softmax_temperature.png")


def fig_derivative():
    f = lambda x: 0.5 * (x - 2) ** 2 + 1
    df = lambda x: (x - 2)
    x = np.linspace(-1.5, 5.5, 200)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(x, f(x), color=NAVY, lw=2.5, label="f(x) = 0.5(x - 2)² + 1")
    for x0, col in [(0, RED), (2, TEAL), (4.5, ORANGE)]:
        xs = np.linspace(x0 - 1.2, x0 + 1.2, 10)
        ax.plot(xs, f(x0) + df(x0) * (xs - x0), color=col, lw=2, ls="--")
        ax.plot(x0, f(x0), "o", color=col, ms=9)
        ax.text(x0, f(x0) - 0.9, f"slope = {df(x0):+.1f}", color=col, ha="center", fontsize=11, weight="bold")
    ax.set_ylim(-0.5, 9); ax.set_title("The derivative = the slope of the tangent line at a point", color=NAVY)
    ax.set_xlabel("x"); ax.set_ylabel("f(x)"); ax.legend(loc="upper center")
    save(fig, "derivative_slope.png")


# ------------------------------------------------------------- gradient descent
LOSS = lambda w: (w - 3) ** 2 + 1
GRAD = lambda w: 2 * (w - 3)


def gd_path(w0=-1.0, lr=0.2, steps=8):
    ws = [w0]
    for _ in range(steps):
        ws.append(ws[-1] - lr * GRAD(ws[-1]))
    return np.array(ws)


def draw_gd_frame(ax, ws, k, lr):
    x = np.linspace(-2, 7, 200)
    ax.plot(x, LOSS(x), color=NAVY, lw=2)
    ax.plot(ws[:k], LOSS(ws[:k]), "o", color=GREY, alpha=0.5, ms=6)
    w = ws[k]
    xs = np.linspace(w - 1.3, w + 1.3, 10)
    ax.plot(xs, LOSS(w) + GRAD(w) * (xs - w), color=ORANGE, ls="--", lw=1.5)
    ax.plot(w, LOSS(w), "o", color=RED, ms=11)
    if k + 1 < len(ws):
        ax.annotate("", xy=(ws[k + 1], LOSS(ws[k + 1])), xytext=(w, LOSS(w)),
                    arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=2))
    ax.axvline(3, color=TEAL, ls=":", lw=1)
    ax.set_ylim(0, 20); ax.set_xlim(-2, 7)
    ax.set_title(f"step {k}: w = {w:.2f}, loss = {LOSS(w):.2f}, slope = {GRAD(w):.2f}", fontsize=10, color=NAVY)
    ax.set_xlabel("w"); ax.set_ylabel("loss")


def fig_gd_frames():
    lr = 0.2
    ws = gd_path(lr=lr, steps=8)
    out = IMG / "gd_frames"; out.mkdir(parents=True, exist_ok=True)
    for k in range(8):
        fig, ax = plt.subplots(figsize=(7, 4.2))
        draw_gd_frame(ax, ws, k, lr)
        ax.text(-1.8, 18.5, f"new w = w - {lr} × slope", fontsize=10, color=GREY)
        fig.savefig(out / f"gd_frame_{k + 1:02d}.png", dpi=120, bbox_inches="tight"); plt.close(fig)
    fig, axes = plt.subplots(2, 4, figsize=(18, 7.5))
    for k, ax in enumerate(axes.flat):
        draw_gd_frame(ax, ws, k, lr)
    fig.suptitle("Gradient descent on loss(w) = (w - 3)² + 1, start w = -1, learning rate 0.2 (read left to right)",
                 color=NAVY, fontsize=14)
    fig.tight_layout(); save(fig, "gd_strip.png")


def fig_learning_rates():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    x = np.linspace(-4, 10, 200)
    for ax, lr, name in zip(axes, [0.03, 0.3, 1.05], ["too small (0.03)", "about right (0.3)", "too large (1.05)"]):
        ws = gd_path(w0=-1.0, lr=lr, steps=10)
        ax.plot(x, LOSS(x), color=NAVY, lw=2)
        ax.plot(ws, LOSS(ws), "-o", color=RED, ms=5, lw=1)
        ax.set_ylim(0, 60); ax.set_xlim(-4, 10)
        ax.set_title(f"learning rate {name}\nafter 10 steps w = {ws[-1]:.2f}", color=NAVY)
        ax.set_xlabel("w"); ax.set_ylabel("loss")
    fig.tight_layout(); save(fig, "learning_rates.png")


def fig_gd_contour():
    L = lambda a, b: a ** 2 + 4 * b ** 2
    a, b = np.meshgrid(np.linspace(-5, 5, 200), np.linspace(-3, 3, 200))
    p = np.array([-4.5, 2.5]); path = [p.copy()]
    for _ in range(25):
        g = np.array([2 * p[0], 8 * p[1]])
        p = p - 0.1 * g; path.append(p.copy())
    path = np.array(path)
    fig, ax = plt.subplots(figsize=(8, 5))
    cs = ax.contour(a, b, L(a, b), levels=[0.5, 2, 5, 10, 20, 35, 50], cmap="viridis")
    ax.clabel(cs, fontsize=8)
    ax.plot(path[:, 0], path[:, 1], "-o", color=RED, ms=4)
    ax.plot(0, 0, "*", color=ORANGE, ms=18, label="minimum (lowest loss)")
    ax.set_xlabel("weight 1"); ax.set_ylabel("weight 2"); ax.legend()
    ax.set_title("Two weights: loss = w1² + 4·w2², gradient descent path (lr 0.1)", color=NAVY)
    save(fig, "gd_contour_2d.png")


def fig_loss_functions():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    e = np.linspace(-3, 3, 200)
    axes[0].plot(e, e ** 2, color=NAVY, lw=2.5); axes[0].plot(e, np.abs(e), color=GREY, ls="--", label="|error| for comparison")
    axes[0].set_title("Squared error: big mistakes cost much more"); axes[0].set_xlabel("prediction - true value"); axes[0].set_ylabel("loss")
    axes[0].legend()
    p = np.linspace(0.005, 1, 200)
    axes[1].plot(p, -np.log(p), color=RED, lw=2.5)
    for pv in [0.9, 0.5, 0.1]:
        axes[1].plot(pv, -np.log(pv), "o", color=NAVY); axes[1].text(pv + 0.02, -np.log(pv) + 0.2, f"p={pv}: {-np.log(pv):.2f}")
    axes[1].set_title("Cross-entropy: -log(probability of the correct answer)"); axes[1].set_xlabel("probability given to the correct answer")
    axes[1].set_ylabel("loss"); axes[1].set_ylim(0, 5.5)
    fig.tight_layout(); save(fig, "loss_functions.png")


def fit_line_gd(x, y, lr=0.05, steps=200):
    w, b = 0.0, 0.0
    hist = [(w, b, np.mean((w * x + b - y) ** 2))]
    for _ in range(steps):
        err = w * x + b - y
        w -= lr * 2 * np.mean(err * x)
        b -= lr * 2 * np.mean(err)
        hist.append((w, b, np.mean((w * x + b - y) ** 2)))
    return hist


def fig_line_fit():
    rng = np.random.default_rng(42)
    x = np.linspace(0, 5, 20); y = 2 * x + 1 + rng.normal(0, 0.8, x.size)
    hist = fit_line_gd(x, y)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].scatter(x, y, color=NAVY, label="data")
    for k, col in zip([0, 3, 15, 200], ["#BBBBBB", "#F7C59F", ORANGE, RED]):
        w, b, l = hist[k]
        axes[0].plot(x, w * x + b, color=col, lw=2, label=f"step {k}: y = {w:.2f}x + {b:.2f}")
    axes[0].set_title("Fitting y = w·x + b by gradient descent"); axes[0].legend(fontsize=9); axes[0].set_xlabel("x"); axes[0].set_ylabel("y")
    axes[1].plot([h[2] for h in hist], color=TEAL, lw=2)
    axes[1].set_yscale("log"); axes[1].set_title("Loss (MSE) goes down with every step"); axes[1].set_xlabel("step"); axes[1].set_ylabel("MSE (log scale)")
    fig.tight_layout(); save(fig, "line_fit_gd.png")


def all_figures():
    fig_vectors(); fig_dot_angles(); fig_word_vectors(); fig_matrix_transform(); fig_matmul()
    fig_distributions(); fig_mean_variance(); fig_softmax_temperature(); fig_derivative()
    fig_gd_frames(); fig_learning_rates(); fig_gd_contour(); fig_loss_functions(); fig_line_fit()
