"""
openai_basics.py - the OpenAI Python SDK: system prompt, multi-turn chat, streaming, JSON output, errors.

Run:  python openai_basics.py
Needs: pip install openai pydantic python-dotenv   and OPENAI_API_KEY in your environment or .env
Without a key, every real call is skipped and the offline fallback (llm_clients.local_chat) answers instead.
The last demo (error handling) always runs: it points the client at a closed local port, so it fails safely.
"""
import os
from pydantic import BaseModel                     # describes the JSON shape we want back
import openai                                      # the official SDK (for error classes)
from openai import OpenAI
from llm_clients import local_chat, OPENAI_MODEL   # offline fallback + example model name

HAS_KEY = bool(os.getenv("OPENAI_API_KEY"))        # True only if a key is configured
SYSTEM = "You are a concise tutor for beginner programmers."


def basic_and_system():
    """1. One question with a system prompt."""
    question = [{"role": "user", "content": "What is a token in one sentence?"}]
    if not HAS_KEY:
        print("[offline]", local_chat(SYSTEM, question)["text"])
        return
    client = OpenAI()                              # reads OPENAI_API_KEY
    resp = client.responses.create(
        model=OPENAI_MODEL,
        instructions=SYSTEM,                       # system prompt
        input=question,
        max_output_tokens=150,
        temperature=0.2,                           # low = focused (not every model accepts this; check docs)
    )
    print(resp.output_text)
    print("tokens in/out:", resp.usage.input_tokens, resp.usage.output_tokens)


def multi_turn():
    """2. The API has no memory: send the whole history every time."""
    history = [
        {"role": "user", "content": "My name is Asha and I live in Hyderabad."},
        {"role": "assistant", "content": "Nice to meet you, Asha!"},
        {"role": "user", "content": "Which city do I live in?"},
    ]
    if not HAS_KEY:
        print("[offline]", local_chat(SYSTEM, history)["text"])
        return
    client = OpenAI()
    resp = client.responses.create(model=OPENAI_MODEL, instructions=SYSTEM, input=history, max_output_tokens=60)
    print(resp.output_text)


def streaming():
    """3. Print the answer piece by piece as it is generated."""
    if not HAS_KEY:
        print("[offline] streaming needs a key; the local fallback prints all at once:")
        print(local_chat(SYSTEM, [{"role": "user", "content": "Write a two-line poem about Python."}])["text"])
        return
    client = OpenAI()
    stream = client.responses.create(model=OPENAI_MODEL, input="Write a two-line poem about Python.",
                                       stream=True)          # stream=True returns events instead of one reply
    for event in stream:
        if event.type == "response.output_text.delta":       # a new piece of text arrived
            print(event.delta, end="", flush=True)
    print()


class Ticket(BaseModel):
    """The JSON shape we want: three fields with fixed types."""
    category: str      # billing / delivery / technical / other
    urgency: int       # 1 (low) .. 5 (high)
    summary: str


def structured_output():
    """4. Ask for JSON that matches the Ticket schema, parsed into a Python object."""
    text = "My order #4521 has not arrived after 10 days and nobody answers the phone!"
    if not HAS_KEY:
        fake = Ticket(category="delivery", urgency=4, summary="Order #4521 late by 10 days; no phone answer.")
        print("[offline fake response]", fake)
        return
    client = OpenAI()
    resp = client.responses.parse(
        model=OPENAI_MODEL,
        instructions="Classify the customer message.",
        input=text,
        text_format=Ticket,                        # the SDK turns the Pydantic class into a JSON schema
    )
    ticket = resp.output_parsed                    # already a validated Ticket object
    print(ticket, "| urgency + 1 =", ticket.urgency + 1)


def error_handling():
    """5. Catch errors by type. Uses a closed local port so it fails safely with no key and no internet."""
    client = OpenAI(api_key="not-a-real-key", base_url="http://127.0.0.1:9/v1",
                    max_retries=1, timeout=5)      # 1 automatic retry, 5-second timeout
    try:
        client.responses.create(model=OPENAI_MODEL, input="hello")
    except openai.RateLimitError:                  # 429: too many requests -> wait and retry later
        print("Rate limited")
    except openai.APIStatusError as e:             # any other HTTP error code (400, 401, 404, 500 ...)
        print("HTTP error", e.status_code, e.message)
    except openai.APIConnectionError as e:         # no response at all (network down, wrong address)
        print("Connection problem (expected in this demo):", type(e).__name__)


if __name__ == "__main__":
    print("Key found:", HAS_KEY, "| model:", OPENAI_MODEL)
    for step in [basic_and_system, multi_turn, streaming, structured_output, error_handling]:
        print(f"\n--- {step.__doc__.splitlines()[0]}")
        step()
