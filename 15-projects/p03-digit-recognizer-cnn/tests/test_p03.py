"""Tests for Project 3 (fast: a few epochs only). Run with:  python -m pytest -q"""
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data import augment, load_arrays, loader, split
from src.models import MLP, SmallCNN
from src.train import fit, predict

torch.set_num_threads(2)


def test_data_shapes_and_split():
    images, labels = load_arrays()
    assert images.shape == (1797, 1, 8, 8) and images.max() <= 1.0
    (x_tr, _), (x_val, _), (x_te, _) = split(images, labels)
    assert len(x_tr) + len(x_val) + len(x_te) == 1797


def test_models_output_ten_scores():
    x = torch.zeros(4, 1, 8, 8)
    assert MLP()(x).shape == (4, 10)
    assert SmallCNN()(x).shape == (4, 10)


def test_augment_keeps_shape_and_range():
    x = torch.rand(5, 1, 8, 8)
    y = augment(x, torch.Generator().manual_seed(0))
    assert y.shape == x.shape and y.min() >= 0 and y.max() <= 1


def test_cnn_learns_quickly():
    images, labels = load_arrays()
    (x_tr, y_tr), (x_val, y_val), (x_te, y_te) = split(images, labels)
    torch.manual_seed(0)
    model, hist = fit(SmallCNN(), loader(x_tr, y_tr, shuffle=True), loader(x_val, y_val), epochs=5)
    acc = (predict(model, torch.from_numpy(x_te)).numpy() == y_te).mean()
    assert acc > 0.85                       # 10% would be random guessing
    assert hist["val_loss"][-1] < hist["val_loss"][0]
