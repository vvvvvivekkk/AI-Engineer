"""
ollama_rest.py - talk to a local Ollama server over its REST API using httpx.

Before running: install Ollama (https://ollama.com), then `ollama pull llama3.2:1b`.
Run:  python ollama_rest.py
Needs: httpx   (pip install httpx)
If no Ollama server is running, the script says so and exits politely.
"""
import json
import os
import httpx

HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")   # where the Ollama server listens
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")            # any model you have pulled


def server_running():
    """True if something answers at HOST within 2 seconds."""
    try:
        return httpx.get(HOST, timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


def list_models():
    """GET /api/tags lists the models on disk."""
    r = httpx.get(f"{HOST}/api/tags", timeout=10)
    r.raise_for_status()                                     # turn HTTP errors into Python exceptions
    return [m["name"] for m in r.json()["models"]]


def chat(messages, stream=False):
    """POST /api/chat with a list of {role, content} messages."""
    body = {"model": MODEL, "messages": messages, "stream": stream,
            "options": {"temperature": 0.2}}                 # sampling settings go in "options"
    if not stream:
        r = httpx.post(f"{HOST}/api/chat", json=body, timeout=300)
        r.raise_for_status()
        data = r.json()
        return data["message"]["content"], data.get("prompt_eval_count"), data.get("eval_count")
    # Streaming: the server sends one JSON object per line until "done" is true
    with httpx.stream("POST", f"{HOST}/api/chat", json=body, timeout=300) as r:
        for line in r.iter_lines():
            if line:
                part = json.loads(line)
                print(part["message"]["content"], end="", flush=True)
                if part.get("done"):
                    print()
    return None, None, None


def generate(prompt):
    """POST /api/generate: single prompt in, text out (no chat roles)."""
    r = httpx.post(f"{HOST}/api/generate", json={"model": MODEL, "prompt": prompt, "stream": False}, timeout=300)
    r.raise_for_status()
    return r.json()["response"]


if __name__ == "__main__":
    if not server_running():
        print(f"No Ollama server at {HOST}. Install from https://ollama.com and run `ollama pull {MODEL}`.")
        raise SystemExit(0)
    print("Models on disk:", list_models())
    text, n_in, n_out = chat([{"role": "system", "content": "Answer in one sentence."},
                              {"role": "user", "content": "What is quantisation?"}])
    print(f"Chat answer ({n_in} prompt tokens, {n_out} output tokens):\n{text}\n")
    print("Streaming answer:")
    chat([{"role": "user", "content": "Count from 1 to 5 in words."}], stream=True)
    print("Generate:", generate("Complete: The three primary colours are"))
