"""
build.py - regenerate this project's diagrams (images/) and both notebooks.

Run from anywhere:  python 15-projects/p10-finetune-lora-dpo/build.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from build_kit import mermaid, notebook  # noqa: E402

PROJECT = HERE.name

ARCH = """
flowchart LR
  G[make_data.py<br/>1,500 email -> JSON pairs<br/>300 chosen/rejected pairs] --> SFT[Step 1: LoRA SFT<br/>sft_lora_cpu.py / TRL SFTTrainer]
  P6[P6 preference export] -. optional .-> DPO
  SFT --> DPO[Step 2: DPO<br/>dpo_cpu.py hand-written loss<br/>/ TRL DPOTrainer]
  DPO --> M[Step 3: merge adapter<br/>merge_export.py]
  M --> GG[llama.cpp<br/>convert to GGUF]
  GG --> OL[Ollama model<br/>served to P7 / P9]
  E[evaluate: JSON validity<br/>exact match, per field] --- SFT
  E --- DPO
"""

LORA = """
flowchart LR
  X[input] --> W[frozen weight W<br/>135M params, not trained]
  X --> A[LoRA A<br/>small] --> B[LoRA B<br/>small]
  W --> S((+))
  B --> S
  S --> Y[output]
"""

# Shared first cells: get the code (skip clone if we are already inside the repo) and install.
SETUP = [
    ("md", "## 1. Get the code\nIn Colab this clones the course repo. If you are already inside the project "
           "folder (running locally), the clone is skipped."),
    ("code", f"""import os, pathlib, subprocess, sys
PROJECT = "{PROJECT}"
if pathlib.Path("src").is_dir() and pathlib.Path("README.md").exists():
    print("Project folder found - using the local copy, no clone needed.")
else:
    if not pathlib.Path("AI-Engineer").exists():
        subprocess.run(["git", "clone", "--depth", "1", "https://github.com/vvvvvivekkk/AI-Engineer.git"], check=True)
    os.chdir(f"AI-Engineer/15-projects/{{PROJECT}}")
print("working in", os.getcwd())"""),
    ("md", "## 2. Install the pinned packages (Colab only)\nColab already has PyTorch with GPU support, so we skip "
           "the `torch` line to avoid replacing it. Locally you install with `pip install -r requirements.txt` in a venv."),
    ("code", """IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    reqs = [l for l in open("requirements.txt") if l.strip() and not l.startswith(("torch==", "#"))]
    open("/tmp/req.txt", "w").writelines(reqs)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "/tmp/req.txt"], check=True)
print("ready")"""),
]




def build():
    mermaid(ARCH, HERE / "images" / "architecture.png")
    mermaid(LORA, HERE / "images" / "lora.png")
    quick = [
        ("md", "# P10 - Fine-tune a small model (LoRA SFT, then DPO): CPU quick start\nTeaches SmolLM2-135M to turn "
               "support emails into strict JSON. This notebook runs a *quick mode* that finishes on a CPU in a few "
               "minutes; the full GPU recipe with TRL is in `colab_gpu_trl-colab-only.ipynb`."),
        *SETUP,
        ("md", "## 3. Build the datasets\n1,500 email -> JSON pairs and 300 chosen/rejected pairs."),
        ("code", "!python -m src.make_data"),
        ("md", "## 4. Step 1 - LoRA SFT (quick mode)\nFirst measures the base model with plain prompting and with one "
               "example in the prompt, then trains LoRA adapters and measures again."),
        ("code", "!python -m src.sft_lora_cpu --steps 15 --eval-n 5 --results results_sft_quick.json"),
        ("md", "## 5. Step 2 - DPO with a hand-written loss (quick mode)"),
        ("code", "!python -m src.dpo_cpu --steps 6 --train-n 12 --eval-n 4 --results results_dpo_quick.json"),
        ("md", "## 6. Step 3 - merge the adapter\nCreates `outputs/merged-model` and an Ollama `Modelfile`, and prints "
               "the GGUF conversion commands."),
        ("code", "!python -m src.merge_export"),
        ("md", "## 7. Run the tests"),
        ("code", "!python -m pytest -q tests"),
    ]
    notebook(quick, HERE / "colab_quickstart.ipynb")

    gpu = [
        ("md", "# P10 - LoRA SFT + DPO with TRL on a free T4 GPU (colab-only)\n**Runtime -> Change runtime type -> "
               "T4 GPU** before running. This uses Hugging Face TRL's `SFTTrainer` and `DPOTrainer` on "
               "SmolLM2-360M-Instruct (change `MODEL` to try e.g. `Qwen/Qwen2.5-0.5B-Instruct`). "
               "Expect roughly 10-20 minutes in total."),
        ("md", "## 1. Check the GPU"),
        ("code", "!nvidia-smi --query-gpu=name,memory.total --format=csv"),
        ("md", "## 2. Get the code and install the pinned packages\nWe keep Colab's own CUDA build of PyTorch."),
        ("code", f"""import os, pathlib, subprocess, sys
