# Module 03 — Exercises

Use NumPy in a notebook or a `.py` file. Some exercises also use the spreadsheet `excel/math-in-a-spreadsheet.xlsx`. They go from easy (1) to hard (12). Worked answers: [`solutions/solutions.md`](solutions/solutions.md); runnable code: [`solutions/solutions.py`](solutions/solutions.py).

Try each one on paper first where you can, then check with code.

---

### Exercise 1 — Vector basics (easy)
For `a = [2, -1, 3]` and `b = [1, 4, 0]`, compute by hand and then with NumPy: `a + b`, `3a`, the length of `a`, and `a · b`.

### Exercise 2 — Receipt as a dot product (easy)
A café sells tea (Rs 20), samosa (Rs 15) and cake (Rs 60). One customer buys 2 teas, 3 samosas and 1 cake. Write the order and the prices as vectors and compute the bill with `@`. Then do it in the spreadsheet's "Dot & cosine" sheet by typing your numbers into the shopping-bill rows.

### Exercise 3 — Which pairs are aligned? (easy)
Without calculating cosine similarity, say whether each dot product is positive, zero or negative, then check with NumPy:
(a) `[1, 0]` and `[0, 5]` (b) `[2, 3]` and `[4, 6]` (c) `[1, 1]` and `[-1, -2]`.

### Exercise 4 — Cosine similarity function (easy-medium)
Write a function `cosine_similarity(u, v)` and show that `cosine_similarity(u, 5*u)` is 1 for any non-zero `u`, while the plain dot product changes. Explain in one sentence why search systems prefer cosine similarity.

### Exercise 5 — Tiny semantic search (medium)
Using the toy word vectors `[is_animal, is_vehicle, size, is_pet]` from notebook 01, add three new words of your choice (for example `"hamster"`, `"bus"`, `"elephant"`). Build a function `search(query_vector, k)` that returns the top-k words. Test it with a query for "small pet".

### Exercise 6 — Shapes (medium)
For each pair, say whether `A @ B` is allowed, and if so the result's shape. Then check with `np.ones`:
(a) (4 × 3) @ (3 × 2) (b) (2 × 5) @ (2 × 5) (c) (1 × 3) @ (3 × 1) (d) (3 × 1) @ (1 × 3).

### Exercise 7 — Matrix multiplication by hand (medium)
Compute `A @ B` by hand for `A = [[1, 2], [0, 1]]` and `B = [[3, 0], [1, 2]]`. Then compute `B @ A`. Are they equal? Check both with NumPy. Change the numbers in the spreadsheet's "Matrix multiply" sheet to verify one cell.

### Exercise 8 — Mean, variance, standard deviation (medium)
Daily phone screen time (hours) for a week: `[3, 5, 4, 6, 2, 8, 7]`.
1. Compute mean, variance and standard deviation by hand (show deviations), then with NumPy.
2. Add an extreme day of 20 hours. How much do the mean and the standard deviation change? What does that tell you?

### Exercise 9 — Softmax by hand (medium)
For scores `[1.0, 2.0, 3.0]`:
1. Compute softmax step by step (exp, total, divide). Check that the probabilities add up to 1.
2. Compute it again with temperature 0.5 and temperature 5. Describe what changes.
3. Show that adding 100 to every score does not change the softmax result. Why is that useful?

### Exercise 10 — Numerical derivative (medium-hard)
Write `numerical_derivative(f, x, h)`. For `f(x) = x³ − 2x`, estimate the slope at x = 0, 1 and 2 with `h = 1e-5`. The exact slope rule is `3x² − 2`; compare. Where is the curve going downhill?

### Exercise 11 — Gradient descent experiments (hard)
Using `loss(w) = (w − 3)² + 1` and `slope(w) = 2(w − 3)`:
1. Run 20 steps of gradient descent from w = 10 with learning rates 0.01, 0.1, 0.5, 0.9 and 1.1. For each, report the final w.
2. Explain what happens at 0.5 (look closely) and at 1.1.
3. Reproduce the 1.1 case in the spreadsheet's "Gradient descent" sheet by changing two cells.

### Exercise 12 — Fit a line from scratch (hard)
Data: hours studied `x = [1, 2, 3, 4, 5, 6]` and test scores `y = [52, 55, 61, 64, 70, 73]`.
1. Use gradient descent (no libraries beyond NumPy) to fit `y = w·x + b`. Choose a learning rate and number of steps that work; report w, b and the final MSE.
2. Compare with `np.polyfit(x, y, 1)`.
3. Plot the loss curve and the fitted line.
4. Use your line to predict the score for 7 hours. Explain in one sentence why we should be careful predicting for 20 hours.
