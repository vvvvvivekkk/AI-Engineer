"""
trl_train.py - the "real-world" version of steps 1 and 2 using Hugging Face TRL.

**TRL** (Transformer Reinforcement Learning) is Hugging Face's library of
trainers for language models. `SFTTrainer` and `DPOTrainer` do everything our
hand-written CPU scripts do (batching, masking the prompt, the DPO loss,
reference model, logging, mixed precision) in a few lines.

Designed for a free Colab **T4 GPU** (see colab_gpu_trl-colab-only.ipynb):
    python -m src.trl_train --model HuggingFaceTB/SmolLM2-360M-Instruct --gpu
It also has a tiny CPU smoke test that checks the code runs (2 steps each):
    python -m src.trl_train --smoke

Recipe:
  1. SFT with a LoRA adapter on all linear layers, loss only on the answer
     (`completion_only_loss=True` with a prompt/completion dataset)
  2. merge the SFT adapter into the base model
  3. DPO with a NEW LoRA adapter on top of the merged SFT model. Because we pass
     `peft_config`, TRL uses the same model with the adapter switched off as the
     frozen reference - so the reference is exactly the SFT model, with no second copy in memory.
"""
from __future__ import annotations

import argparse
import json

import torch

from .common import DATA, OUT, evaluate, load_jsonl


def lora_config():
    from peft import LoraConfig
    return LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, target_modules="all-linear", task_type="CAUSAL_LM")


def run_sft(model_id: str, steps: int, batch: int, lr: float, gpu: bool, train_n: int | None) -> str:
    from datasets import load_dataset
    from trl import SFTConfig, SFTTrainer
    ds = load_dataset("json", data_files=str(DATA / "sft_train.jsonl"), split="train")
    if train_n:
        ds = ds.select(range(min(train_n, len(ds))))
    # prompt = system + user turns, completion = the assistant's JSON (the only part that is trained)
    ds = ds.map(lambda r: {"prompt": r["messages"][:-1], "completion": r["messages"][-1:]},
                remove_columns=ds.column_names)
    args = SFTConfig(output_dir=str(OUT / "trl-sft"), max_steps=steps, per_device_train_batch_size=batch,
                     gradient_accumulation_steps=1, learning_rate=lr, lr_scheduler_type="cosine", warmup_steps=max(1, steps // 20),
                     logging_steps=max(1, steps // 10), max_length=256, completion_only_loss=True,
                     fp16=gpu, use_cpu=not gpu, report_to="none", save_strategy="no")
    trainer = SFTTrainer(model=model_id, args=args, train_dataset=ds, peft_config=lora_config())
    trainer.train()
    out = str(OUT / "trl-sft-adapter")
    trainer.save_model(out)                      # saves the LoRA adapter (+ tokenizer)
    return out


def merged_sft_model(model_id: str, adapter_dir: str, gpu: bool):
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
    model = PeftModel.from_pretrained(base, adapter_dir).merge_and_unload()
    return tok, model.to("cuda" if gpu else "cpu")


def run_dpo(model, tok, steps: int, batch: int, lr: float, beta: float, gpu: bool, train_n: int | None):
    from datasets import load_dataset
    from trl import DPOConfig, DPOTrainer
    ds = load_dataset("json", data_files=str(DATA / "dpo_train.jsonl"), split="train").remove_columns(["mistake"])
    if train_n:
        ds = ds.select(range(min(train_n, len(ds))))
    args = DPOConfig(output_dir=str(OUT / "trl-dpo"), beta=beta, max_steps=steps, per_device_train_batch_size=batch,
                     learning_rate=lr, logging_steps=max(1, steps // 10), max_length=256,
                     fp16=gpu, use_cpu=not gpu, report_to="none", save_strategy="no")
    trainer = DPOTrainer(model=model, ref_model=None, args=args, train_dataset=ds, processing_class=tok,
                         peft_config=lora_config())
    trainer.train()
    trainer.save_model(str(OUT / "trl-dpo-adapter"))
    return trainer.model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="HuggingFaceTB/SmolLM2-360M-Instruct")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--sft-steps", type=int, default=300)
    ap.add_argument("--dpo-steps", type=int, default=100)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--eval-n", type=int, default=100)
    ap.add_argument("--smoke", action="store_true", help="2 steps each on CPU with the 135M model")
    a = ap.parse_args()
    train_n = None
    if a.smoke:
        a.model, a.gpu, a.sft_steps, a.dpo_steps, a.batch, a.eval_n, train_n = \
            "HuggingFaceTB/SmolLM2-135M-Instruct", False, 2, 2, 2, 2, 16
    if a.gpu and not torch.cuda.is_available():
        raise SystemExit("--gpu was given but no GPU is visible. In Colab: Runtime -> Change runtime type -> T4 GPU.")
    test = load_jsonl(DATA / "sft_test.jsonl")[:a.eval_n]

    adapter = run_sft(a.model, a.sft_steps, a.batch, 2e-4, a.gpu, train_n)
    tok, sft_model = merged_sft_model(a.model, adapter, a.gpu)
    after_sft, _ = evaluate(sft_model, tok, test)
    print("after TRL SFT:", after_sft)
    dpo_model = run_dpo(sft_model, tok, a.dpo_steps, max(1, a.batch // 2), 5e-5, 0.1, a.gpu, train_n)
    after_dpo, outs = evaluate(dpo_model, tok, test)
    print("after TRL DPO:", after_dpo)
    print("sample:", outs[0])
    res = {"model": a.model, "sft_steps": a.sft_steps, "dpo_steps": a.dpo_steps, "after_sft": after_sft,
           "after_dpo": after_dpo, "smoke_test": a.smoke}
    (OUT / "trl_results.json").write_text(json.dumps(res, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
