"""
solutions.py - runnable solutions for Module 07 exercises 1-10. All run WITHOUT API keys.

Run all:          python solutions.py
Run one (e.g. 9): python solutions.py 9
Needs: numpy, pandas, tiktoken, pydantic, torch, transformers, httpx; optional: openai, anthropic, google-genai
"""
import json
import os
import random
import re
import sys
import time

import numpy as np

SMOL = "HuggingFaceTB/SmolLM2-135M-Instruct"
_cache = {}


def smol():
    """Load SmolLM2 once (float32 is much faster than its stored bfloat16 on CPU)."""
    if not _cache:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        _cache["tok"] = AutoTokenizer.from_pretrained(SMOL)
        _cache["model"] = AutoModelForCausalLM.from_pretrained(SMOL, dtype=torch.float32).eval()
    return _cache["tok"], _cache["model"]


def local_chat(system, messages, max_new_tokens=80):
    """Offline fallback used by several solutions."""
    import torch
    tok, model = smol()
    chat = [{"role": "system", "content": system}] + list(messages)
    inputs = tok.apply_chat_template(chat, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    n_in = inputs["input_ids"].shape[1]
    return {"text": tok.decode(out[0][n_in:], skip_special_tokens=True).strip(),
            "input_tokens": n_in, "output_tokens": int(out.shape[1] - n_in), "source": "local SmolLM2"}


# ---------------------------------------------------------------- 1
def ex1():
    import torch
    tok, model = smol()
    for prompt in ["I drank a cup of", "The opposite of hot is", "My favourite programming language is"]:
        ids = tok(prompt, return_tensors="pt")["input_ids"]
        with torch.no_grad():
            probs = torch.softmax(model(input_ids=ids).logits[0, -1], dim=-1)
        top = torch.topk(probs, 5)
        print(prompt, "->", [(tok.decode(int(i)), round(float(p), 3)) for p, i in zip(top.values, top.indices)])


# ---------------------------------------------------------------- 2
def softmax(x):
    x = np.asarray(x, dtype=float)
    e = np.exp(x - x.max())
    return e / e.sum()


def ex2():
    logits = np.array([3.0, 2.0, 1.0, 0.5])
    for T in [0.1, 1.0, 5.0]:
        print(f"T={T}:", {k: round(float(v), 3) for k, v in zip(["cat", "dog", "fish", "bird"], softmax(logits / T))})


# ---------------------------------------------------------------- 3
def get_key(name):
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    value = os.getenv(name)
    if not value:
        print(f"{name} not set - using offline fallback")
        return None
    print(f"{name} found ({len(value)} characters)")    # report presence only, never the value
    return value


def ex3():
    get_key("OPENAI_API_KEY")
    get_key("MY_MADE_UP_KEY_NAME")


# ---------------------------------------------------------------- 4
def top_p_filter(probs, p):
    probs = np.asarray(probs, dtype=float)
    order = np.argsort(probs)[::-1]                         # most likely first
    cumulative = np.cumsum(probs[order])
    n_keep = int(np.searchsorted(cumulative, p - 1e-12)) + 1   # first index where the total reaches p
    keep = order[:n_keep]
    new = np.zeros_like(probs)
    new[keep] = probs[keep]
    return keep, new / new.sum()


def sample(probs, temperature, top_p, rng):
    logp = np.log(np.asarray(probs, dtype=float) + 1e-12)   # back to log space, then apply temperature
    p = softmax(logp / temperature)
    _, p = top_p_filter(p, top_p)
    return int(rng.choice(len(p), p=p))


def ex4():
    probs = [0.5, 0.2, 0.15, 0.1, 0.05]
    for p in [0.6, 0.8, 0.95]:
        keep, new = top_p_filter(probs, p)
        print(f"p={p}: keep {keep.tolist()} -> {np.round(new, 3).tolist()}")
    rng = np.random.default_rng(0)
    draws = [sample(probs, 1.0, 0.8, rng) for _ in range(1000)]
    print("1000 samples (T=1, top_p=0.8) counts:", np.bincount(draws, minlength=5).tolist())


# ---------------------------------------------------------------- 5
class Conversation:
    def __init__(self, system):
        import tiktoken
        self.enc = tiktoken.get_encoding("o200k_base")
        self.system = system
        self.messages = []

    def add_user(self, text):
        self.messages.append({"role": "user", "content": text})

    def add_assistant(self, text):
        self.messages.append({"role": "assistant", "content": text})

    def _tokens(self, msgs):
        return sum(len(self.enc.encode(m["content"])) + 4 for m in msgs)

    def token_count(self):
        return self._tokens([{"role": "system", "content": self.system}] + self.messages)

    def trimmed(self, max_tokens):
        sys_msg = [{"role": "system", "content": self.system}]
        kept = []
        for m in reversed(self.messages):                   # walk backwards from the newest message
            if self._tokens(sys_msg + [m] + kept) > max_tokens:
                break
            kept.insert(0, m)
        while kept and kept[0]["role"] != "user":           # history must start with a user turn
            kept.pop(0)
        return sys_msg + kept


def ex5():
    c = Conversation("You are a friendly maths tutor.")
    for i in range(20):
        c.add_user(f"Question {i}: what is {i} squared, and why?")
        c.add_assistant(f"{i} squared is {i*i}, because you multiply {i} by itself.")
    t = c.trimmed(300)
    print("full tokens:", c.token_count(), "| trimmed messages:", len(t) - 1,
          "| trimmed tokens:", c._tokens(t), "| first kept:", t[1]["content"][:30])


# ---------------------------------------------------------------- 6
def ask(provider, system, messages):
    keys = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY"}
    if not os.getenv(keys[provider]) and not (provider == "gemini" and os.getenv("GOOGLE_API_KEY")):
        return {"text": f"(fake answer from {provider})", "input_tokens": 0, "output_tokens": 0, "source": "fake"}
    if provider == "openai":
        from openai import OpenAI
        client = OpenAI()
        r = client.responses.create(model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
                                    instructions=system, input=messages, max_output_tokens=300)
        return {"text": r.output_text, "input_tokens": r.usage.input_tokens,
                "output_tokens": r.usage.output_tokens, "source": "openai"}
    if provider == "anthropic":
        from anthropic import Anthropic
        client = Anthropic()
        m = client.messages.create(model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5"), max_tokens=300,
                                   system=system, messages=messages)
        return {"text": "".join(b.text for b in m.content if b.type == "text"),
                "input_tokens": m.usage.input_tokens, "output_tokens": m.usage.output_tokens, "source": "anthropic"}
    from google import genai
    from google.genai import types
    client = genai.Client()
    contents = [types.Content(role="model" if m["role"] == "assistant" else "user",
                              parts=[types.Part(text=m["content"])]) for m in messages]
    r = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"), contents=contents,
                                       config=types.GenerateContentConfig(system_instruction=system))
    return {"text": r.text, "input_tokens": r.usage_metadata.prompt_token_count,
            "output_tokens": r.usage_metadata.candidates_token_count, "source": "gemini"}


