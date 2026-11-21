# Module 13 - Trainer notes

Before teaching: read `concepts.md`, run notebooks 01-03 yourself (03 downloads ~270 MB - do it before class, the model is then cached), and if possible run notebook 04 once on Colab so you know how long it takes. Open `excel/gpu-memory-estimator.xlsx` for a live demo.

## 1. What students should be able to do after the session

- Choose between prompting, RAG and fine-tuning for a scenario and justify it.
- Write a correct chat-format JSONL example and explain why the chat template and loss masking matter.
- Explain LoRA's formula and count its trainable parameters for a given layer and rank.
- Explain 4-bit quantisation and what QLoRA adds.
- Run a LoRA fine-tune with `peft`, evaluate before/after, save, reload and merge the adapter.
- Explain how to share an adapter safely (token in environment, licence, model card).

## 2. Teaching sequence (2-hour session)

| Time | Activity | Details |
|---|---|---|
| 0:00-0:10 | Hook | Show the Chai Corner before/after outputs from notebook 03 (style 0% → most). Ask: "How did a laptop do that?" |
| 0:10-0:25 | Prompt vs RAG vs fine-tune | Decision diagram slide. Students classify the 4 cases of exercise 1 in pairs. |
| 0:25-0:40 | SFT data and chat templates | Open `data/chai_corner_train.jsonl`; run notebook 03 steps 2-5 to show the template and the masked labels. |
| 0:40-1:00 | LoRA | Recipe-card analogy, LoRA picture slide, parameter counting on the board (exercise 2). Run notebook 01 steps 5-7. |
| 1:00-1:05 | Break | Start notebook 03's training cell before the break if the machine is slow. |
| 1:05-1:25 | Quantisation and QLoRA | Rounding-prices analogy; notebook 02 steps 3-5; memory estimator spreadsheet live. |
| 1:25-1:45 | Real fine-tune | Notebook 03 steps 6-13: before, LoRA wrap, train, after, read outputs critically (invented facts!), save, reload, merge. |
| 1:45-1:55 | QLoRA on Colab + sharing | Walk through notebook 04's cells (do not run live unless you have a GPU ready). Explain the guarded push. |
| 1:55-2:00 | Recap and homework | Exercises 5-12; exercise 12 is the capstone. |

For a 1-hour version: skip notebook 02 (show the quant-levels slide only) and show notebook 03 outputs instead of training live.

## 3. Common student mistakes and fixes

1. **Fine-tuning to teach facts.** Fix: show the invented facts in notebook 03's after-training answers. Facts → RAG.
2. **Building the prompt string by hand instead of using the chat template.** Fix: print `apply_chat_template(..., tokenize=False)` and compare; always use the tokenizer's template.
3. **Forgetting `add_generation_prompt=True` at inference.** The model then continues the user's message instead of answering. Fix: show both outputs side by side.
4. **Evaluating on training examples.** Fix: insist on the held-out `chai_corner_test.jsonl`; explain overfitting with the "memorised answers to last year's exam" analogy.
5. **Learning rate copied from full fine-tuning (e.g. 1e-5) for LoRA, so nothing changes - or 1e-2, so loss explodes.** Fix: start around 1e-4 to 2e-4 on GPU runs; watch the loss curve.
6. **Thinking `r` is "the bigger the better".** Fix: notebook 01 shows r = 2 already recovers a rank-2 change; exercise 8.
7. **Using `bf16=True` on a T4.** The T4 lacks fast bfloat16; use `fp16=True` (as in notebook 04).
8. **Merging into the 4-bit model.** Fix: load a 16-bit base, attach the adapter, then `merge_and_unload()`.
9. **Loading the base in bfloat16 by accident and getting different results after merging.** Fix: pass `dtype=torch.float32` (CPU) explicitly, as our notebooks do.
10. **Pasting an HF token into a notebook.** Fix: environment variable or Colab secret only; the notebooks' push cells are guarded and do nothing by default.
11. **Version errors** (e.g. `max_seq_length` unknown in `SFTConfig`). Fix: argument names change between versions; check the installed version and the docs (`max_length` in current TRL).

## 4. Questions to check understanding (with answers)

1. *When should you fine-tune instead of using RAG?* When the problem is behaviour, style, format or a narrow skill (or you need a smaller, cheaper model), not missing facts - and you have data and an eval.
2. *What does `-100` in the labels mean?* "Ignore this position in the loss" - used to mask the prompt so only the answer is learned.
3. *Why does LoRA start with B = 0?* So B A = 0 and the model behaves exactly like the original before training.
4. *How many trainable numbers does LoRA add to a d × k layer?* r × (d + k).
5. *What is merging?* Computing W' = W + (alpha/r) B A once, so the adapter adds no inference cost and `peft` is not needed.
6. *Why is full fine-tuning so memory-hungry?* Each trainable weight needs its gradient and optimizer states as well - about 16 bytes per parameter with Adam in mixed precision.
7. *What does NF4 do differently from uniform 4-bit?* Places its 16 levels according to a normal distribution, denser near zero where most weights are.
8. *What are the parts of QLoRA?* 4-bit NF4 frozen base, 16-bit LoRA adapters, double quantisation, paged optimizers.
9. *Training loss fell a lot but test loss rose. What happened?* Overfitting - reduce epochs/learning rate, add data, or use more dropout.
10. *How do you share an adapter safely?* `push_to_hub` with a token from the environment or a secret; include a model card; respect the base model's licence.

## 5. Adapting for faster / slower groups

**Faster groups**
- Exercise 9 (no loss masking) and exercise 11 (merge correctness) in class.
- Replace the hand-written loop in notebook 03 with TRL's `SFTTrainer` (the reference cell at the end) and compare.
- Discuss DoRA, rsLoRA and other `LoraConfig` options; read the LoRA and QLoRA papers' abstracts.
- Run notebook 04 with `Qwen/Qwen2.5-1.5B-Instruct` and compare memory and quality with the 0.5B model.

**Slower groups**
- Spend longer on the decision diagram and the chat format; skip notebook 02's code and show the chart.
- Use the analogies (sticky notes, recipe card, rounding prices) more than the maths; do one parameter count together.
- Run notebook 03 with fewer test questions to save time, or show the saved outputs.
- Treat notebook 04 as a guided read-through.
