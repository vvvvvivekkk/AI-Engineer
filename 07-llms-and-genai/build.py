import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook

"""
build.py for Module 07 - LLMs and Generative AI.
Regenerates: images/ (Mermaid + matplotlib), notebooks/, slides/, pdf/, excel/.
Run from the repo root:  python 07-llms-and-genai/build.py
"""
IMG = HERE / "images"
NB = HERE / "notebooks"
MOD = "07-llms-and-genai"
SMOL = "HuggingFaceTB/SmolLM2-135M-Instruct"

PRICING = {
    "OpenAI": "https://openai.com/api/pricing/",
    "Anthropic": "https://platform.claude.com/docs/en/about-claude/pricing",
    "Google Gemini": "https://ai.google.dev/gemini-api/docs/pricing",
}


# ---------------------------------------------------------------------------
# 1. Diagrams
# ---------------------------------------------------------------------------
def build_diagrams():
    mermaid("""
flowchart LR
    A["Tokens so far"] --> B["Transformer<br/>forward pass"]
    B --> C["Probabilities for<br/>every vocab token"]
    C --> D["Sampling<br/>(greedy / temperature / top-p)"]
    D --> E["Append chosen token"]
    E --> F{"End token or<br/>max_tokens?"}
    F -- no --> A
    F -- yes --> G["Finished answer"]
""", IMG / "generation-loop.png")

    mermaid("""
flowchart LR
    D1[("Trillions of tokens<br/>web, books, code")] --> P["1. Pre-training<br/>predict next token"]
    P --> BM["Base model<br/>continues text"]
    D2[("Example conversations<br/>written by people")] --> S["2. Instruction tuning (SFT)"]
    BM --> S
    S --> IM["Instruct / chat model"]
    D3[("Human preferences<br/>answer A better than B")] --> R["3. RLHF or DPO"]
    IM --> R
    R --> AM["Assistant you use<br/>helpful, safer"]
""", IMG / "training-stages.png")

    mermaid("""
flowchart LR
    C["Your Python code<br/>messages + settings"] --> SDK["Provider SDK<br/>openai / anthropic / google-genai"]
    K[".env / env var<br/>API key"] -.read by.-> SDK
    SDK -- "HTTPS request (JSON)" --> API["Provider servers<br/>run the LLM"]
    API -- "response: text + usage" --> SDK
    API -. "or a stream of events" .-> SDK
    SDK --> R["Python object<br/>.output_text / .content / .text"]
""", IMG / "api-call-flow.png")

    mermaid("""
flowchart TD
    A["Call the API"] --> B{"Success?"}
    B -- yes --> Z["Use the answer"]
    B -- no --> C{"Temporary error?<br/>429, 5xx, 529, timeout"}
    C -- "no (400, 401, 404)" --> X["Stop: fix the request<br/>or the key"]
    C -- yes --> D{"Attempts left?"}
    D -- no --> Y["Give up gracefully<br/>message / fallback model"]
    D -- yes --> W["Wait 1s, 2s, 4s ...<br/>+ random jitter"]
    W --> A
""", IMG / "retry-backoff.png")

    mermaid("""
flowchart LR
    I["Install Ollama<br/>ollama.com"] --> P["ollama pull llama3.2:1b"]
    P --> S(("Local server<br/>localhost:11434"))
    S --> T["Terminal<br/>ollama run"]
    S --> R["REST API<br/>/api/chat, /api/generate"]
    S --> Py["Python client<br/>import ollama"]
    S --> O["OpenAI-compatible<br/>/v1 endpoint"]
""", IMG / "ollama-flow.png")

    mermaid("""
flowchart TD
    A{"Must data stay<br/>on your machines?"} -- yes --> L["Open-weight model<br/>Ollama / own server"]
    A -- no --> B{"How hard is the task?"}
    B -- "simple: tag, extract, route" --> S["Small, cheap, fast tier"]
    B -- "hard: reasoning, code, long reports" --> F["Frontier / top tier"]
    S --> C{"Passes your test set?"}
    C -- no --> F
    C -- yes --> D["Estimate monthly cost<br/>with the calculator"]
    F --> D
    D --> E["Ship, log usage,<br/>re-check every few months"]
""", IMG / "model-choice.png")


def build_plots():
    """Real next-token probabilities from SmolLM2 + the temperature/top-p figure."""
    import numpy as np
    import torch
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from transformers import AutoTokenizer, AutoModelForCausalLM

    tok = AutoTokenizer.from_pretrained(SMOL)
    model = AutoModelForCausalLM.from_pretrained(SMOL, dtype=torch.float32)
    ids = tok("The capital of France is", return_tensors="pt")["input_ids"]
    with torch.no_grad():
        logits = model(input_ids=ids).logits[0, -1]
    probs = torch.softmax(logits, -1)
    top = torch.topk(probs, 10)
    labels = [repr(tok.decode(int(i))) for i in top.indices]
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.barh(labels[::-1], top.values.numpy()[::-1], color="#0F9D9A")
    for y, v in enumerate(top.values.numpy()[::-1]):
        ax.text(v + 0.005, y, f"{v:.1%}", va="center", fontsize=9)
    ax.set_xlabel("probability of being the next token")
    ax.set_title("SmolLM2-135M: 'The capital of France is' -> next token")
    fig.tight_layout()
    fig.savefig(IMG / "next-token-probs.png", dpi=150)
    plt.close(fig)

    top_logits = logits[top.indices].numpy()
    fig, axes = plt.subplots(1, 4, figsize=(17, 4.2), sharey=True)
    for ax, T in zip(axes[:3], [0.3, 1.0, 1.8]):
        p = np.exp(top_logits / T - (top_logits / T).max()); p /= p.sum()
        ax.bar(range(10), p, color="#0F9D9A")
        ax.set_title(f"temperature = {T}")
        ax.set_xticks(range(10), labels=labels, rotation=60, fontsize=8)
    p = np.exp(top_logits - top_logits.max()); p /= p.sum()
    order = np.argsort(p)[::-1]
    keep = order[: int(np.searchsorted(np.cumsum(p[order]), 0.9)) + 1]
    colors = ["#0F9D9A" if i in keep else "#C9CED6" for i in range(10)]
    axes[3].bar(range(10), p, color=colors)
    axes[3].set_title("top-p = 0.9 (grey = removed)")
    axes[3].set_xticks(range(10), labels=labels, rotation=60, fontsize=8)
    axes[0].set_ylabel("probability (top-10 tokens, renormalised)")
    fig.tight_layout()
    fig.savefig(IMG / "sampling-temperature.png", dpi=140)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Notebooks
# ---------------------------------------------------------------------------
INSTALL_BASE = '''import importlib.util, subprocess, sys
# Install a package only if it is missing (Colab already has most of these).
def ensure(pkg, module=None):
    if importlib.util.find_spec(module or pkg) is None:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg], check=True)
'''

LOCAL_CHAT = '''import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

LOCAL_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
_tok = AutoTokenizer.from_pretrained(LOCAL_MODEL)
_model = AutoModelForCausalLM.from_pretrained(LOCAL_MODEL, dtype=torch.float32)   # float32: fast on CPU

def local_chat(system, messages, max_new_tokens=80):
    """OFFLINE FALLBACK: answer with a tiny local model. Same inputs/outputs as the API helpers below."""
    chat = [{"role": "system", "content": system}] + list(messages)
    inputs = _tok.apply_chat_template(chat, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    with torch.no_grad():
        out = _model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    n_in = inputs["input_ids"].shape[1]
    return {"text": _tok.decode(out[0][n_in:], skip_special_tokens=True).strip(),
            "input_tokens": n_in, "output_tokens": out.shape[1] - n_in,
            "source": "offline-fallback (SmolLM2-135M)"}

print(local_chat("Answer in one sentence.", [{"role": "user", "content": "What is Python?"}]))'''