def ex6():
    for p in ["openai", "anthropic", "gemini"]:
        print(p, ask(p, "Be brief.", [{"role": "user", "content": "Name one planet."}]))


# ---------------------------------------------------------------- 7
def monthly_cost(req_per_day, in_tokens, out_tokens, price_in, price_out, days=30):
    return req_per_day * days * (in_tokens * price_in + out_tokens * price_out) / 1e6


def ex7():
    FAKE = {"small (FAKE prices)": (0.20, 0.80), "large (FAKE prices)": (5.00, 25.00)}   # not real prices
    sys_t, q_t, a_t, rpd = 400, 40, 180, 2000
    for name, (pi, po) in FAKE.items():
        total = monthly_cost(rpd, sys_t + q_t, a_t, pi, po)
        sys_part = monthly_cost(rpd, sys_t, 0, pi, po)
        print(f"{name}: ${total:,.2f}/month; system prompt share {sys_part / total:.0%}")


# ---------------------------------------------------------------- 8
def ex8():
    from pydantic import BaseModel, ValidationError

    class Invoice(BaseModel):
        vendor: str
        total: float
        currency: str
        date: str

    def try_parse(raw):
        m = re.search(r"\{.*?\}", raw, re.S)
        if not m:
            raise ValueError("no JSON object found")
        return Invoice(**json.loads(m.group(0)))

    def extract_invoice(text):
        if os.getenv("ANTHROPIC_API_KEY"):
            from anthropic import Anthropic
            client = Anthropic()
            return client.messages.parse(model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5"), max_tokens=300,
                                         messages=[{"role": "user", "content": f"Extract the invoice: {text}"}],
                                         output_format=Invoice).parsed_output
        prompts = [
            f'Return JSON with keys vendor, total, currency, date for this invoice: {text}',
            'Output ONLY one line of JSON exactly like {"vendor": "...", "total": 0.0, "currency": "...", '
            f'"date": "YYYY-MM-DD"}} and nothing else. Invoice: {text}',
        ]
        for attempt, prompt in enumerate(prompts, start=1):
            raw = local_chat("You extract data and reply in JSON.", [{"role": "user", "content": prompt}], 80)["text"]
            try:
                return try_parse(raw)
            except (ValueError, json.JSONDecodeError, ValidationError, TypeError) as e:
                print(f"   attempt {attempt} failed: {type(e).__name__}: {str(e)[:60]!r}")
        return None

    texts = ["Invoice from Sri Ganesh Traders dated 2026-10-02. Total due: 4,500 INR.",
             "Amogha Sweets bill, 12 Nov 2026, amount 1250.50 rupees (INR).",
             "Cloud hosting invoice - DigitalWave Ltd - 2026-09-30 - USD 89.99"]
    ok = 0
    for t in texts:
        r = extract_invoice(t)
        ok += r is not None
        print(t[:45], "->", r)
    print(f"valid JSON: {ok}/{len(texts)}")


