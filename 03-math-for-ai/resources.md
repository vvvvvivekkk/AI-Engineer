# Module 03 — Resources

Links chosen from the course's curated source lists (see the repo's `SOURCES.md`) plus official documentation. Each line says why it is worth your time. They are grouped from "gentlest" to "most advanced": a beginner only needs the first two groups.

## Gentle, beginner-friendly practice
- [Khan Academy — Derivatives](https://www.khanacademy.org/math/calculus-1/cs1-derivatives-definition-and-basic-rules) — the one calculus idea gradient descent depends on, explained slowly with practice questions.
- [Khan Academy — Partial derivatives](https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives) — extends slopes to several variables, which is exactly what a gradient is.
- [Khan Academy — Statistics & Probability](https://www.khanacademy.org/math/statistics-probability) — distributions, mean, variance and more, from scratch.
- [Desmos: line from slope & intercept](https://www.desmos.com/calculator/5kn5x8f7zk) — drag the sliders to see how `y = m·x + b` changes; a perfect warm-up for the line-fitting example.
- [NumPy documentation](https://numpy.org/doc/stable/) — `numpy.linalg` (norms, matrix products) lets you check every hand calculation in code.

## Maths turning into ML code
- [Linear regression from scratch](https://www.cs.toronto.edu/~frossard/post/linear_regression/) — connects the loss function, its derivative and the update step in code, the same path as notebook 04 §9.
- [Logistic regression from scratch](https://medium.com/@martinpella/logistic-regression-from-scratch-in-python-124c5636b8ac) — shows the sigmoid and log-loss (cross-entropy) becoming a working classifier (Medium may limit free reads).
- [Neural Networks: Zero to Hero (Karpathy)](https://www.youtube.com/watch?v=VMj-3S1tku0&list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ) — the first video builds automatic derivatives by hand; the most intuitive picture of gradients in ML. Watch before Module 05.
- [Neural Networks and Deep Learning (Nielsen)](http://neuralnetworksanddeeplearning.com/) — a free online book with the clearest explanation of how gradients flow through a network.
- [Colah's blog](http://colah.github.io/) — visual essays (for example, backpropagation on computational graphs) that build intuition with pictures.

## Fuller courses and references
- [Dive into Deep Learning (D2L)](https://d2l.ai/) — has a maths appendix (linear algebra, calculus, probability) tied directly to runnable code.
- [Linear algebra lecture playlist](https://www.youtube.com/playlist?list=PLE7DDD91010BC51F8) — a full university lecture series on vectors and matrices, for those who want depth.
- [An Introduction to Statistical Learning](https://www.statlearning.com) — the standard gentle statistics-for-ML textbook, free as an official PDF from this site.
- [CS229 cheat sheets](https://github.com/afshinea/stanford-cs-229-machine-learning) — compact refreshers on probability, statistics and linear algebra.
- [Andrew Ng ML notes](https://github.com/ashishpatel26/Andrew-NG-Notes) — revision notes on the maths behind classic ML.

## Advanced (after the course, optional)
- [Stanford CS229](http://cs229.stanford.edu/) — the course site has linear-algebra and probability review notes written for ML students.
- [Mathematical Introduction to Deep Learning](https://arxiv.org/abs/2103.11201) — a rigorous, proof-based treatment for learners who want the formal side after the intuition.

## Notes for trainers
- This module intentionally avoids proofs. If a student wants them, point to the "Fuller courses" group rather than derailing the session.
- The spreadsheet `excel/math-in-a-spreadsheet.xlsx` is often the best "resource" in the room: change a cell and the maths updates in front of everyone.
