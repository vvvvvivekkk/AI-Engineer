"""
llm_client.py - one small function, call_llm(), that talks to a language model.

Why this file exists:
  Every prompt experiment in this module needs "send a system prompt + a user
  message, get text back". Real providers (Anthropic, OpenAI) need an API key.
  This classroom machine has no key, so the function falls back to a tiny
  local model that runs on a CPU. Your code calls call_llm() the same way in
  both cases, so you can swap the "engine" without touching anything else.

Order of preference:
  1. ANTHROPIC_API_KEY is set  -> real Claude call
  2. OPENAI_API_KEY is set     -> real OpenAI call
  3. neither                   -> local HuggingFaceTB/SmolLM2-135M-Instruct (offline, free, weak)

Run it:  python code/llm_client.py
"""
import os                     # os lets us read environment variables (where API keys live)
from functools import lru_cache  # lru_cache remembers a function's result so we load the model only once

# Model names change often. They are read from environment variables so you can
# update them without editing code. Check the provider's models page for current names.
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")   # see https://docs.anthropic.com/en/docs/about-claude/models
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")              # see https://platform.openai.com/docs/models
LOCAL_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"                  # a 135-million-parameter model: tiny, fast, not very clever


@lru_cache(maxsize=1)                       # load the local model the first time only, then reuse it
def _load_local():
    """Download (first time) and load the tiny local chat model."""
    from transformers import AutoModelForCausalLM, AutoTokenizer  # imported here so API users never pay the import cost
    tok = AutoTokenizer.from_pretrained(LOCAL_MODEL)              # the tokenizer turns text into token ids and back
    model = AutoModelForCausalLM.from_pretrained(LOCAL_MODEL)     # the model predicts the next token
    model.eval()                                                  # "evaluation mode": no training behaviour
    return tok, model


def _messages(user: str, examples) -> list[dict]:
    """Turn few-shot examples into fake earlier chat turns, then add the real user message.
    Example pairs (input, ideal_output) become user -> assistant -> user -> assistant ..."""
    msgs = []
    for example_in, example_out in (examples or []):
        msgs.append({"role": "user", "content": example_in})          # what a user might say
        msgs.append({"role": "assistant", "content": example_out})    # the perfect answer we want copied
    msgs.append({"role": "user", "content": user})                     # the real request comes last
    return msgs


def _call_local(system: str, user: str, max_tokens: int, temperature: float, examples=None) -> str:
    """Run the tiny local model with the same system/user structure as the APIs."""
    import torch                                                  # PyTorch runs the model's maths
    tok, model = _load_local()
    messages = [{"role": "system", "content": system}] + _messages(user, examples)  # rules first, then the chat
    inputs = tok.apply_chat_template(messages, add_generation_prompt=True,
                                     return_tensors="pt", return_dict=True)  # wraps the messages in the model's chat format
    with torch.no_grad():                                         # no gradients needed: we are not training
        out = model.generate(**inputs, max_new_tokens=max_tokens,
                             do_sample=temperature > 0,           # temperature 0 -> always pick the most likely token
                             temperature=temperature if temperature > 0 else None,
                             top_p=None, top_k=None,
                             pad_token_id=tok.eos_token_id)
    new_tokens = out[0][inputs["input_ids"].shape[1]:]            # keep only the tokens the model added
    return tok.decode(new_tokens, skip_special_tokens=True).strip()


def call_llm(system: str, user: str, max_tokens: int = 200, temperature: float = 0.0,
             examples: list[tuple[str, str]] | None = None) -> str:
    """Send a system prompt + (optional few-shot example turns) + one user message; return the reply text."""
    if os.getenv("ANTHROPIC_API_KEY"):                            # 1. real Claude call if a key exists
        import anthropic
        client = anthropic.Anthropic()                            # the SDK reads ANTHROPIC_API_KEY itself
        resp = client.messages.create(model=ANTHROPIC_MODEL, max_tokens=max_tokens,
                                      temperature=temperature, system=system,
                                      messages=_messages(user, examples))
        return resp.content[0].text                               # the reply is a list of content blocks; take the text
    if os.getenv("OPENAI_API_KEY"):                               # 2. real OpenAI call if that key exists
        from openai import OpenAI
        client = OpenAI()                                         # reads OPENAI_API_KEY itself
        resp = client.chat.completions.create(model=OPENAI_MODEL, max_tokens=max_tokens,
                                              temperature=temperature,
                                              messages=[{"role": "system", "content": system}]
                                                       + _messages(user, examples))
        return resp.choices[0].message.content
    return _call_local(system, user, max_tokens, temperature, examples)  # 3. offline fallback


def backend_name() -> str:
    """Say which engine call_llm() will use, so printouts are honest."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return f"Anthropic ({ANTHROPIC_MODEL})"
    if os.getenv("OPENAI_API_KEY"):
        return f"OpenAI ({OPENAI_MODEL})"
    return f"LOCAL offline stand-in ({LOCAL_MODEL}) - small and weak, results are illustrative"


if __name__ == "__main__":                                        # runs only when you execute this file directly
    print("Backend:", backend_name())
    print(call_llm("You are a helpful assistant. Answer in one short sentence.",
                   "What is a prompt?", max_tokens=40))