def build_notebooks():
    # ---------------- Notebook 01: how LLMs work ----------------
    notebook([
        ("md", """# 01 - How LLMs work: next tokens, sampling and the context window

**Goal:** look inside a real (tiny) LLM and watch it predict the next token, see how **temperature** and **top-p** change its choices, and measure a **context window**.

We use `HuggingFaceTB/SmolLM2-135M-Instruct` — a 135-million-parameter model that runs on any CPU. Big chat models work the same way, with far more parameters. No API keys. First run downloads about 270 MB."""),
        ("md", "## Setup\nInstall anything missing and load the model and tokenizer. `model.eval()` switches the model to inference (use) mode."),
        ("code", INSTALL_BASE + '''ensure("transformers"); ensure("torch")

import torch, numpy as np, matplotlib.pyplot as plt
from transformers import AutoTokenizer, AutoModelForCausalLM
torch.manual_seed(0)

NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"
tok = AutoTokenizer.from_pretrained(NAME)
# dtype=torch.float32: the weights are stored in bfloat16, which is very slow on most CPUs
model = AutoModelForCausalLM.from_pretrained(NAME, dtype=torch.float32).eval()
print(f"Loaded {NAME}: {sum(p.numel() for p in model.parameters())/1e6:.0f}M parameters, vocab {tok.vocab_size:,}")'''),
        ("md", """## 1. Next-token probabilities

The model outputs one **logit** (raw score) per vocabulary token for the position after the last token. **Softmax** turns logits into probabilities. We print the 10 most likely next tokens."""),
        ("code", '''def next_token_probs(text):
    ids = tok(text, return_tensors="pt")["input_ids"]
    with torch.no_grad():
        logits = model(input_ids=ids).logits[0, -1]     # scores for the NEXT token
    return logits, torch.softmax(logits, dim=-1)

prompt = "The capital of France is"
logits, probs = next_token_probs(prompt)
top = torch.topk(probs, 10)
for p, i in zip(top.values, top.indices):
    print(f"{tok.decode(int(i))!r:<14} {float(p):6.1%}")
print("Sum of ALL probabilities:", round(float(probs.sum()), 4))'''),
        ("md", "Draw it as a bar chart. The model is ranking possible continuations, not looking up a fact."),
        ("code", '''labels = [repr(tok.decode(int(i))) for i in top.indices]
plt.figure(figsize=(8, 4))
plt.barh(labels[::-1], top.values.numpy()[::-1], color="teal")
plt.xlabel("probability"); plt.title(f"Next token after {prompt!r}")
plt.tight_layout(); plt.show()'''),
        ("md", """## 2. The generation loop, by hand

**Autoregressive** generation: predict → pick → append → repeat. Here we always pick the top token (**greedy decoding**) and print the probability of each choice. Watch how confident the model is at each step."""),
        ("code", '''text = prompt
for step in range(10):
    _, p = next_token_probs(text)
    best = int(torch.argmax(p))
    text += tok.decode(best)
    print(f"step {step+1:>2}: picked {tok.decode(best)!r:<12} with p={float(p[best]):.2f}")
print("\\nResult:", text)'''),
        ("md", """## 3. Temperature

**Temperature** divides every logit before softmax. Low temperature sharpens the distribution (the favourite wins almost always); high temperature flattens it (surprising tokens get a real chance)."""),
        ("code", '''top_logits = logits[top.indices]
fig, axes = plt.subplots(1, 3, figsize=(15, 3.8), sharey=True)
for ax, T in zip(axes, [0.3, 1.0, 1.8]):
    p = torch.softmax(top_logits / T, dim=-1).numpy()
    ax.bar(range(10), p, color="teal"); ax.set_title(f"temperature = {T}")
    ax.set_xticks(range(10), labels=labels, rotation=60, fontsize=8)
axes[0].set_ylabel("probability (top 10, renormalised)")
plt.tight_layout(); plt.show()'''),
        ("md", """## 4. Top-p (nucleus) sampling

**Top-p** keeps the smallest group of most-likely tokens whose probabilities add up to at least p, throws the rest away, and renormalises. Let's write it and see which tokens survive p = 0.9 and p = 0.5."""),
        ("code", '''def top_p_keep(probs, p):
    sorted_p, sorted_idx = torch.sort(probs, descending=True)
    cumulative = torch.cumsum(sorted_p, dim=0)
    n_keep = int((cumulative < p).sum()) + 1              # tokens needed to reach p
    return sorted_idx[:n_keep]

for p in [0.5, 0.9]:
    keep = top_p_keep(probs, p)
    print(f"top-p={p}: keeps {len(keep)} tokens ->", [tok.decode(int(i)) for i in keep][:15])'''),
        ("md", """## 5. Sampling with `generate()`

Now let Hugging Face do it. `do_sample=True` turns on random sampling; we try three temperatures, three runs each (different random **seeds** — starting points for the random number generator). Low temperature stays close to the most likely wording; high temperature wanders further (and gets weirder). Even at low temperature, runs can differ when the first few tokens have similar probabilities."""),
        ("code", '''chat = [{"role": "user", "content": "Give me a name for a cat cafe."}]
inputs = tok.apply_chat_template(chat, add_generation_prompt=True, return_tensors="pt", return_dict=True)
for T in [0.2, 0.8, 1.5]:
    print(f"--- temperature {T}")
    for seed in range(3):
        torch.manual_seed(seed)
        out = model.generate(**inputs, max_new_tokens=15, do_sample=True, temperature=T, top_p=0.95)
        print("  ", tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip())'''),
        ("md", """## 6. The context window

The **context window** is the most tokens the model can handle at once (input + output). For SmolLM2 it is in the model config. Frontier API models allow far more — check each provider's model page."""),
        ("code", '''print("max_position_embeddings (context window):", model.config.max_position_embeddings)
print("tokenizer.model_max_length:", tok.model_max_length)'''),
        ("md", """In a chat app the **whole history is re-sent every turn**, so input tokens grow with each message. Let's simulate a 12-turn conversation and count tokens per request, then see when it would overflow a small 1,024-token window."""),
        ("code", '''history = [{"role": "system", "content": "You are a helpful travel assistant for trips in India."}]
window = 1024
rows = []
for turn in range(1, 13):
    history.append({"role": "user", "content": f"Question {turn}: suggest three things to do in city number {turn}, with timings and prices."})
    history.append({"role": "assistant", "content": "Here are three ideas: a morning heritage walk (7-9am), a food market visit in the afternoon, and an evening boat ride. Prices vary; check locally. " * 2})
    n = len(tok.apply_chat_template(history, tokenize=True, return_dict=False))   # list of token IDs
    rows.append((turn, n))
    flag = "  <-- over the window, must trim or summarise!" if n > window else ""
    print(f"turn {turn:>2}: {n:>5} tokens sent{flag}")'''),
        ("md", "A simple fix is a **sliding window**: keep the system prompt and only the most recent messages that fit. (Module 08 covers smarter options like summarising old turns.)"),
        ("code", '''def trim_history(history, max_tokens):
    system, rest = history[:1], history[1:]
    while rest and len(tok.apply_chat_template(system + rest, tokenize=True, return_dict=False)) > max_tokens:
        rest = rest[2:]                       # drop the oldest user+assistant pair
    return system + rest

trimmed = trim_history(history, window)
print("messages before:", len(history), " after:", len(trimmed),
      " tokens after:", len(tok.apply_chat_template(trimmed, tokenize=True, return_dict=False)))'''),
        ("md", """## 7. Why chat templates matter (base vs instruct behaviour)

Instruct models were trained with special markers around each role. Without them the model behaves more like a **base model** and continues the text. Below, the raw text looks like the start of a quiz page, so the model continues the quiz with more questions instead of answering. With the chat template, the same model answers.

Notice also that SmolLM2's template inserts a default system prompt when we don't give one."""),
        ("code", '''question = "What is the capital of France?"
raw = tok("Geography quiz:\\n1. " + question + "\\n2.", return_tensors="pt")
out = model.generate(**raw, max_new_tokens=25, do_sample=False)
print("RAW (no template):", repr(tok.decode(out[0][raw["input_ids"].shape[1]:], skip_special_tokens=True)))

templ = tok.apply_chat_template([{"role": "user", "content": question}], add_generation_prompt=True,
                                return_tensors="pt", return_dict=True)
out = model.generate(**templ, max_new_tokens=25, do_sample=False)
print("WITH TEMPLATE:   ", repr(tok.decode(out[0][templ["input_ids"].shape[1]:], skip_special_tokens=True)))
print("\\nThe template text the model actually saw:\\n" + tok.apply_chat_template([{"role": "user", "content": question}], add_generation_prompt=True, tokenize=False))'''),
        ("md", """## Try it yourself
1. Change `prompt` to `"The best programming language for beginners is"`. How spread out are the probabilities?
2. In section 5, set `temperature=3.0`. What happens to the text?
3. Change `window` to 4096. At which turn would the conversation overflow now?
4. Pick a prompt where the top token has less than 20% probability. What does that tell you about how "sure" the model is?"""),
    ], NB / "01-how-llms-work.ipynb")

    # ---------------- Notebook 02: calling APIs ----------------
    notebook([
        ("md", """# 02 - Calling LLM APIs: OpenAI, Anthropic and Gemini

**Goal:** learn the request shape of the three big provider SDKs — **messages and roles**, **system prompts**, **streaming**, **structured JSON output**, **errors and retries** — in a way that runs **with or without API keys**.

- If a key is set (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`), the real API is called.
- If not, every call uses a clearly labelled **offline fallback**: a tiny local model (SmolLM2-135M) or a fake response. You still see the real code.

**Never paste a key into a notebook.** Put it in a `.env` file (see `.env.example` in this module) or, on Colab, in the Secrets panel (key icon on the left)."""),
        ("md", "## Setup\nInstall the three official SDKs (they are small) plus `python-dotenv`, which loads keys from a `.env` file."),
        ("code", INSTALL_BASE + '''for pkg, mod in [("openai", "openai"), ("anthropic", "anthropic"), ("google-genai", "google.genai"),
                 ("python-dotenv", "dotenv"), ("pydantic", "pydantic"), ("transformers", "transformers")]:
    ensure(pkg, mod)
import openai, anthropic
from google import genai
print("openai", openai.__version__, "| anthropic", anthropic.__version__, "| google-genai", genai.__version__)'''),
        ("md", """## 1. Load keys safely

`load_dotenv()` copies `KEY=value` lines from a `.env` file into **environment variables**. We print only *whether* each key exists — never the key itself. On Colab, the commented lines show how to read from Secrets."""),
        ("code", '''import os
from dotenv import load_dotenv
load_dotenv()          # looks for a .env file in this folder or its parents

# On Colab, uncomment to copy secrets into environment variables:
# from google.colab import userdata
# for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
#     try: os.environ[k] = userdata.get(k)
#     except Exception: pass

HAS = {
    "openai": bool(os.getenv("OPENAI_API_KEY")),
    "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
    "gemini": bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
}
# Example model names (late 2026) - they change often; override in .env. Check each provider's models page.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
print("Keys found:", HAS)'''),
        ("md", "## 2. The offline fallback\nThis function answers with SmolLM2 on the CPU. It takes the same `system` + `messages` as the real helpers and returns the same kind of dictionary, so the rest of the notebook does not care which one ran."),
        ("code", LOCAL_CHAT),
        ("md", """## 3. Messages and roles

A chat request is a list of messages. Roles: **system** (rules for the assistant), **user** (the person), **assistant** (the model's earlier replies). Each provider puts the system prompt in a slightly different place:

| Provider | System prompt goes in | Assistant role name |
|---|---|---|
| OpenAI (Responses API) | `instructions=` | `assistant` |
| Anthropic | `system=` | `assistant` |
| Gemini | `config=GenerateContentConfig(system_instruction=...)` | `model` |"""),
        ("code", '''SYSTEM = "You are a concise tutor for beginner programmers. Answer in at most two sentences."
QUESTION = [{"role": "user", "content": "What is an API key and why must I keep it secret?"}]
print(SYSTEM); print(QUESTION)'''),
        ("md", """## 4. OpenAI

The **Responses API** (`client.responses.create`) is OpenAI's current main endpoint; `resp.output_text` joins the text output and `resp.usage` holds token counts. The real call runs only if a key exists."""),
        ("code", '''from openai import OpenAI

def ask_openai(system, messages, max_tokens=200):
    if not HAS["openai"]:
        return local_chat(system, messages)                 # offline fallback
    client = OpenAI()                                       # reads OPENAI_API_KEY
    resp = client.responses.create(model=OPENAI_MODEL, instructions=system, input=messages,
                                   max_output_tokens=max_tokens)
    return {"text": resp.output_text, "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens, "source": f"openai:{OPENAI_MODEL}"}

print(ask_openai(SYSTEM, QUESTION))'''),
        ("md", """## 5. Anthropic (Claude)

`client.messages.create` needs `max_tokens`. The reply's `content` is a list of **blocks**; text blocks have `.text`. `stop_reason` says why it stopped (`end_turn`, `max_tokens`, ...)."""),
        ("code", '''from anthropic import Anthropic

def ask_anthropic(system, messages, max_tokens=200):
    if not HAS["anthropic"]:
        return local_chat(system, messages)
    client = Anthropic()                                    # reads ANTHROPIC_API_KEY
    msg = client.messages.create(model=ANTHROPIC_MODEL, max_tokens=max_tokens, system=system, messages=messages)
    text = "".join(b.text for b in msg.content if b.type == "text")
    return {"text": text, "input_tokens": msg.usage.input_tokens,
            "output_tokens": msg.usage.output_tokens, "source": f"anthropic:{ANTHROPIC_MODEL}"}

print(ask_anthropic(SYSTEM, QUESTION))'''),
        ("md", """## 6. Google Gemini

The `google-genai` SDK uses `client.models.generate_content`. History is a list of `Content` objects with `parts`; the assistant role is called `model`. Keep the client in a variable (writing `genai.Client().models...` in one line can fail because Python may close the unnamed client early)."""),
        ("code", '''from google.genai import types

def ask_gemini(system, messages, max_tokens=200):
    if not HAS["gemini"]:
        return local_chat(system, messages)
    client = genai.Client()                                 # reads GEMINI_API_KEY / GOOGLE_API_KEY
    contents = [types.Content(role="model" if m["role"] == "assistant" else "user",
                              parts=[types.Part(text=m["content"])]) for m in messages]
    resp = client.models.generate_content(model=GEMINI_MODEL, contents=contents,
        config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=max_tokens))
    u = resp.usage_metadata
    return {"text": resp.text, "input_tokens": u.prompt_token_count,
            "output_tokens": u.candidates_token_count, "source": f"gemini:{GEMINI_MODEL}"}

print(ask_gemini(SYSTEM, QUESTION))'''),
        ("md", "## 7. Same question, three providers\nPut the answers side by side in a table. Without keys all three rows come from the fallback, but the code path is identical."),
        ("code", '''import pandas as pd
rows = []
for name, fn in [("openai", ask_openai), ("anthropic", ask_anthropic), ("gemini", ask_gemini)]:
    r = fn(SYSTEM, QUESTION)
    rows.append({"provider": name, "source": r["source"], "in": r["input_tokens"], "out": r["output_tokens"],
                 "answer": r["text"][:90]})
pd.set_option("display.max_colwidth", 100)
pd.DataFrame(rows)'''),
        ("md", """## 8. The API has no memory

Each call is independent. To continue a conversation you must send the **whole history**. Compare asking "What is my name?" with and without the earlier turns."""),
        ("code", '''no_history = [{"role": "user", "content": "What is my name?"}]
with_history = [
    {"role": "user", "content": "Hi, my name is Asha."},
    {"role": "assistant", "content": "Hello Asha! How can I help?"},
    {"role": "user", "content": "What is my name?"},
]
print("WITHOUT history:", ask_anthropic("Answer briefly.", no_history)["text"])
print("WITH history:   ", ask_anthropic("Answer briefly.", with_history)["text"])'''),
        ("md", """## 9. Streaming

**Streaming** shows text as it is generated. Real code for each provider is below (it runs only with a key). The offline fallback streams locally with Hugging Face's `TextIteratorStreamer`, which runs generation in a background **thread** (a second line of work inside the same program) and hands us text pieces as they appear."""),
        ("code", '''from threading import Thread
from transformers import TextIteratorStreamer

def stream_local(system, messages):
    chat = [{"role": "system", "content": system}] + messages
    inputs = _tok.apply_chat_template(chat, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    streamer = TextIteratorStreamer(_tok, skip_prompt=True, skip_special_tokens=True)
    Thread(target=_model.generate, kwargs={**inputs, "streamer": streamer, "max_new_tokens": 60}).start()
    for piece in streamer:
        print(piece, end="", flush=True)
    print()

def stream_answer(provider, system, messages):
    if provider == "openai" and HAS["openai"]:
        client = OpenAI()
        for event in client.responses.create(model=OPENAI_MODEL, instructions=system, input=messages, stream=True):
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
        print()
    elif provider == "anthropic" and HAS["anthropic"]:
        client = Anthropic()
        with client.messages.stream(model=ANTHROPIC_MODEL, max_tokens=200, system=system, messages=messages) as s:
            for text in s.text_stream:
                print(text, end="", flush=True)
        print()
    elif provider == "gemini" and HAS["gemini"]:
        client = genai.Client()
        for chunk in client.models.generate_content_stream(model=GEMINI_MODEL, contents=messages[-1]["content"],
                config=types.GenerateContentConfig(system_instruction=system)):
            print(chunk.text or "", end="", flush=True)
        print()
    else:
        print("[offline fallback, streamed locally] ", end="")
        stream_local(system, messages)

stream_answer("anthropic", "You are a poet.", [{"role": "user", "content": "Write two short lines about the monsoon."}])'''),
        ("md", """## 10. Structured JSON output

Programs need data in a fixed shape. We describe the shape with a **Pydantic** model (a Python class that validates data). Each SDK has a helper that sends the **schema** and parses the reply:

- OpenAI: `client.responses.parse(..., text_format=Ticket).output_parsed`
- Anthropic: `client.messages.parse(..., output_format=Ticket).parsed_output`
- Gemini: `config=GenerateContentConfig(response_mime_type="application/json", response_schema=Ticket)` then `.parsed`"""),
        ("code", '''from pydantic import BaseModel, ValidationError

class Ticket(BaseModel):
    category: str     # billing / delivery / technical / other
    urgency: int      # 1 (low) .. 5 (high)
    summary: str

MESSAGE = "My order #4521 has not arrived after 10 days and nobody answers the phone!"

def classify(provider):
    instr = "Classify the customer message into category, urgency (1-5) and a one-line summary."
    if provider == "openai" and HAS["openai"]:
        client = OpenAI()
        return client.responses.parse(model=OPENAI_MODEL, instructions=instr, input=MESSAGE,
                                      text_format=Ticket).output_parsed
    if provider == "anthropic" and HAS["anthropic"]:
        client = Anthropic()
        return client.messages.parse(model=ANTHROPIC_MODEL, max_tokens=300, system=instr,
                                     messages=[{"role": "user", "content": MESSAGE}],
                                     output_format=Ticket).parsed_output
    if provider == "gemini" and HAS["gemini"]:
        client = genai.Client()
        return client.models.generate_content(model=GEMINI_MODEL, contents=f"{instr}\\n\\n{MESSAGE}",
            config=types.GenerateContentConfig(response_mime_type="application/json",
                                               response_schema=Ticket)).parsed
    return None   # no key for this provider

for p in ["openai", "anthropic", "gemini"]:
    print(p, "->", classify(p) or "(no key: skipped)")'''),
        ("md", """### Validation matters: what if the model returns bad JSON?

Without native structured output (older or tiny models), you ask for JSON in the prompt and **must validate**. Our tiny local model often gets the format wrong — a perfect demonstration. We try to parse; if it fails we fall back to a safe default instead of crashing."""),
        ("code", '''import json, re

def classify_local(message):
    prompt = ('Reply with ONLY a JSON object with keys "category" (string), "urgency" (integer 1-5) '
              f'and "summary" (string) for this customer message: {message}')
    raw = local_chat("You output JSON only.", [{"role": "user", "content": prompt}], max_new_tokens=60)["text"]
    print("raw model output:", repr(raw[:150]))
    try:
        match = re.search(r"\\{.*\\}", raw, re.S)              # grab the first {...} block, if any
        return Ticket(**json.loads(match.group(0))), "parsed"
    except (AttributeError, json.JSONDecodeError, ValidationError, TypeError) as e:
        print("validation failed:", type(e).__name__)
        return Ticket(category="other", urgency=3, summary=message[:60]), "safe default"

ticket, how = classify_local(MESSAGE)
print(how, "->", ticket)'''),
        ("md", """## 11. Errors, status codes and retries

Real calls fail sometimes. We can trigger a **real** SDK error safely, with no key and no internet: point each client at a closed port on this computer (`127.0.0.1:9`). The SDK builds a genuine request, fails to connect, retries according to its settings, and raises its typed exception. This also proves our call syntax is accepted by the installed SDKs."""),
        ("code", '''import time
BAD = "http://127.0.0.1:9"     # nothing listens here -> connection refused, instantly

t0 = time.time()
try:
    OpenAI(api_key="not-a-real-key", base_url=BAD + "/v1", max_retries=2).responses.create(
        model=OPENAI_MODEL, instructions=SYSTEM, input=QUESTION, max_output_tokens=50)
except openai.APIConnectionError as e:
    print(f"OpenAI    -> {type(e).__name__} after {time.time()-t0:.1f}s (includes 2 automatic retries)")

try:
    Anthropic(api_key="not-a-real-key", base_url=BAD, max_retries=0).messages.create(
        model=ANTHROPIC_MODEL, max_tokens=50, system=SYSTEM, messages=QUESTION)
except anthropic.APIConnectionError as e:
    print("Anthropic ->", type(e).__name__)

try:
    gclient = genai.Client(api_key="not-a-real-key", http_options=types.HttpOptions(
        base_url=BAD, retry_options=types.HttpRetryOptions(attempts=1)))
    gclient.models.generate_content(model=GEMINI_MODEL, contents="hi")
except Exception as e:
    print("Gemini    ->", type(e).__name__)'''),
        ("md", """The pattern for real code: catch the **most specific** errors first. Only temporary errors (429 rate limit, 5xx server errors, 529 overloaded, connection problems) are worth retrying; 400/401/403/404 mean "fix your request or key".

| Exception (OpenAI / Anthropic) | HTTP code | Retry? |
|---|---|---|
| `BadRequestError` | 400 | no |
| `AuthenticationError` | 401 | no |
| `PermissionDeniedError` | 403 | no |
| `NotFoundError` | 404 (often a wrong model name) | no |
| `RateLimitError` | 429 | yes, after waiting |
| `InternalServerError` | 5xx | yes |
| `APIConnectionError` / `APITimeoutError` | none | yes |

Here is a safe wrapper that tries a provider and falls back to the local model on any API failure:"""),
        ("code", '''def safe_ask(provider_fn, system, messages):
    try:
        return provider_fn(system, messages)
    except (openai.RateLimitError, anthropic.RateLimitError):
        print("Rate limited: slow down, then retry later. Using fallback for now.")
    except (openai.AuthenticationError, anthropic.AuthenticationError):
        print("Bad API key: check your .env file. Using fallback.")
    except (openai.APIStatusError, anthropic.APIStatusError) as e:
        print(f"HTTP error {e.status_code}: {e.message}. Using fallback.")
    except (openai.APIConnectionError, anthropic.APIConnectionError):
        print("Network problem. Using fallback.")
    return local_chat(system, messages)

print(safe_ask(ask_anthropic, SYSTEM, QUESTION)["source"])'''),
        ("md", """### Exponential backoff

The OpenAI and Anthropic SDKs already retry temporary errors (2 times by default; set `max_retries=` on the client). When you need your own loop — for logging, or to switch models — use **exponential backoff with jitter**: wait 1s, 2s, 4s ... plus a little randomness. Below, a fake API fails 60% of the time so you can watch it work (waits are shortened for the demo)."""),
        ("code", '''import random
random.seed(1)

class TemporaryError(Exception): pass

def flaky_api(prompt):
    if random.random() < 0.6:
        raise TemporaryError("429 rate limit (simulated)")
    return f"answer to {prompt!r}"

def with_backoff(fn, *args, attempts=5, base=0.1):
    for i in range(attempts):
        try:
            return fn(*args)
        except TemporaryError as e:
            if i == attempts - 1:
                raise
            wait = base * 2 ** i + random.uniform(0, base)
            print(f"  attempt {i+1} failed ({e}); retrying in {wait:.2f}s")
            time.sleep(wait)

print(with_backoff(flaky_api, "What is top-p?"))'''),
        ("md", """## Try it yourself
1. Add a fourth helper `ask_local` and include it in the comparison table.
2. Change `SYSTEM` to make the tutor answer like a pirate. Does the fallback model follow it?
3. Add a `language: str` field to `Ticket`. Update `classify_local` and check validation.
4. If you have a free Gemini key, put it in `.env` and rerun the notebook. Which cells change?"""),
    ], NB / "02-calling-llm-apis.ipynb")

    # ---------------- Notebook 03: tokens, cost, local models ----------------
    notebook([
        ("md", """# 03 - Tokens, cost, local models (Ollama) and choosing a model

**Goal:** count tokens with `tiktoken`, estimate the cost of an LLM feature, read the module's Excel cost calculator, understand how **Ollama** runs models locally (with an offline fallback when Ollama isn't installed), and pick a model with a simple decision guide.

**About prices:** prices change often, so this notebook uses **made-up example prices** that are clearly labelled. For real numbers, use the official pricing pages:
- OpenAI: https://openai.com/api/pricing/
- Anthropic: https://platform.claude.com/docs/en/about-claude/pricing
- Google Gemini: https://ai.google.dev/gemini-api/docs/pricing"""),
        ("md", "## Setup"),
        ("code", INSTALL_BASE + '''for pkg, mod in [("tiktoken", "tiktoken"), ("openpyxl", "openpyxl"), ("httpx", "httpx"), ("transformers", "transformers")]:
    ensure(pkg, mod)
import tiktoken, numpy as np, pandas as pd, matplotlib.pyplot as plt
enc = tiktoken.get_encoding("o200k_base")
pd.set_option("display.max_colwidth", 120)   # show long text in tables without cutting it off
print("ready")'''),
        ("md", """## 1. Counting tokens

`tiktoken` is exact for recent OpenAI models and a reasonable estimate for others (Anthropic and Gemini have their own tokenizers and `count_tokens` API calls, which need a key). A chat adds a few extra tokens per message for the role markers."""),
        ("code", '''def count(text):
    return len(enc.encode(text))

def count_messages(messages, overhead=4):
    return sum(count(m["content"]) + overhead for m in messages)

system = "You are a helpful support agent for an online bakery in Hyderabad. Answer in under 80 words."
user = "Hi, my cake order #5512 was supposed to arrive at 4pm but it's 6pm now. Can you check?"
msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
print("system:", count(system), "tokens | user:", count(user), "tokens | whole request ~", count_messages(msgs))'''),
        ("md", "Rule-of-thumb check: about 4 characters per token for English. Let's compare the rule with the real count on a few texts."),
        ("code", '''texts = {
    "short English": "Please summarise this article in three bullet points.",
    "Python code": "def add(a, b):\\n    return a + b\\n\\nprint(add(2, 3))",
    "JSON": '{"order_id": 5512, "status": "out_for_delivery", "eta_minutes": 25}',
    "Hindi": "कृपया इस लेख का तीन बिंदुओं में सारांश दें।",
}
pd.DataFrame([{"text": k, "chars": len(v), "rule_of_thumb (chars/4)": round(len(v) / 4), "real tokens": count(v)}
              for k, v in texts.items()])'''),
        ("md", """## 2. Estimating cost

Cost of one call = input tokens × input price + output tokens × output price (prices are per **1 million** tokens). The prices below are **invented for practice only**."""),
        ("code", '''# !!! EXAMPLE PRICES - MADE UP FOR PRACTICE, NOT REAL. Fill in real ones from the official pages. !!!
EXAMPLE_PRICES = {               # (input $ per 1M tokens, output $ per 1M tokens)
    "example-small-model":  (0.20, 0.80),
    "example-medium-model": (1.00, 5.00),
    "example-large-model":  (5.00, 25.00),
}

def cost_per_request(n_in, n_out, prices):
    p_in, p_out = prices
    return n_in * p_in / 1e6 + n_out * p_out / 1e6

n_in, n_out = count_messages(msgs), 150
for name, prices in EXAMPLE_PRICES.items():
    one = cost_per_request(n_in, n_out, prices)
    print(f"{name:<22} per request ${one:.6f} | 1,000 req/day for 30 days: ${one * 1000 * 30:,.2f}")'''),
        ("md", "Plot monthly cost against traffic. Notice how the model choice matters more than almost anything else once traffic grows. Output tokens usually dominate because they cost more."),
        ("code", '''traffic = np.array([100, 500, 1000, 5000, 10000, 50000])
plt.figure(figsize=(8, 4))
for name, prices in EXAMPLE_PRICES.items():
    plt.plot(traffic, traffic * 30 * cost_per_request(n_in, n_out, prices), marker="o", label=name)
plt.xscale("log"); plt.yscale("log")
plt.xlabel("requests per day"); plt.ylabel("$ per month (EXAMPLE prices)")
plt.title("Monthly cost vs traffic (made-up example prices)"); plt.legend(); plt.grid(alpha=0.3)
plt.tight_layout(); plt.show()'''),
        ("md", """## 3. The Excel cost calculator

`excel/07-llm-cost-calculator.xlsx` does the same with **live formulas**. Yellow cells are inputs; prices are blank until you fill them in from the official pricing pages. We open it with `openpyxl` to look at the formulas. (If the file is not next to this notebook — e.g. on Colab — it is downloaded from the course repo.)"""),
        ("code", '''import pathlib, httpx, openpyxl
path = pathlib.Path("../excel/07-llm-cost-calculator.xlsx")
if not path.exists():
    url = "https://raw.githubusercontent.com/vvvvvivekkk/AI-Engineer/main/07-llms-and-genai/excel/07-llm-cost-calculator.xlsx"
    try:
        path = pathlib.Path("07-llm-cost-calculator.xlsx")
        path.write_bytes(httpx.get(url, timeout=30, follow_redirects=True).raise_for_status().content)
    except Exception as e:
        print("Could not download the workbook:", e); path = None
if path:
    wb = openpyxl.load_workbook(path)
    print("Sheets:", wb.sheetnames)
    ws = wb["Calculator"]
    for cell in ws[1]:
        print(f"{cell.column_letter}1 {cell.value!r:<32} row 2 -> {ws.cell(row=2, column=cell.column).value!r}")'''),
        ("md", """## 4. Log real usage

After every real API call, record the **usage** numbers the provider returns (they are what you are billed for). A tiny log like the one below — appended to a CSV in a real app — lets you check the estimate against reality. Here the records are simulated."""),
        ("code", '''log = pd.DataFrame([
    {"time": "09:00", "model": "example-small-model", "input_tokens": 61, "output_tokens": 120},
    {"time": "09:01", "model": "example-small-model", "input_tokens": 64, "output_tokens": 98},
    {"time": "09:03", "model": "example-medium-model", "input_tokens": 950, "output_tokens": 410},
])
log["cost_$"] = [cost_per_request(r.input_tokens, r.output_tokens, EXAMPLE_PRICES[r.model]) for r in log.itertuples()]
print(log)
print("Total (example prices): $", round(log["cost_$"].sum(), 6))'''),
        ("md", """## 5. Local models with Ollama

**Ollama** runs open-weight models on your own computer and serves them at `http://localhost:11434`. It cannot be installed on the course server, so this cell **checks** whether an Ollama server is reachable. If yes, it calls the REST API; if not, it falls back to SmolLM2 through `transformers` — same idea, different engine.

On your own laptop: install from https://ollama.com, run `ollama pull llama3.2:1b`, and re-run this cell. Full scripts: `code/ollama_rest.py`, `code/ollama_client.py`, `code/ollama_commands.sh`."""),
        ("code", '''import os
OLLAMA = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
messages = [{"role": "system", "content": "Answer in one sentence."},
            {"role": "user", "content": "What is quantisation in LLMs?"}]

def ollama_available():
    try:
        return httpx.get(OLLAMA, timeout=2).status_code == 200
    except httpx.HTTPError:
        return False

if ollama_available():
    r = httpx.post(f"{OLLAMA}/api/chat", json={"model": OLLAMA_MODEL, "messages": messages, "stream": False}, timeout=300)
    print("[Ollama]", r.json()["message"]["content"])
else:
    print("Ollama not reachable here -> offline fallback with transformers (SmolLM2-135M)")
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tok = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-135M-Instruct")
    model = AutoModelForCausalLM.from_pretrained("HuggingFaceTB/SmolLM2-135M-Instruct", dtype=torch.float32)
    inputs = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=50, do_sample=False)
    print("[fallback]", tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))'''),
        ("md", """The same Ollama server through three different doors (shown, not run here):

```python
# 1) official Python client:  pip install ollama
import ollama
resp = ollama.chat(model="llama3.2:1b", messages=messages)
print(resp.message.content)

# 2) OpenAI SDK pointed at Ollama's OpenAI-compatible endpoint
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")   # key is ignored but required
print(client.chat.completions.create(model="llama3.2:1b", messages=messages).choices[0].message.content)

# 3) terminal:  ollama run llama3.2:1b "What is quantisation?"
```

**How much memory does a local model need?** Roughly: parameters × bits per parameter ÷ 8, plus some overhead for the context. Let's compute it."""),
        ("code", '''def approx_memory_gb(params_billion, bits=4, overhead=1.2):
    return params_billion * 1e9 * bits / 8 / 1e9 * overhead

for size in [0.135, 1, 3, 8, 70]:
    print(f"{size:>6}B params: 16-bit ~{approx_memory_gb(size, 16):6.1f} GB | 4-bit ~{approx_memory_gb(size, 4):5.1f} GB")'''),
        ("md", """## 6. Choosing a model

A tiny decision helper that encodes the guide from `concepts.md`. It is deliberately simple; real decisions come from testing on your own examples."""),
        ("code", '''def recommend(private_data, difficulty, input_tokens, monthly_budget_usd):
    if private_data:
        return "Open-weight model run locally (Ollama) or on your own server"
    if input_tokens > 100_000:
        return "A model with a very large context window - check provider model pages; or use RAG (Module 09)"
    if difficulty == "simple":
        return "Smallest/cheapest tier of a major provider; test it first"
    if monthly_budget_usd < 20:
        return "Free tier (e.g. Gemini) or local model; upgrade only if quality fails"
    return "Provider's top tier for hard tasks; measure cost with the calculator"

scenarios = [
    ("Hospital notes summariser", True, "hard", 3000, 500),
    ("Tag 50k support tickets / day", False, "simple", 300, 300),
    ("Analyse a 400-page contract", False, "hard", 250_000, 1000),
    ("Student homework helper prototype", False, "hard", 1000, 0),
    ("Coding assistant for a team", False, "hard", 8000, 2000),
]
pd.DataFrame([{"scenario": s, "recommendation": recommend(*args)} for s, *args in scenarios])'''),
        ("md", """## Try it yourself
1. Open the Excel calculator, fill in today's real prices for two models from the official pages, and compare with the Python numbers.
2. Change `n_out` from 150 to 600. By how much does monthly cost grow for each example model?
3. Add a "needs image input" option to `recommend()`.
4. On your own computer, install Ollama and run `code/ollama_rest.py`. Compare speed with SmolLM2."""),
    ], NB / "03-tokens-cost-and-local-models.ipynb")


