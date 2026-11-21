"""
lora_finetune_cpu.py - LoRA fine-tune a tiny chat model on a laptop CPU (no GPU needed).

The same steps as notebooks/02-lora-finetune-cpu.ipynb, as one script.

What happens:
  1. load SmolLM2-135M-Instruct (a 135-million-parameter chat model, ~270 MB download)
  2. measure how well it follows the "Chai Corner" house style BEFORE training
  3. wrap it with LoRA adapters using the `peft` library (only ~0.5% of weights train)
  4. train for a few dozen steps on 48 examples
  5. measure the house style AFTER training
  6. save the small adapter, and merge it into the base model

Run from the 13-fine-tuning folder:  python code/lora_finetune_cpu.py
Takes a few minutes on a 2-core CPU.
"""
import json                     # read the .jsonl dataset
import pathlib                  # file paths
import random                   # shuffle the training order
import time                     # time the training run

import torch                    # the deep-learning library that does the maths
from peft import LoraConfig, get_peft_model          # LoRA helpers
from transformers import AutoModelForCausalLM, AutoTokenizer  # load model + tokenizer

torch.manual_seed(0)            # fixed seed -> same results each run
random.seed(0)

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE.parent / "data"
OUT = HERE.parent / "outputs"   # where the adapter is saved (ignored by git is fine)
MODEL_ID = "HuggingFaceTB/SmolLM2-135M-Instruct"
PREFIX, SUFFIX = "Chai Corner here!", "Have a warm day!"


def load_jsonl(path):
    """Read a JSON Lines file into a list of dictionaries."""
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def encode(example, tok, max_len=128):
    """Turn one chat example into input_ids and labels.

    labels are a copy of input_ids, except the prompt part is set to -100.
    -100 means "ignore this position in the loss", so the model only learns
    to produce the assistant's answer, not to repeat the question.
    """
    msgs = example["messages"]
    prompt_ids = tok.apply_chat_template(msgs[:-1], add_generation_prompt=True, tokenize=True)
    full_ids = tok.apply_chat_template(msgs, tokenize=True)
    # Some versions return a dict-like object; keep only the list of ids.
    if not isinstance(prompt_ids, list):
        prompt_ids = prompt_ids["input_ids"]
    if not isinstance(full_ids, list):
        full_ids = full_ids["input_ids"]
    full_ids = full_ids[:max_len]
    labels = [-100] * len(prompt_ids) + full_ids[len(prompt_ids):]
    return full_ids, labels[:len(full_ids)]


def collate(batch, pad_id):
    """Pad a list of (ids, labels) to the same length so they fit in one tensor."""
    width = max(len(ids) for ids, _ in batch)
    ids = torch.full((len(batch), width), pad_id)
    lab = torch.full((len(batch), width), -100)
    att = torch.zeros((len(batch), width), dtype=torch.long)
    for i, (x, y) in enumerate(batch):
        ids[i, :len(x)] = torch.tensor(x)
        lab[i, :len(y)] = torch.tensor(y)
        att[i, :len(x)] = 1            # 1 = real token, 0 = padding
    return ids, att, lab


@torch.no_grad()
def generate(model, tok, question, system):
    """Ask the model one question and return its reply as text (greedy decoding)."""
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": question}]
    enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    out = model.generate(**enc, max_new_tokens=40, do_sample=False, pad_token_id=tok.pad_token_id)
    return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def style_score(model, tok, rows):
    """Fraction of test answers that start with the prefix and contain the suffix."""
    hits, samples = 0, []
    for r in rows:
        reply = generate(model, tok, r["messages"][1]["content"], r["messages"][0]["content"])
        hits += reply.startswith(PREFIX) and SUFFIX in reply
        samples.append(reply)
    return hits / len(rows), samples


@torch.no_grad()
def eval_loss(model, encoded, pad_id):
    """Average loss on held-out examples (lower = model finds the answers more likely)."""
    model.eval()
    ids, att, lab = collate(encoded, pad_id)
    return model(input_ids=ids, attention_mask=att, labels=lab).loss.item()


def main():
    train, test = load_jsonl(DATA / "chai_corner_train.jsonl"), load_jsonl(DATA / "chai_corner_test.jsonl")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32)

    enc_train = [encode(r, tok) for r in train]
    enc_test = [encode(r, tok) for r in test]

    before_loss = eval_loss(model, enc_test, tok.pad_token_id)
    before_style, _ = style_score(model, tok, test)
    print(f"BEFORE  test loss {before_loss:.3f}  style {before_style:.0%}")

    # LoRA: add small trainable matrices to the attention projections.
    cfg = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05,
                     target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], task_type="CAUSAL_LM")
    model = get_peft_model(model, cfg)
    model.print_trainable_parameters()

    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=2e-3)
    steps, bs = 36, 4
    t0 = time.time()
    model.train()
    for step in range(1, steps + 1):
        batch = random.sample(enc_train, bs)          # pick 4 random examples
        ids, att, lab = collate(batch, tok.pad_token_id)
        loss = model(input_ids=ids, attention_mask=att, labels=lab).loss
        loss.backward()                               # work out gradients
        opt.step()                                    # nudge the LoRA weights
        opt.zero_grad()                               # clear gradients for the next step
        if step % 6 == 0:
            print(f"step {step:3d}  loss {loss.item():.3f}  ({time.time() - t0:.0f}s)")

    after_loss = eval_loss(model, enc_test, tok.pad_token_id)
    after_style, samples = style_score(model, tok, test)
    print(f"AFTER   test loss {after_loss:.3f}  style {after_style:.0%}")
    for r, s in list(zip(test, samples))[:3]:
        print("Q:", r["messages"][1]["content"], "\nA:", s, "\n")

    OUT.mkdir(exist_ok=True)
    model.save_pretrained(OUT / "chai-lora-adapter")  # saves only the small adapter files
    merged = model.merge_and_unload()                  # fold LoRA into the base weights
    print("merged model type:", type(merged).__name__)


if __name__ == "__main__":
    main()
