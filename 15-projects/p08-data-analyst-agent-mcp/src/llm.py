"""
llm.py - one small, swappable way to "ask a language model something".

An **LLM provider** is the place the model runs. This file supports four:

  local      a small Hugging Face model running on your own CPU (default, no key needed)
  ollama     a model served by Ollama on your machine (http://localhost:11434)
  anthropic  Claude through the Anthropic API (needs ANTHROPIC_API_KEY)
  openai     GPT models through the OpenAI API (needs OPENAI_API_KEY)

You pick one in the `.env` file with LLM_PROVIDER=... . Every other file in the
project only calls `generate(...)`, so switching provider never changes their code.
Think of it like a universal travel plug: the laptop (our code) stays the same,
only the adapter (provider) changes.
"""
from __future__ import annotations

import os                       # read settings from environment variables
from functools import lru_cache  # remember the loaded local model so we load it once

try:                            # python-dotenv copies values from .env into os.environ
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:             # if it is not installed we simply rely on real env vars
    pass


class LLMError(RuntimeError):
    """Raised with a clear, human-readable message when a provider cannot be used."""


def provider() -> str:
    """Which provider is selected (lower-case). Defaults to 'local'."""
    return os.getenv("LLM_PROVIDER", "local").strip().lower()


def _real_key(name: str) -> str:
    """Return an API key from the environment, or raise if it is missing / a placeholder."""
    key = os.getenv(name, "").strip()
    if not key or key.startswith("your-"):
        raise LLMError(f"{name} is not set. Put your real key in .env (see .env.example), "
                       f"or set LLM_PROVIDER=local to use the free offline model.")
    return key


@lru_cache(maxsize=2)
def _local_model(model_id: str):
    """Download (first time only) and load a small chat model + its tokenizer."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
    model.eval()                # "inference mode": no training behaviour such as dropout
    return tok, model


def _generate_local(prompt: str, system: str | None, max_new_tokens: int, temperature: float) -> str:
    import torch
    model_id = os.getenv("LOCAL_MODEL", "HuggingFaceTB/SmolLM2-135M-Instruct")
    tok, model = _local_model(model_id)
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    sample = temperature > 0    # temperature 0 = always pick the most likely next word (repeatable)
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=sample,
                             temperature=temperature if sample else None, top_p=0.95 if sample else None,
                             pad_token_id=tok.pad_token_id or tok.eos_token_id)
    return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def _generate_ollama(prompt: str, system: str | None, max_new_tokens: int, temperature: float) -> str:
    import httpx
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    try:
        r = httpx.post(f"{host}/api/chat", timeout=120, json={
            "model": model, "messages": msgs, "stream": False,
            "options": {"temperature": temperature, "num_predict": max_new_tokens}})
        r.raise_for_status()
    except httpx.HTTPError as e:
        raise LLMError(f"Could not reach Ollama at {host} ({e}). Is `ollama serve` running and "
                       f"did you `ollama pull {model}`?") from e
    return r.json()["message"]["content"].strip()


def _generate_anthropic(prompt: str, system: str | None, max_new_tokens: int, temperature: float) -> str:
    key = _real_key("ANTHROPIC_API_KEY")
    import anthropic
    client = anthropic.Anthropic(api_key=key)
    kwargs = {"system": system} if system else {}
    msg = client.messages.create(model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5"),
                                 max_tokens=max_new_tokens, temperature=temperature,
                                 messages=[{"role": "user", "content": prompt}], **kwargs)
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()


def _generate_openai(prompt: str, system: str | None, max_new_tokens: int, temperature: float) -> str:
    key = _real_key("OPENAI_API_KEY")
    from openai import OpenAI
    client = OpenAI(api_key=key)
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    resp = client.chat.completions.create(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), messages=msgs,
                                          max_tokens=max_new_tokens, temperature=temperature)
    return (resp.choices[0].message.content or "").strip()


_BACKENDS = {"local": _generate_local, "ollama": _generate_ollama,
             "anthropic": _generate_anthropic, "openai": _generate_openai}


def generate(prompt: str, system: str | None = None, max_new_tokens: int = 200,
             temperature: float = 0.0) -> str:
    """Send one prompt to the selected provider and return the reply text."""
    name = provider()
    if name not in _BACKENDS:
        raise LLMError(f"Unknown LLM_PROVIDER={name!r}. Use one of: {', '.join(_BACKENDS)}")
    return _BACKENDS[name](prompt, system, max_new_tokens, temperature)
