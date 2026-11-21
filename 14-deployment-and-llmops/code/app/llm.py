"""
llm.py - one small function that "talks to a model".

If ANTHROPIC_API_KEY is set, it calls the real Anthropic API.
If not, it uses an offline stand-in (a fake model) so the app still works
for teaching, testing and Docker demos with no key and no internet.
"""
import os            # read environment variables
import time          # measure how long a call takes

# Model name is read from an environment variable so you can change it without editing code.
# As of late 2026 check https://docs.anthropic.com/en/docs/about-claude/models for current names.
MODEL = os.getenv("LLM_MODEL", "claude-haiku-latest")

# Rough price per 1 million tokens, also from env vars (prices change - always check the provider page).
PRICE_IN_PER_M = float(os.getenv("PRICE_IN_PER_M", "1.0"))
PRICE_OUT_PER_M = float(os.getenv("PRICE_OUT_PER_M", "5.0"))


def has_real_key() -> bool:
    """True only if ANTHROPIC_API_KEY is set to something other than the .env.example placeholder."""
    key = os.getenv("ANTHROPIC_API_KEY", "")
    return bool(key) and key != "your-key-here"


def count_tokens(text: str) -> int:
    """Very rough token estimate: about 4 characters per token for English text."""
    return max(1, len(text) // 4)


def fake_generate(prompt: str) -> str:
    """Offline stand-in: a predictable reply so tests always get the same answer."""
    return f"(offline demo model) You said: {prompt[:200]}"


def generate(prompt: str, max_tokens: int = 256) -> dict:
    """Return a dict with the reply text, token counts, cost and latency."""
    start = time.perf_counter()                       # start the stopwatch
    if has_real_key():                                # real call only when a real key exists
        import anthropic                              # imported here so the package is optional
        client = anthropic.Anthropic()                # the client reads the key from the env var itself
        msg = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text
        tokens_in, tokens_out = msg.usage.input_tokens, msg.usage.output_tokens
        model_used = MODEL
    else:                                             # no key: use the fake model
        text = fake_generate(prompt)
        tokens_in, tokens_out = count_tokens(prompt), count_tokens(text)
        model_used = "offline-stand-in"
    latency_ms = (time.perf_counter() - start) * 1000  # stop the stopwatch, convert to milliseconds
    cost = tokens_in / 1e6 * PRICE_IN_PER_M + tokens_out / 1e6 * PRICE_OUT_PER_M
    return {"text": text, "model": model_used, "input_tokens": tokens_in,
            "output_tokens": tokens_out, "cost_usd": round(cost, 6), "latency_ms": round(latency_ms, 2)}
