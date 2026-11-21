<!-- nav:start -->
> [🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 12 Data Annotation & RLHF](../12-data-annotation-and-rlhf/README.md) · [14 Deployment & LLMOps ➡️](../14-deployment-and-llmops/README.md)  
> **🎛️ Module 13 · Fine-tuning (LoRA / QLoRA)**  
> [📖 Lesson](concepts.md) · [📄 PDF handout](pdf/13-fine-tuning-handout.pdf) · [🎞️ Slides](slides/13-fine-tuning.pptx) · [📓 Notebooks](notebooks/) · [✍️ Exercises](exercises.md) · [✅ Solutions](solutions/) · [🧑‍🏫 Trainer notes](trainer-notes.md) · [🔗 Resources](resources.md)
<!-- nav:end -->

# Module 13 - Fine-tuning LLMs: SFT, LoRA and QLoRA (week 21)

This module teaches you to change how a language model behaves by training it a little more on your own examples. You will learn when fine-tuning is the right tool (and when prompting or RAG is better), how to prepare chat-format training data, how **LoRA** (Low-Rank Adaptation - training small add-on matrices instead of the whole model) works down to the matrix maths, how **quantisation** (storing weights in fewer bits) makes **QLoRA** possible, and how to evaluate, merge and share what you trained.

## Learning goals

By the end you can:
1. Decide between prompt engineering, RAG and fine-tuning for a given problem.
2. Write SFT data in chat-format JSONL and explain chat templates and loss masking.
3. Explain full fine-tuning vs parameter-efficient fine-tuning (PEFT) and estimate GPU memory.
4. Explain LoRA with the formula h = Wx + (alpha/r)·BAx and implement it from scratch.
5. Explain 4-bit quantisation, NF4 and QLoRA.
6. LoRA-fine-tune a real chat model with `peft` on a CPU, and QLoRA a bigger one on a Colab GPU with `trl`.
7. Evaluate before vs after, save and reload adapters, merge them, and push to the Hugging Face Hub safely.

## Prerequisites

- Module 05 (PyTorch: tensors, loss, `backward()`, optimizers).
- Module 06/07 (tokenizers, transformers, what an LLM is).
- Module 09 (RAG), for the "fine-tune vs RAG" decision.
- Module 12 (SFT is stage 1 of RLHF; evals).

## Time estimate

- Reading `concepts.md`: 75 minutes.
- Notebooks 01-02: 45 minutes. Notebook 03: 30 minutes (including a few minutes of CPU training). Notebook 04 on Colab: 30 minutes.
- Exercises: 3-4 hours.
- Classroom session: 2 hours (see `trainer-notes.md`).

## Which tool to use, and why

| Notebook | Where | Why |
|---|---|---|
| 01-lora-from-scratch | Colab or local Jupyter (CPU) | Small tensors; no downloads |
| 02-quantisation-explained | Colab or local Jupyter (CPU) | Pure maths on a CPU; shows what `bitsandbytes` does |
| 03-lora-finetune-cpu | Local Jupyter or Colab (CPU is fine) | Real 135M-parameter model, ~270 MB download, a few minutes of training |
| 04-qlora-colab-only | **Colab with a T4 GPU only** | 4-bit layers (`bitsandbytes`) need an NVIDIA GPU. Runtime → Change runtime type → T4 GPU |

Use **VS Code** for the scripts in `code/`.

## Library versions

Checked in late 2026 with transformers 5.23, peft 0.22, trl 1.18 (and torch 2.15 on CPU). These libraries rename arguments between versions - if something errors, compare your versions with these and check the official docs. Notebook 04 pins its versions.

## API keys and tokens

No key is needed. Pushing to the Hugging Face Hub is optional and needs an `HF_TOKEN` environment variable (or a Colab secret). Copy `.env.example` to `.env` for local use; never commit `.env`.

## File map

| Path | What it is |
|---|---|
| `concepts.md` | The main lesson - read this first |
| `images/` | Diagrams (PNG) and their Mermaid sources (`.mmd`) |
| `notebooks/01-lora-from-scratch.ipynb` | Low rank, a hand-written LoRA layer, training, merging, and `peft` comparison |
| `notebooks/02-quantisation-explained.ipynb` | Absmax, block-wise and NF4-style 4-bit quantisation; GPU memory estimator |
| `notebooks/03-lora-finetune-cpu.ipynb` | LoRA fine-tune of SmolLM2-135M-Instruct on CPU: before/after, save, reload, merge, guarded push |
| `notebooks/04-qlora-colab-only.ipynb` | QLoRA of Qwen2.5-0.5B-Instruct on a T4 with transformers + peft + trl + bitsandbytes |
| `code/make_sft_dataset.py` | Builds the Chai Corner dataset in `data/` |
| `code/lora_layer.py` | LoRA linear layer from scratch with a self-test |
| `code/lora_finetune_cpu.py` | Notebook 03 as one script |
| `code/qlora_sft_trl.py` | Notebook 04 as one script (GPU only) |
| `code/merge_and_push.py` | Load an adapter, merge it, and optionally push to the Hub |
| `data/chai_corner_train.jsonl`, `data/chai_corner_test.jsonl` | 48 / 12 chat-format examples |
| `slides/13-fine-tuning.pptx` | Teaching deck with speaker notes |
| `pdf/13-fine-tuning-handout.pdf` | Printable version of `concepts.md` |
| `excel/gpu-memory-estimator.xlsx` | Memory estimates per model size and method (live formulas) |
| `excel/finetune-experiment-tracker.xlsx` | Log every run: settings, losses, metrics, notes |
| `exercises.md` / `solutions/` | 12 exercises (easy → hard) and worked solutions |
| `trainer-notes.md` | How to teach this module |
| `resources.md` | Curated further reading |
| `build.py` | Regenerates images, notebooks, slides, PDF and Excel |

Rebuild everything: `python 13-fine-tuning/build.py` (from the repo root). Notebook outputs (adapters, merged models) are written to `notebooks/outputs/`, which you can delete at any time.

<!-- nav:start -->
---
[🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 12 Data Annotation & RLHF](../12-data-annotation-and-rlhf/README.md) · [14 Deployment & LLMOps ➡️](../14-deployment-and-llmops/README.md)
<!-- nav:end -->
