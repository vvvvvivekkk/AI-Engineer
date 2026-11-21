"""
nb_cells.py - the text and code of every notebook in module 03 (used by build.py).
Edit notebooks here, then rerun build.py. No data files or internet are needed.
"""

SETUP = """import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(precision=3, suppress=True)   # print numbers neatly
NAVY, TEAL, RED, ORANGE = "#1B263B", "#0F9D9A", "#D1495B", "#F28C28"   # course colours"""


def nb01_vectors():
    return [
        ("md", """# 01 · Vectors, dot product and cosine similarity

**What you will learn**
- a **vector** is a list of numbers *and* an arrow
- adding and scaling vectors, and a vector's **length**
- the **dot product** ("multiply matching pairs, then add") and what its sign means
- **cosine similarity**, the number behind semantic search and RAG
- a first look at **embeddings** with toy word vectors

Intuition only: no proofs. Run each cell with Shift + Enter."""),
        ("md", """## 0. Setup

We import NumPy (arrays) and matplotlib (charts), and set a few colours."""),
        ("code", SETUP),
        ("md", """## 1. A vector is a list of numbers

A house described by `[bedrooms, bathrooms, area in 100 sq ft]`. Each position always means the same thing. The number of entries is the vector's **dimension**."""),
        ("code", """house = np.array([3, 2, 14])
print("vector:", house, "| dimension:", house.size)"""),
        ("md", """## 2. …and an arrow

A 2-D vector `[3, 2]` is an arrow from `(0, 0)` to the point `(3, 2)`. `quiver` draws arrows; the extra arguments make the arrow lengths match the axis units."""),
        ("code", """a = np.array([3, 2])
b = np.array([1, 3])

def draw(vectors, colors, labels, lim=6):
    fig, ax = plt.subplots(figsize=(5, 5))
    for v, c, l in zip(vectors, colors, labels):
        ax.quiver(0, 0, v[0], v[1], angles="xy", scale_units="xy", scale=1, color=c)
        ax.text(v[0] * 1.05, v[1] * 1.05, l, color=c, fontsize=12)
    ax.set_xlim(-1, lim); ax.set_ylim(-1, lim); ax.set_aspect("equal"); ax.grid(alpha=0.3)
    ax.axhline(0, color="grey", lw=0.8); ax.axvline(0, color="grey", lw=0.8)
    plt.show()

draw([a, b], [NAVY, TEAL], ["a = [3, 2]", "b = [1, 3]"])"""),
        ("md", """## 3. Adding and scaling

Adding adds matching entries (as arrows: tip to tail). Multiplying by a single number (a **scalar**) stretches the arrow; a negative number flips it."""),
        ("code", """print("a + b  =", a + b)
print("2 * a  =", 2 * a)
print("-1 * a =", -1 * a)
draw([a, b, a + b, 2 * a], [NAVY, TEAL, RED, ORANGE], ["a", "b", "a + b", "2a"], lim=7)"""),
        ("md", """## 4. Length (magnitude, norm)

Length = square every entry, add, take the square root (Pythagoras). `np.linalg.norm` does it for us."""),
        ("code", """v = np.array([3, 4])
by_hand = np.sqrt((v ** 2).sum())
print("by hand:", by_hand, "| numpy:", np.linalg.norm(v))"""),
        ("md", """## 5. The dot product: multiply pairs, then add

Shopping bill: quantities `[2, 1, 3]` times prices `[799, 2499, 249]`, all added up. Three ways to write it give the same single number."""),
        ("code", """qty = np.array([2, 1, 3])
price = np.array([799, 2499, 249])

print("pairs multiplied:", qty * price)
print("summed by hand:  ", (qty * price).sum())
print("np.dot:          ", np.dot(qty, price))
print("@ operator:      ", qty @ price)"""),
        ("md", """## 6. What the sign of the dot product means

Positive = arrows point a similar way, zero = right angle (unrelated), negative = roughly opposite."""),
        ("code", """a = np.array([3, 1])
for name, b in [("similar", np.array([2.5, 1.5])), ("right angle", np.array([-1, 3])), ("opposite", np.array([-2.5, -1.2]))]:
    print(f"{name:12s} a · b = {a @ b:6.2f}")"""),
        ("md", """## 7. A weighted sum is a dot product (a tiny "neuron")

Final grade = 0.5 × exam + 0.3 × project + 0.2 × homework. The weights say how important each input is. A neuron in a neural network does exactly this."""),
        ("code", """weights = np.array([0.5, 0.3, 0.2])
student = np.array([80, 90, 70])     # exam, project, homework
print("final grade:", student @ weights)"""),
        ("md", """## 8. Cosine similarity

The raw dot product grows with length. **Cosine similarity** divides by both lengths, so only the *direction* counts. Result: −1 (opposite) … 0 (unrelated) … +1 (same direction)."""),
        ("code", """def cosine_similarity(u, v):
    return (u @ v) / (np.linalg.norm(u) * np.linalg.norm(v))

u = np.array([1, 2])
print("u vs 10u (longer, same direction):", round(cosine_similarity(u, 10 * u), 3))
print("u vs perpendicular:               ", round(cosine_similarity(u, np.array([-2, 1])), 3))
print("u vs -u:                          ", round(cosine_similarity(u, -u), 3))
print("dot product u·10u (grows with length):", u @ (10 * u))"""),
        ("md", """## 9. Toy embeddings

An **embedding** is a vector that represents meaning. Real ones have hundreds of numbers learned by a model. Here we hand-make 4-number "embeddings" with features we can read:
`[is_animal, is_vehicle, size, is_pet]`. That makes it easy to see *why* two words are similar."""),
        ("code", """words = {
    "cat":   np.array([1.0, 0.0, 0.2, 1.0]),
    "dog":   np.array([1.0, 0.0, 0.4, 1.0]),
    "lion":  np.array([1.0, 0.0, 0.7, 0.0]),
    "car":   np.array([0.0, 1.0, 0.5, 0.0]),
    "truck": np.array([0.0, 1.0, 0.9, 0.0]),
    "bike":  np.array([0.0, 0.8, 0.2, 0.1]),
}
names = list(words)
sim = np.array([[cosine_similarity(words[a], words[b]) for b in names] for a in names])
print(np.round(sim, 2))"""),
        ("md", """## 10. Similarity as a heatmap

Bright squares = similar meaning. Animals form one bright block, vehicles another."""),
        ("code", """fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(sim, cmap="viridis", vmin=0, vmax=1)
ax.set_xticks(range(len(names)), names); ax.set_yticks(range(len(names)), names)
for i in range(len(names)):
    for j in range(len(names)):
        ax.text(j, i, f"{sim[i, j]:.2f}", ha="center", va="center", color="white", fontsize=9)
ax.set_title("Cosine similarity between toy word vectors")
fig.colorbar(im); plt.show()"""),
        ("md", """## 11. A tiny "semantic search"

Given a query vector, rank every word by cosine similarity. This is exactly what a vector database does in RAG (Module 09), only with millions of real embeddings. Our query: "a big pet-like animal"."""),
        ("code", """query = np.array([1.0, 0.0, 0.8, 0.5])
ranked = sorted(names, key=lambda w: cosine_similarity(query, words[w]), reverse=True)
for w in ranked:
    print(f"{w:6s} {cosine_similarity(query, words[w]):.3f}")"""),
        ("md", """## 12. Real embeddings (preview)

In Modules 06 and 09 you will get real embeddings from a model such as `sentence-transformers/all-MiniLM-L6-v2` (384 numbers per sentence). The code looks like this; we do not run it here to keep this notebook offline and fast:

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
vecs = model.encode(["I love my cat", "My kitten is adorable", "The truck broke down"])
# cosine_similarity(vecs[0], vecs[1]) is high, cosine_similarity(vecs[0], vecs[2]) is low
```"""),
        ("md", """## Your turn

1. Add a word `"puppy"` to `words` and check it is most similar to `"dog"`.
2. Make a query for "a small vehicle" and print the top 2 words.

## Recap
Vector = list = arrow. Dot product = multiply pairs and add; sign shows alignment. Cosine similarity = dot product ÷ lengths, from −1 to +1; it compares meaning between embeddings."""),
    ]


