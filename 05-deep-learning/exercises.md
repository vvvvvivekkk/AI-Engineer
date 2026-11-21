# Module 05 — Exercises

Graded easy → hard. Use Colab or a local notebook. All data comes from scikit-learn's built-in `load_digits` / `load_diabetes`, so nothing is downloaded. For the digits exercises, reuse the data-loading cell from the notebooks (60/20/20 train/validation/test split, pixels divided by 16).

Solutions: `solutions/solutions.md` and runnable `solutions/solutions.py`. Try first!

---

## Easy

### Exercise 1 — Predict the shape
Write down the shape **before** running each line, then check:

```python
(torch.zeros(3, 4) @ torch.ones(4, 2)).shape
torch.rand(10, 64).reshape(-1, 1, 8, 8).shape
torch.rand(5, 3).sum(dim=0).shape
torch.rand(5, 3).sum(dim=1).shape
torch.rand(32, 16, 8, 8).flatten(1).shape
```

### Exercise 2 — Autograd vs pencil
For f(x) = x³ + 2x, work out the slope at x = 2 by hand (rule: the slope of xⁿ is n·xⁿ⁻¹). Then compute it with autograd (`requires_grad=True`, `.backward()`, `.grad`).

### Exercise 3 — Count parameters by hand
How many learnable parameters do these have? Work it out, then check with `sum(p.numel() for p in model.parameters())`.
1. `nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 10))`
2. `nn.Conv2d(1, 8, kernel_size=3)`

Hint: a Linear layer has in × out weights + out biases. A Conv2d has in_channels × out_channels × k × k weights + out_channels biases. The Excel "Parameter Counter" sheet does this too.

### Exercise 4 — Cross-entropy by hand
1. The network gives the correct class probability 0.5. What is the cross-entropy loss (−log p)?
2. For logits `[2.0, 1.0, 0.0]` and correct class 0, compute softmax by hand (eˣ / sum of eˣ), then the loss. Check with `nn.CrossEntropyLoss()(torch.tensor([[2., 1., 0.]]), torch.tensor([0]))`.

---

## Medium

### Exercise 5 — Learning-rate sweep
Train the notebook-02 MLP (64 → 128 → 10) for 20 epochs with Adam at learning rates `1e-4, 1e-3, 1e-2, 1e-1, 1.0`. Use `torch.manual_seed(0)` before each run. Report validation accuracy for each. Which is too slow? Which is unstable? Explain using the foggy-hill analogy.

### Exercise 6 — How big should the hidden layer be?
Train MLPs with hidden sizes 8, 32, 128, 512 (30 epochs each). Report parameter count and test accuracy. Is bigger always better? What would you expect if the training set were tiny?

### Exercise 7 — Find the four bugs
This loop runs but trains badly or crashes. Find and fix **four** bugs, and explain each in one sentence.

```python
model = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 10), nn.Softmax(dim=1))
loss_fn = nn.CrossEntropyLoss()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loader = DataLoader(TensorDataset(X_train_t, torch.tensor(y_train, dtype=torch.float32)),
                    batch_size=64, shuffle=True)
for epoch in range(20):
    for xb, yb in loader:
        loss = loss_fn(model(xb), yb)
        loss.backward()
        opt.step()
with torch.no_grad():
    print((model(X_val_t).argmax(1) == y_val_t).float().mean())
```
(Hint: one bug is about gradients, one about the loss input, one about label type, one about evaluation mode — imagine the model had dropout.)

### Exercise 8 — Neural network for regression
Use `load_diabetes` (80/20 split, `random_state=42`). Build an MLP 10 → 32 → 1 with `nn.MSELoss`. Standardise the **target** (subtract the training mean, divide by training standard deviation) for training, and convert predictions back before measuring. Train full-batch for 300 steps with Adam (`lr=1e-2`). Compare its test MAE with `LinearRegression` from module 04. Is the neural network worth it here?

---

## Hard

### Exercise 9 — More data beats tricks
Train the big MLP (64 → 256 → 256 → 10, no dropout) for 100 epochs on (a) the first 200 training images and (b) all ~1,077 training images. Report the final validation loss and the test accuracy for each. Relate the result to overfitting.

### Exercise 10 — A reusable early-stopping class
Write a class `EarlyStopper(patience, min_delta)` with:
- `step(val_loss, model) -> bool`: records the best weights when validation loss improves by more than `min_delta`; returns `True` when there has been no improvement for `patience` epochs.
- `restore(model)`: loads the best weights back.

Use it to train the big MLP on 200 images, then report the stopping epoch and test accuracy.

### Exercise 11 — Data augmentation for the CNN
**Data augmentation** = creating extra variety in training data by changing images slightly in ways that keep their meaning. Write a function that shifts each training batch by a random −1, 0 or +1 pixel horizontally and vertically (`torch.roll(xb, shifts=(dy, dx), dims=(2, 3))`). Train the notebook-03 CNN for 40 epochs with and without it and compare test accuracy. Did it help? Think carefully about what a 1-pixel shift (with wrap-around) does to an 8×8 image, and suggest what kind of augmentation would make more sense for tiny images.

### Exercise 12 — Checkpoint and resume
Train the MLP for 5 epochs. Save a **checkpoint** dictionary with the model state_dict, the optimizer state_dict and the epoch number. Then, as if starting a fresh session, build a new model and optimizer, load the checkpoint into both, and train 5 more epochs. Show that the validation loss continues to improve from where it left off (rather than starting again from random). Why does the optimizer state matter for Adam?
