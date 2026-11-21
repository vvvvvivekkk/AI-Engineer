# Module 03 — Worked solutions

Runnable code for every answer: [`solutions.py`](solutions.py) (`python 03-math-for-ai/solutions/solutions.py`).

---

## Exercise 1 — Vector basics
- `a + b = [2+1, −1+4, 3+0] = [3, 3, 3]`
- `3a = [6, −3, 9]`
- length of `a` = √(4 + 1 + 9) = √14 ≈ 3.742
- `a · b = 2×1 + (−1)×4 + 3×0 = 2 − 4 + 0 = −2`

NumPy: `a + b`, `3 * a`, `np.linalg.norm(a)`, `a @ b`. The negative dot product says the two arrows point somewhat away from each other.

## Exercise 2 — Receipt as a dot product
`[2, 3, 1] @ [20, 15, 60] = 40 + 45 + 60 = Rs 145`. In the spreadsheet, type 2, 3, 1 into the quantity cells and 20, 15, 60 into the price cells; the "total bill" cell shows 145.

## Exercise 3 — Which pairs are aligned?
- (a) `[1, 0]` and `[0, 5]`: one points right, one points up → right angle → **0**.
- (b) `[2, 3]` and `[4, 6]`: the second is twice the first → same direction → **positive** (26).
- (c) `[1, 1]` and `[−1, −2]`: roughly opposite → **negative** (−3).

## Exercise 4 — Cosine similarity function
```python
def cosine_similarity(u, v):
    return (u @ v) / (np.linalg.norm(u) * np.linalg.norm(v))
```
For `u = [1, 2, −1]`: `cosine_similarity(u, 5*u) = 1.0`, but `u·u = 6` and `u·(5u) = 30`. **Why search prefers cosine:** it compares direction (meaning) and ignores length, so a long document is not automatically "more similar" to everything.

## Exercise 5 — Tiny semantic search
With hamster `[1, 0, 0.05, 1]`, bus `[0, 1, 1.0, 0]`, elephant `[1, 0, 1.0, 0]` added, the query "small pet" `[1, 0, 0, 1]` returns hamster (0.999), cat (0.990), dog (0.962). Your numbers depend on the vectors you chose; check that pets come first and vehicles last.

## Exercise 6 — Shapes
| Pair | Allowed? | Result |
|---|---|---|
| (4 × 3) @ (3 × 2) | yes (3 = 3) | (4 × 2) |
| (2 × 5) @ (2 × 5) | **no** (5 ≠ 2) | error; `A @ B.T` would give (2 × 2) |
| (1 × 3) @ (3 × 1) | yes | (1 × 1): a single dot product |
| (3 × 1) @ (1 × 3) | yes | (3 × 3): every pair multiplied (an "outer product") |

## Exercise 7 — Matrix multiplication by hand
`A @ B`: row 1 of A `[1, 2]` · columns of B → `1×3 + 2×1 = 5`, `1×0 + 2×2 = 4`; row 2 `[0, 1]` → `1`, `2`. So `[[5, 4], [1, 2]]`.
`B @ A`: `[[3, 6], [1, 4]]`. **Not equal**: order matters in matrix multiplication.

## Exercise 8 — Mean, variance, standard deviation
1. Mean = 35 / 7 = 5. Deviations: `[−2, 0, −1, 1, −3, 3, 2]`. Squares: `[4, 0, 1, 1, 9, 9, 4]`, sum 28, variance = 28 / 7 = **4**, std = **2** hours.
2. With a 20-hour day: mean ≈ 6.88, std ≈ 5.30. One extreme value moved the mean by almost 2 hours and more than doubled the standard deviation. Averages and spreads are sensitive to **outliers** (extreme values); the median is more robust.

## Exercise 9 — Softmax by hand
1. `exp([1, 2, 3]) = [2.718, 7.389, 20.086]`, total 30.193 → `[0.090, 0.245, 0.665]`, sums to 1.
2. T = 0.5 → `[0.016, 0.117, 0.867]` (sharper: the top score dominates). T = 5 → `[0.269, 0.329, 0.402]` (flatter: closer to equal).
3. Adding 100 to every score gives exactly the same result, because every `exp` is multiplied by the same factor, which cancels when dividing by the total. That is why the stable softmax subtracts the maximum score first: it avoids `exp(1000)` overflowing to infinity without changing the answer.

## Exercise 10 — Numerical derivative
| x | estimate | exact 3x² − 2 |
|---|---|---|
| 0 | −2.0000 | −2 |
| 1 | 1.0000 | 1 |
| 2 | 10.0001 | 10 |

The curve goes downhill where the slope is negative: around x = 0 (precisely between x ≈ −0.82 and x ≈ 0.82).

## Exercise 11 — Gradient descent experiments
Final w after 20 steps from w = 10:

| learning rate | final w | what happened |
|---|---|---|
| 0.01 | 7.67 | too small: still far from 3 |
| 0.1 | 3.08 | smooth convergence |
| 0.5 | 3.0000 | lands exactly on 3 in **one** step (for this particular loss, lr 0.5 gives `w − 0.5 × 2(w − 3) = 3`) |
| 0.9 | 3.08 | overshoots each step, bouncing from side to side, but the bounces shrink |
| 1.1 | 271.36 | every bounce is bigger than the last: **divergence** |

In the spreadsheet set "start w" to 10 and "learning rate" to 1.1; the w column grows without limit.

## Exercise 12 — Fit a line from scratch
With learning rate 0.03 and 5000 steps: `w ≈ 4.371`, `b ≈ 47.200`, MSE ≈ 0.514, matching `np.polyfit` (`[4.371, 47.2]`). (A learning rate around 0.1 or more diverges here because the x values make the slopes large; try it.) The b value needs many steps because it changes slowly; that is normal.

Prediction for 7 hours: ≈ **77.8**. Predicting for 20 hours would give ≈ 134, which is impossible for a test out of 100: a straight line fitted on 1–6 hours should not be trusted far outside that range (**extrapolation**).
