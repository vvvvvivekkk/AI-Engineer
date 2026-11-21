"""
next_token_demo.py - show the top-k next-token probabilities of a small LLM, then generate step by step.

Run:  python next_token_demo.py "The capital of France is"
Needs: transformers, torch  (first run downloads SmolLM2-135M-Instruct, about 270 MB)
"""
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"
prompt = sys.argv[1] if len(sys.argv) > 1 else "The capital of France is"

tok = AutoTokenizer.from_pretrained(NAME)              # text <-> token IDs
model = AutoModelForCausalLM.from_pretrained(NAME, dtype=torch.float32)  # the model; float32 is fast on CPU
model.eval()                                           # inference mode (switches off training-only behaviour)


def top_k_next(text, k=10):
    """Return the k most likely next tokens and their probabilities."""
    ids = tok(text, return_tensors="pt")["input_ids"]  # tokenize the text
    with torch.no_grad():                              # no training, so no gradients
        logits = model(input_ids=ids).logits[0, -1]    # scores for the token AFTER the last one
    probs = torch.softmax(logits, dim=-1)              # scores -> probabilities summing to 1
    top = torch.topk(probs, k)                         # the k biggest
    return [(tok.decode(int(i)), float(p)) for p, i in zip(top.values, top.indices)]


print(f"Prompt: {prompt!r}\nTop next tokens:")
for token, p in top_k_next(prompt):
    bar = "#" * int(p * 60)                            # a little text bar chart
    print(f"  {token!r:<14} {p:6.1%} {bar}")

# Generate 8 tokens greedily, showing the winner and its probability each time
print("\nGreedy generation, one token at a time:")
text = prompt
for step in range(8):
    best_token, best_p = top_k_next(text, k=1)[0]      # the single most likely next token
    text += best_token                                 # append it and repeat
    print(f"  step {step + 1}: + {best_token!r:<12} ({best_p:.0%})  ->  {text!r}")