# ---------------------------------------------------------------- 9
class FakeAPIError(Exception):
    def __init__(self, status_code, retry_after=None):
        super().__init__(f"HTTP {status_code}")
        self.status_code, self.retry_after = status_code, retry_after


TEMPORARY = {429, 500, 502, 503, 529}


def call_with_retry(fn, max_attempts=5, base=0.5, max_wait=8, sleep=time.sleep):
    log = []
    for attempt in range(max_attempts):
        try:
            result = fn()
            log.append((attempt + 1, "ok", 0))
            return result, log
        except FakeAPIError as e:
            if e.status_code not in TEMPORARY:
                log.append((attempt + 1, f"permanent {e.status_code}", 0))
                raise
            if attempt == max_attempts - 1:
                log.append((attempt + 1, f"gave up on {e.status_code}", 0))
                raise
            wait = e.retry_after if e.retry_after is not None else random.uniform(0, min(max_wait, base * 2 ** attempt))
            log.append((attempt + 1, f"temporary {e.status_code}", round(wait, 3)))
            sleep(wait)


def make_api(codes):
    """Returns a fake API that raises the given codes in order, then succeeds."""
    it = iter(codes)
    def api():
        code = next(it, None)
        if code is None:
            return "success"
        raise FakeAPIError(code, retry_after=1.0 if code == 429 else None)
    return api


def ex9():
    no_sleep = lambda s: None                               # tests should not actually wait
    r, log = call_with_retry(make_api([500, 429]), sleep=no_sleep)
    print("test 1:", r, log); assert r == "success" and log[1][2] == 1.0   # honoured retry_after
    try:
        call_with_retry(make_api([401]), sleep=no_sleep)
    except FakeAPIError as e:
        print("test 2: failed fast with", e.status_code); assert e.status_code == 401
    try:
        call_with_retry(make_api([503] * 10), max_attempts=4, sleep=no_sleep)
    except FakeAPIError as e:
        print("test 3: gave up with", e.status_code)
    print("all tests passed")


# ---------------------------------------------------------------- 10
def ex10():
    import httpx
    import pandas as pd
    prompts = ["Summarise: the meeting moved to Friday 3pm.", "Translate 'good morning' to Hindi.",
               "Give one tip for a job interview.", "What is 17 * 3?", "Write a 6-word slogan for a juice shop."]
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        ollama_up = httpx.get(host, timeout=2).status_code == 200
    except httpx.HTTPError:
        ollama_up = False
    rows = []
    for p in prompts:
        msgs = [{"role": "user", "content": p}]
        t0 = time.time()
        if ollama_up:
            r = httpx.post(f"{host}/api/chat", json={"model": os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
                                                     "messages": msgs, "stream": False}, timeout=300).json()
            local = {"text": r["message"]["content"], "output_tokens": r.get("eval_count"), "source": "ollama"}
        else:
            local = local_chat("Be brief.", msgs, 40)
        t_local = time.time() - t0
        t0 = time.time()
        hosted = ask("anthropic", "Be brief.", msgs)
        rows.append({"prompt": p[:30], "local_source": local["source"], "local_s": round(t_local, 2),
                     "local_answer": local["text"][:50], "hosted_source": hosted["source"],
                     "hosted_s": round(time.time() - t0, 2), "hosted_answer": hosted["text"][:40]})
    print(pd.DataFrame(rows).to_string())


if __name__ == "__main__":
    chosen = [int(a) for a in sys.argv[1:]] or range(1, 11)
    for n in chosen:
        print(f"\n===== Exercise {n} =====")
        globals()[f"ex{n}"]()
