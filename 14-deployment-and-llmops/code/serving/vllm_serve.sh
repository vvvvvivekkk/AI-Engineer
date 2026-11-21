#!/usr/bin/env bash
# vllm_serve.sh - start an OpenAI-compatible model server with vLLM.
# NEEDS: a Linux machine with an NVIDIA GPU (e.g. a cloud GPU or Colab T4 for small models).
# It is NOT installed in this course's shared environment - read and run it on a GPU box.
#
#   pip install vllm                # large install; do it in its own virtual environment
#   bash vllm_serve.sh
#
# What the flags mean:
#   Qwen/Qwen2.5-0.5B-Instruct  -> any Hugging Face model id vLLM supports (small one = fits a small GPU)
#   --port 8001                 -> where the server listens (8000 is taken by our FastAPI app)
#   --max-model-len 4096        -> longest prompt+answer in tokens; smaller = less GPU memory
#   --gpu-memory-utilization    -> fraction of GPU memory vLLM may reserve (0.0 - 1.0)
#   --api-key                   -> clients must send this key; read from an env var, never hard-coded
set -euo pipefail                       # stop on the first error
MODEL="${VLLM_MODEL:-Qwen/Qwen2.5-0.5B-Instruct}"
vllm serve "$MODEL" \
  --port 8001 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.85 \
  --api-key "${VLLM_API_KEY:?set VLLM_API_KEY first}"

# Alternative with Docker (official image), GPU passed through:
# docker run --gpus all -p 8001:8000 -e HF_TOKEN=$HF_TOKEN vllm/vllm-openai:latest --model "$MODEL"
