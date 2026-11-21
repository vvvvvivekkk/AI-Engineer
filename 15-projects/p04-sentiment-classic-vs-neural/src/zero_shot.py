"""
zero_shot.py - Model 3: pretrained transformers that were NEVER trained on our reviews.

"Zero-shot" = the model gets zero labelled examples from our dataset. It relies on what it learned
from huge amounts of other text. Three ways are available (ZERO_SHOT_METHOD in .env):

  * nli  (default) - a small Natural Language Inference model (25 MB). NLI models answer
                     "does sentence A imply sentence B?". We ask: does the review imply
                     "The sentiment of this review is positive." vs "... negative."?
                     True zero-shot: it was never trained on sentiment labels at all.
  * sst2           - DistilBERT fine-tuned on SST-2 movie-review sentiment (260 MB). Not strictly
                     zero-shot (it has seen sentiment labels), but zero-shot for OUR product reviews.
                     A good picture of "use a pretrained model off the shelf".
  * llm            - ask a chat model "positive or negative?" via src/llm.py (LLM_PROVIDER in .env).
                     The default local 360M model is weak at this; use ollama/anthropic/openai for
                     a fair LLM result.
"""
from __future__ import annotations

import os
from functools import lru_cache

import torch

NLI_MODEL = os.getenv("NLI_MODEL", "MoritzLaurer/xtremedistil-l6-h256-zeroshot-v1.1-all-33")
SST2_MODEL = os.getenv("SST2_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")


@lru_cache(maxsize=None)
def _pipe(task: str, model: str):
    from transformers import pipeline
    torch.set_num_threads(int(os.getenv("TORCH_THREADS", "2")))
    return pipeline(task, model=model)


def classify(texts: list[str], method: str = "nli") -> list[int]:
    """Return 1 for positive, 0 for negative, for each text."""
    if method == "nli":
        clf = _pipe("zero-shot-classification", NLI_MODEL)
        out = clf(list(texts), candidate_labels=["positive", "negative"],
                  hypothesis_template="The sentiment of this review is {}.", batch_size=16)
        out = [out] if isinstance(out, dict) else out
        return [int(o["labels"][0] == "positive") for o in out]
    if method == "sst2":
        clf = _pipe("sentiment-analysis", SST2_MODEL)
        return [int(o["label"] == "POSITIVE") for o in clf(list(texts), batch_size=16)]
    if method == "llm":
        from .llm import generate
        preds = []
        for t in texts:
            reply = generate(f"Review: {t}\nIs the sentiment of this review positive or negative? "
                             "Answer with one word: positive or negative.", max_new_tokens=5).lower()
            preds.append(int("positive" in reply and "negative" not in reply))
        return preds
    raise ValueError(f"unknown zero-shot method {method!r} (use nli, sst2 or llm)")
