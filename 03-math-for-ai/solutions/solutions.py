"""
solutions.py - runnable answers to every exercise in 03-math-for-ai/exercises.md.

Run:   python 03-math-for-ai/solutions/solutions.py
"""
from pathlib import Path                                   # file paths

import matplotlib                                          # plotting
matplotlib.use("Agg")                                      # save to file, no window
import matplotlib.pyplot as plt
import numpy as np                                         # arrays

OUT = Path(__file__).resolve().parent.parent / "outputs"   # results (ignored by git)
OUT.mkdir(exist_ok=True)


def cosine_similarity(u, v):
    return (u @ v) / (np.linalg.norm(u) * np.linalg.norm(v))   # dot product divided by both lengths


def ex1():
    a, b = np.array([2, -1, 3]), np.array([1, 4, 0])
    print("a+b =", a + b, "| 3a =", 3 * a, "| |a| =", round(np.linalg.norm(a), 3), "| a.b =", a @ b)


def ex2():
    order, prices = np.array([2, 3, 1]), np.array([20, 15, 60])   # tea, samosa, cake
    print("bill:", order @ prices)


def ex3():
    for u, v in [([1, 0], [0, 5]), ([2, 3], [4, 6]), ([1, 1], [-1, -2])]:
        print(u, v, "dot =", np.dot(u, v))


def ex4():
    u = np.array([1.0, 2.0, -1.0])
    print("cos(u, 5u) =", round(cosine_similarity(u, 5 * u), 6), "| dot u.u =", u @ u, "| dot u.5u =", u @ (5 * u))


WORDS = {
    "cat": [1, 0, 0.2, 1], "dog": [1, 0, 0.4, 1], "lion": [1, 0, 0.7, 0],
    "car": [0, 1, 0.5, 0], "truck": [0, 1, 0.9, 0], "bike": [0, 0.8, 0.2, 0.1],
    "hamster": [1, 0, 0.05, 1], "bus": [0, 1, 1.0, 0], "elephant": [1, 0, 1.0, 0],
}
WORDS = {k: np.array(v, dtype=float) for k, v in WORDS.items()}


def search(query, k=3):
    scores = {w: float(cosine_similarity(query, v)) for w, v in WORDS.items()}
    return [(w, round(s, 3)) for w, s in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:k]]


def ex5():
    print("small pet:", search(np.array([1, 0, 0.0, 1]), k=3))


def ex6():
    for sa, sb in [((4, 3), (3, 2)), ((2, 5), (2, 5)), ((1, 3), (3, 1)), ((3, 1), (1, 3))]:
        try:
            print(sa, "@", sb, "->", (np.ones(sa) @ np.ones(sb)).shape)
        except ValueError:
            print(sa, "@", sb, "-> not allowed (inner sizes differ)")


def ex7():
    A, B = np.array([[1, 2], [0, 1]]), np.array([[3, 0], [1, 2]])
    print("A@B =\n", A @ B, "\nB@A =\n", B @ A)


def ex8():
    t = np.array([3, 5, 4, 6, 2, 8, 7], dtype=float)
    print("deviations:", t - t.mean())
    print(f"mean {t.mean():.3f} var {t.var():.3f} std {t.std():.3f}")
    t2 = np.append(t, 20)
    print(f"with a 20h day: mean {t2.mean():.3f} std {t2.std():.3f}")


def softmax(z, temperature=1.0):
    z = np.asarray(z, float) / temperature
    e = np.exp(z - z.max())
    return e / e.sum()


def ex9():
    s = np.array([1.0, 2.0, 3.0])
    print("exp:", np.exp(s).round(3), "total:", np.exp(s).sum().round(3))
    for t in [1, 0.5, 5]:
        print(f"T={t}:", softmax(s, t).round(3))
    print("scores + 100:", softmax(s + 100).round(3))


def numerical_derivative(f, x, h=1e-5):
    return (f(x + h) - f(x)) / h


def ex10():
    f = lambda x: x ** 3 - 2 * x
    for x in [0, 1, 2]:
        print(f"x={x}: estimate {numerical_derivative(f, x):.4f}, exact {3 * x ** 2 - 2}")


def run_gd(lr, w=10.0, steps=20):
    for _ in range(steps):
        w = w - lr * 2 * (w - 3)
    return w


def ex11():
    for lr in [0.01, 0.1, 0.5, 0.9, 1.1]:
        print(f"lr={lr}: final w = {run_gd(lr):.4f}")


def ex12():
    x = np.array([1, 2, 3, 4, 5, 6], dtype=float)
    y = np.array([52, 55, 61, 64, 70, 73], dtype=float)
    w, b, lr, losses = 0.0, 0.0, 0.03, []
    for _ in range(5000):
        err = w * x + b - y
        losses.append(np.mean(err ** 2))
        w -= lr * 2 * np.mean(err * x)
        b -= lr * 2 * np.mean(err)
    print(f"gradient descent: w={w:.3f} b={b:.3f} MSE={losses[-1]:.3f}")
    print("polyfit:", np.round(np.polyfit(x, y, 1), 3))
    print(f"prediction for 7 hours: {w * 7 + b:.1f}")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.5))
    a1.plot(losses); a1.set_yscale("log"); a1.set_title("MSE per step"); a1.set_xlabel("step")
    a2.scatter(x, y); a2.plot(x, w * x + b, color="red"); a2.set_title("fitted line"); a2.set_xlabel("hours"); a2.set_ylabel("score")
    fig.tight_layout(); fig.savefig(OUT / "ex12_line_fit.png", dpi=110); plt.close(fig)


if __name__ == "__main__":
    for i, f in enumerate([ex1, ex2, ex3, ex4, ex5, ex6, ex7, ex8, ex9, ex10, ex11, ex12], start=1):
        print(f"\n===== Exercise {i} =====")
        f()
