"""
merge_and_push.py - load a LoRA adapter, merge it into its base model, save it, and optionally push.

Examples (from the 13-fine-tuning folder):
  python code/merge_and_push.py --adapter outputs/chai-lora-adapter
  python code/merge_and_push.py --adapter outputs/chai-lora-adapter --push your-username/chai-lora

Pushing needs the HF_TOKEN environment variable (or a .env file). Nothing is pushed without --push.
"""
import argparse                                    # read command-line options
import json                                        # read adapter_config.json
import os                                          # read environment variables
import pathlib                                     # file paths

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    from dotenv import load_dotenv                 # optional: load HF_TOKEN from a .env file
    load_dotenv()
except ImportError:
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True, help="folder written by model.save_pretrained()")
    ap.add_argument("--out", default="outputs/merged-model", help="where to save the merged model")
    ap.add_argument("--push", default=None, help="Hub repo id, e.g. your-username/my-adapter")
    a = ap.parse_args()

    adapter = pathlib.Path(a.adapter)
    cfg = json.loads((adapter / "adapter_config.json").read_text())   # remembers which base model was used
    base_id = cfg["base_model_name_or_path"]
    print("base model:", base_id)

    base = AutoModelForCausalLM.from_pretrained(base_id, dtype=torch.float32)   # 16/32-bit, never 4-bit, for merging
    model = PeftModel.from_pretrained(base, adapter)                            # attach the adapter
    tok = AutoTokenizer.from_pretrained(base_id)

    if a.push:                                        # push the small adapter, not the merged weights
        token = os.getenv("HF_TOKEN")
        if not token:
            raise SystemExit("Set HF_TOKEN in your environment or .env to push.")
        model.push_to_hub(a.push, token=token)
        tok.push_to_hub(a.push, token=token)
        print("pushed adapter to https://huggingface.co/" + a.push)

    merged = model.merge_and_unload()                 # W' = W + (alpha/r) B A
    merged.save_pretrained(a.out)
    tok.save_pretrained(a.out)
    print("merged model saved to", a.out)


if __name__ == "__main__":
    main()
