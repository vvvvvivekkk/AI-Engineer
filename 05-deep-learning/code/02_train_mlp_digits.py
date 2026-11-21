"""
02_train_mlp_digits.py
Train a multi-layer perceptron (MLP) on scikit-learn's 8x8 digits, save the weights, and load them back.
Run:  python 02_train_mlp_digits.py        (under a minute on CPU; uses a GPU automatically if present)
"""
# Path for file locations next to this script
from pathlib import Path
# PyTorch core, layers, and batching helpers
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
# the digits dataset and the splitter come from scikit-learn (no download needed)
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

# use the GPU if there is one, otherwise the CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
# tiny models run faster on a single CPU thread
if device == "cpu":
    torch.set_num_threads(1)
# same random start every run
torch.manual_seed(0)

# load 1,797 digit images as rows of 64 pixel values (0..16)
X, y = load_digits(return_X_y=True)
# scale pixels to 0..1 and use 32-bit floats, which neural networks expect
X = (X / 16.0).astype("float32")
# 80% for training+validation, 20% locked away for the final test
X_tv, X_test, y_tv, y_test = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
# split the 80% again: 75% train, 25% validation
X_train, X_val, y_train, y_val = train_test_split(X_tv, y_tv, test_size=0.25, random_state=0, stratify=y_tv)


# helper: NumPy arrays -> tensors (labels must be long integers for CrossEntropyLoss)
def to_tensors(Xa, ya):
    return torch.tensor(Xa), torch.tensor(ya, dtype=torch.long)


Xtr, ytr = to_tensors(X_train, y_train)
Xva, yva = to_tensors(X_val, y_val)
Xte, yte = to_tensors(X_test, y_test)
# DataLoader serves shuffled batches of 64 examples
loader = DataLoader(TensorDataset(Xtr, ytr), batch_size=64, shuffle=True)


# the model: 64 pixels -> 128 hidden neurons -> 10 scores (logits)
class DigitMLP(nn.Module):
    def __init__(self, hidden=128):
        super().__init__()                    # always call the parent constructor
        self.layer1 = nn.Linear(64, hidden)   # first fully connected layer
        self.layer2 = nn.Linear(hidden, 10)   # output layer, one score per digit

    def forward(self, x):
        x = torch.relu(self.layer1(x))        # weighted sums, then ReLU bends
        return self.layer2(x)                 # raw scores; no softmax (the loss does it)


# helper: accuracy of a model on some data, in evaluation mode without gradients
def accuracy(model, Xs, ys):
    model.eval()
    with torch.no_grad():
        preds = model(Xs.to(device)).argmax(dim=1)   # biggest score = predicted digit
    return (preds == ys.to(device)).float().mean().item()


# build the model on the chosen device
model = DigitMLP().to(device)
# classification loss and the Adam optimizer
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

# 40 epochs = 40 passes over the training set
for epoch in range(40):
    model.train()                                     # training mode
    for xb, yb in loader:                             # one batch at a time
        xb, yb = xb.to(device), yb.to(device)         # same device as the model
        loss = loss_fn(model(xb), yb)                 # forward pass + loss
        optimizer.zero_grad()                         # clear old gradients
        loss.backward()                               # backprop
        optimizer.step()                              # update weights
    if epoch % 10 == 9:                               # report every 10 epochs
        print(f"epoch {epoch+1}: last batch loss {loss.item():.3f}, val acc {accuracy(model, Xva, yva):.3f}")

# the final, one-time test
print("test accuracy:", round(accuracy(model, Xte, yte), 3))

# save only the learned weights (the state_dict) next to this script
path = Path(__file__).with_name("digit_mlp.pt")
torch.save(model.state_dict(), path)
# rebuild an empty model from the class and load the saved numbers into it
restored = DigitMLP().to(device)
restored.load_state_dict(torch.load(path, map_location=device))
print("restored model test accuracy:", round(accuracy(restored, Xte, yte), 3), "| saved to", path.name)
