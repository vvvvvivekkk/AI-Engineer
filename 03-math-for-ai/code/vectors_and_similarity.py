"""
vectors_and_similarity.py - vectors, dot product and cosine similarity in plain NumPy,
ending with a tiny "semantic search" over hand-made word vectors.

Run:   python 03-math-for-ai/code/vectors_and_similarity.py
"""
import numpy as np                                    # arrays and maths


def length(v):
    """Length (norm) of a vector: square each number, add them, take the square root."""
    return np.sqrt(np.sum(v ** 2))                    # same as np.linalg.norm(v)


def dot(a, b):
    """Dot product: multiply matching pairs, then add everything up."""
    return np.sum(a * b)                              # same as a @ b or np.dot(a, b)


def cosine_similarity(a, b):
    """How aligned two vectors are, from -1 (opposite) to +1 (same direction)."""
    return dot(a, b) / (length(a) * length(b))        # divide by both lengths so only direction counts


# --- Basic examples --------------------------------------------------------------------
a = np.array([3, 2])                                  # 3 steps right, 2 up
b = np.array([1, 3])                                  # 1 step right, 3 up
print("a + b =", a + b)                               # add matching numbers: [4, 5]
print("2 * a =", 2 * a)                               # scaling stretches the arrow: [6, 4]
print("length of [3, 4] =", length(np.array([3, 4]))) # 5.0, the classic 3-4-5 triangle

qty = np.array([2, 1, 3])                             # how many of each item
price = np.array([799, 2499, 249])                    # price of each item
print("shopping bill (a dot product):", dot(qty, price))   # 2*799 + 1*2499 + 3*249 = 4844

# --- The sign of the dot product -------------------------------------------------------
x = np.array([3, 1])
for name, y in [("similar", np.array([2.5, 1.5])), ("right angle", np.array([-1, 3])), ("opposite", np.array([-2.5, -1.2]))]:
    print(f"{name:12s} dot = {dot(x, y):6.2f}   cosine = {cosine_similarity(x, y):5.2f}")

# --- Toy embeddings: [is_animal, is_vehicle, size, is_pet] -----------------------------
words = {
    "cat":   np.array([1.0, 0.0, 0.2, 1.0]),
    "dog":   np.array([1.0, 0.0, 0.4, 1.0]),
    "lion":  np.array([1.0, 0.0, 0.7, 0.0]),
    "car":   np.array([0.0, 1.0, 0.5, 0.0]),
    "truck": np.array([0.0, 1.0, 0.9, 0.0]),
    "bike":  np.array([0.0, 0.8, 0.2, 0.1]),
}


def search(query, k=3):
    """Return the k words whose vectors are most similar to the query vector."""
    scores = {w: round(float(cosine_similarity(query, v)), 3) for w, v in words.items()}   # score every word
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:k]  # best first, keep k


print("\nmost similar to 'cat':", search(words["cat"]))
print("query 'big vehicle':  ", search(np.array([0.0, 1.0, 1.0, 0.0])))
