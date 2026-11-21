"""
dpo_cpu.py - Step 2: DPO written by hand in PyTorch (CPU demo).

**DPO** (direct preference optimisation) teaches a model to prefer the "chosen"
answer over the "rejected" one, without training a separate reward model
(the older RLHF recipe). Analogy: a driving instructor who doesn't give marks
out of 10, but repeatedly says "that turn was better than this one".

The whole idea fits in one formula. For each pair:
    logp(answer) = how likely the model finds the answer (sum of token log-probabilities)
    margin = [logp_policy(chosen) - logp_ref(chosen)] - [logp_policy(rejected) - logp_ref(rejected)]
    loss   = -log(sigmoid(beta * margin))
  * the **policy** is the model we are training
  * the **reference** is a frozen copy (here: the SFT model before DPO). Comparing
    with it stops the policy drifting too far from what it already knew.
  * **beta** controls how strongly we push (0.1 is a common default).
Minimising the loss raises the chosen answer's likelihood relative to the rejected one.

Trick used here: the reference log-probs are computed ONCE before training
(the reference never changes), so we never need two models in memory.
TRL's DPOTrainer offers the same option (precompute_ref_log_probs=True).

Run:  python -m src.dpo_cpu                 (default: 30 steps on 64 pairs; a few minutes on an idle 2-core CPU)
      python -m src.dpo_cpu --steps 6 --train-n 12 --eval-n 4   (quick mode)
"""
from __future__ import annotations

import argparse
import json
import random
import time

import torch
import torch.nn.functional as F

from .common import DATA, OUT, collate, encode_sft, evaluate, load_base, load_jsonl


def dpo_loss(pi_c: torch.Tensor, pi_r: torch.Tensor, ref_c: torch.Tensor, ref_r: torch.Tensor,
             beta: float = 0.1) -> tuple[torch.Tensor, torch.Tensor]:
    """The DPO loss (mean over the batch) and the per-pair margins (for logging)."""
    margin = (pi_c - ref_c) - (pi_r - ref_r)
    return -F.logsigmoid(beta * margin).mean(), margin


def seq_logps(model, batch: list[tuple[list[int], list[int]]], pad_id: int) -> torch.Tensor:
    """Sum of log-probabilities of the ANSWER tokens (labels != -100) for each sequence."""
    ids, att, lab = collate(batch, pad_id)
    logits = model(input_ids=ids, attention_mask=att).logits[:, :-1]      # prediction for the NEXT token
    targets = lab[:, 1:]
    mask = targets != -100
    logp = torch.log_softmax(logits.float(), dim=-1)
    picked = torch.gather(logp, 2, targets.clamp(min=0).unsqueeze(-1)).squeeze(-1)
    return (picked * mask).sum(dim=1)


def encode_pair(pair: dict, tok) -> tuple[tuple, tuple]:
    return encode_sft(pair["prompt"] + pair["chosen"], tok), encode_sft(pair["prompt"] + pair["rejected"], tok)


@torch.no_grad()
def pair_logps(model, encoded: list[tuple], pad_id: int, bs: int = 8) -> tuple[torch.Tensor, torch.Tensor]:
    model.eval()
    c, r = [], []
    for i in range(0, len(encoded), bs):
        chunk = encoded[i:i + bs]
        c.append(seq_logps(model, [x[0] for x in chunk], pad_id))
        r.append(seq_logps(model, [x[1] for x in chunk], pad_id))
    return torch.cat(c), torch.cat(r)


def load_policy():
    """Start from the SFT adapter if step 1 was run; otherwise from a fresh LoRA on the base model."""
    from peft import LoraConfig, PeftModel, get_peft_model
    tok, base = load_base()
    path = OUT / "sft-lora-adapter"
    if path.exists():
        print("starting from the SFT adapter in outputs/sft-lora-adapter")
        return tok, PeftModel.from_pretrained(base, str(path), is_trainable=True), "sft-adapter"
    print("no SFT adapter found - starting from the base model with a new LoRA adapter")
    cfg = LoraConfig(r=16, lora_alpha=32, task_type="CAUSAL_LM", target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
    return tok, get_peft_model(base, cfg), "base"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--beta", type=float, default=0.1)
    ap.add_argument("--train-n", type=int, default=64)
    ap.add_argument("--eval-n", type=int, default=10, help="test emails for the JSON check after DPO")
    ap.add_argument("--pairs", default=str(DATA / "dpo_train.jsonl"), help="e.g. data/dpo_from_p6.jsonl")
    ap.add_argument("--results", default="results_dpo.json", help="file name in data/ for the metrics")
    args = ap.parse_args()
    torch.manual_seed(0)
    random.seed(0)

    tok, model, start = load_policy()
    train = [encode_pair(p, tok) for p in load_jsonl(args.pairs)[:args.train_n]]
    test = [encode_pair(p, tok) for p in load_jsonl(DATA / "dpo_test.jsonl")]
    pad = tok.pad_token_id

    t0 = time.time()
    ref_c, ref_r = pair_logps(model, train, pad)                 # reference = model before DPO (frozen numbers)
    test_ref_c, test_ref_r = pair_logps(model, test, pad)
    before_pref = (test_ref_c > test_ref_r).float().mean().item()
    print(f"reference log-probs ready ({time.time() - t0:.0f}s). Held-out pairs where chosen is already "
          f"more likely: {before_pref:.0%}")

    sft_test = load_jsonl(DATA / "sft_test.jsonl")[:args.eval_n]
    before_json, _ = evaluate(model, tok, sft_test)                 # the starting point, same emails as after
    print("JSON check before DPO:", before_json)

    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.lr)
    idx = list(range(len(train)))
    losses = []
    for step in range(1, args.steps + 1):
        model.train()
        b = random.sample(idx, args.batch)
        pi_c = seq_logps(model, [train[i][0] for i in b], pad)
        pi_r = seq_logps(model, [train[i][1] for i in b], pad)
        loss, margin = dpo_loss(pi_c, pi_r, ref_c[b], ref_r[b], args.beta)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        opt.zero_grad()
        losses.append(round(loss.item(), 4))
        if step % 5 == 0 or step == 1:
            print(f"step {step:3d}  dpo loss {loss.item():.3f}  mean margin {margin.mean().item():+.2f}  "
                  f"({time.time() - t0:.0f}s)")

    pi_c, pi_r = pair_logps(model, test, pad)
    after_pref = (pi_c > pi_r).float().mean().item()
    reward_acc = (((pi_c - test_ref_c) - (pi_r - test_ref_r)) > 0).float().mean().item()
    print(f"held-out pairs where chosen is more likely: before {before_pref:.0%} -> after {after_pref:.0%}; "
          f"implicit-reward accuracy {reward_acc:.0%}")

    after_json, outs = evaluate(model, tok, sft_test)
    print("JSON check after DPO:", after_json)
    model.save_pretrained(OUT / "dpo-lora-adapter")
    results = {"start": start, "pairs_file": args.pairs, "steps": args.steps, "beta": args.beta, "lr": args.lr,
               "train_pairs": len(train), "test_pairs": len(test),
               "heldout_chosen_more_likely_before": round(before_pref, 3),
               "heldout_chosen_more_likely_after": round(after_pref, 3),
               "heldout_implicit_reward_accuracy": round(reward_acc, 3),
               "json_eval_before_dpo": before_json, "json_eval_after_dpo": after_json, "loss_curve": losses, "sample_outputs": outs[:3],
               "seconds": round(time.time() - t0)}
    (DATA / args.results).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("saved adapter -> outputs/dpo-lora-adapter, metrics -> data/results_dpo.json")


if __name__ == "__main__":
    main()