# ---------------------------------------------------------------------------
# 3. Slides
# ---------------------------------------------------------------------------
def build_slides():
    deck = {
        "title": "Module 07 - LLMs and Generative AI",
        "subtitle": "How LLMs work, how to call them, what they cost, how to run them locally",
        "slides": [
            {"title": "What we will cover",
             "bullets": ["What an LLM really does: next-token prediction", "Temperature, top-p and the context window",
                         "Pre-training, instruction tuning, RLHF", "OpenAI, Anthropic and Gemini APIs from Python",
                         "Tokens, cost, Ollama, choosing a model"],
             "notes": "Tell students: by the end you will have called three different AI providers from Python, estimated what a feature costs per month, and seen how to run a model on your own laptop. Everything runs even without API keys."},
            {"title": "An LLM is autocomplete at scale",
             "bullets": ["Trained to predict the next token", "Billions of parameters, trillions of training tokens",
                         "Learns grammar, facts, style as a side effect", "Produces likely text, not checked facts -> hallucinations",
                         "No memory between calls; has a training cutoff"],
             "notes": "Use the phone keyboard analogy. Ask: if it only predicts likely words, why can it answer questions? Because predicting well requires knowing a lot. Stress hallucination: fluent and confident is not the same as correct."},
            {"title": "Next-token probabilities", "image": str(IMG / "next-token-probs.png"),
             "bullets": ["Logits -> softmax -> probabilities", "' Paris' 47%, ' the' 27% ...", "Ranking continuations, not looking up facts"],
             "notes": "These are real numbers from SmolLM2-135M in notebook 01. Point out that ' the' is also a reasonable continuation. Run the notebook cell live if possible."},
            {"title": "The generation loop", "image": str(IMG / "generation-loop.png"),
             "bullets": ["Predict, pick, append, repeat", "Stops at end token or max_tokens", "Why answers stream word by word", "Why long answers cost more"],
             "notes": "Autoregressive means each token depends on the previous ones. Walk around the loop once with 'The capital of France is' -> ' Paris' -> '.'."},
            {"title": "Temperature and top-p", "image": str(IMG / "sampling-temperature.png"),
             "bullets": ["Low temperature: focused, repeatable", "High temperature: creative, risky", "Top-p: keep tokens covering p of probability", "Usually tune one, not both"],
             "notes": "Cautious diner versus adventurous diner. Low temperature always orders the favourite. Top-p cuts the long tail of unlikely tokens. Mention that some newer models fix these settings; check docs."},
            {"title": "The context window",
             "bullets": ["Max tokens for input + output in one request", "Whole chat history is re-sent each turn", "Too long -> trim, summarise, or retrieve (RAG)", "Every input token is paid for, every time"],
             "notes": "Desk analogy: only papers on the desk can be used, and you pay per page. Show notebook 01 section 6 where the conversation overflows a 1,024-token window."},
            {"title": "How LLMs are trained", "image": str(IMG / "training-stages.png"),
             "bullets": ["Pre-training: read the library -> base model", "SFT: worked examples -> instruct model", "RLHF / DPO: coach picks better answers"],
             "notes": "Library, teacher, coach. A base model continues text; ask it a question and it may write more questions. Instruction tuning teaches the chat format. Preference tuning teaches which answers people prefer."},
            {"title": "Calling an API", "image": str(IMG / "api-call-flow.png"),
             "bullets": ["SDK = official Python library", "API key from env var / .env, never in code", "Response = text + usage (tokens billed)"],
             "notes": "Draw the round trip. Emphasise key safety: bots scan GitHub for keys within minutes. Show .env.example and .gitignore."},
            {"title": "Messages and roles",
             "bullets": ["system: rules for the assistant", "user: the person", "assistant: earlier model replies (Gemini: 'model')", "No memory: send the whole history every time"],
             "code": "messages = [\n {'role': 'user', 'content': 'My name is Asha.'},\n {'role': 'assistant', 'content': 'Hi Asha!'},\n {'role': 'user', 'content': 'What is my name?'},\n]",
             "notes": "Pen pal with amnesia: each letter must recap everything. Show notebook 02 section 8 where the model only knows the name when history is included."},
            {"title": "Three SDKs, one shape",
             "bullets": ["OpenAI: responses.create(instructions=, input=)", "Anthropic: messages.create(system=, messages=, max_tokens=)", "Gemini: models.generate_content(contents=, config=)", "Model names change: read them from .env"],
             "code": "from anthropic import Anthropic\nclient = Anthropic()\nmsg = client.messages.create(\n  model=ANTHROPIC_MODEL, max_tokens=200,\n  system='You are a concise tutor.',\n  messages=[{'role':'user','content':'Hi'}])\nprint(msg.content[0].text)",
             "notes": "The differences are mostly where the system prompt goes and what the response object looks like. Show the comparison table in notebook 02 section 7."},
            {"title": "Streaming and JSON output",
             "bullets": ["Streaming: show text as it arrives (feels fast)", "Structured output: answer in a fixed JSON schema", "Describe the schema with Pydantic", "Always validate; have a fallback"],
             "notes": "Show the local streaming demo. Then the Ticket example: the tiny local model often breaks the JSON, which is exactly why validation and a safe default matter."},
            {"title": "Errors and retries", "image": str(IMG / "retry-backoff.png"),
             "bullets": ["400/401/403/404: fix the request, don't retry", "429, 5xx, 529, timeouts: retry with backoff", "SDKs retry twice by default (max_retries)", "Catch specific exceptions first"],
             "notes": "Exponential backoff: wait 1, 2, 4, 8 seconds plus jitter. Show notebook 02 section 11: we trigger real SDK connection errors by pointing at a closed local port, no key needed."},
            {"title": "Tokens and cost",
             "bullets": ["Price per 1M tokens, input and output priced separately", "cost = in x price_in + out x price_out", "tiktoken to estimate; usage field for truth", "Prices change: never hard-code, link the official page"],
             "notes": "Open the Excel calculator. Fill in today's prices together from the official pages (links are in the Prices sheet). Show how monthly cost scales with traffic and output length."},
            {"title": "Local models with Ollama", "image": str(IMG / "ollama-flow.png"),
             "bullets": ["Open-weight models on your own machine", "ollama pull / run / list", "REST API on localhost:11434", "Python client and OpenAI-compatible /v1"],
             "notes": "Benefits: free per token, private, offline. Costs: smaller models, needs RAM. If you have Ollama on your laptop, demo 'ollama run llama3.2:1b' live. Otherwise show code/ollama_rest.py."},
            {"title": "Choosing a model", "image": str(IMG / "model-choice.png"),
             "bullets": ["Privacy first, then difficulty", "Context length, latency, budget", "Start small; move up only if tests fail", "Re-check every few months"],
             "notes": "There is no best model, only the best for a task and budget. Leaderboards are hints; your own 20-50 test examples decide."},
            {"title": "Common mistakes",
             "bullets": ["API key pasted in a notebook or pushed to GitHub", "Expecting the model to remember earlier calls", "Retrying 401/400 errors forever", "Trusting JSON without validation", "Ignoring output tokens when estimating cost"],
             "notes": "Ask who has seen each one. The key leak is the most expensive mistake: rotate the key immediately if it happens."},
            {"title": "Recap and exercises",
             "bullets": ["LLM = next-token predictor + sampling", "Context window, temperature, top-p", "Same request shape across three SDKs", "Estimate cost; validate output; retry wisely", "Exercises 1-4 in class, 5-10 at home"],
             "notes": "Quick quiz: what does temperature do? Where does the system prompt go in each SDK? Which errors should be retried? Then hand out exercises.md."},
        ],
    }
    slides(deck, HERE / "slides" / f"{MOD}.pptx")