def nb02_matrices():
    return [
        ("md", """# 02 · Matrices: data tables and transformations

**What you will learn**
- a **matrix** as a table of data (rows = examples, columns = features)
- **transpose** and shapes
- matrix × vector = many dot products at once
- matrix × matrix, the **shape rule**, and why order matters
- a 2×2 matrix as a **transformation** that moves the whole plane
- one neural-network layer: `X @ W + b`"""),
        ("md", """## 0. Setup"""),
        ("code", SETUP),
        ("md", """## 1. A matrix as a data table

Rows = students, columns = maths, science, english. This is the "X" matrix of machine learning: one row per example, one column per **feature**."""),
        ("code", """scores = np.array([
    [80, 72, 65],
    [65, 90, 70],
    [70, 88, 92],
])
print(scores)
print("shape (rows, columns):", scores.shape)
print("student 1 as a vector:", scores[1])
print("science column:       ", scores[:, 1])"""),
        ("md", """## 2. Transpose: flip rows and columns

`.T` turns a (3 × 2) matrix into (2 × 3)."""),
        ("code", """M = np.array([[1, 2], [3, 4], [5, 6]])
print(M, M.shape)
print(M.T, M.T.shape)"""),
        ("md", """## 3. Matrix × vector = one dot product per row

Final grade weights `[0.5, 0.3, 0.2]`. `scores @ weights` dots every student's row with the weights. Compare with the loop version."""),
        ("code", """weights = np.array([0.5, 0.3, 0.2])
print("all at once:", scores @ weights)
print("row by row: ", [float(row @ weights) for row in scores])"""),
        ("md", """## 4. Matrix × matrix

Each cell of the answer = (a row of the left matrix) · (a column of the right matrix).
**Restaurant example.** Left: what each table ordered (rows = tables, columns = dishes). Right: each dish's price and calories (rows = dishes). The answer: each table's total price and calories."""),
        ("code", """orders = np.array([      # dosa, idli, coffee
    [2, 0, 2],              # table 1
    [1, 3, 1],              # table 2
])
dish_info = np.array([     # price, calories
    [80, 350],              # dosa
    [50, 150],              # idli
    [30, 100],              # coffee
])
totals = orders @ dish_info
print(totals)
print("shapes:", orders.shape, "@", dish_info.shape, "->", totals.shape)
print("check table 1 price by hand:", 2 * 80 + 0 * 50 + 2 * 30)"""),
        ("md", """## 5. The shape rule (and the error you will see a lot)

(m × **n**) @ (**n** × p) works and gives (m × p). If the inner numbers differ, NumPy raises an error. We catch it with `try/except` so the notebook keeps running."""),
        ("code", """A = np.ones((3, 2))
B = np.ones((3, 4))
try:
    A @ B
except ValueError as e:
    print("Error:", e)
print("Fix by transposing A:", (A.T @ B).shape)"""),
        ("md", """## 6. Order matters: A @ B is usually not B @ A"""),
        ("code", """A = np.array([[1, 2], [3, 4]])
B = np.array([[0, 1], [1, 0]])
print("A @ B =\\n", A @ B)
print("B @ A =\\n", B @ A)"""),
        ("md", """## 7. A matrix as a transformation

Multiply every point of a square grid by a 2×2 matrix and plot where the points go. Change the matrix in the cell and rerun to experiment."""),
        ("code", """def show_transform(M, title):
    pts = np.array([[x, y] for x in np.linspace(-1, 1, 11) for y in np.linspace(-1, 1, 11)])
    moved = pts @ M.T                      # same as applying M to every point
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.scatter(pts[:, 0], pts[:, 1], s=8, color="lightgrey", label="before")
    ax.scatter(moved[:, 0], moved[:, 1], s=8, color=TEAL, label="after")
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5); ax.set_aspect("equal"); ax.grid(alpha=0.3)
    ax.set_title(title); ax.legend(loc="lower right"); plt.show()

show_transform(np.array([[2, 0], [0, 1]]), "scale x by 2")
show_transform(np.array([[1, 1], [0, 1]]), "shear")"""),
        ("md", """Rotation by an angle θ uses cos and sin. Here 45°: the grid turns into a diamond."""),
        ("code", """theta = np.deg2rad(45)
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
show_transform(R, "rotate 45°")"""),
        ("md", """## 8. The identity matrix: "do nothing"

`np.eye(n)` has 1s on the diagonal and 0s elsewhere. Multiplying by it changes nothing, like multiplying a number by 1."""),
        ("code", """I = np.eye(3)
print(I)
print("scores @ I equals scores?", np.array_equal(scores @ I, scores))"""),
        ("md", """## 9. One neural-network layer: `X @ W + b`

- `X`: 4 examples × 3 features
- `W`: 3 features × 2 neurons (the model learns these numbers; here random)
- `b`: one bias per neuron, added to every row by broadcasting

The output has one row per example and one column per neuron."""),
        ("code", """rng = np.random.default_rng(0)
X = rng.normal(size=(4, 3))
W = rng.normal(size=(3, 2))
b = np.array([0.1, -0.2])
out = X @ W + b
print("X", X.shape, "@ W", W.shape, "+ b", b.shape, "->", out.shape)
print(out)
relu = np.maximum(out, 0)       # a common "squashing" step: negatives become 0
print("after ReLU:\\n", relu)"""),
        ("md", """## Your turn
1. Add a third table to `orders` (any numbers) and recompute `totals`. What is the new shape?
2. Find a 2×2 matrix that flips the grid upside down (mirror in the x-axis) and check it with `show_transform`.

## Recap
Matrix = table of numbers. Matrix @ vector = a dot product per row. Matrix @ matrix = rows of A · columns of B; inner shapes must match. A 2×2 matrix moves the plane. A neural-network layer is `X @ W + b`."""),
    ]


