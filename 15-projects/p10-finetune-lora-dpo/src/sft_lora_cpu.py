"""
sft_lora_cpu.py - Step 1: LoRA supervised fine-tuning on a laptop CPU.

**LoRA** (low-rank adaptation) - instead of changing all 135 million weights,
we freeze them and add small extra matrices to some layers; only those train
(here about 0.7% of the parameter count). Analogy: instead of rewriting a
textbook, you add sticky notes to a few pages. The notes are tiny (a few MB),
quick to train, and can be removed or merged in later.

What this script does:
  1. load SmolLM2-135M-Instruct
  2. BASELINE: measure JSON validity / exact match with plain prompting AND with
     one worked example in the prompt ("few-shot")
  3. add LoRA adapters with `peft` and train for a few dozen steps
  4. measure again, save the adapter to outputs/sft-lora-adapter and the
     numbers to data/results_sft.json

Run:  python -m src.sft_lora_cpu                      (default: 30 steps, 10 test emails; ~5 min on an idle 2-core CPU)
      python -m src.sft_lora_cpu --steps 15 --eval-n 5   (quick mode, used by the Colab quick-start)
      python -m src.sft_lora_cpu --zero-shot    (also measure plain prompting without an example)
"""
from __future__ import annotations

import argparse
import json
import random
import time

import torch
from peft import LoraConfig, get_peft_model

from .common import DATA, MODEL_ID, OUT, collate, encode_sft, evaluate, load_base, load_jsonl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--train-n", type=int, default=400, help="CPU subset of the 1,350 training examples")
    ap.add_argument("--eval-n", type=int, default=10)
    ap.add_argument("--zero-shot", action="store_true", help="also test plain prompting (slow: the base model rambles)")
    ap.add_argument("--results", default="results_sft.json", help="file name in data/ for the metrics")
    args = ap.parse_args()
    torch.manual_seed(0)
    random.seed(0)
    torch.set_num_threads(max(1, torch.get_num_threads()))

    train = load_jsonl(DATA / "sft_train.jsonl")[:args.train_n]
    test = load_jsonl(DATA / "sft_test.jsonl")[:args.eval_n]
    tok, model = load_base()

    t0 = time.time()
    zero = evaluate(model, tok, test, few_shot=False)[0] if args.zero_shot else None
    few, few_out = evaluate(model, tok, test, few_shot=True)
    print(f"BEFORE (prompting)  zero-shot {zero}\n                    few-shot  {few}   ({time.time() - t0:.0f}s)")
    print("  sample few-shot output:", few_out[0][:120])

    # LoRA on the attention projections: r = size of the small matrices, alpha = their scaling.
    cfg = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                     target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
    model = get_peft_model(model, cfg)
    model.print_trainable_parameters()

    encoded = [encode_sft(r["messages"], tok) for r in train]
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.lr)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 5))   # short warm-up
    model.train()
    t1, losses = time.time(), []
    for step in range(1, args.steps + 1):
        ids, att, lab = collate(random.sample(encoded, args.batch), tok.pad_token_id)
        loss = model(input_ids=ids, attention_mask=att, labels=lab).loss
        loss.backward()                         # compute gradients (only LoRA weights have them)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        opt.zero_grad()
        losses.append(round(loss.item(), 4))
        if step % 10 == 0 or step == 1:
            print(f"step {step:3d}  loss {loss.item():.3f}  ({time.time() - t1:.0f}s)")

    after, out = evaluate(model, tok, test)
    print(f"AFTER LoRA SFT (no examples in prompt) {after}")
    for r, o in list(zip(test, out))[:3]:
        print(" email:", r["messages"][1]["content"].replace("\n", " | ")[:90], "\n   ->", o)

    OUT.mkdir(exist_ok=True)
    model.save_pretrained(OUT / "sft-lora-adapter")          # only the small adapter files
    tok.save_pretrained(OUT / "sft-lora-adapter")
    results = {"base_model": MODEL_ID, "steps": args.steps, "batch": args.batch, "lr": args.lr,
               "train_examples": len(train), "test_examples": len(test),
               "before_zero_shot": zero, "before_few_shot": few, "after_sft": after,
               "loss_curve": losses, "train_seconds": round(time.time() - t1), "sample_outputs": out[:5]}
    (DATA / args.results).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("saved adapter -> outputs/sft-lora-adapter, metrics -> data/results_sft.json")


if __name__ == "__main__":
    main()
