"""
vllm_client.py - talk to a vLLM server using the OpenAI-style API.

vLLM speaks the same "language" (HTTP API format) as OpenAI, so the same client
code works against OpenAI, vLLM, Ollama, LM Studio and many hosted providers -
you only change base_url, the key and the model name.

Run (after starting serving/vllm_serve.sh on a GPU machine):
    export VLLM_BASE_URL=http://localhost:8001/v1
    export VLLM_API_KEY=the-key-you-chose
    python vllm_client.py
Without VLLM_BASE_URL set, it prints the request it WOULD send and exits (offline safe).
"""
import json
import os
import httpx

BASE_URL = os.getenv("VLLM_BASE_URL")                      # e.g. http://localhost:8001/v1
API_KEY = os.getenv("VLLM_API_KEY", "not-set")
MODEL = os.getenv("VLLM_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")

# The request body follows the OpenAI "chat completions" format.
payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "In one sentence, what is continuous batching?"},
    ],
    "max_tokens": 80,
    "temperature": 0.2,
}

if not BASE_URL:                                            # offline: show, don't send
    print("VLLM_BASE_URL not set - this is the request that would be sent:")
    print(json.dumps(payload, indent=2))
else:
    # Option A: plain HTTP with httpx (no extra packages)
    r = httpx.post(f"{BASE_URL}/chat/completions", json=payload,
                   headers={"Authorization": f"Bearer {API_KEY}"}, timeout=60)
    r.raise_for_status()                                    # turn HTTP errors into Python exceptions
    print(r.json()["choices"][0]["message"]["content"])

    # Option B: the official openai package (pip install openai) - same server, nicer API
    try:
        from openai import OpenAI
        client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
        resp = client.chat.completions.create(**payload)
        print(resp.choices[0].message.content)
    except ImportError:
        print("openai package not installed; Option A already worked.")
