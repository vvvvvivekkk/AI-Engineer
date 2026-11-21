"""
ollama_client.py - the official `ollama` Python package, plus the OpenAI-compatible endpoint.

Before running: install Ollama (https://ollama.com), then `ollama pull llama3.2:1b`.
Run:  python ollama_client.py
Needs: pip install ollama openai
"""
import os
import ollama                                   # official Python client for a local Ollama server
from openai import OpenAI

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

try:
    ollama.list()                               # quick check that the server is up
except Exception:
    print(f"No Ollama server reachable at {HOST}. Install it from https://ollama.com and pull {MODEL}.")
    raise SystemExit(0)

# 1. Chat with roles, like the cloud APIs
resp = ollama.chat(model=MODEL, messages=[
    {"role": "system", "content": "You are a concise tutor."},
    {"role": "user", "content": "What is a context window?"},
], options={"temperature": 0.2})               # sampling settings go in options
print(resp.message.content)

# 2. Streaming: stream=True returns an iterator of partial responses
for part in ollama.chat(model=MODEL, messages=[{"role": "user", "content": "Name three fruits."}], stream=True):
    print(part.message.content, end="", flush=True)
print()

# 3. JSON output: pass a JSON schema in `format`
schema = {"type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
          "required": ["city", "country"]}
resp = ollama.chat(model=MODEL, messages=[{"role": "user", "content": "Capital of Japan? Reply as JSON."}],
                   format=schema)
print(resp.message.content)

# 4. Same server through the OpenAI SDK: only base_url and a dummy api_key change
client = OpenAI(base_url=f"{HOST}/v1", api_key="ollama")   # Ollama ignores the key, but the SDK needs one
chat = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": "Say hello in Telugu."}])
print(chat.choices[0].message.content)
