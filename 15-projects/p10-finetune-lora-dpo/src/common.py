"""
common.py - helpers shared by the SFT, DPO and evaluation scripts.

Words used here:
  **token** - a small piece of text (a word or part of a word). Models read and
      write tokens, each identified by a number (its "id").
  **chat template** - the exact text layout a chat model was trained on
      (where the system, user and assistant turns start and end). The tokenizer
      applies it for us with apply_chat_template.
  **labels with -100** - when training, we only want the model to learn the
      ANSWER, not to repeat the email. Positions set to -100 are ignored by the loss.
  **greedy decoding** - always pick the single most likely next token
      (repeatable, good for evaluation).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"                         # adapters / merged models (large, not committed)
MODEL_ID = os.getenv("BASE_MODEL", "HuggingFaceTB/SmolLM2-135M-Instruct")
KEYS = ["order_id", "product", "intent", "urgency"]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def load_base(model_id: str = MODEL_ID):
    """Load the tokenizer and the base model in full precision (CPU friendly)."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
    return tok, model


def _ids(x):
    """apply_chat_template may return a list or a dict-like object depending on the version."""
    return x if isinstance(x, list) else x["input_ids"]


def encode_sft(messages: list[dict], tok, max_len: int = 192) -> tuple[list[int], list[int]]:
    """Token ids for the full conversation, and labels that hide the prompt part with -100."""
    prompt_ids = _ids(tok.apply_chat_template(messages[:-1], add_generation_prompt=True, tokenize=True))
    full_ids = _ids(tok.apply_chat_template(messages, tokenize=True))[:max_len]
    labels = ([-100] * len(prompt_ids) + full_ids[len(prompt_ids):])[:len(full_ids)]
    return full_ids, labels


def collate(batch: list[tuple[list[int], list[int]]], pad_id: int):
    """Pad examples to the same length so they stack into one tensor (a 'batch')."""
    width = max(len(ids) for ids, _ in batch)
    ids = torch.full((len(batch), width), pad_id)
    lab = torch.full((len(batch), width), -100)
    att = torch.zeros((len(batch), width), dtype=torch.long)
    for i, (x, y) in enumerate(batch):
        ids[i, :len(x)] = torch.tensor(x)
        lab[i, :len(y)] = torch.tensor(y)
        att[i, :len(x)] = 1
    return ids, att, lab


FEW_SHOT = [  # used only for the "prompting" baseline: show the base model one worked example
    {"role": "user", "content": "Hi,\nMy FitBand Pro (ORD-55555) came with a cracked case.\nThanks,\nAnna"},
    {"role": "assistant", "content": '{"order_id": "ORD-55555", "product": "FitBand Pro", "intent": "damaged_item", '
                                     '"urgency": "medium"}'},
]


@torch.no_grad()
def generate_json(model, tok, system: str, email: str, few_shot: bool = False, max_new_tokens: int = 48) -> str:
    msgs = [{"role": "system", "content": system}] + (FEW_SHOT if few_shot else []) + [{"role": "user", "content": email}]
    enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    enc = {k: v.to(model.device) for k, v in enc.items()}          # same device as the model (CPU or GPU)
    out = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=tok.pad_token_id)
    return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def score_output(text: str, target: dict) -> dict:
    """Strict checks: valid JSON object with exactly our keys? exact match? per-field matches?"""
    try:
        obj = json.loads(text)
        valid = isinstance(obj, dict) and set(obj) == set(KEYS)
    except json.JSONDecodeError:
        obj, valid = None, False
    fields = {k: bool(valid and obj.get(k) == target[k]) for k in KEYS}
    return {"valid_json": valid, "exact_match": valid and obj == target, **fields}


def evaluate(model, tok, rows: list[dict], few_shot: bool = False) -> tuple[dict, list[str]]:
    """Run the model on test rows; return averaged scores and the raw outputs."""
    model.eval()
    scores, outputs = [], []
    for r in rows:
        system, email = r["messages"][0]["content"], r["messages"][1]["content"]
        text = generate_json(model, tok, system, email, few_shot=few_shot)
        outputs.append(text)
        scores.append(score_output(text, r["target"]))
    avg = {k: round(sum(s[k] for s in scores) / len(scores), 3) for k in scores[0]}
    return avg, outputs
