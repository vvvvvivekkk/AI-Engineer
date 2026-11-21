"""
anthropic_basics.py - the Anthropic (Claude) Python SDK: system prompt, multi-turn, streaming, JSON output, errors.

Run:  python anthropic_basics.py
Needs: pip install anthropic pydantic python-dotenv   and ANTHROPIC_API_KEY in your environment or .env
Without a key, real calls are skipped and the offline fallback answers. The error demo always runs safely.
"""
import os
from pydantic import BaseModel
import anthropic                                        # for the error classes
from anthropic import Anthropic
from llm_clients import local_chat, ANTHROPIC_MODEL

HAS_KEY = bool(os.getenv("ANTHROPIC_API_KEY"))
SYSTEM = "You are a concise tutor for beginner programmers."


def basic_and_system():
    """1. One question with a system prompt."""
    question = [{"role": "user", "content": "What is a token in one sentence?"}]
    if not HAS_KEY:
        print("[offline]", local_chat(SYSTEM, question)["text"])
        return
    client = Anthropic()                                # reads ANTHROPIC_API_KEY
    msg = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=150,                                 # required: maximum length of the answer
        system=SYSTEM,                                  # the system prompt is a separate parameter
        messages=question,
    )
    print(msg.content[0].text)                          # the reply is a list of content blocks
    print("tokens in/out:", msg.usage.input_tokens, msg.usage.output_tokens, "| stop:", msg.stop_reason)


def multi_turn():
    """2. Send the full history; roles must alternate user/assistant and end with user."""
    history = [
        {"role": "user", "content": "My name is Asha and I live in Hyderabad."},
        {"role": "assistant", "content": "Nice to meet you, Asha!"},
        {"role": "user", "content": "Which city do I live in?"},
    ]
    if not HAS_KEY:
        print("[offline]", local_chat(SYSTEM, history)["text"])
        return
    client = Anthropic()
    msg = client.messages.create(model=ANTHROPIC_MODEL, max_tokens=60, system=SYSTEM, messages=history)
    print(msg.content[0].text)


def streaming():
    """3. Stream text as it is generated with the messages.stream helper."""
    prompt = [{"role": "user", "content": "Write a two-line poem about Python."}]
    if not HAS_KEY:
        print("[offline] streaming needs a key; local fallback:")
        print(local_chat(SYSTEM, prompt)["text"])
        return
    client = Anthropic()
    with client.messages.stream(model=ANTHROPIC_MODEL, max_tokens=120, messages=prompt) as stream:
        for text in stream.text_stream:                 # yields each new piece of text
            print(text, end="", flush=True)
        final = stream.get_final_message()              # the complete message, including usage
    print("\noutput tokens:", final.usage.output_tokens)


class Ticket(BaseModel):
    category: str      # billing / delivery / technical / other
    urgency: int       # 1 (low) .. 5 (high)
    summary: str


def structured_output():
    """4. Structured output: messages.parse validates the reply against a Pydantic model."""
    text = "My order #4521 has not arrived after 10 days and nobody answers the phone!"
    if not HAS_KEY:
        print("[offline fake response]", Ticket(category="delivery", urgency=4,
                                                summary="Order #4521 late by 10 days; no phone answer."))
        return
    client = Anthropic()
    msg = client.messages.parse(
        model=ANTHROPIC_MODEL,
        max_tokens=300,
        system="Classify the customer message.",
        messages=[{"role": "user", "content": text}],
        output_format=Ticket,                           # the SDK sends the JSON schema and parses the result
    )
    print(msg.parsed_output)                            # a validated Ticket object


def count_tokens():
    """5. Ask the API how many input tokens a request will use (needs a key, costs nothing)."""
    if not HAS_KEY:
        print("[offline] count_tokens needs a key; use tiktoken for a rough estimate instead.")
        return
    client = Anthropic()
    r = client.messages.count_tokens(model=ANTHROPIC_MODEL, system=SYSTEM,
                                          messages=[{"role": "user", "content": "What is a token?"}])
    print("input tokens:", r.input_tokens)


def error_handling():
    """6. Catch errors by type (safe demo against a closed local port)."""
    client = Anthropic(api_key="not-a-real-key", base_url="http://127.0.0.1:9",
                       max_retries=1, timeout=5)
    try:
        client.messages.create(model=ANTHROPIC_MODEL, max_tokens=10,
                               messages=[{"role": "user", "content": "hello"}])
    except anthropic.RateLimitError:                    # 429
        print("Rate limited - wait and retry")
    except anthropic.APIStatusError as e:               # 400/401/403/404/500/529 ...
        print("HTTP error", e.status_code, e.message)
    except anthropic.APIConnectionError as e:           # network problem
        print("Connection problem (expected in this demo):", type(e).__name__)


if __name__ == "__main__":
    print("Key found:", HAS_KEY, "| model:", ANTHROPIC_MODEL)
    for step in [basic_and_system, multi_turn, streaming, structured_output, count_tokens, error_handling]:
        print(f"\n--- {step.__doc__.splitlines()[0]}")
        step()
