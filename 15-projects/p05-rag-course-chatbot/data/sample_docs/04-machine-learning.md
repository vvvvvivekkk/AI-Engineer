# Module 04 - Machine learning

## Supervised vs unsupervised
In **supervised learning** every training example has a correct answer (a label), and the model learns to predict it. Classification predicts a category; regression predicts a number. In **unsupervised learning** there are no labels; the model finds structure on its own, for example grouping customers with K-means.

## Train/test split
Always keep part of the data hidden as a **test set**, usually 20%. Train on the rest and measure on the test set only at the end. It is like a final exam the student has never seen.

## Overfitting
**Overfitting** happens when a model memorises the training data, including its noise, and does badly on new data. Signs: a high training score but a low test score. Fixes: more data, a simpler model, regularisation, or cross-validation to choose settings.

## Cross-validation
**k-fold cross-validation** splits the training data into k slices. The model trains on k-1 slices and is scored on the remaining one, k times, and the scores are averaged. Five folds is a common choice.

## Metrics
**Precision** asks: of everything predicted positive, how much really was positive? **Recall** asks: of all the real positives, how many did we find? **F1** is the harmonic mean of the two. For regression use **MAE** (average absolute error) or **RMSE** (which punishes big errors more).
