"""
03_train_cnn_digits.py
Train a small convolutional neural network (CNN) on the 8x8 digits.
Run:  python 03_train_cnn_digits.py        (under a minute on CPU)
"""
# PyTorch pieces
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
# data from scikit-learn
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

# choose GPU if available, otherwise CPU (one thread is fastest for tiny models)
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cpu":
    torch.set_num_threads(1)
torch.manual_seed(0)

# load and scale the pixels to 0..1
X, y = load_digits(return_X_y=True)
X = (X / 16.0).astype("float32")
# simple 80/20 train/test split for this script
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
# Conv2d wants (batch, channels, height, width): 1 grey channel, 8x8 pixels
Xtr = torch.tensor(X_train).reshape(-1, 1, 8, 8)
Xte = torch.tensor(X_test).reshape(-1, 1, 8, 8)
# labels as long integers
ytr = torch.tensor(y_train, dtype=torch.long)
yte = torch.tensor(y_test, dtype=torch.long)
# shuffled batches of 64
loader = DataLoader(TensorDataset(Xtr, ytr), batch_size=64, shuffle=True)


# two conv blocks, then a linear layer that outputs 10 digit scores
class DigitCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)   # 16 learnable 3x3 filters
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)  # 32 filters looking at 16 maps
        self.pool = nn.MaxPool2d(2)                               # halves height and width
        self.dropout = nn.Dropout(0.25)                           # switch off 25% during training
        self.fc = nn.Linear(32 * 2 * 2, 10)                       # 128 numbers -> 10 scores

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))   # (N, 16, 4, 4)
        x = self.pool(torch.relu(self.conv2(x)))   # (N, 32, 2, 2)
        x = x.flatten(start_dim=1)                 # (N, 128)
        return self.fc(self.dropout(x))            # (N, 10) logits


# model, loss and optimizer
model = DigitCNN().to(device)
loss_fn = nn.CrossEntropyLoss()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
print("parameters:", sum(p.numel() for p in model.parameters()))

# standard training loop
for epoch in range(30):
    model.train()
    for xb, yb in loader:
        xb, yb = xb.to(device), yb.to(device)   # move batch to device
        loss = loss_fn(model(xb), yb)           # forward + loss
        opt.zero_grad()                         # clear gradients
        loss.backward()                         # backprop
        opt.step()                              # update

# evaluate once: eval mode turns dropout off, no_grad skips gradient bookkeeping
model.eval()
with torch.no_grad():
    acc = (model(Xte.to(device)).argmax(1) == yte.to(device)).float().mean().item()
print("CNN test accuracy:", round(acc, 3))
