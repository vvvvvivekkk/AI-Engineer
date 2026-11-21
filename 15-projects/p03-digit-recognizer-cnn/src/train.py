"""
train.py - the PyTorch training loop with early stopping.

One epoch = the model sees every training image once. For each batch:
  1. forward pass  - the model makes predictions (scores for digits 0-9)
  2. loss          - cross-entropy: big when the right digit got a low score
  3. backward pass - loss.backward() works out how each weight affected the loss (backpropagation)
  4. step          - the optimiser (Adam) nudges every weight to reduce the loss
Early stopping: after each epoch we check the validation loss. If it hasn't improved for
`patience` epochs we stop and roll back to the best weights. Like taking a cake out of the oven
when it stops rising, instead of waiting until it burns (overfits).
"""
from __future__ import annotations

import copy

import torch
from torch import nn

from .data import augment


def run_epoch(model, data_loader, loss_fn, optimizer=None, aug_gen=None):
    """Train (if an optimizer is given) or evaluate for one pass. Returns (avg loss, accuracy)."""
    training = optimizer is not None
    model.train(training)                         # switches dropout on (train) or off (eval)
    total_loss, correct, seen = 0.0, 0, 0
    with torch.set_grad_enabled(training):        # no gradient bookkeeping when only evaluating
        for x, y in data_loader:
            if training and aug_gen is not None:
                x = augment(x, aug_gen)
            logits = model(x)                     # 1. forward
            loss = loss_fn(logits, y)             # 2. loss
            if training:
                optimizer.zero_grad()             # clear gradients from the previous batch
                loss.backward()                   # 3. backward
                optimizer.step()                  # 4. update weights
            total_loss += loss.item() * len(y)
            correct += (logits.argmax(1) == y).sum().item()
            seen += len(y)
    return total_loss / seen, correct / seen


def fit(model, train_loader, val_loader, epochs=60, lr=1e-3, patience=8, use_augment=False, seed=0):
    """Train with Adam + early stopping. Returns (best model, history dict)."""
    torch.manual_seed(seed)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    aug_gen = torch.Generator().manual_seed(seed) if use_augment else None
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    best_loss, best_state, bad_epochs = float("inf"), None, 0
    for epoch in range(epochs):
        tr_loss, tr_acc = run_epoch(model, train_loader, loss_fn, optimizer, aug_gen)
        va_loss, va_acc = run_epoch(model, val_loader, loss_fn)
        for k, v in zip(history, (tr_loss, va_loss, tr_acc, va_acc)):
            history[k].append(v)
        if va_loss < best_loss - 1e-4:            # improved: remember these weights
            best_loss, best_state, bad_epochs = va_loss, copy.deepcopy(model.state_dict()), 0
        else:
            bad_epochs += 1
            if bad_epochs >= patience:            # no improvement for a while: stop
                break
    model.load_state_dict(best_state)             # roll back to the best epoch
    history["best_epoch"] = int(min(range(len(history["val_loss"])), key=history["val_loss"].__getitem__)) + 1
    history["epochs_run"] = len(history["val_loss"])
    return model, history


@torch.no_grad()
def predict(model, x: torch.Tensor) -> torch.Tensor:
    model.eval()
    return model(x).argmax(1)
