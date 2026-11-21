"""
llm_clients.py - one small helper per provider (OpenAI, Anthropic, Gemini) plus an offline fallback.

Every function takes the same inputs:
    system   - the system prompt (instructions for the assistant)
    messages - a list like [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "..."}]
and returns a dict: {"text": ..., "input_tokens": ..., "output_tokens": ..., "source": ...}

If the provider's API key is not set, the function does NOT call the internet. It answers with a tiny
local model (SmolLM2-135M-Instruct via Hugging Face transformers) and labels the answer "offline-fallback".

Use:
    from llm_clients import ask
    print(ask("anthropic", "Be brief.", [{"role": "user", "content": "What is a token?"}]))
"""
import os                                   # read environment variables (API keys, model names)

try:                                        # python-dotenv is optional: it loads a .env file if present
    from dotenv import load_dotenv
    load_dotenv()                           # copies KEY=value lines from .env into os.environ
except ImportError:
    pass

# Example model names (as of late 2026). They change often: override them in .env.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
LOCAL_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"

_local = {}                                 # cache so the local model is loaded only once


def local_chat(system, messages, max_new_tokens=120):
    """Offline stand-in: answer with SmolLM2-135M-Instruct on the CPU (no key, no internet after download)."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    if not _local:                                              # first call: download/load the model
        _local["tok"] = AutoTokenizer.from_pretrained(LOCAL_MODEL)
        _local["model"] = AutoModelForCausalLM.from_pretrained(LOCAL_MODEL, dtype=torch.float32)  # fast on CPU
    tok, model = _local["tok"], _local["model"]
    chat = [{"role": "system", "content": system}] + list(messages)        # system goes first for this model
    inputs = tok.apply_chat_template(chat, add_generation_prompt=True,
                                     return_tensors="pt", return_dict=True)  # add the model's chat markers
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    n_in = inputs["input_ids"].shape[1]                         # how many tokens we sent
    text = tok.decode(out[0][n_in:], skip_special_tokens=True)  # keep only the newly generated tokens
    return {"text": text.strip(), "input_tokens": n_in, "output_tokens": out.shape[1] - n_in,
            "source": f"offline-fallback ({LOCAL_MODEL})"}


def ask_openai(system, messages, max_tokens=300):
    """OpenAI Responses API. Falls back to the local model when OPENAI_API_KEY is missing."""
    if not os.getenv("OPENAI_API_KEY"):
        return local_chat(system, messages)
    from openai import OpenAI
    client = OpenAI()                                           # reads OPENAI_API_KEY from the environment
    resp = client.responses.create(
        model=OPENAI_MODEL,
        instructions=system,                                    # the system prompt
        input=messages,                                         # user/assistant history
        max_output_tokens=max_tokens,                           # cap on the answer length
    )
    return {"text": resp.output_text, "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens, "source": f"openai:{OPENAI_MODEL}"}


def ask_anthropic(system, messages, max_tokens=300):
    """Anthropic Messages API. Falls back to the local model when ANTHROPIC_API_KEY is missing."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return local_chat(system, messages)
    from anthropic import Anthropic
    client = Anthropic()                                        # reads ANTHROPIC_API_KEY
    msg = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,                                  # required by Anthropic
        system=system,                                          # system prompt is its own parameter
        messages=messages,
    )
    text = "".join(block.text for block in msg.content if block.type == "text")   # join all text blocks
    return {"text": text, "input_tokens": msg.usage.input_tokens,
            "output_tokens": msg.usage.output_tokens, "source": f"anthropic:{ANTHROPIC_MODEL}"}


def ask_gemini(system, messages, max_tokens=300):
    """Google Gemini via google-genai. Falls back when neither GEMINI_API_KEY nor GOOGLE_API_KEY is set."""
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        return local_chat(system, messages)
    from google import genai
    from google.genai import types
    client = genai.Client()                                     # reads GEMINI_API_KEY / GOOGLE_API_KEY
    # Gemini calls the assistant role "model" and wraps text in "parts"
    contents = [types.Content(role="model" if m["role"] == "assistant" else "user",
                              parts=[types.Part(text=m["content"])]) for m in messages]
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=max_tokens),
    )
    u = resp.usage_metadata
    return {"text": resp.text, "input_tokens": u.prompt_token_count,
            "output_tokens": u.candidates_token_count, "source": f"gemini:{GEMINI_MODEL}"}


def ask(provider, system, messages, max_tokens=300):
    """Pick a provider by name: 'openai', 'anthropic', 'gemini' or 'local'."""
    funcs = {"openai": ask_openai, "anthropic": ask_anthropic, "gemini": ask_gemini}
    if provider == "local":
        return local_chat(system, messages)
    return funcs[provider](system, messages, max_tokens)


if __name__ == "__main__":
    question = [{"role": "user", "content": "Explain what an API key is in one sentence."}]
    for p in ["openai", "anthropic", "gemini"]:
        r = ask(p, "You are a concise tutor.", question)
        print(f"[{p}] via {r['source']}  (in={r['input_tokens']}, out={r['output_tokens']})\n  {r['text']}\n")