def nb03_probability():
    return [
        ("md", """# 03 · Probability, distributions, mean/variance and softmax

**What you will learn**
- probability as a number from 0 to 1, and simulation with NumPy
- the **law of large numbers**
- uniform, normal and binomial **distributions**
- **mean**, **variance** and **standard deviation**, by hand and with NumPy
- **softmax** (scores → probabilities) and **temperature**
- sampling a "next word" like a language model, and **cross-entropy**"""),
        ("md", """## 0. Setup

`default_rng(42)` makes our random numbers repeatable (the 42 is a **seed**)."""),
        ("code", SETUP + """
rng = np.random.default_rng(42)"""),
        ("md", """## 1. Simulating a coin

`rng.random(n)` gives n numbers between 0 and 1. "Heads" = number below 0.5. With 10 flips the share of heads can be far from 0.5."""),
        ("code", """flips = rng.random(10) < 0.5
print(flips.astype(int))
print("share of heads:", flips.mean())"""),
        ("md", """## 2. The law of large numbers

Keep flipping and track the running share of heads. It wobbles at first, then settles near 0.5."""),
        ("code", """n = 5000
flips = rng.random(n) < 0.5
running = np.cumsum(flips) / np.arange(1, n + 1)
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.plot(running, color=NAVY)
ax.axhline(0.5, color=RED, ls="--", label="true probability 0.5")
ax.set_xscale("log"); ax.set_xlabel("number of flips (log scale)"); ax.set_ylabel("share of heads")
ax.set_title("Running share of heads settles near 0.5"); ax.legend(); plt.show()
print("after", n, "flips:", running[-1])"""),
        ("md", """## 3. Three distributions

- **uniform**: every value equally likely (a die)
- **normal**: bell curve around a mean (heights)
- **binomial**: number of successes in a fixed number of yes/no tries (heads in 10 flips)"""),
        ("code", """die = rng.integers(1, 7, 6000)
heights = rng.normal(loc=165, scale=8, size=6000)
heads = rng.binomial(n=10, p=0.5, size=6000)

fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))
axes[0].hist(die, bins=np.arange(0.5, 7.5), rwidth=0.85, color=TEAL); axes[0].set_title("uniform: die")
axes[1].hist(heights, bins=40, color=NAVY); axes[1].set_title("normal: heights")
axes[2].hist(heads, bins=np.arange(-0.5, 11.5), rwidth=0.85, color=ORANGE); axes[2].set_title("binomial: heads in 10")
plt.tight_layout(); plt.show()"""),
        ("md", """## 4. Mean, variance and standard deviation by hand

- mean = sum ÷ count
- variance = average of squared distances from the mean
- standard deviation = square root of variance (same units as the data)"""),
        ("code", """data = np.array([4, 8, 6, 5, 7])
mean = data.sum() / len(data)
deviations = data - mean
variance = (deviations ** 2).mean()
std = np.sqrt(variance)
print("deviations:", deviations)
print(f"mean={mean}, variance={variance}, std={std:.3f}")
print("numpy agrees:", data.mean(), data.var(), round(data.std(), 3))"""),
        ("md", """Note: NumPy's `var()`/`std()` divide by n (the "population" version). pandas' `.var()`/`.std()` divide by n − 1 (the "sample" version) by default, so the numbers differ slightly on small data. Neither is wrong; just know which one you used."""),
        ("md", """## 5. Same mean, different spread

Two archers both average the bullseye (0), but one is much more scattered."""),
        ("code", """tight = rng.normal(0, 1, 2000)
loose = rng.normal(0, 3, 2000)
print(f"tight: mean={tight.mean():.2f} std={tight.std():.2f}")
print(f"loose: mean={loose.mean():.2f} std={loose.std():.2f}")
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.hist(loose, bins=60, alpha=0.6, color=NAVY, label="std 3")
ax.hist(tight, bins=60, alpha=0.6, color=TEAL, label="std 1")
ax.set_title("Same mean, different variance"); ax.legend(); plt.show()
within1 = np.mean(np.abs(heights - heights.mean()) < heights.std())
print(f"share of heights within 1 std of the mean: {within1:.1%} (about 68% for a normal distribution)")"""),
        ("md", """## 6. Softmax: scores to probabilities

Two steps: `exp` every score (all positive, bigger gaps), then divide by the total (sums to 1).
We subtract the largest score first: it does not change the answer but stops `exp` from overflowing on big numbers. This is called the **numerically stable** version."""),
        ("code", """def softmax(scores, temperature=1.0):
    z = np.asarray(scores, dtype=float) / temperature
    z = z - z.max()                 # stability trick, result unchanged
    e = np.exp(z)
    return e / e.sum()

logits = np.array([2.0, 1.0, 0.1])
print("exp:     ", np.exp(logits))
print("softmax: ", softmax(logits))
print("sum:     ", softmax(logits).sum())
print("big scores still fine:", softmax([1000, 999, 998]))"""),
        ("md", """## 7. Temperature

Divide scores by the temperature before softmax. Low → sharp (predictable). High → flat (varied). This is the `temperature` setting of LLM APIs (Module 07)."""),
        ("code", """vocab = ["cat", "dog", "car", "tree", "sky"]
logits = np.array([3.0, 2.2, 1.0, 0.4, -0.5])
fig, axes = plt.subplots(1, 3, figsize=(13, 3.5), sharey=True)
for ax, t in zip(axes, [0.5, 1.0, 2.0]):
    p = softmax(logits, t)
    ax.bar(vocab, p, color=TEAL); ax.set_title(f"temperature {t}"); ax.set_ylim(0, 1)
    print(f"T={t}:", dict(zip(vocab, p.round(3))))
plt.show()"""),
        ("md", """## 8. Sampling the "next word"

A language model turns logits into probabilities with softmax, then **samples** (picks at random, weighted by probability). `rng.choice(..., p=probs)` does that. Count what we get from 1000 picks at two temperatures."""),
        ("code", """for t in [0.5, 2.0]:
    probs = softmax(logits, t)
    picks = rng.choice(vocab, size=1000, p=probs)
    words, counts = np.unique(picks, return_counts=True)
    print(f"T={t}:", dict(zip(words, counts)))"""),
        ("md", """## 9. Cross-entropy: how wrong was the prediction?

Cross-entropy loss = −log(probability the model gave to the **correct** answer). Confident and right → small loss. Confident and wrong → big loss."""),
        ("code", """probs = softmax(logits)
for correct in ["cat", "car", "sky"]:
    p = probs[vocab.index(correct)]
    print(f"correct word '{correct}': p = {p:.3f}, loss = {-np.log(p):.3f}")"""),
        ("md", """## Your turn
1. Roll two dice 10,000 times and plot a histogram of their **sum**. Which total is most common? (Hint: `rng.integers(1, 7, (10000, 2)).sum(axis=1)`.)
2. Find the temperature at which "cat" gets at least 90 % probability.

## Recap
Probabilities are 0..1 and sum to 1. Distributions describe how likely each value is. Mean = centre, variance/std = spread. Softmax turns scores into probabilities; temperature sharpens or flattens them; cross-entropy scores a prediction."""),
    ]


