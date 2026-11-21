"""
matrices.py - matrices as data tables, matrix multiplication (with the shape rule) and
a single neural-network layer, X @ W + b.

Run:   python 03-math-for-ai/code/matrices.py
"""
import numpy as np                                     # arrays and maths

# --- A matrix as a data table ------------------------------------------------------------
scores = np.array([[80, 72, 65],                       # rows = students
                   [65, 90, 70],                       # columns = maths, science, english
                   [70, 88, 92]])
weights = np.array([0.5, 0.3, 0.2])                    # importance of each subject
print("final grades:", scores @ weights)               # one dot product per row, all at once
print("transpose shape:", scores.T.shape)              # rows and columns swapped


# --- Matrix multiplication written out by hand --------------------------------------------
def matmul_by_hand(A, B):
    """Multiply A (m x n) by B (n x p) with plain loops, to show what @ does."""
    m, n = A.shape                                     # rows and columns of A
    n2, p = B.shape                                    # rows and columns of B
    if n != n2:                                        # the shape rule: inner numbers must match
        raise ValueError(f"cannot multiply {A.shape} by {B.shape}: inner sizes {n} and {n2} differ")
    C = np.zeros((m, p))                               # empty answer, m rows by p columns
    for i in range(m):                                 # every row of A...
        for j in range(p):                             # ...with every column of B
            C[i, j] = np.sum(A[i, :] * B[:, j])        # one dot product per answer cell
    return C


orders = np.array([[2, 0, 2],                          # table 1: 2 dosa, 0 idli, 2 coffee
                   [1, 3, 1]])                         # table 2
dish_info = np.array([[80, 350],                       # dosa: price, calories
                      [50, 150],                       # idli
                      [30, 100]])                      # coffee
print("by hand:\n", matmul_by_hand(orders, dish_info))
print("with @:\n", orders @ dish_info)                 # identical answer, much faster

try:
    matmul_by_hand(orders, orders)                     # (2x3) @ (2x3): inner 3 vs 2 -> not allowed
except ValueError as err:
    print("shape error:", err)

# --- A matrix as a transformation ---------------------------------------------------------
rotate90 = np.array([[0, -1], [1, 0]])                 # turns points 90 degrees anticlockwise
print("[1, 0] rotated:", rotate90 @ np.array([1, 0]))  # the x-direction becomes the y-direction

# --- One neural-network layer -------------------------------------------------------------
rng = np.random.default_rng(0)                         # seeded random numbers
X = rng.normal(size=(4, 3))                            # 4 examples, 3 features each
W = rng.normal(size=(3, 2))                            # 3 inputs -> 2 neurons (learned in real life)
b = np.array([0.1, -0.2])                              # one bias per neuron
out = np.maximum(X @ W + b, 0)                         # weighted sums + bias, then ReLU (negatives -> 0)
print("layer output shape:", out.shape)                # (4, 2): one row per example, one column per neuron
print(out.round(3))
