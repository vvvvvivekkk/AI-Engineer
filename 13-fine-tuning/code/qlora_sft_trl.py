"""
qlora_sft_trl.py - QLoRA fine-tuning with transformers + peft + trl + bitsandbytes.

NEEDS AN NVIDIA GPU (e.g. a free Colab T4). Same steps as notebooks/04-qlora-colab-only.ipynb.
Checked against transformers 5.23.0, peft 0.22.0, trl 1.18.2 (late 2026).

Install:  pip install "transformers==5.23.0" "peft==0.22.0" "trl==1.18.2" bitsandbytes accelerate datasets
Run:      python code/qlora_sft_trl.py        (from the 13-fine-tuning folder)
"""
import pathlib                                     # file paths
import torch                                       # GPU tensors
from datasets import load_dataset                  # reads our JSONL files
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"            # a small instruct model; 1.5B also fits a T4


def main():
    if not torch.cuda.is_available():              # bitsandbytes 4-bit layers need CUDA
        raise SystemExit("This script needs an NVIDIA GPU. Use notebooks/03 for CPU training.")

    # 1. Data: convert chat examples into prompt/completion form so loss is computed on the answer only.
    ds = load_dataset("json", data_files={"train": str(DATA / "chai_corner_train.jsonl"),
                                          "test": str(DATA / "chai_corner_test.jsonl")})
    ds = ds.map(lambda ex: {"prompt": ex["messages"][:-1], "completion": ex["messages"][-1:]},
                remove_columns=["messages"])

    # 2. Load the base model in 4-bit NF4 with double quantisation; compute in float16 (T4-friendly).
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token               # make sure padding works
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, quantization_config=bnb,
                                                 device_map="auto", dtype=torch.float16)
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

    # 3. LoRA adapters on every linear layer.
    peft_config = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
                             target_modules="all-linear", task_type="CAUSAL_LM")

    # 4. Training settings.
    args = SFTConfig(output_dir="outputs/qlora-chai", num_train_epochs=3,
                     per_device_train_batch_size=4, gradient_accumulation_steps=2,
                     learning_rate=2e-4, lr_scheduler_type="cosine", warmup_steps=2,
                     logging_steps=2, max_length=256, fp16=True, bf16=False,
                     optim="paged_adamw_8bit", gradient_checkpointing=True,
                     eval_strategy="epoch", save_strategy="no", report_to="none")

    # 5. Train. Passing peft_config makes the trainer add the LoRA adapters.
    trainer = SFTTrainer(model=model, args=args, train_dataset=ds["train"], eval_dataset=ds["test"],
                         processing_class=tok, peft_config=peft_config)
    trainer.model.print_trainable_parameters()
    trainer.train()
    print("final eval:", trainer.evaluate())

    # 6. Save only the adapter (small) plus the tokenizer.
    trainer.model.save_pretrained("outputs/qlora-chai-adapter")
    tok.save_pretrained("outputs/qlora-chai-adapter")
    print("adapter saved to outputs/qlora-chai-adapter")


if __name__ == "__main__":
    main()