# ---------------------------------------------------------------------------
# 4. Excel cost calculator (live formulas, prices are inputs)
# ---------------------------------------------------------------------------
def build_excel():
    out = HERE / "excel" / "07-llm-cost-calculator.xlsx"
    fill = "fill in from official pricing page"
    prices = [["Label (used by Calculator)", "Provider", "Model name (type exact name)", "Input $ per 1M tokens",
               "Output $ per 1M tokens", "Official pricing page", "Date you checked", "Status"],
              ["EXAMPLE-ONLY", "Example (made-up numbers, NOT real prices)", "example-model", 1.00, 4.00,
               "(shows the format only)", "", ""],
              ["OpenAI-small", "OpenAI", fill, None, None, PRICING["OpenAI"], "", ""],
              ["OpenAI-large", "OpenAI", fill, None, None, PRICING["OpenAI"], "", ""],
              ["Anthropic-small", "Anthropic", fill, None, None, PRICING["Anthropic"], "", ""],
              ["Anthropic-large", "Anthropic", fill, None, None, PRICING["Anthropic"], "", ""],
              ["Gemini-small", "Google Gemini", fill, None, None, PRICING["Google Gemini"], "", ""],
              ["Gemini-large", "Google Gemini", fill, None, None, PRICING["Google Gemini"], "", ""],
              ["Local-Ollama", "Your own computer (Ollama)", "e.g. llama3.2:1b", 0, 0,
               "https://ollama.com", "", ""]]
    for r in range(2, len(prices) + 1):
        prices[r - 1][7] = f'=IF(OR(D{r}="",E{r}=""),"{fill}","ok")'

    calc = [["Scenario", "Model label (from Prices)", "Requests per day", "Avg input tokens", "Avg output tokens",
             "Days per month", "Input $ per 1M", "Output $ per 1M", "Cost per request $", "Cost per day $",
             "Cost per month $", "Cost per year $"]]
    scen = [("Support chatbot", "EXAMPLE-ONLY", 1000, 600, 200, 30),
            ("Document summariser", "Anthropic-small", 200, 4000, 400, 22),
            ("Ticket tagging batch", "Gemini-small", 20000, 300, 20, 30),
            ("Coding assistant", "OpenAI-large", 300, 8000, 1000, 22),
            ("Private notes bot", "Local-Ollama", 500, 1500, 300, 30)]
    for i, (name, label, rpd, tin, tout, days) in enumerate(scen, start=2):
        calc.append([name, label, rpd, tin, tout, days,
                     f"=IFERROR(VLOOKUP(B{i},Prices!$A$2:$E$30,4,FALSE),0)",
                     f"=IFERROR(VLOOKUP(B{i},Prices!$A$2:$E$30,5,FALSE),0)",
                     f"=(D{i}*G{i}+E{i}*H{i})/1000000",
                     f"=I{i}*C{i}", f"=J{i}*F{i}", f"=K{i}*12"])
    n = len(calc)
    calc.append(["TOTAL", "", "", "", "", "", "", "", "", f"=SUM(J2:J{n})", f"=SUM(K2:K{n})", f"=SUM(L2:L{n})"])

    compare = [["Model label", "Monthly cost $ for the Calculator's row-2 scenario", "Status of prices"]]
    for r in range(2, len(prices) + 1):
        compare.append([f"=Prices!A{r}",
                        f"=Calculator!$C$2*Calculator!$F$2*(Calculator!$D$2*N(Prices!D{r})+Calculator!$E$2*N(Prices!E{r}))/1000000",
                        f"=Prices!H{r}"])

    est = [["Paste a sample text", "Characters", "Estimated tokens (chars / 4)", "Estimated words (tokens x 0.75)"],
           ["Hi, my cake order #5512 was supposed to arrive at 4pm but it's 6pm now. Can you check?",
            "=LEN(A2)", "=ROUND(B2/4,0)", "=ROUND(C2*0.75,0)"],
           ["You are a helpful support agent for an online bakery in Hyderabad. Answer in under 80 words.",
            "=LEN(A3)", "=ROUND(B3/4,0)", "=ROUND(C3*0.75,0)"],
           ["", "=LEN(A4)", "=ROUND(B4/4,0)", "=ROUND(C4*0.75,0)"]]

    howto = [["Step", "What to do"],
             [1, "Open the 'Prices' sheet. For each provider, open the official pricing page (link in column F)."],
             [2, "Type the exact model name in column C and its input and output prices per 1 million tokens in columns D and E (yellow cells). Write today's date in column G."],
             [3, "Prices are blank on purpose: they change often and must come from the official page. Column H says 'ok' once both prices are filled."],
             [4, "The EXAMPLE-ONLY row uses made-up numbers to show the format. Do not use it for real decisions."],
             [5, "Open 'Calculator'. Change the yellow cells: model label (dropdown), requests per day, average input/output tokens, days per month."],
             [6, "Every other cell is a live formula: cost per request = (input tokens x input price + output tokens x output price) / 1,000,000."],
             [7, "'Compare models' shows the row-2 scenario priced with every model in the Prices sheet."],
             [8, "'Token estimator' gives a rough token count from characters (about 4 characters per token in English). For exact counts use tiktoken (notebook 03)."],
             [9, "Local models (Ollama) have no per-token price, but you pay for hardware and electricity."]]

    workbook({"How to use": howto, "Prices": prices, "Calculator": calc, "Compare models": compare,
              "Token estimator": est}, out,
             col_widths={"How to use": [8, 110], "Prices": [18, 30, 34, 14, 14, 52, 14, 32],
                         "Calculator": [22, 22, 12, 12, 12, 10, 12, 12, 14, 12, 14, 14],
                         "Compare models": [20, 44, 32], "Token estimator": [70, 12, 18, 20]})

    # Post-process: yellow input cells, number formats, dropdown, notes
    from openpyxl import load_workbook
    from openpyxl.styles import PatternFill, Font
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.comments import Comment
    wb = load_workbook(out)
    yellow = PatternFill("solid", fgColor="FFF2CC")
    ws = wb["Prices"]
    for r in range(2, len(prices) + 1):
        for col in "CDEG":
            ws[f"{col}{r}"].fill = yellow
        for col in "DE":
            ws[f"{col}{r}"].number_format = '"$"#,##0.000'
    ws["D1"].comment = Comment("Fill in from the provider's official pricing page (column F). Prices change often.", "course")
    ws["E1"].comment = Comment("Fill in from the provider's official pricing page (column F). Output usually costs more than input.", "course")
    ws.cell(row=len(prices) + 2, column=1, value="Yellow cells are inputs. Blank prices count as 0 in the Calculator until you fill them in.").font = Font(italic=True)

    ws = wb["Calculator"]
    dv = DataValidation(type="list", formula1=f"=Prices!$A$2:$A${len(prices)}", allow_blank=False)
    ws.add_data_validation(dv)
    for r in range(2, len(scen) + 2):
        dv.add(f"B{r}")
        for col in "BCDEF":
            ws[f"{col}{r}"].fill = yellow
        for col in "GH":
            ws[f"{col}{r}"].number_format = '"$"#,##0.000'
        ws[f"I{r}"].number_format = '"$"#,##0.000000'
        for col in "JKL":
            ws[f"{col}{r}"].number_format = '"$"#,##0.00'
    for col in "JKL":
        ws[f"{col}{len(scen) + 2}"].number_format = '"$"#,##0.00'
        ws[f"{col}{len(scen) + 2}"].font = Font(bold=True)
    ws.cell(row=len(scen) + 4, column=1, value="Yellow cells are inputs. Rows using a model whose prices are blank show $0 until you fill in the Prices sheet.").font = Font(italic=True)

    ws = wb["Compare models"]
    for r in range(2, len(prices) + 1):
        ws[f"B{r}"].number_format = '"$"#,##0.00'
    ws = wb["Token estimator"]
    for r in range(2, 5):
        ws[f"A{r}"].fill = yellow
    wb.save(out)


if __name__ == "__main__":
    build_diagrams()
    build_plots()
    build_notebooks()
    build_slides()
    build_excel()
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / f"{MOD}-handout.pdf", title="Module 07 - LLMs and Generative AI")
    print("Module 07 built.")
