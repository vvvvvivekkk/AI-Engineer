"""
01_tensors_autograd.py
Tensors, autograd, and fitting a straight line with gradient descent - first by hand, then with an optimizer.
Run:  python 01_tensors_autograd.py        (a few seconds on CPU)
"""
# torch is PyTorch; nn holds ready-made layers and losses
import torch
import torch.nn as nn

# fix the random numbers so every run gives the same output
torch.manual_seed(0)

# ---- tensors ----
# a 2x2 grid of float numbers
a = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
# shape = size in each direction, dtype = number type
print("shape:", tuple(a.shape), "dtype:", a.dtype)
# @ is matrix multiplication, the core operation of every layer
print("a @ a =", (a @ a).tolist())

# ---- autograd ----
# requires_grad=True tells PyTorch to record operations on w
w = torch.tensor(3.0, requires_grad=True)
# a loss that is smallest when w = 5
loss = (w - 5) ** 2
# backward() computes d(loss)/d(w) and stores it in w.grad
loss.backward()
# by hand: 2 * (3 - 5) = -4
print("gradient at w=3:", w.grad.item())

# ---- gradient descent by hand ----
# 50 x-values between -1 and 1
x = torch.linspace(-1, 1, 50)
# targets follow y = 2x + 1 plus a little random noise
y = 2 * x + 1 + 0.2 * torch.randn(50)
# start with random slope and intercept, both tracked by autograd
w = torch.randn(1, requires_grad=True)
b = torch.randn(1, requires_grad=True)
# learning rate = size of each downhill step
lr = 0.1
# repeat the learn step 100 times
for step in range(100):
    # forward: predictions and mean squared error
    loss = ((w * x + b - y) ** 2).mean()
    # backward: gradients of the loss for w and b
    loss.backward()
    # update the weights without recording the update itself
    with torch.no_grad():
        w -= lr * w.grad
        b -= lr * b.grad
    # gradients add up by default, so reset them for the next step
    w.grad.zero_()
    b.grad.zero_()
print(f"by hand:   w={w.item():.3f} b={b.item():.3f}  (true 2 and 1)")

# ---- the same, the PyTorch way ----
# nn.Linear(1, 1) holds one weight and one bias for us
model = nn.Linear(1, 1)
# mean squared error loss
loss_fn = nn.MSELoss()
# SGD optimizer performs w = w - lr * grad for every parameter
opt = torch.optim.SGD(model.parameters(), lr=0.1)
# nn.Linear expects a column: (rows, features)
X_col, Y_col = x.reshape(-1, 1), y.reshape(-1, 1)
for step in range(100):
    loss = loss_fn(model(X_col), Y_col)   # forward + loss
    opt.zero_grad()                       # clear old gradients
    loss.backward()                       # new gradients
    opt.step()                            # update weights
print(f"optimizer: w={model.weight.item():.3f} b={model.bias.item():.3f}")
