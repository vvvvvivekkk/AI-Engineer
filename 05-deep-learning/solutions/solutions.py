"""
solutions.py - runnable solutions for module 05 exercises 1-12.
Run:  python solutions.py          (about 1-2 minutes on a laptop CPU)
See solutions.md for explanations.
"""
import copy
import math
import os
import tempfile
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.datasets import load_digits, load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cpu":
    torch.set_num_threads(1)

# ---- shared digits data (same split as the notebooks) ----
X, y = load_digits(return_X_y=True)
X = (X / 16.0).astype("float32")
X_tv, X_te, y_tv, y_te = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
X_tr, X_va, y_tr, y_va = train_test_split(X_tv, y_tv, test_size=0.25, random_state=0, stratify=y_tv)
T = lambda a: torch.tensor(a)
L = lambda a: torch.tensor(a, dtype=torch.long)
Xtr, Xva, Xte, ytr, yva, yte = T(X_tr), T(X_va), T(X_te), L(y_tr), L(y_va), L(y_te)


def fit(model, Xa, ya, epochs=30, lr=1e-3, bs=64, augment=None):
    """Standard training loop; returns the model. augment(xb) may change each batch."""
    model.to(device)
    loader = DataLoader(TensorDataset(Xa, ya), batch_size=bs, shuffle=True)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    for _ in range(epochs):
        model.train()
        for xb, yb in loader:
            if augment is not None:
                xb = augment(xb)
            xb, yb = xb.to(device), yb.to(device)
            loss = loss_fn(model(xb), yb)
            opt.zero_grad(); loss.backward(); opt.step()
    return model


def acc(model, Xa, ya):
    model.eval()
    with torch.no_grad():
        return (model(Xa.to(device)).argmax(1) == ya.to(device)).float().mean().item()


def ex1():
    print("Ex1:", tuple((torch.zeros(3, 4) @ torch.ones(4, 2)).shape),
          tuple(torch.rand(10, 64).reshape(-1, 1, 8, 8).shape),
          tuple(torch.rand(5, 3).sum(dim=0).shape),
          tuple(torch.rand(5, 3).sum(dim=1).shape),
          tuple(torch.rand(32, 16, 8, 8).flatten(1).shape))


def ex2():
    x = torch.tensor(2.0, requires_grad=True)
    f = x ** 3 + 2 * x
    f.backward()
    print("Ex2: df/dx at 2 =", x.grad.item(), "(by hand 3*2^2 + 2 = 14)")


def ex3():
    mlp = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 10))
    conv = nn.Conv2d(1, 8, kernel_size=3)
    print("Ex3: MLP params", sum(p.numel() for p in mlp.parameters()),
          "| Conv2d(1,8,3) params", sum(p.numel() for p in conv.parameters()))


def ex4():
    print("Ex4: -log(0.5) =", round(-math.log(0.5), 3))
    logits = torch.tensor([[2.0, 1.0, 0.0]])
    probs = torch.softmax(logits, dim=1)
    loss = nn.CrossEntropyLoss()(logits, torch.tensor([0]))
    print("     softmax", probs.numpy().round(3), "loss", round(loss.item(), 3),
          "= -log(p0) =", round(-math.log(probs[0, 0].item()), 3))


def ex5():
    for lr in [1e-4, 1e-3, 1e-2, 1e-1, 1.0]:
        torch.manual_seed(0)
        m = fit(nn.Sequential(nn.Linear(64, 128), nn.ReLU(), nn.Linear(128, 10)), Xtr, ytr, epochs=20, lr=lr)
        print(f"Ex5: lr={lr:<7} val acc {acc(m, Xva, yva):.3f}")


def ex6():
    for h in [8, 32, 128, 512]:
        torch.manual_seed(0)
        m = fit(nn.Sequential(nn.Linear(64, h), nn.ReLU(), nn.Linear(h, 10)), Xtr, ytr, epochs=30)
        print(f"Ex6: hidden={h:<4} params={sum(p.numel() for p in m.parameters()):6d} test acc {acc(m, Xte, yte):.3f}")


def ex7():
    # fixed version of the buggy loop
    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 10)).to(device)   # fix 2: no Softmax layer
    loss_fn = nn.CrossEntropyLoss()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    y_long = torch.tensor(y_tr, dtype=torch.long)                                      # fix 3: long labels
    loader = DataLoader(TensorDataset(Xtr, y_long), batch_size=64, shuffle=True)
    for epoch in range(20):
        model.train()
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            loss = loss_fn(model(xb), yb)
            opt.zero_grad()                                                             # fix 1: zero grads
            loss.backward()
            opt.step()
    model.eval()                                                                        # fix 4: eval mode
    with torch.no_grad():
        print("Ex7: fixed loop val acc", round((model(Xva.to(device)).argmax(1) == yva.to(device)).float().mean().item(), 3))


