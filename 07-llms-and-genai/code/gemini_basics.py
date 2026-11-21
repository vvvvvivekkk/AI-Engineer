"""
gemini_basics.py - the Google Gen AI SDK (google-genai) for Gemini: system prompt, chat, streaming, JSON, errors.

Run:  python gemini_basics.py
Needs: pip install google-genai pydantic python-dotenv   and GEMINI_API_KEY (or GOOGLE_API_KEY)
Without a key, real calls are skipped and the offline fallback answers. The error demo always runs safely.

Note: always store the client in a variable (client = genai.Client()) before calling it. Writing
genai.Client().models.generate_content(...) in one line can fail with "client has been closed",
because Python may clean up the unnamed client object before the request is sent.
"""
import os
from pydantic import BaseModel
from google import genai
from google.genai import types, errors           # types = request/response classes, errors = exception classes
from llm_clients import local_chat, GEMINI_MODEL

HAS_KEY = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
SYSTEM = "You are a concise tutor for beginner programmers."


def basic_and_system():
    """1. One question with a system instruction and generation settings."""
    q = "What is a token in one sentence?"
    if not HAS_KEY:
        print("[offline]", local_chat(SYSTEM, [{"role": "user", "content": q}])["text"])
        return
    client = genai.Client()                       # reads GEMINI_API_KEY / GOOGLE_API_KEY
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=q,                               # a plain string is fine for one user turn
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,            # the system prompt
            temperature=0.2,                      # low = focused
            max_output_tokens=150,
        ),
    )
    print(resp.text)
    u = resp.usage_metadata
    print("tokens in/out:", u.prompt_token_count, u.candidates_token_count)


def multi_turn():
    """2. History as Content objects; Gemini calls the assistant role 'model'."""
    history = [
        types.Content(role="user", parts=[types.Part(text="My name is Asha and I live in Hyderabad.")]),
        types.Content(role="model", parts=[types.Part(text="Nice to meet you, Asha!")]),
        types.Content(role="user", parts=[types.Part(text="Which city do I live in?")]),
    ]
    if not HAS_KEY:
        print("[offline]", local_chat(SYSTEM, [
            {"role": "user", "content": "My name is Asha and I live in Hyderabad."},
            {"role": "assistant", "content": "Nice to meet you, Asha!"},
            {"role": "user", "content": "Which city do I live in?"}])["text"])
        return
    client = genai.Client()                       # keep the client in a variable (see note at top)
    resp = client.models.generate_content(model=GEMINI_MODEL, contents=history,
                                                  config=types.GenerateContentConfig(system_instruction=SYSTEM))
    print(resp.text)


def streaming():
    """3. generate_content_stream yields chunks as they are produced."""
    if not HAS_KEY:
        print("[offline] streaming needs a key; local fallback:")
        print(local_chat(SYSTEM, [{"role": "user", "content": "Write a two-line poem about Python."}])["text"])
        return
    client = genai.Client()
    for chunk in client.models.generate_content_stream(model=GEMINI_MODEL,
                                                               contents="Write a two-line poem about Python."):
        print(chunk.text or "", end="", flush=True)
    print()


class Ticket(BaseModel):
    category: str
    urgency: int
    summary: str


def structured_output():
    """4. JSON output: set response_mime_type and response_schema; .parsed gives a Ticket."""
    text = "My order #4521 has not arrived after 10 days and nobody answers the phone!"
    if not HAS_KEY:
        print("[offline fake response]", Ticket(category="delivery", urgency=4,
                                                summary="Order #4521 late by 10 days; no phone answer."))
        return
    client = genai.Client()
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=f"Classify this customer message: {text}",
        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=Ticket),
    )
    print(resp.parsed)                            # a Ticket object (resp.text holds the raw JSON string)


def error_handling():
    """5. Catch errors (safe demo against a closed local port, one attempt only)."""
    client = genai.Client(api_key="not-a-real-key",
                          http_options=types.HttpOptions(base_url="http://127.0.0.1:9", timeout=5000,
                                                         retry_options=types.HttpRetryOptions(attempts=1)))
    try:
        client.models.generate_content(model=GEMINI_MODEL, contents="hello")
    except errors.ClientError as e:               # 4xx: fix the request (429 = rate limit: wait)
        print("Client error", e.code, e.message)
    except errors.ServerError as e:               # 5xx: retry later
        print("Server error", e.code)
    except Exception as e:                        # connection problems surface as httpx errors
        print("Connection problem (expected in this demo):", type(e).__name__)


if __name__ == "__main__":
    print("Key found:", HAS_KEY, "| model:", GEMINI_MODEL)
    for step in [basic_and_system, multi_turn, streaming, structured_output, error_handling]:
        print(f"\n--- {step.__doc__.splitlines()[0]}")
        step()
