# Module 13 - Solutions

Runnable code for exercises 2, 3, 4, 6, 7 and 11 is in `solutions.py` (run `python solutions/solutions.py` from the module folder).

## 1. Prompt, RAG or fine-tune?
a) **RAG.** Rates change weekly; facts must be current and checkable. Fine-tuning would bake in stale numbers.
b) **Prompting** (plus a JSON validator and a retry). 99% is already high; fine-tuning would add cost for little gain. If the remaining 1% matters, add structured-output features or validation first.
c) **Fine-tuning** (LoRA or full fine-tune of the small model). Clear narrow task, lots of labelled data, cost matters - exactly what fine-tuning is for.
d) **Fine-tuning** is reasonable for style, but try few-shot prompting with 3-5 of their posts first; it may be enough. 300 posts is a decent SFT set if prompting falls short.

## 2. LoRA parameter counting
a) 2048 × 8192 = **16,777,216**.
b) r × (d + k) = 16 × (2048 + 8192) = **163,840**.
c) 163,840 / 16,777,216 ≈ **0.98%**.

## 3. Memory arithmetic (3B parameters, no activations)
a) 3e9 × 2 bytes = **6 GB**.
b) 3e9 × 16 bytes = **48 GB**.
c) weights 3e9 × 0.55 ≈ 1.65 GB + adapter 3e9 × 0.005 × 16 = 0.24 GB → **≈ 1.9 GB** (plus activations, often 1-3 GB for short sequences).

## 4. Spot the bug
1. OK (no system message is allowed).
2. Broken: the answer is labelled `user`, so there is no assistant message to learn from - and two user turns in a row usually indicates a mistake.
3. Broken: it ends with a user message; there is no assistant answer to train on.
4. Broken: single quotes are not valid JSON. Use `json.dumps()` to write files instead of `str()`.

## 5. Chat templates
SmolLM2 and Qwen2.5 both use `<|im_start|>role ... <|im_end|>` markers (the "ChatML" style), but they differ in details such as the **default system message** each adds when you do not supply one (SmolLM2 adds "You are a helpful AI assistant named SmolLM...", Qwen adds its own) and in their special tokens and tokenizers. Other families (Llama, Gemma, Mistral) use completely different markers. A model learns to react to *its* markers; training or running with the wrong template means the model sees unfamiliar text, so quality drops sharply or it never stops generating. Always use `tokenizer.apply_chat_template` of the model you are training.

## 6. Scaling factor
- alpha/r = 16/8 = 2.0; with r = 16 and alpha = 16 it becomes 1.0, so each unit of B A counts half as much. Setting alpha = 2r keeps the scaling at 2 when you change r, so you do not need to retune the learning rate as much.
- At initialisation B = 0, so B A = 0 and the output equals the base output whatever alpha is. `solutions.py` checks this with alpha = 1, 16 and 1000.

## 7. Quantisation error vs block size
From `solutions.py` (4-bit absmax, our fake weights with outliers):

| Block | Mean abs error | Scale overhead (bits/weight) |
|---|---|---|
| 16 | ~0.0016 | 2.0 |
| 64 | ~0.0027 | 0.5 |
| 256 | ~0.0057 | 0.125 |
| 4096 | ~0.0131 | 0.008 |

Smaller blocks = lower error but more memory for scales. 64 is a good compromise (it is the block size QLoRA uses), adding only 0.5 bits per weight - and double quantisation shrinks that further.

## 8. Rank experiment (what you should observe)
Trainable parameters grow linearly with r (r = 2 → ~230k, r = 8 → ~920k, r = 32 → ~3.7M for the four attention projections of SmolLM2-135M). For this easy style task, r = 2 already learns most of the style; larger r rarely helps on 48 examples and can overfit faster. Exact numbers vary from run to run; the point is to change one setting at a time and record everything.

## 9. Loss masking
Without masking, the loss also includes predicting the system prompt and the question. Those tokens are the same or very similar in every example, so a big part of the "learning" is spent memorising the system message, and the reported loss looks lower without the answers being better. With masking, all of the training signal goes into the answer, so the style is usually learned in fewer steps. When comparing, always measure loss on answer tokens only (use the masked labels for evaluation in both runs).

## 10. Your own dataset (marking guide)
A good report has: a clear house style that is automatically checkable (for example a regex for `REF-\d{4}`); 48/12 split with no duplicates between train and test; before/after numbers in a small table; three good and three bad outputs with comments (look for invented facts); one concrete next step (more varied questions, fewer epochs, add RAG for facts).

## 11. Merge correctness test
`solutions.py` loads the adapter onto a **float32** base, computes logits with the PeftModel, merges, recomputes, and finds a maximum difference around 1e-4 → `allclose(atol=1e-4)` passes, and greedy generations match. Small differences appear because floating-point addition is not exactly associative: (Wx) + (BAx) is computed in a different order from (W + BA)x. Important trap: in recent transformers versions `from_pretrained` may load weights in the checkpoint's stored dtype (bfloat16 for SmolLM2). Merging in bfloat16 rounds the tiny LoRA update away and the logits can differ by more than 1.0 - so load the base in float32 (or float16/bfloat16 knowingly) and use a tolerance that matches the dtype.

## 12. QLoRA capstone (marking guide)
- Notebook ran on a T4 with `fp16=True` (not bf16); the tracker has four runs with exactly one change each.
- Adapter pushed to a **private** repo using a Colab secret or environment variable - no token visible anywhere in the notebook.
- Model card lists: base model and its licence, dataset description and size, LoRA settings (r, alpha, target modules), training settings (epochs, learning rate, batch), before/after metrics, and limitations (for example "may invent shop facts; use with RAG").
