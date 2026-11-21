"""
sampling_demo.py - how temperature and top-p change which token gets picked.

Run:  python sampling_demo.py
Needs: numpy, matplotlib. Saves sampling_demo.png next to where you run it.
Uses a made-up list of next-token scores so it runs instantly with no model download.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")                                   # draw to a file, no window
import matplotlib.pyplot as plt

tokens = [" Paris", " the", " located", " called", " a", " Lyon", " not", " known"]
logits = np.array([4.0, 3.4, 2.2, 0.7, 0.5, 0.2, -0.3, -0.8])   # raw scores (higher = more likely)


def softmax(x):
    e = np.exp(x - x.max())                             # subtract max for numerical safety
    return e / e.sum()


def apply_temperature(logits, T):
    """Divide scores by T before softmax: T<1 sharpens, T>1 flattens."""
    return softmax(logits / T)


def top_p_filter(probs, p=0.9):
    """Keep the smallest set of top tokens whose probabilities add up to at least p, then renormalise."""
    order = np.argsort(probs)[::-1]                     # indices from most to least likely
    cumulative = np.cumsum(probs[order])                # running total
    keep = order[: int(np.searchsorted(cumulative, p)) + 1]   # first position where the total reaches p
    filtered = np.zeros_like(probs)
    filtered[keep] = probs[keep]
    return filtered / filtered.sum(), keep


rng = np.random.default_rng(0)                          # fixed seed = repeatable "random" picks
for T in [0.2, 1.0, 1.8]:
    probs = apply_temperature(logits, T)
    picks = rng.choice(len(tokens), size=20, p=probs)   # sample 20 times
    print(f"T={T}: probs={np.round(probs, 2)}")
    print("        20 samples:", "".join(tokens[i] for i in picks[:20]).replace(" ", "|")[:120])

probs = apply_temperature(logits, 1.0)
filtered, keep = top_p_filter(probs, 0.9)
print("\nTop-p 0.9 keeps:", [tokens[i] for i in keep])

fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
for ax, T in zip(axes, [0.2, 1.0, 1.8]):
    ax.bar(tokens, apply_temperature(logits, T), color="#0F9D9A")
    ax.set_title(f"temperature = {T}")
    ax.tick_params(axis="x", rotation=45)
axes[0].set_ylabel("probability")
fig.tight_layout()
fig.savefig("sampling_demo.png", dpi=120)
print("Saved sampling_demo.png")
