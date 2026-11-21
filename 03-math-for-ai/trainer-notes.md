# Module 03 — Trainer notes

Read `concepts.md`, run the four notebooks, and play with every sheet of `excel/math-in-a-spreadsheet.xlsx` before teaching. Plan about 2–3 hours of preparation the first time. You do **not** need a maths degree: everything here is taught by picture and by example, and you can answer "why does the formula work?" with "we are using it, not proving it; Module 04 and 05 show it in action".

Many students arrive afraid of maths. Your main job is to make each idea feel concrete and harmless: a receipt, a compass, a hillside in fog.

## 1. What students should be able to do after the session

- Describe a vector both as a list of numbers and as an arrow; add, scale and find the length of one in NumPy.
- Compute a dot product by hand and with `@`, and say what its sign means.
- Compute cosine similarity and explain why it is used to compare embeddings in search and RAG.
- Read a matrix as a data table, predict the shape of a matrix product, and explain `X @ W + b` as one neural-network layer.
- Explain probability, a distribution, mean, variance and standard deviation in plain words, and compute them in NumPy.
- Compute softmax by hand for three scores and say what temperature does.
- Explain a derivative as a slope and estimate one numerically.
- Describe gradient descent step by step, and predict what too small / too large learning rates do.
- Name MSE and cross-entropy and say when each is used.

## 2. Teaching sequence (2-hour session)

| Time | Activity | Materials | Notes |
|---|---|---|---|
| 0:00–0:08 | Hook: "everything in AI is a list of numbers" (show an image as a pixel grid and a sentence turned into numbers) | slides 1–2, `images/math_map.png` | Defuse maths anxiety: no proofs today. |
| 0:08–0:25 | Vectors and dot product: arrows, adding, length, the receipt, the sign | notebook 01 §1–7, slides 3–5, spreadsheet "Dot & cosine" | Students do Exercise 2 on paper. |
| 0:25–0:40 | Cosine similarity and toy embeddings; tiny semantic search | notebook 01 §8–11, slide 6 | Ask them to invent a word vector and predict its neighbours. |
| 0:40–0:58 | Matrices: table view, matrix × vector, the restaurant bill, shape rule, transformations, `X @ W + b` | notebook 02, slides 7–9, spreadsheet "Matrix multiply" | Make everyone predict a shape before running a cell. |
| 0:58–1:05 | Break | | |
| 1:05–1:25 | Probability, distributions, mean/variance; softmax and temperature; sampling a next word | notebook 03, slides 10–12, spreadsheet "Softmax" | Change the temperature cell live. |
| 1:25–1:50 | Derivative as slope, loss functions, gradient descent frames, learning rates, 2-D bowl, fitting a line | notebook 04, slides 13–17, spreadsheet "Gradient descent" and "GD fit a line" | The learning-rate 1.1 demo is the highlight. |
| 1:50–2:00 | Common mistakes, recap, set exercises | slides 18–19 | In class: 1–5. Homework: 6–12. |

For a slower or longer course, split into two sessions: **A** = vectors, cosine, matrices; **B** = probability, softmax, derivatives, gradient descent.

**Showing the "animation":** put `images/gd_frames/gd_frame_01.png` … `gd_frame_08.png` on eight consecutive slides with no transition and click through them, or show `images/gd_strip.png` as one picture.

## 3. Common student mistakes and how to fix them

