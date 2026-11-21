"""
merge_export.py - Step 3: merge the LoRA adapter into the base model and prepare it for Ollama.

**Merging** - adding the small LoRA matrices into the original weights, so you
get one normal model again (no `peft` needed to run it). Like gluing the sticky
notes into the textbook.

**GGUF** - the single-file model format used by llama.cpp and Ollama. It can
store **quantised** weights (numbers with fewer bits, e.g. 4-bit instead of
32-bit) so the model is smaller and faster on a CPU, with a small quality loss.

This script does the merge (works on CPU) and writes an Ollama `Modelfile`.
The GGUF conversion itself uses llama.cpp's converter - the commands are printed
at the end and explained in the README. They were NOT run in the build
environment (llama.cpp and Ollama are not installed there).

Run:  python -m src.merge_export                 (merges outputs/dpo-lora-adapter, else the SFT adapter)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .common import OUT, load_base

MODELFILE = '''# Ollama Modelfile for the fine-tuned ticket extractor
FROM ./ticket-extractor-q8_0.gguf
PARAMETER temperature 0
PARAMETER num_predict 64
SYSTEM """Extract the support ticket as JSON with keys order_id, product, intent, urgency. Use null when a value is missing. Reply with JSON only."""
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", type=Path, default=None)
    args = ap.parse_args()
    from peft import PeftModel
    adapter = args.adapter or next((p for p in [OUT / "dpo-lora-adapter", OUT / "sft-lora-adapter"] if p.exists()), None)
    if adapter is None:
        raise SystemExit("No adapter found. Run `python -m src.sft_lora_cpu` first.")
    tok, base = load_base()
    model = PeftModel.from_pretrained(base, str(adapter))
    merged = model.merge_and_unload()                     # fold LoRA into the base weights
    target = OUT / "merged-model"
    merged.save_pretrained(target, safe_serialization=True)
    tok.save_pretrained(target)
    (OUT / "Modelfile").write_text(MODELFILE, encoding="utf-8")
    size = sum(f.stat().st_size for f in target.glob("*")) / 1e6
    print(f"merged {adapter.name} -> {target} ({size:.0f} MB); wrote outputs/Modelfile")
    print("\nNext steps (on a machine with git, cmake/pip and Ollama):\n"
          "  git clone https://github.com/ggml-org/llama.cpp\n"
          "  pip install -r llama.cpp/requirements.txt\n"
          f"  python llama.cpp/convert_hf_to_gguf.py {target} --outfile outputs/ticket-extractor-q8_0.gguf --outtype q8_0\n"
          "  cd outputs && ollama create ticket-extractor -f Modelfile\n"
          "  ollama run ticket-extractor \"Hi, my FitBand Pro (ORD-12345) arrived broken.\"")


if __name__ == "__main__":
    main()
