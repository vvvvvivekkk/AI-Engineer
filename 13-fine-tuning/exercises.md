# Module 13 - Exercises

Graded from easy (1) to hard (12). Worked solutions are in `solutions/solutions.md` and `solutions/solutions.py`.

## Easy

**1. Prompt, RAG or fine-tune?** For each case, choose the first approach you would try and give one reason.
a) A bank's chatbot must answer questions using this week's interest rates.
b) A model must always return valid JSON with the fields `name`, `date`, `amount` from invoices, and a well-written prompt already gets it right 99% of the time.
c) A company wants a 1B-parameter model to classify support tickets into its own 40 categories as cheaply as possible, and has 5,000 labelled tickets.
d) A writer wants a model to answer in the style of their own blog, and has 300 of their posts.

**2. LoRA parameter counting.** A layer has W of shape 2048 x 8192.
a) How many numbers are in W?
b) How many trainable numbers does LoRA add with r = 16?
c) What percentage of W is that?

**3. Memory arithmetic.** Using the rough rules from `concepts.md` section 6.3, estimate the GPU memory (ignoring activations) to: a) run a 3B model in 16-bit; b) fully fine-tune it; c) QLoRA it (assume 0.5% trainable parameters, 16 bytes per trainable parameter for the adapter).

**4. Spot the bug in the data.** Which of these JSONL lines will break or harm SFT, and why?
```
{"messages": [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Chai Corner here! Hello! Have a warm day!"}]}
{"messages": [{"role": "user", "content": "Hours?"}, {"role": "user", "content": "We open at 7 am."}]}
{"messages": [{"role": "system", "content": "You are Chai Corner's assistant."}, {"role": "user", "content": "Wi-Fi?"}]}
{'messages': [{'role': 'user', 'content': 'Parking?'}, {'role': 'assistant', 'content': 'Free street parking.'}]}
```

## Medium

**5. Chat templates.** Load the tokenizers of `HuggingFaceTB/SmolLM2-135M-Instruct` and `Qwen/Qwen2.5-0.5B-Instruct` (tokenizers download quickly) and print the chat template output for the same two-message conversation. List two differences. Why must you never train with one model's template and run with another's?

**6. Scaling factor.** In notebook 01, the LoRA output is multiplied by alpha / r. If you double r from 8 to 16 but keep alpha = 16, what happens to the scaling? Why do many people set alpha = 2r? Show numerically with the `LoRALinear` class that, at initialisation, the output does not depend on alpha at all.

**7. Quantisation error.** In notebook 02, change the block size to 16, 64, 256 and 4096 (whole tensor). Plot mean absolute error against block size. Also estimate the memory cost of the scales (one 32-bit float per block) in bits per weight. Which block size would you choose and why?

**8. Rank experiment.** In notebook 03, change `r` to 2, 8 and 32 (keep everything else the same). Record trainable parameters, final test loss and style score in `excel/finetune-experiment-tracker.xlsx`. What do you observe?

**9. Loss masking matters.** In notebook 03, train once *without* masking (set `labels = full_ids` for every token). Compare test loss on the answer tokens only and the style score. Explain the difference.

## Hard

**10. Your own dataset.** Build a 60-example chat-format dataset for a new persona of your choice (for example a polite railway helpdesk that always ends with a ticket reference format `REF-XXXX`). Split 48/12, fine-tune with notebook 03, and write a short report: before/after numbers, three good outputs, three bad outputs, and what you would change next.

**11. Merge correctness test.** Write a script that loads your saved adapter from notebook 03, generates answers for the 12 test questions with (a) the PeftModel and (b) the merged model, and asserts the outputs are identical. Also compare the logits of one forward pass with `torch.allclose`. Explain why tiny numerical differences can appear and what tolerance is reasonable.

**12. QLoRA capstone (Colab).** Run notebook 04 on a T4 with your dataset from exercise 10. Then change one setting at a time (r, learning rate, epochs) for three more runs, record everything in the tracker, and push the best adapter to the Hub (private repo) with a model card that states the base model, data, settings, evaluation results and limitations. Never put your token in the notebook.