| Mistake | What it looks like | Fix |
|---|---|---|
| Confusing `a * b` with `a @ b` | They get an array instead of one number for a dot product | `*` multiplies item by item; `@` multiplies and **adds**. Show both side by side. |
| Ignoring shapes before multiplying matrices | `ValueError: matmul: Input operand 1 has a mismatch in its core dimension` | Write the shapes down: (m × n) @ (n × p). The inner numbers must match. Transpose with `.T` if needed. |
| Thinking A @ B equals B @ A | Wrong answers when order is swapped | Do Exercise 7 together; show the two different results. |
| Thinking cosine similarity of 0 means "opposite" | Misreading search scores | 0 = unrelated (right angle); −1 = opposite. Use the three-panel picture. |
| Forgetting softmax outputs add up to 1 / applying it to only some scores | Probabilities that sum to more than 1 | Always check `probs.sum()`; softmax uses the total of **all** scores. |
| `exp` overflow with large scores (`inf`, `nan`) | `RuntimeWarning: overflow encountered in exp` | Subtract the maximum score first (stable softmax); the answer does not change. |
| Adding the gradient instead of subtracting | The loss goes **up** every step | The gradient points uphill. Update is `w = w - lr * slope`. |
| Learning rate too large | Values grow to huge numbers or `nan` | Lower the learning rate by 10×. Show the spreadsheet with 1.1. |
| Mixing up variance and standard deviation | "The variance is 4 cm" | Variance is in squared units; standard deviation (its square root) is in the data's units. |
| NumPy vs pandas standard deviation differ | Slightly different numbers for the same data | NumPy divides by n, pandas by n − 1 by default. Both are fine; say which you used. |
| Believing a tiny `h` is always better in numerical derivatives | Weird results with `h = 1e-15` | Computers round tiny numbers; `h` around `1e-5` is a good default. |

## 4. Questions to check understanding (with answers)

1. **What is `[1, 2, 3] · [4, 5, 6]`?** 4 + 10 + 18 = 32.
2. **Two vectors have cosine similarity 0.98. What does that mean?** They point in almost the same direction; as embeddings, their meanings are very similar.
3. **Why do search systems use cosine similarity rather than the plain dot product?** It ignores length, so only direction (meaning) counts.
4. **Can you multiply a (5 × 3) matrix by a (5 × 3) matrix? What about (5 × 3) by (3 × 5)?** No (3 ≠ 5). Yes, result (5 × 5).
5. **In `X @ W + b`, if X is (32 × 10) and the layer has 4 neurons, what shape is W and the output?** W is (10 × 4); output is (32 × 4).
6. **Two classes have the same average mark, 70. What extra number tells you how different they are?** The standard deviation (spread).
7. **Softmax of [5, 5, 5]?** [1/3, 1/3, 1/3]: equal scores give equal probabilities.
8. **What does raising the temperature do to an LLM's output?** Flattens the probabilities, so less likely words get picked more often: more varied, less predictable.
9. **The slope at the current weight is +4 and the learning rate is 0.1. What is the update?** w decreases by 0.4 (moves left, downhill).
10. **Loss goes up and up during training. Name two likely causes.** Learning rate too large, or the gradient was added instead of subtracted.
11. **Which loss for predicting house prices, and which for spam/not spam?** MSE for prices (numbers); cross-entropy for categories.
12. **The model gave the correct answer probability 0.01. Is the cross-entropy loss small or large?** Large (≈ 4.6): confident and wrong is punished.

## 5. Adapting for faster or slower groups

**Slower groups**
- Use only 2-D vectors and the spreadsheet; delay NumPy code to the second pass.
- Skip transformations (§7 of notebook 02) and the 2-D contour plot; keep the 1-D gradient descent frames.
- Do every calculation once on the board by hand before showing code.
- Spend extra time on the receipt (dot product) and the foggy hillside (derivative) analogies.

**Faster groups**
- Show the exact derivative rules for `x²` and `x³` and compare with the numerical estimates.
- Add momentum to gradient descent (keep a running "velocity" of past steps) and compare paths on the 2-D bowl.
- Compute real embeddings with `sentence-transformers/all-MiniLM-L6-v2` (the code is in notebook 01 §12) and rank a few sentences by cosine similarity.
- Ask them to fit a line with both gradient descent and `np.linalg.lstsq`, and discuss why deep learning uses gradient descent anyway (millions of weights, no neat formula).
