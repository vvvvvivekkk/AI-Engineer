"""
models.py - two neural networks for 8x8 digit images.

MLP (multi-layer perceptron): flattens the 8x8 picture into a list of 64 numbers and passes it
through fully-connected layers. It ignores which pixels are neighbours.

CNN (convolutional neural network): slides small 3x3 "filters" over the picture. Each filter is a
tiny pattern detector (an edge, a curve). Because the same filter is used everywhere, a stroke is
recognised wherever it appears. Pooling then shrinks the picture, keeping the strongest signals.
Analogy: the MLP reads a page as one long string of letters; the CNN looks at it through a small
magnifying glass that it moves across the page.
"""
import torch
from torch import nn


class MLP(nn.Module):
    def __init__(self, hidden: int = 128, dropout: float = 0.2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),                 # (batch, 1, 8, 8) -> (batch, 64)
            nn.Linear(64, hidden),        # every input connects to every hidden unit
            nn.ReLU(),                    # activation: keep positives, zero out negatives
            nn.Dropout(dropout),          # randomly switch off 20% of units while training (anti-overfitting)
            nn.Linear(hidden, 10),        # 10 outputs = one score ("logit") per digit
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class SmallCNN(nn.Module):
    def __init__(self, dropout: float = 0.3):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),   # 16 filters of 3x3 -> (batch, 16, 8, 8)
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),  # 32 filters look at the 16 maps -> (batch, 32, 8, 8)
            nn.ReLU(),
            nn.MaxPool2d(2),                              # keep the max of each 2x2 square -> (batch, 32, 4, 4)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),                                 # 32*4*4 = 512 numbers
            nn.Dropout(dropout),
            nn.Linear(32 * 4 * 4, 64),
            nn.ReLU(),
            nn.Linear(64, 10),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


def count_params(model: nn.Module) -> int:
    """How many numbers the model learns."""
    return sum(p.numel() for p in model.parameters())
