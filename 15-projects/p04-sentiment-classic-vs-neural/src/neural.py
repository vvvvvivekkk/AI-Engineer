"""
neural.py - Model 2: a tiny PyTorch neural network (an "embedding bag", like fastText).

Steps:
  1. tokenise - split text into lowercase words, and also add word pairs ("not_bad")
  2. vocabulary - give every token seen at least twice in training an id number; unknown -> id 1
  3. embedding - each id looks up a learned vector of 32 numbers (a "meaning" for that token)
  4. bag       - average the vectors of all tokens in the review (word order is mostly lost)
  5. linear    - turn the averaged vector into 2 scores: negative / positive
It learns its own word vectors from only 800 reviews, so it knows nothing about words it never saw.
"""
from __future__ import annotations

import re
from collections import Counter

import torch
from torch import nn

PAD, UNK = 0, 1


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z']+", text.lower())
    pairs = [f"{a}_{b}" for a, b in zip(words, words[1:])]   # bigrams help with "not good"
    return words + pairs


class Vocab:
    def __init__(self, texts, min_count: int = 2):
        counts = Counter(t for text in texts for t in tokenize(text))
        self.itos = ["<pad>", "<unk>"] + sorted(t for t, c in counts.items() if c >= min_count)
        self.stoi = {t: i for i, t in enumerate(self.itos)}

    def encode(self, text: str) -> list[int]:
        return [self.stoi.get(t, UNK) for t in tokenize(text)] or [UNK]

    def __len__(self):
        return len(self.itos)


class BagModel(nn.Module):
    def __init__(self, vocab_size: int, dim: int = 32):
        super().__init__()
        self.bag = nn.EmbeddingBag(vocab_size, dim, mode="mean")  # look up + average in one step
        self.out = nn.Linear(dim, 2)

    def forward(self, ids, offsets):
        return self.out(self.bag(ids, offsets))


def _batch(vocab: Vocab, texts):
    """EmbeddingBag takes all ids in one flat list plus 'offsets' saying where each review starts."""
    encoded = [vocab.encode(t) for t in texts]
    offsets = torch.tensor([0] + [len(e) for e in encoded[:-1]]).cumsum(0)
    ids = torch.tensor([i for e in encoded for i in e])
    return ids, offsets


class NeuralSentiment:
    """Small wrapper with fit / predict, so it can be used like the scikit-learn model."""

    def __init__(self, dim: int = 32, epochs: int = 30, lr: float = 0.02, seed: int = 0):
        self.dim, self.epochs, self.lr, self.seed = dim, epochs, lr, seed

    def fit(self, texts, labels):
        torch.manual_seed(self.seed)
        self.vocab = Vocab(texts)
        self.model = BagModel(len(self.vocab), self.dim)
        opt = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        loss_fn = nn.CrossEntropyLoss()
        y = torch.tensor(list(labels))
        texts = list(texts)
        g = torch.Generator().manual_seed(self.seed)
        for _ in range(self.epochs):
            self.model.train()
            perm = torch.randperm(len(texts), generator=g)
            for start in range(0, len(texts), 32):            # mini-batches of 32 reviews
                idx = perm[start:start + 32]
                ids, offsets = _batch(self.vocab, [texts[i] for i in idx])
                loss = loss_fn(self.model(ids, offsets), y[idx])
                opt.zero_grad()
                loss.backward()
                opt.step()
        return self

    @torch.no_grad()
    def predict(self, texts) -> list[int]:
        self.model.eval()
        ids, offsets = _batch(self.vocab, list(texts))
        return self.model(ids, offsets).argmax(1).tolist()

    def unknown_rate(self, texts) -> float:
        """Share of single words the model has never seen - explains failures on new vocabulary."""
        words = [w for t in texts for w in re.findall(r"[a-z']+", t.lower())]
        return sum(w not in self.vocab.stoi for w in words) / max(1, len(words))
