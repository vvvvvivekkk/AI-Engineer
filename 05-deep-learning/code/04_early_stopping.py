"""
04_early_stopping.py
Train an over-sized MLP on a tiny training set, with dropout and early stopping.
Run:  python 04_early_stopping.py          (well under a minute on CPU)
"""
# copy lets us snapshot the best weights
import copy
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

# device and reproducibility
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cpu":
    torch.set_num_threads(1)
torch.manual_seed(0)

# data: train / validation / test
X, y = load_digits(return_X_y=True)
X = (X / 16.0).astype("float32")
X_tv, X_te, y_tv, y_te = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
X_tr, X_va, y_tr, y_va = train_test_split(X_tv, y_tv, test_size=0.25, random_state=0, stratify=y_tv)
# keep only 200 training images so overfitting happens quickly
Xtr, ytr = torch.tensor(X_tr[:200]), torch.tensor(y_tr[:200], dtype=torch.long)
Xva, yva = torch.tensor(X_va).to(device), torch.tensor(y_va, dtype=torch.long).to(device)
Xte, yte = torch.tensor(X_te).to(device), torch.tensor(y_te, dtype=torch.long).to(device)
loader = DataLoader(TensorDataset(Xtr, ytr), batch_size=32, shuffle=True)

# a big MLP with dropout after each hidden layer
model = nn.Sequential(
    nn.Linear(64, 256), nn.ReLU(), nn.Dropout(0.3),
    nn.Linear(256, 256), nn.ReLU(), nn.Dropout(0.3),
    nn.Linear(256, 10),
).to(device)
loss_fn = nn.CrossEntropyLoss()
# AdamW = Adam with weight decay (keeps weights small)
opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)

# early-stopping bookkeeping
patience = 10                  # how many epochs without improvement we tolerate
best_val = float("inf")        # best validation loss so far
best_state = None              # weights at that point
waited = 0                     # epochs since the last improvement

for epoch in range(300):       # an upper limit; early stopping usually ends sooner
    model.train()
    for xb, yb in loader:
        xb, yb = xb.to(device), yb.to(device)
        loss = loss_fn(model(xb), yb)
        opt.zero_grad()
        loss.backward()
        opt.step()
    # validation loss for this epoch (dropout off, no gradients)
    model.eval()
    with torch.no_grad():
        val_loss = loss_fn(model(Xva), yva).item()
    if val_loss < best_val:                          # improvement: remember these weights
        best_val, waited = val_loss, 0
        best_state = copy.deepcopy(model.state_dict())
        best_epoch = epoch
    else:                                            # no improvement: count, and maybe stop
        waited += 1
        if waited >= patience:
            print(f"stopping at epoch {epoch}; best was epoch {best_epoch} (val loss {best_val:.3f})")
            break

# roll back to the best weights and test once
model.load_state_dict(best_state)
model.eval()
with torch.no_grad():
    acc = (model(Xte).argmax(1) == yte).float().mean().item()
print("test accuracy with best weights:", round(acc, 3))
