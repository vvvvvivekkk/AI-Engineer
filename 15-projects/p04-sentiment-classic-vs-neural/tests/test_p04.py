"""Tests for Project 4. Run with:  python -m pytest -q
The zero-shot test downloads a 25 MB model the first time (Hugging Face)."""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import classic, llm, zero_shot
from src.data import load_challenge, load_split
from src.neural import NeuralSentiment, tokenize


def ints(labels):
    return [int(l == "positive") for l in labels]


def test_data_is_balanced_and_challenge_exists():
    train, test = load_split()
    assert len(train) == 800 and len(test) == 200
    assert abs(train.label.eq("positive").mean() - 0.5) < 0.05
    assert set(load_challenge().kind) == {"sarcasm", "unseen_words", "negation", "mixed"}


def test_tokenize_adds_word_pairs():
    assert tokenize("Not bad at all") == ["not", "bad", "at", "all", "not_bad", "bad_at", "at_all"]


def test_classic_model_learns():
    train, test = load_split()
    model = classic.build().fit(train.text, ints(train.label))
    acc = (model.predict(test.text) == ints(test.label)).mean()
    assert acc > 0.8
    assert len(classic.top_words(model)["positive"]) == 8


def test_neural_model_learns():
    train, test = load_split()
    model = NeuralSentiment(epochs=10).fit(train.text, ints(train.label))
    acc = sum(p == y for p, y in zip(model.predict(test.text), ints(test.label))) / len(test)
    assert acc > 0.75


def test_zero_shot_nli_on_obvious_reviews():
    preds = zero_shot.classify(["I absolutely love it, wonderful product!",
                                "Horrible, it broke and I want a refund."], "nli")
    assert preds == [1, 0]


def test_missing_api_key_gives_clear_error(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(llm.LLMConfigError, match="ANTHROPIC_API_KEY"):
        llm.generate("hello")
