"""
generate_text.py - tiny text generation on a CPU with SmolLM2-135M-Instruct.

Run:  python generate_text.py
Needs: transformers, torch  (first run downloads about 270 MB)
The model is very small, so expect odd or wrong answers. The mechanics are the same as big chat models.
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"
torch.manual_seed(0)                                   # fix the random seed so sampling gives the same text each run

# --- Way 1: plain text continuation with a pipeline --------------------------
gen = pipeline("text-generation", model=NAME, dtype=torch.float32)   # float32: bfloat16 weights are very slow on most CPUs
out = gen("The three most useful Python libraries are", max_new_tokens=30, do_sample=False)
print("Continuation:\n", out[0]["generated_text"], "\n")

# --- Way 2: chat format, the way instruct models expect to be used -----------
tok = AutoTokenizer.from_pretrained(NAME)
model = AutoModelForCausalLM.from_pretrained(NAME, dtype=torch.float32)
messages = [
    {"role": "system", "content": "You are a friendly teacher. Answer in one sentence."},
    {"role": "user", "content": "What is a token in NLP?"},
]
# apply_chat_template wraps the messages in the special markers this model was trained with
inputs = tok.apply_chat_template(messages, add_generation_prompt=True,
                                 return_tensors="pt", return_dict=True)
with torch.no_grad():
    new = model.generate(**inputs, max_new_tokens=40, do_sample=False)   # greedy: always pick the top token
answer = tok.decode(new[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)  # keep only the new tokens
print("Chat answer:\n", answer)
