# Module 13 - Resources

Curated from the course source-notes for this module. Each link has one line on why it is useful. Fine-tuning libraries change quickly - always check the version you have installed against the official docs (as of late 2026).

## Official libraries and docs
- [PEFT](https://github.com/huggingface/peft) - the standard LoRA/QLoRA library used in notebooks 01, 03 and 04; its README links to the full docs.
- [TRL](https://github.com/huggingface/trl) - `SFTTrainer`, `DPOTrainer`, GRPO and more behind one API; used in notebook 04.
- [Fine-tuning a pretrained model (Hugging Face docs)](https://huggingface.co/docs/transformers/training) - the canonical minimal `Trainer` recipe; works with tiny models on CPU.
- [Hugging Face Learn](https://huggingface.co/learn) - free course chapters on fine-tuning, datasets and evaluation.

## Courses and guides
- [LLM Course (mlabonne)](https://github.com/mlabonne/llm-course) - notebooks on SFT, DPO, quantisation and merging with clear explanations; the best next step after this module.
- [Mastering LLMs (Parlance Labs)](https://parlance-labs.com/education/) - practitioner talks on when fine-tuning is (and is not) worth it, plus evals.
- [RLHF in Notebooks](https://github.com/ash80/RLHF_in_notebooks) - hands-on reward model and PPO on GPT-2; connects this module to module 12.

## Faster or easier fine-tuning tools
- [Unsloth](https://github.com/unslothai/unsloth) - faster, lower-memory LoRA/QLoRA that fits small models on a free Colab or Kaggle GPU.
- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) - fine-tune many open models from a config file or web UI with little code.
- [Axolotl](https://github.com/axolotl-ai-cloud/axolotl) - YAML-driven, reproducible fine-tuning runs popular with practitioners.
- [Ludwig](https://github.com/ludwig-ai/ludwig) - declarative low-code fine-tuning.

## Datasets worth studying
- [LIMA dataset](https://huggingface.co/datasets/GAIR/lima) - about 1,000 curated SFT examples; evidence that data quality beats quantity.
- [The Flan Collection](https://github.com/google-research/FLAN/tree/main/flan/v2) - how a large instruction-tuning mixture is assembled.

## Papers
- [Fine-Tuning Language Models from Human Preferences](https://arxiv.org/abs/1909.08593) - early preference fine-tuning on GPT-2; background for TRL.
- LoRA (Hu et al., 2021) and QLoRA (Dettmers et al., 2023) - search their titles on arXiv: "LoRA: Low-Rank Adaptation of Large Language Models" and "QLoRA: Efficient Finetuning of Quantized LLMs". Read the abstracts and the first figure.

## After fine-tuning: running your model
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - convert and quantise a merged model to GGUF to run it on a CPU.
- [Ollama](https://ollama.com) - serve your own GGUF model behind a local API.
- [OpenAI platform docs](https://platform.openai.com/docs) - the hosted fine-tuning path, to compare with self-hosted training.

## Scaling up (advanced)
- [DeepSpeed](https://github.com/microsoft/DeepSpeed) - memory and parallelism optimisations for models that do not fit on one GPU.
- [OpenRLHF](https://github.com/OpenRLHF/OpenRLHF) - distributed RLHF framework (Ray + vLLM + DeepSpeed).
- [veRL](https://github.com/verl-project/verl) - production RL post-training for reasoning and tool-using models.
- [ART (Agent Reinforcement Trainer)](https://github.com/OpenPipe/ART) - adds GRPO training loops to an existing agent app.
- [minRLHF](https://github.com/thomfoster/minRLHF) - a minimal, readable PPO-for-language-models implementation.

## Book
- [LLM Engineer's Handbook](https://www.amazon.com/LLM-Engineers-Handbook-engineering-production/dp/1836200072) (paid) - end-to-end data pipelines, fine-tuning and deployment.