def ex8():
    Xd, yd = load_diabetes(return_X_y=True)
    Xa, Xb, ya, yb = train_test_split(Xd, yd, test_size=0.2, random_state=42)
    lin_mae = mean_absolute_error(yb, LinearRegression().fit(Xa, ya).predict(Xb))
    mu, sd = ya.mean(), ya.std()                                    # standardise the target
    Xa_t = torch.tensor(Xa, dtype=torch.float32).to(device)
    ya_t = torch.tensor((ya - mu) / sd, dtype=torch.float32).reshape(-1, 1).to(device)
    torch.manual_seed(0)
    net = nn.Sequential(nn.Linear(10, 32), nn.ReLU(), nn.Linear(32, 1)).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=1e-2, weight_decay=1e-3)
    loss_fn = nn.MSELoss()
    for _ in range(300):                                            # full-batch training (small data)
        loss = loss_fn(net(Xa_t), ya_t)
        opt.zero_grad(); loss.backward(); opt.step()
    net.eval()
    with torch.no_grad():
        pred = net(torch.tensor(Xb, dtype=torch.float32).to(device)).cpu().numpy().ravel() * sd + mu
    print(f"Ex8: MLP MAE {mean_absolute_error(yb, pred):.1f} vs LinearRegression MAE {lin_mae:.1f}")


def big_mlp():
    return nn.Sequential(nn.Linear(64, 256), nn.ReLU(), nn.Linear(256, 256), nn.ReLU(), nn.Linear(256, 10))


def ex9():
    loss_fn = nn.CrossEntropyLoss()
    for n in [200, len(Xtr)]:
        torch.manual_seed(0)
        m = fit(big_mlp(), Xtr[:n], ytr[:n], epochs=100, bs=32)
        m.eval()
        with torch.no_grad():
            vl = loss_fn(m(Xva.to(device)), yva.to(device)).item()
        print(f"Ex9: {n:4d} training images -> final val loss {vl:.3f}, test acc {acc(m, Xte, yte):.3f}")


class EarlyStopper:
    """Ex10: call .step(val_loss, model) once per epoch; returns True when training should stop."""
    def __init__(self, patience=5, min_delta=0.0):
        self.patience, self.min_delta = patience, min_delta
        self.best, self.best_state, self.waited = float("inf"), None, 0

    def step(self, val_loss, model):
        if val_loss < self.best - self.min_delta:        # meaningful improvement
            self.best, self.waited = val_loss, 0
            self.best_state = copy.deepcopy(model.state_dict())
            return False
        self.waited += 1
        return self.waited >= self.patience

    def restore(self, model):
        model.load_state_dict(self.best_state)


def ex10():
    torch.manual_seed(0)
    model = big_mlp().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()
    loader = DataLoader(TensorDataset(Xtr[:200], ytr[:200]), batch_size=32, shuffle=True)
    stopper = EarlyStopper(patience=8, min_delta=0.001)
    for epoch in range(300):
        model.train()
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            loss = loss_fn(model(xb), yb); opt.zero_grad(); loss.backward(); opt.step()
        model.eval()
        with torch.no_grad():
            vl = loss_fn(model(Xva.to(device)), yva.to(device)).item()
        if stopper.step(vl, model):
            break
    stopper.restore(model)
    print(f"Ex10: stopped at epoch {epoch}, best val loss {stopper.best:.3f}, test acc {acc(model, Xte, yte):.3f}")


class DigitCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.pool = nn.MaxPool2d(2)
        self.drop = nn.Dropout(0.25)
        self.fc = nn.Linear(128, 10)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        return self.fc(self.drop(x.flatten(1)))


def random_shift(xb):
    """Ex11 augmentation: shift each batch by -1, 0 or +1 pixel in each direction."""
    dx, dy = np.random.randint(-1, 2, size=2)
    return torch.roll(xb, shifts=(int(dy), int(dx)), dims=(2, 3))


def ex11():
    img = lambda t: t.reshape(-1, 1, 8, 8)
    np.random.seed(0)
    for name, aug in [("no augmentation", None), ("random 1-pixel shifts", random_shift)]:
        torch.manual_seed(0)
        m = fit(DigitCNN(), img(Xtr), ytr, epochs=40, augment=aug)
        print(f"Ex11: CNN {name:22s} test acc {acc(m, img(Xte), yte):.3f}")


def ex12():
    path = os.path.join(tempfile.gettempdir(), "ckpt_ex12.pt")
    loss_fn = nn.CrossEntropyLoss()
    loader = DataLoader(TensorDataset(Xtr, ytr), batch_size=64, shuffle=True)

    def run_epochs(model, opt, n):
        for _ in range(n):
            model.train()
            for xb, yb in loader:
                xb, yb = xb.to(device), yb.to(device)
                loss = loss_fn(model(xb), yb); opt.zero_grad(); loss.backward(); opt.step()
        model.eval()
        with torch.no_grad():
            return loss_fn(model(Xva.to(device)), yva.to(device)).item()

    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(64, 128), nn.ReLU(), nn.Linear(128, 10)).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    v1 = run_epochs(model, opt, 5)
    torch.save({"model": model.state_dict(), "optimizer": opt.state_dict(), "epoch": 5}, path)
    # --- pretend this is a new session ---
    ck = torch.load(path, map_location=device)
    model2 = nn.Sequential(nn.Linear(64, 128), nn.ReLU(), nn.Linear(128, 10)).to(device)
    opt2 = torch.optim.Adam(model2.parameters(), lr=1e-3)
    model2.load_state_dict(ck["model"]); opt2.load_state_dict(ck["optimizer"])
    v2 = run_epochs(model2, opt2, 5)
    print(f"Ex12: val loss after epoch {ck['epoch']}: {v1:.3f} -> after resuming to epoch 10: {v2:.3f}")
    os.remove(path)


if __name__ == "__main__":
    for f in [ex1, ex2, ex3, ex4, ex5, ex6, ex7, ex8, ex9, ex10, ex11, ex12]:
        f()
