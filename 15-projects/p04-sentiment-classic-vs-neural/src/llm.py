"""
llm.py - one tiny function, generate(prompt), that can talk to four kinds of language model.

Pick the provider in your .env file with LLM_PROVIDER=:
  * local     (default) - a small Hugging Face model on your own CPU; no key, first run downloads it
  * ollama              - a model served by Ollama on your machine (http://localhost:11434)
  * anthropic           - Claude via the Anthropic API (needs ANTHROPIC_API_KEY)
  * openai              - OpenAI API (needs OPENAI_API_KEY)
Hosted calls use plain HTTP (httpx) so no extra SDKs are required. If a key is missing you get a
clear error message instead of a confusing crash.
"""
from __future__ import annotations

import os
from functools import lru_cache

try:  # load settings from a .env file if python-dotenv is installed
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class LLMConfigError(RuntimeError):
    """Raised when the chosen provider is not configured (e.g. missing API key)."""


def provider() -> str:
    return os.getenv("LLM_PROVIDER", "local").strip().lower()


@lru_cache(maxsize=1)
def _local_pipe():
    """Load the local model once and reuse it (loading is the slow part)."""
    import torch
    from transformers import pipeline
    torch.set_num_threads(int(os.getenv("TORCH_THREADS", "2")))
    name = os.getenv("LOCAL_MODEL", "HuggingFaceTB/SmolLM2-360M-Instruct")
    return pipeline("text-generation", model=name)


def generate(prompt: str, system: str | None = None, max_new_tokens: int = 200) -> str:
    """Send one prompt, get the model's text reply back."""
    p = provider()
    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]

    if p == "local":
        out = _local_pipe()(messages, max_new_tokens=max_new_tokens, do_sample=False)
        return out[0]["generated_text"][-1]["content"].strip()

    import httpx
    if p == "ollama":
        url = os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/chat"
        body = {"model": os.getenv("OLLAMA_MODEL", "llama3.2:1b"), "messages": messages, "stream": False}
        try:
            r = httpx.post(url, json=body, timeout=120)
        except httpx.ConnectError as e:
            raise LLMConfigError("Could not reach Ollama. Start it with `ollama serve` "
                                 "and pull a model, e.g. `ollama pull llama3.2:1b`.") from e
        r.raise_for_status()
        return r.json()["message"]["content"].strip()

    if p == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if not key or key == "your-key-here":
            raise LLMConfigError("LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set in .env")
        body = {"model": os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5"), "max_tokens": max_new_tokens,
                "messages": [{"role": "user", "content": prompt}]}
        if system:
            body["system"] = system
        r = httpx.post("https://api.anthropic.com/v1/messages", json=body, timeout=120,
                       headers={"x-api-key": key, "anthropic-version": "2023-06-01"})
        r.raise_for_status()
        return "".join(b.get("text", "") for b in r.json()["content"]).strip()

    if p == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        if not key or key == "your-key-here":
            raise LLMConfigError("LLM_PROVIDER=openai but OPENAI_API_KEY is not set in .env")
        body = {"model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"), "messages": messages,
                "max_tokens": max_new_tokens}
        r = httpx.post("https://api.openai.com/v1/chat/completions", json=body, timeout=120,
                       headers={"Authorization": f"Bearer {key}"})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()

    raise LLMConfigError(f"Unknown LLM_PROVIDER={p!r}. Use local, ollama, anthropic or openai.")
