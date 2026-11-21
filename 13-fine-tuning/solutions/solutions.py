"""
solutions.py - runnable solutions for module 13 exercises 2, 3, 4, 6, 7 and 11.

Run from the 13-fine-tuning folder:  python solutions/solutions.py
Exercise 11 runs only if you have already saved an adapter with notebook 03 or code/lora_finetune_cpu.py.
"""
import ast                                         # parse Python-style dicts (exercise 4)
import json                                        # parse JSON lines
import math
import pathlib
import sys

import torch
import torch.nn as nn

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "code"))
from lora_layer import LoRALinear                  # our from-scratch LoRA layer


def ex2():
    d, k, r = 2048, 8192, 16
    full, lora = d * k, r * (d + k)
    print(f"Ex2: W has {full:,} numbers; LoRA r=16 adds {lora:,} ({100 * lora / full:.2f}%)")


def ex3():
    p = 3e9
    print(f"Ex3: inference 16-bit {2 * p / 1e9:.1f} GB | full FT {16 * p / 1e9:.1f} GB | "
          f"QLoRA {(0.55 * p + 0.005 * p * 16) / 1e9:.2f} GB (plus activations)")


def check_line(line):
    """Exercise 4: return a problem description, or None if the line looks fine for SFT."""
    try:
        row = json.loads(line)
    except json.JSONDecodeError:
        try:
            ast.literal_eval(line)
            return "not valid JSON (single quotes) - JSON needs double quotes"
        except Exception:
            return "not valid JSON"
    msgs = row.get("messages", [])
    roles = [m.get("role") for m in msgs]
    if not roles or roles[-1] != "assistant":
        return "last message is not from the assistant - nothing to learn"
    for a, b in zip(roles, roles[1:]):
        if a == b:
            return f"two '{a}' messages in a row - roles probably mislabelled"
    return None


def ex4():
    lines = [
        '{"messages": [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Chai Corner here! Hello! Have a warm day!"}]}',
        '{"messages": [{"role": "user", "content": "Hours?"}, {"role": "user", "content": "We open at 7 am."}]}',
        '{"messages": [{"role": "system", "content": "You are Chai Corner\'s assistant."}, {"role": "user", "content": "Wi-Fi?"}]}',
        "{'messages': [{'role': 'user', 'content': 'Parking?'}, {'role': 'assistant', 'content': 'Free street parking.'}]}",
    ]
    for i, line in enumerate(lines, 1):
        print(f"Ex4 line {i}: {check_line(line) or 'OK'}")


def ex6():
    torch.manual_seed(0)
    base = nn.Linear(32, 32)
    x = torch.randn(4, 32)
    outs = [LoRALinear(base, r=8, alpha=a)(x) for a in (1, 16, 1000)]
    print("Ex6: scaling r=8,alpha=16 ->", 16 / 8, "| r=16,alpha=16 ->", 16 / 16,
          "| outputs equal at init for any alpha:", all(torch.allclose(outs[0], o) for o in outs))


def absmax_block_error(w, block, bits=4):
    qmax = 2 ** (bits - 1) - 1
    blocks = w.view(-1, block)
    scale = blocks.abs().amax(dim=1, keepdim=True) / qmax          # one scale per block
    deq = torch.clamp(torch.round(blocks / scale), -qmax, qmax) * scale
    return (blocks - deq).abs().mean().item()


def ex7():
    torch.manual_seed(0)
    w = torch.randn(4096) * 0.02
    w[torch.randint(0, 4096, (5,))] = 0.4
    for block in [16, 64, 256, 4096]:
        err = absmax_block_error(w, block)
        extra_bits = 32 / block                                     # one fp32 scale shared by `block` weights
        print(f"Ex7: block {block:4d}: mean abs error {err:.5f}, scale overhead {extra_bits:.3f} bits/weight")


def ex11():
    adapter = HERE / "outputs" / "chai-lora-adapter"
    if not adapter.exists():
        adapter = HERE / "notebooks" / "outputs" / "chai-corner-lora"
    if not adapter.exists():
        print("Ex11: no saved adapter found - run notebook 03 or code/lora_finetune_cpu.py first.")
        return
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    base_id = json.loads((adapter / "adapter_config.json").read_text())["base_model_name_or_path"]
    tok = AutoTokenizer.from_pretrained(base_id)
    peft_model = PeftModel.from_pretrained(AutoModelForCausalLM.from_pretrained(base_id, dtype=torch.float32), adapter).eval()
    enc = tok.apply_chat_template([{"role": "user", "content": "Do you have Wi-Fi?"}],
                                  add_generation_prompt=True, return_tensors="pt", return_dict=True)
    with torch.no_grad():
        logits_peft = peft_model(**enc).logits
        merged = peft_model.merge_and_unload()
        logits_merged = merged(**enc).logits
    diff = (logits_peft - logits_merged).abs().max().item()
    print(f"Ex11: max logit difference {diff:.2e}; allclose(atol=1e-4): {torch.allclose(logits_peft, logits_merged, atol=1e-4)}")


if __name__ == "__main__":
    ex2(); ex3(); ex4(); ex6(); ex7(); ex11()