def nb04_gradient_descent():
    return [
        ("md", """# 04 · Derivatives, gradients and gradient descent

**What you will learn**
- slope of a line, and the **derivative** as the slope of a curve at a point
- estimating a derivative with a tiny step (**numerical derivative**)
- **gradient descent** step by step, shown as a sequence of frames (a flip-book "animation")
- the effect of the **learning rate**
- gradient descent with two weights on a contour map
- **loss functions** (MSE, cross-entropy) and fitting a line from scratch"""),
        ("md", """## 0. Setup"""),
        ("code", SETUP),
        ("md", """## 1. Slope of a straight line

Slope = rise ÷ run: how much `y` goes up for one step right."""),
        ("code", """x1, y1 = 1, 3
x2, y2 = 4, 9
print("slope =", (y2 - y1) / (x2 - x1))"""),
        ("md", """## 2. The slope of a curve at one point

For a curve, take a *tiny* step `h` and measure the change. As `h` shrinks, the estimate settles on the true slope. For f(x) = x², the slope at x = 3 is 6."""),
        ("code", """def f(x):
    return x ** 2

def numerical_derivative(func, x, h=1e-4):
    return (func(x + h) - func(x)) / h

for h in [1, 0.1, 0.01, 0.0001]:
    print(f"h = {h:<7} slope estimate = {numerical_derivative(f, 3, h):.4f}")"""),
        ("md", """## 3. Tangent lines

The **tangent line** touches the curve at one point with the curve's slope there. Negative slope = downhill to the right; zero = flat bottom; positive = uphill to the right."""),
        ("code", """def loss(w):
    return (w - 3) ** 2 + 1

xs = np.linspace(-2, 7, 200)
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(xs, loss(xs), color=NAVY, lw=2)
for w0, c in [(0, RED), (3, TEAL), (5.5, ORANGE)]:
    s = numerical_derivative(loss, w0)
    t = np.linspace(w0 - 1.2, w0 + 1.2, 10)
    ax.plot(t, loss(w0) + s * (t - w0), "--", color=c)
    ax.plot(w0, loss(w0), "o", color=c); ax.text(w0, loss(w0) + 1.5, f"slope {s:.1f}", color=c, ha="center")
ax.set_ylim(0, 20); ax.set_xlabel("w"); ax.set_ylabel("loss"); ax.set_title("Slope tells us which way is downhill")
plt.show()"""),
        ("md", """## 4. Gradient descent, one step at a time

Rule: `new_w = w − learning_rate × slope`.
If the slope is negative, `− learning_rate × slope` is positive, so w moves right (downhill). If positive, w moves left. Start at w = −1 with learning rate 0.2.
The exact slope of `(w − 3)² + 1` is `2(w − 3)`; we use it directly here."""),
        ("code", """def slope(w):
    return 2 * (w - 3)

w, lr = -1.0, 0.2
history = [w]
for step in range(1, 11):
    w = w - lr * slope(w)
    history.append(w)
    print(f"step {step:2d}: w = {w:6.3f}   loss = {loss(w):6.3f}   slope = {slope(w):6.3f}")"""),
        ("md", """## 5. The "animation": a sequence of frames

We draw one picture per step (the red dot is the current w, the orange dashes are the tangent, the arrow shows the next step) and save each as a PNG in `outputs/gd_frames/`. Shown together in a grid they read like a flip-book. Notice the steps shrink as the slope flattens."""),
        ("code", """from pathlib import Path
frames_dir = Path("outputs/gd_frames")
frames_dir.mkdir(parents=True, exist_ok=True)

def draw_frame(ax, k):
    ax.plot(xs, loss(xs), color=NAVY)
    ax.plot(history[:k], [loss(h) for h in history[:k]], "o", color="grey", alpha=0.5)
    w = history[k]
    t = np.linspace(w - 1.3, w + 1.3, 10)
    ax.plot(t, loss(w) + slope(w) * (t - w), "--", color=ORANGE)
    ax.plot(w, loss(w), "o", color=RED, ms=10)
    ax.annotate("", xy=(history[k + 1], loss(history[k + 1])), xytext=(w, loss(w)),
                arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=2))
    ax.set_ylim(0, 20); ax.set_title(f"step {k}: w={w:.2f}", fontsize=10)

for k in range(8):                                   # save each frame as its own image
    fig, ax = plt.subplots(figsize=(5, 3))
    draw_frame(ax, k)
    fig.savefig(frames_dir / f"frame_{k + 1:02d}.png", dpi=80, bbox_inches="tight")
    plt.close(fig)

fig, axes = plt.subplots(2, 4, figsize=(16, 6.5))    # and show all 8 together
for k, ax in enumerate(axes.flat):
    draw_frame(ax, k)
plt.tight_layout(); plt.show()
print("saved:", sorted(p.name for p in frames_dir.iterdir()))"""),
        ("md", """## 6. Learning rate: too small, about right, too large

Same start, three step sizes, 10 steps each. Too small crawls; too large overshoots and blows up (**divergence**)."""),
        ("code", """def run_gd(lr, w=-1.0, steps=10):
    path = [w]
    for _ in range(steps):
        w = w - lr * slope(w)
        path.append(w)
    return np.array(path)

fig, axes = plt.subplots(1, 3, figsize=(14, 3.8))
for ax, lr in zip(axes, [0.03, 0.3, 1.05]):
    p = run_gd(lr)
    ax.plot(np.linspace(-4, 10, 200), loss(np.linspace(-4, 10, 200)), color=NAVY)
    ax.plot(p, loss(p), "-o", color=RED, ms=4, lw=1)
    ax.set_xlim(-4, 10); ax.set_ylim(0, 60); ax.set_title(f"lr = {lr}: final w = {p[-1]:.2f}")
plt.tight_layout(); plt.show()"""),
        ("md", """## 7. Two weights: walking down a bowl

Loss = w1² + 4·w2². The **gradient** is the list of both slopes: `[2·w1, 8·w2]`. Each step moves against it. The contour lines are like a hiking map: each line has equal loss."""),
        ("code", """def loss2(w):
    return w[0] ** 2 + 4 * w[1] ** 2

def gradient2(w):
    return np.array([2 * w[0], 8 * w[1]])

w = np.array([-4.5, 2.5]); path = [w.copy()]
for _ in range(25):
    w = w - 0.1 * gradient2(w)
    path.append(w.copy())
path = np.array(path)

A, B = np.meshgrid(np.linspace(-5, 5, 200), np.linspace(-3, 3, 200))
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.contour(A, B, A ** 2 + 4 * B ** 2, levels=[0.5, 2, 5, 10, 20, 35, 50], cmap="viridis")
ax.plot(path[:, 0], path[:, 1], "-o", color=RED, ms=3)
ax.plot(0, 0, "*", color=ORANGE, ms=16)
ax.set_xlabel("w1"); ax.set_ylabel("w2"); ax.set_title("Gradient descent with two weights"); plt.show()
print("start loss:", loss2(path[0]), "| end loss:", round(loss2(path[-1]), 5))"""),
        ("md", """## 8. Loss functions

- **MSE** (mean squared error) for numbers: average of (prediction − truth)².
- **Cross-entropy** for categories: −log(probability of the correct answer)."""),
        ("code", """y_true = np.array([3.0, 5.0, 7.0])
good = np.array([3.1, 4.8, 7.2])
bad = np.array([1.0, 8.0, 4.0])
mse = lambda p, t: np.mean((p - t) ** 2)
print("MSE good predictions:", round(mse(good, y_true), 3))
print("MSE bad predictions: ", round(mse(bad, y_true), 3))
for p in [0.9, 0.5, 0.1, 0.01]:
    print(f"cross-entropy when correct answer had p={p}: {-np.log(p):.3f}")"""),
        ("md", """## 9. Machine learning in miniature: fit a line with gradient descent

Data roughly follows y = 2x + 1 plus noise. We learn `w` (slope) and `b` (intercept) from zero:
1. predict `w*x + b` · 2. error = prediction − y · 3. gradients of MSE: `dw = 2·mean(error·x)`, `db = 2·mean(error)` · 4. update both."""),
        ("code", """rng = np.random.default_rng(42)
x = np.linspace(0, 5, 20)
y = 2 * x + 1 + rng.normal(0, 0.8, x.size)

w, b, lr = 0.0, 0.0, 0.05
losses, snapshots = [], {}
for step in range(201):
    pred = w * x + b
    error = pred - y
    losses.append(np.mean(error ** 2))
    if step in (0, 3, 15, 200):
        snapshots[step] = (w, b)
    w -= lr * 2 * np.mean(error * x)
    b -= lr * 2 * np.mean(error)

print(f"learned: y = {w:.3f}x + {b:.3f}")
print("np.polyfit answer:", np.round(np.polyfit(x, y, 1), 3))"""),
        ("md", """Plot the line at a few steps, and the loss curve. The loss drops fast at first, then levels off."""),
        ("code", """fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].scatter(x, y, color=NAVY)
for step, (ww, bb) in snapshots.items():
    axes[0].plot(x, ww * x + bb, label=f"step {step}")
axes[0].legend(); axes[0].set_title("The line swings into place")
axes[1].plot(losses, color=TEAL); axes[1].set_yscale("log")
axes[1].set_xlabel("step"); axes[1].set_ylabel("MSE (log scale)"); axes[1].set_title("Loss goes down")
plt.tight_layout(); plt.show()"""),
        ("md", """## Your turn
1. Rerun section 9 with `lr = 0.2`. What happens? Then try `lr = 0.01` for 200 steps. Which is closer to the polyfit answer?
2. Change the loss in section 4 to `(w + 2)**2` (and its slope to `2*(w + 2)`). Where does gradient descent end up?

## Recap
Derivative = slope at a point. Gradient = all the slopes. Gradient descent: step against the gradient, repeat. Learning rate = step size. Loss = one number for "how wrong". Together: training."""),
    ]


def all_notebooks():
    return {
        "01-vectors-and-similarity.ipynb": nb01_vectors(),
        "02-matrices.ipynb": nb02_matrices(),
        "03-probability-and-softmax.ipynb": nb03_probability(),
        "04-derivatives-and-gradient-descent.ipynb": nb04_gradient_descent(),
    }
