"""
attention_numpy.py - self-attention computed by hand for the 3-word sentence "the cat sat".

Run:  python attention_numpy.py
Needs: numpy, matplotlib  (both come with the course requirements)

Nothing here is trained. The small matrices are hand-made so that every number
can be checked with a calculator. A real transformer does exactly these steps,
only with learned matrices that have hundreds or thousands of columns.
"""
import numpy as np                      # numpy does the matrix maths
import matplotlib                       # matplotlib draws the heatmap
matplotlib.use("Agg")                   # "Agg" = draw to a file, no window needed
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. The words and their embeddings (one row per word, 4 numbers per word)
# ---------------------------------------------------------------------------
words = ["the", "cat", "sat"]           # our tiny sentence
X = np.array([
    [1.0, 0.0, 0.0, 0.2],               # "the": a small function word
    [0.0, 1.0, 0.8, 0.0],               # "cat": a noun (thing)
    [0.0, 0.6, 1.0, 1.0],               # "sat": a verb that needs a "thing" doing it
])                                      # shape (3 words, 4 numbers)

# ---------------------------------------------------------------------------
# 2. The three weight matrices that turn embeddings into Q, K and V
#    Each is 4 x 3: 4 numbers in, 3 numbers out (d = 3).
# ---------------------------------------------------------------------------
W_q = np.array([[0.5, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.5, 1.0],
                [0.0, 1.0, 0.5]])       # makes "queries": what each word is looking for
W_k = np.array([[0.3, 0.0, 0.0],
                [0.0, 1.0, 0.5],
                [0.0, 0.5, 0.5],
                [0.2, 0.0, 0.0]])       # makes "keys": the label each word offers
W_v = np.array([[1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.0, 0.5, 0.5]])       # makes "values": the information each word hands over


def softmax(scores):
    """Turn each row of scores into positive weights that add up to 1."""
    shifted = scores - scores.max(axis=-1, keepdims=True)   # subtract the row max so exp() never overflows
    e = np.exp(shifted)                                      # e to the power of each score
    return e / e.sum(axis=-1, keepdims=True)                 # divide by the row total


def self_attention(X, causal=False):
    """Return (weights, output) for embeddings X using the matrices above."""
    Q = X @ W_q                         # @ means matrix multiply: every word gets a query vector
    K = X @ W_k                         # ... a key vector
    V = X @ W_v                         # ... and a value vector
    d = Q.shape[1]                      # size of each query/key vector (3 here)
    scores = Q @ K.T / np.sqrt(d)       # step 1+2: every query dotted with every key, then scaled by sqrt(d)
    if causal:                          # optional: a text generator may not look at future words
        future = np.triu(np.ones_like(scores), k=1).astype(bool)   # True above the diagonal
        scores = np.where(future, -np.inf, scores)                 # -infinity becomes weight 0 after softmax
    weights = softmax(scores)           # step 3: each row now sums to 1
    output = weights @ V                # step 4: blend the value vectors using the weights
    return weights, output


def plot_heatmap(weights, title, path):
    """Save a labelled heatmap of the attention weights."""
    fig, ax = plt.subplots(figsize=(4.6, 3.8))
    im = ax.imshow(weights, cmap="Blues", vmin=0, vmax=1)            # darker blue = more attention
    ax.set_xticks(range(len(words)), labels=words)                   # columns: words being looked at
    ax.set_yticks(range(len(words)), labels=words)                   # rows: the word doing the looking
    ax.set_xlabel("attends to (key)")
    ax.set_ylabel("word (query)")
    for i in range(len(words)):                                      # write each weight inside its square
        for j in range(len(words)):
            ax.text(j, i, f"{weights[i, j]:.2f}", ha="center", va="center",
                    color="white" if weights[i, j] > 0.5 else "black")
    ax.set_title(title)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    w, out = self_attention(X)                         # full (two-way) attention
    print("Attention weights (rows = query word):")
    print(np.round(w, 2))
    print("Each row sums to:", np.round(w.sum(axis=1), 6))
    print("New vector for each word after attention:")
    print(np.round(out, 2))
    wc, _ = self_attention(X, causal=True)             # masked version used by text generators
    print("Causal (masked) weights:")
    print(np.round(wc, 2))
    plot_heatmap(w, "Self-attention: 'the cat sat'", "attention_heatmap.png")
    print("Saved attention_heatmap.png")
