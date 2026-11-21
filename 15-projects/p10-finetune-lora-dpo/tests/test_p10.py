"""Fast tests (no training): data, scoring, the prompt mask and the hand-written DPO loss."""
import json
import math
from pathlib import Path

import torch

from src.common import KEYS, encode_sft, load_jsonl, score_output
from src.dpo_cpu import dpo_loss
from src.make_data import corrupt, make_example
import random

ROOT = Path(__file__).resolve().parents[1]


def test_dataset_sizes_and_format():
    train, test = load_jsonl(ROOT / "data/sft_train.jsonl"), load_jsonl(ROOT / "data/sft_test.jsonl")
    assert len(train) == 1350 and len(test) == 150
    emails_train = {r["messages"][1]["content"] for r in train}
    assert not emails_train & {r["messages"][1]["content"] for r in test}      # no leakage train -> test
    r = train[0]
    assert [m["role"] for m in r["messages"]] == ["system", "user", "assistant"]
    assert json.loads(r["messages"][2]["content"]) == r["target"] and set(r["target"]) == set(KEYS)


def test_dpo_pairs_differ_and_rejected_is_worse():
    for p in load_jsonl(ROOT / "data/dpo_train.jsonl")[:50]:
        assert p["chosen"][0]["content"] != p["rejected"][0]["content"]
        target = json.loads(p["chosen"][0]["content"])
        assert not score_output(p["rejected"][0]["content"], target)["exact_match"]


def test_score_output_is_strict():
    t = {"order_id": None, "product": "SoundBuds X", "intent": "refund", "urgency": "medium"}
    assert score_output(json.dumps(t), t)["exact_match"]
    assert not score_output("```json\n" + json.dumps(t) + "\n```", t)["valid_json"]      # fences are invalid
    assert not score_output(json.dumps({**t, "extra": 1}), t)["valid_json"]               # wrong keys
    s = score_output(json.dumps({**t, "intent": "cancel_order"}), t)
    assert s["valid_json"] and not s["exact_match"] and s["product"] and not s["intent"]


def test_dpo_loss_matches_formula_and_direction():
    pi_c, pi_r = torch.tensor([-5.0]), torch.tensor([-7.0])
    ref_c, ref_r = torch.tensor([-6.0]), torch.tensor([-6.0])
    loss, margin = dpo_loss(pi_c, pi_r, ref_c, ref_r, beta=0.1)
    assert math.isclose(margin.item(), 2.0)          # (-5 - -6) - (-7 - -6) = 1 - (-1)
    assert math.isclose(loss.item(), -math.log(1 / (1 + math.exp(-0.2))), rel_tol=1e-6)
    # equal policy and reference -> margin 0 -> loss = log(2)
    l0, _ = dpo_loss(ref_c, ref_r, ref_c, ref_r)
    assert math.isclose(l0.item(), math.log(2), rel_tol=1e-6)
    # gradient: raising the chosen log-prob must LOWER the loss
    x = torch.tensor([-5.0], requires_grad=True)
    dpo_loss(x, pi_r, ref_c, ref_r)[0].backward()
    assert x.grad.item() < 0


def test_prompt_tokens_are_masked():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-135M-Instruct")
    msgs = load_jsonl(ROOT / "data/sft_train.jsonl")[0]["messages"]
    ids, labels = encode_sft(msgs, tok)
    trained = [t for t, l in zip(ids, labels) if l != -100]
    assert labels[0] == -100 and 0 < len(trained) < len(ids)
    assert "order_id" in tok.decode(trained) and "Extract" not in tok.decode(trained)


def test_generator_is_seeded():
    a = [make_example(random.Random(1)) for _ in range(3)]
    b = [make_example(random.Random(1)) for _ in range(3)]
    assert a == b
    bad, kind = corrupt({"order_id": None, "product": None, "intent": "refund", "urgency": "low"}, random.Random(3))
    assert isinstance(bad, str) and kind