PROJECT = "{PROJECT}"
if not pathlib.Path("src").is_dir():
    if not pathlib.Path("AI-Engineer").exists():
        subprocess.run(["git", "clone", "--depth", "1", "https://github.com/vvvvvivekkk/AI-Engineer.git"], check=True)
    os.chdir(f"AI-Engineer/15-projects/{{PROJECT}}")
reqs = [l for l in open("requirements.txt") if l.strip() and not l.startswith(("torch==", "#"))]
open("/tmp/req.txt", "w").writelines(reqs)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "/tmp/req.txt"], check=True)
print(os.getcwd())"""),
        ("md", "## 3. Build the datasets"),
        ("code", "!python -m src.make_data"),
        ("md", "## 4. Baseline: prompting the base model\nHow often does the untuned model return valid, exactly "
               "correct JSON - with and without one example in the prompt?"),
        ("code", """import torch
from src.common import evaluate, load_base, load_jsonl, DATA
MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
test = load_jsonl(DATA / "sft_test.jsonl")[:100]
tok, base = load_base(MODEL)
base = base.to("cuda")
print("zero-shot:", evaluate(base, tok, test)[0])
print("few-shot: ", evaluate(base, tok, test, few_shot=True)[0])
del base; torch.cuda.empty_cache()"""),
        ("md", "## 5. SFT + DPO with TRL\n`src/trl_train.py`: SFT with LoRA on all linear layers and loss only on the "
               "answer (`completion_only_loss=True`), merge, then DPO with a new LoRA adapter (`peft_config`), so the "
               "frozen reference is the SFT model. `fp16=True` because the T4 has no bfloat16."),
        ("code", "!python -m src.trl_train --model HuggingFaceTB/SmolLM2-360M-Instruct --gpu --sft-steps 300 --dpo-steps 100 --batch 8 --eval-n 100"),
        ("md", "## 6. Results"),
        ("code", "print(open('outputs/trl_results.json').read())"),
        ("md", "## 7. Merge the DPO adapter and export\nMerge on top of the SFT-merged model, save, and convert to GGUF "
               "with llama.cpp so Ollama can serve it."),
        ("code", """from peft import PeftModel
from src.trl_train import merged_sft_model
tok, sft = merged_sft_model(MODEL, "outputs/trl-sft-adapter", gpu=False)
final = PeftModel.from_pretrained(sft, "outputs/trl-dpo-adapter").merge_and_unload()
final.save_pretrained("outputs/final-merged"); tok.save_pretrained("outputs/final-merged")
!git clone --depth 1 https://github.com/ggml-org/llama.cpp /content/llama.cpp
!pip install -q -r /content/llama.cpp/requirements.txt
!python /content/llama.cpp/convert_hf_to_gguf.py outputs/final-merged --outfile outputs/ticket-extractor-q8_0.gguf --outtype q8_0
!ls -lh outputs/*.gguf"""),
        ("md", "## 8. Download\nDownload `outputs/ticket-extractor-q8_0.gguf`, put it next to the `Modelfile` that "
               "`python -m src.merge_export` writes, and run `ollama create ticket-extractor -f Modelfile`."),
        ("code", """from google.colab import files
files.download("outputs/ticket-extractor-q8_0.gguf")"""),
    ]
    notebook(gpu, HERE / "colab_gpu_trl-colab-only.ipynb")


if __name__ == "__main__":
    build()
