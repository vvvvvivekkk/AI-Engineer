import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook

"""
build.py for Module 06 - NLP and Transformers.
Regenerates: images/ (Mermaid + matplotlib), notebooks/, slides/, pdf/, excel/.
Run from the repo root:  python 06-nlp-and-transformers/build.py
"""
import numpy as np

IMG = HERE / "images"
NB = HERE / "notebooks"
MOD = "06-nlp-and-transformers"

# Small helper cell reused by every notebook: installs packages only if they are missing (e.g. on Colab).
INSTALL = '''import importlib.util, subprocess, sys
# Install a package only if it is missing (Colab already has most of these).
for pkg, mod in [("transformers", "transformers"), ("sentence-transformers", "sentence_transformers"),
                 ("tiktoken", "tiktoken"), ("torch", "torch")]:
    if importlib.util.find_spec(mod) is None:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg], check=True)
print("Packages ready")'''


# ---------------------------------------------------------------------------
# 1. Diagrams
# ---------------------------------------------------------------------------
def build_diagrams():
    mermaid("""
flowchart LR
    A["Raw text<br/>'I love NLP'"] --> B["Tokens<br/>I | ' love' | ' N' | LP"]
    B --> C["Token IDs<br/>40, 3021, 452, 12852"]
    C --> D["Embeddings<br/>one vector per token"]
    D --> E["Transformer<br/>layers"]
    E --> F["Output<br/>label / vector / next token"]
""", IMG / "nlp-pipeline.png")

    mermaid("""
flowchart TD
    S["'unbelievably fast'"] --> T["Tokenizer: tiktoken cl100k_base<br/>(learned vocab of sub-words)"]
    T --> P1["un"]
    T --> P2["belie"]
    T --> P3["vably"]
    T --> P4["' fast'"]
    P1 --> I["IDs: 359, 32898, 89234, 5043"]
    P2 --> I
    P3 --> I
    P4 --> I
""", IMG / "tokenization.png")

    mermaid("""
flowchart LR
    subgraph RNN["RNN: one step at a time"]
        direction LR
        r1["the"] --> r2["cat"] --> r3["sat"] --> r4["down"]
    end
    subgraph ATT["Attention: everyone sees everyone"]
        direction LR
        a1["the"] <--> a2["cat"]
        a2 <--> a3["sat"]
        a1 <--> a3
        a3 <--> a4["down"]
        a2 <--> a4
    end
""", IMG / "rnn-vs-attention.png")

    mermaid("""
flowchart TD
    IN["Token embeddings<br/>+ positional encoding"] --> LN1["Layer norm"]
    LN1 --> ATT["Multi-head<br/>self-attention"]
    ATT --> ADD1(("+ residual"))
    IN --> ADD1
    ADD1 --> LN2["Layer norm"]
    LN2 --> FFN["Feed-forward<br/>network"]
    FFN --> ADD2(("+ residual"))
    ADD1 --> ADD2
    ADD2 --> OUT["To next block<br/>(repeat N times)"]
""", IMG / "transformer-block.png")

    mermaid("""
flowchart LR
    L1["Level 1: pipeline()<br/>one line, everything automatic"] --> L2["Level 2: AutoTokenizer + AutoModel<br/>see IDs, logits, probabilities"]
    L2 --> L3["Level 3: raw tensors<br/>hidden states, attention weights"]
    HUB[("Hugging Face Hub<br/>models + model cards")] -.downloads.-> L1
    HUB -.downloads.-> L2
""", IMG / "hf-levels.png")


def build_plots():
    """Matplotlib figures: the attention heatmap (pure NumPy) and the embedding similarity grid."""
    import importlib.util
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    spec = importlib.util.spec_from_file_location("att", HERE / "code" / "attention_numpy.py")
    att = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(att)
    w, _ = att.self_attention(att.X)
    att.plot_heatmap(w, "Self-attention: 'the cat sat'", IMG / "attention-heatmap.png")

    from sentence_transformers import SentenceTransformer
    sents = ["How do I reset my password?", "I forgot my login details.",
             "The cat is sleeping on the sofa.", "A kitten naps on the couch.",
             "What is the price of the premium plan?", "How much does the subscription cost?"]
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    v = model.encode(sents, normalize_embeddings=True)
    sim = v @ v.T
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(sim, cmap="viridis", vmin=-0.1, vmax=1)
    short = [s if len(s) < 30 else s[:28] + ".." for s in sents]
    ax.set_xticks(range(6), labels=short, rotation=40, ha="right")
    ax.set_yticks(range(6), labels=short)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f"{sim[i, j]:.2f}", ha="center", va="center",
                    color="black" if sim[i, j] > 0.6 else "white", fontsize=9)
    ax.set_title("Cosine similarity of sentence embeddings (all-MiniLM-L6-v2)")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(IMG / "embedding-similarity.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Notebooks
# ---------------------------------------------------------------------------
def build_notebooks():
    # ---------------- Notebook 01 ----------------
    notebook([
        ("md", """# 01 - Tokens and embeddings

**Goal:** see exactly how real models cut text into **tokens** (small pieces of text), turn them into **token IDs** (numbers), and how **embeddings** (lists of numbers that carry meaning) let us compare sentences.

Runs on a normal CPU in a couple of minutes. No API keys needed. The first run downloads a few small files from the Hugging Face Hub."""),
        ("md", "## Setup\nThis cell installs any missing package. On Colab and in the course environment everything is usually already there, so it finishes instantly."),
        ("code", INSTALL),
        ("md", """## 1. A tokenizer from Hugging Face

`AutoTokenizer.from_pretrained(name)` downloads the tokenizer that belongs to a model. We start with GPT-2's tokenizer, which uses **BPE (Byte-Pair Encoding)** — a recipe that builds a vocabulary of common sub-word pieces.

- `tokenize(text)` shows the text pieces.
- `tok(text)["input_ids"]` shows the numbers the model really receives."""),
        ("code", '''from transformers import AutoTokenizer

text = "Tokenization isn't magic: unbelievably, ChatGPT reads tokens!"
gpt2_tok = AutoTokenizer.from_pretrained("gpt2")      # downloads once, then cached
print("Tokens:", gpt2_tok.tokenize(text))
print("IDs:   ", gpt2_tok(text)["input_ids"])
print("Vocabulary size:", gpt2_tok.vocab_size)'''),
        ("md", """**What to notice:** `Ġ` is GPT-2's way of drawing "a space comes before this token". The space belongs to the token. Common words (`magic`, `reads`) are one token; `Tokenization` is two.

## 2. Compare tokenizers

Different models use different vocabularies. BERT uses **WordPiece** (pieces glued to the previous one start with `##`) and lower-cases everything. SmolLM2 uses its own BPE vocab."""),
        ("code", '''for name in ["bert-base-uncased", "gpt2", "HuggingFaceTB/SmolLM2-135M-Instruct"]:
    tok = AutoTokenizer.from_pretrained(name)
    pieces = tok.tokenize(text)
    print(f"{name:<40} {len(pieces):>2} tokens: {pieces}")'''),
        ("md", """## 3. tiktoken — OpenAI's tokenizer

**tiktoken** is a fast tokenizer library from OpenAI. An **encoding** is one vocabulary plus its merge rules. `cl100k_base` (about 100k tokens) and `o200k_base` (about 200k tokens) are two of them. Bigger vocabularies usually need fewer tokens for the same text."""),
        ("code", '''import tiktoken

for enc_name in ["cl100k_base", "o200k_base"]:
    enc = tiktoken.get_encoding(enc_name)
    ids = enc.encode(text)
    print(f"{enc_name}: {len(ids)} tokens")
    print("   pieces:", [enc.decode([i]) for i in ids])
    print("   decode(encode(text)) == text ->", enc.decode(ids) == text)'''),
        ("md", """## 4. Tokens per word in different kinds of text

Pricing and limits are counted in **tokens**, not words. Let's measure how many tokens different texts need. Code, numbers and non-English text often need more tokens per word."""),
        ("code", '''enc = tiktoken.get_encoding("o200k_base")
samples = {
    "plain English": "The weather in Hyderabad is warm and sunny today.",
    "Python code":   "for i in range(10): print(i ** 2)",
    "long number":   "Order 8473629104 costs 12345.67 rupees",
    "Hindi":         "आज हैदराबाद में मौसम गर्म और धूप वाला है।",
    "rare words":    "Pneumonoultramicroscopicsilicovolcanoconiosis is a word.",
}
for label, s in samples.items():
    n_tok, n_words = len(enc.encode(s)), len(s.split())
    print(f"{label:<14} words={n_words:>2}  tokens={n_tok:>2}  tokens/word={n_tok / n_words:.2f}")'''),
        ("md", """**Rule of thumb:** for English, 1 token is about 4 characters or 0.75 words. Always measure for your own text.

## 5. Embeddings: meaning as numbers

An **embedding** is a vector (a list of numbers). `sentence-transformers/all-MiniLM-L6-v2` turns any sentence into 384 numbers, trained so that sentences with similar meaning get similar vectors."""),
        ("code", '''from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
sentences = [
    "How do I reset my password?",
    "I forgot my login details.",
    "The cat is sleeping on the sofa.",
    "A kitten naps on the couch.",
    "What is the price of the premium plan?",
    "How much does the subscription cost?",
]
vectors = embedder.encode(sentences)
print("Shape:", vectors.shape, "-> 6 sentences x 384 numbers")
print("First 8 numbers of sentence 0:", vectors[0][:8].round(3))'''),
        ("md", """## 6. Cosine similarity by hand

**Cosine similarity** measures whether two vectors point the same way: 1 = same direction, 0 = unrelated, -1 = opposite. Formula: dot product divided by (length of a × length of b). We write it ourselves first, then check against the library."""),
        ("code", '''import numpy as np

def cosine(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

print("password vs login :", round(cosine(vectors[0], vectors[1]), 3))
print("password vs kitten:", round(cosine(vectors[0], vectors[3]), 3))
print("cat vs kitten     :", round(cosine(vectors[2], vectors[3]), 3))

from sentence_transformers import util
print("library check     :", round(float(util.cos_sim(vectors[2], vectors[3])), 3))'''),
        ("md", "## 7. The full similarity grid as a heatmap\nA **heatmap** colours each cell of a table by its value. Bright squares off the diagonal show pairs with similar meaning."),
        ("code", '''import matplotlib.pyplot as plt

sim = np.array([[cosine(a, b) for b in vectors] for a in vectors])
fig, ax = plt.subplots(figsize=(7, 5))
im = ax.imshow(sim, cmap="viridis", vmin=-0.1, vmax=1)
labels = [s[:22] for s in sentences]
ax.set_xticks(range(6), labels=labels, rotation=45, ha="right")
ax.set_yticks(range(6), labels=labels)
for i in range(6):
    for j in range(6):
        ax.text(j, i, f"{sim[i, j]:.2f}", ha="center", va="center", color="white" if sim[i, j] < 0.6 else "black")
fig.colorbar(im)
ax.set_title("Cosine similarity")
plt.tight_layout()
plt.show()'''),
        ("md", """## 8. A tiny semantic search engine

**Semantic search** finds text by meaning, not by matching words. Embed the question, score every stored sentence, return the best. This is the core of RAG (Module 09)."""),
        ("code", '''def search(query, k=2):
    q = embedder.encode(query)
    scores = [cosine(q, v) for v in vectors]
    best = np.argsort(scores)[::-1][:k]          # indices of the k highest scores
    return [(sentences[i], round(scores[i], 3)) for i in best]

for q in ["I can't remember my password", "is there a monthly fee?", "pets resting"]:
    print(q, "->", search(q))'''),
        ("md", """## Try it yourself
1. Add your own sentence in another language you know to `samples` and compare tokens per word.
2. Add two sentences that mean the same thing but share no words. Does MiniLM score them high?
3. Search for something with no good match. What scores come back? (Hint: there is always a "best" result, even when it is bad — real systems use a minimum score.)"""),
    ], NB / "01-tokens-and-embeddings.ipynb")

    # ---------------- Notebook 02 ----------------
    notebook([
        ("md", """# 02 - Attention by hand (NumPy)

**Goal:** compute **self-attention** — the core calculation inside every transformer — for the 3-word sentence "the cat sat", using only NumPy (Python's library for arrays of numbers). Then compare it with the real attention weights of a small pretrained model.

No downloads in sections 1-6. Section 7 downloads DistilBERT (about 270 MB)."""),
        ("md", """## 1. Embeddings for three words

Each word gets a vector of 4 numbers. These are hand-made so we can follow the maths; in a real model they are learned. One row = one word."""),
        ("code", '''import numpy as np
np.set_printoptions(precision=3, suppress=True)

words = ["the", "cat", "sat"]
X = np.array([
    [1.0, 0.0, 0.0, 0.2],   # the
    [0.0, 1.0, 0.8, 0.0],   # cat
    [0.0, 0.6, 1.0, 1.0],   # sat
])
print("X shape:", X.shape, "(3 words, 4 numbers each)")'''),
        ("md", """## 2. Query, Key and Value matrices

Three **weight matrices** turn each embedding into:
- a **query** (what this word is looking for),
- a **key** (the label it offers to others),
- a **value** (the information it hands over).

Each matrix is 4×3: 4 numbers in, 3 out. `@` is NumPy's matrix-multiply operator."""),
        ("code", '''W_q = np.array([[0.5, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.5, 1.0], [0.0, 1.0, 0.5]])
W_k = np.array([[0.3, 0.0, 0.0], [0.0, 1.0, 0.5], [0.0, 0.5, 0.5], [0.2, 0.0, 0.0]])
W_v = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.5, 0.5]])

Q, K, V = X @ W_q, X @ W_k, X @ W_v
print("Q =\\n", Q, "\\nK =\\n", K, "\\nV =\\n", V)'''),
        ("md", """## 3. Step 1 and 2: scores, then scale

Every query is compared with every key using a **dot product** (multiply matching numbers and add). `K.T` is K **transposed** (rows become columns) so that one matrix multiply compares all pairs at once. We divide by √d (d = 3) to keep the numbers moderate."""),
        ("code", '''d = Q.shape[1]
scores = Q @ K.T / np.sqrt(d)
print("Scaled scores (row = word asking, column = word being looked at):\\n", scores)

# Check one cell by hand: 'sat' (row 2) looking at 'cat' (column 1)
manual = sum(Q[2, i] * K[1, i] for i in range(d)) / np.sqrt(d)
print("sat->cat by hand:", round(manual, 3), " from matrix:", round(scores[2, 1], 3))'''),
        ("md", """## 4. Step 3: softmax

**Softmax** turns a row of scores into positive weights that add up to 1: take e (≈2.718) to the power of each score, then divide by the row total. Bigger score → bigger share."""),
        ("code", '''def softmax(s):
    e = np.exp(s - s.max(axis=-1, keepdims=True))   # subtracting the max avoids huge numbers; result is identical
    return e / e.sum(axis=-1, keepdims=True)

weights = softmax(scores)
print("Attention weights:\\n", weights)
print("Row sums:", weights.sum(axis=1))'''),
        ("md", "## 5. Step 4: blend the values\nEach word's new vector is the weighted average of all value vectors. 'sat' now carries a lot of 'cat' information — it knows who is sitting."),
        ("code", '''output = weights @ V
for w, row in zip(words, output):
    print(f"{w:>4} ->", row)'''),
        ("md", "## 6. Heatmap, and the causal mask\nA **causal mask** stops each word from looking at words to its right, which is what text-generating models do (they must not see the future). We set those scores to minus infinity, so softmax gives them weight 0."),
        ("code", '''import matplotlib.pyplot as plt

mask = np.triu(np.ones((3, 3)), k=1).astype(bool)        # True above the diagonal = "future"
causal_weights = softmax(np.where(mask, -np.inf, scores))

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, w, title in [(axes[0], weights, "Full self-attention"), (axes[1], causal_weights, "Causal (masked)")]:
    ax.imshow(w, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(3), labels=words); ax.set_yticks(range(3), labels=words)
    ax.set_xlabel("attends to"); ax.set_ylabel("word")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{w[i, j]:.2f}", ha="center", va="center", color="white" if w[i, j] > 0.5 else "black")
    ax.set_title(title)
plt.tight_layout(); plt.show()'''),
        ("md", """## 7. Multi-head attention in a few lines

**Multi-head attention** runs several attention calculations with different matrices, then joins (concatenates) the results. Here we make 2 random heads to show the shapes."""),
        ("code", '''rng = np.random.default_rng(0)

def one_head(X, d_head=2):
    Wq, Wk, Wv = (rng.normal(size=(X.shape[1], d_head)) for _ in range(3))
    q, k, v = X @ Wq, X @ Wk, X @ Wv
    return softmax(q @ k.T / np.sqrt(d_head)) @ v

heads = [one_head(X) for _ in range(2)]
combined = np.concatenate(heads, axis=1)
print("each head output:", heads[0].shape, " combined:", combined.shape)'''),
        ("md", """## 8. Real attention from a pretrained model

Now look at a trained model. `output_attentions=True` asks DistilBERT to return its attention weights: one grid per layer per head. DistilBERT has 6 layers × 12 heads. The tokenizer adds special tokens `[CLS]` (start) and `[SEP]` (end)."""),
        ("code", '''import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

name = "distilbert-base-uncased-finetuned-sst-2-english"
tok = AutoTokenizer.from_pretrained(name)
# attn_implementation="eager" = plain maths, so the attention weights can be returned
model = AutoModelForSequenceClassification.from_pretrained(name, attn_implementation="eager")
inputs = tok("the animal didn't cross the street because it was tired", return_tensors="pt")
with torch.no_grad():
    out = model(**inputs, output_attentions=True)
tokens = tok.convert_ids_to_tokens(inputs["input_ids"][0])
print("tokens:", tokens)
print("layers:", len(out.attentions), " shape of one layer:", tuple(out.attentions[0].shape), "(batch, heads, tokens, tokens)")'''),
        ("md", """Real heads are messy: many look at nearby words, punctuation or `[SEP]`. Let's search all 6 × 12 = 72 heads for the one where `it` pays the most attention to `animal`, and compare with `street`."""),
        ("code", '''i, a, s = tokens.index("it"), tokens.index("animal"), tokens.index("street")
best = max(((l, h) for l in range(6) for h in range(12)),
           key=lambda lh: float(out.attentions[lh[0]][0, lh[1], i, a]))
layer, head = best
att = out.attentions[layer][0, head].numpy()
print(f"Best head: layer {layer}, head {head}")
print(f"  it -> animal: {att[i, a]:.2f}    it -> street: {att[i, s]:.3f}")'''),
        ("md", "Plot that head. Read the row for `it`: one dark square over `animal`. This head seems to have learned something like 'link a pronoun to the noun it refers to' — nobody programmed that; it emerged from training."),
        ("code", '''fig, ax = plt.subplots(figsize=(7, 6))
ax.imshow(att, cmap="Blues")
ax.set_xticks(range(len(tokens)), labels=tokens, rotation=90)
ax.set_yticks(range(len(tokens)), labels=tokens)
ax.set_title(f"DistilBERT layer {layer} head {head}")
plt.tight_layout(); plt.show()'''),
        ("md", """## Try it yourself
1. Change the embedding of "sat" so it attends more to "the". Which numbers did you change?
2. Remove the `/ np.sqrt(d)` scaling and multiply X by 10. What happens to the weights? (They become almost all-or-nothing.)
3. For every head in layer 0, print which token `it` attends to most. Are early layers more "local" (looking at neighbours)?"""),
    ], NB / "02-attention-by-hand.ipynb")

    # ---------------- Notebook 03 ----------------
    notebook([
        ("md", """# 03 - Hugging Face pipelines, tokenizers, models and the Hub

**Goal:** use the Hugging Face `transformers` library at three levels: the one-line `pipeline`, tokenizer + model by hand, and reading what the model returns. We do **sentiment analysis** (is a text positive or negative?) and **text generation** with tiny models that run on a CPU.

Downloads about 550 MB the first time (two models). No API keys."""),
        ("md", "## Setup\nInstall anything missing, and fix the random seed so generated text is the same every run."),
        ("code", INSTALL + '''
import torch
torch.manual_seed(0)'''),
        ("md", """## 1. Level 1: `pipeline`

`pipeline(task, model=...)` bundles tokenizer + model + post-processing. We name the model explicitly; without a name the library picks a default and prints a warning. The model card for this one is on the Hub: https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english"""),
        ("code", '''from transformers import pipeline

clf = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
reviews = [
    "I love this course, the examples are so clear!",
    "The battery died after one hour. Terrible.",
    "It was okay, nothing special.",
    "Great, it broke on the first day.",
]
for r, res in zip(reviews, clf(reviews)):
    print(f"{res['label']:<8} {res['score']:.3f}  {r}")'''),
        ("md", """**Look closely:** "It was okay" gets a confident label even though it is neutral — this model only knows two labels. "Great, it broke..." is sarcasm and is probably labelled POSITIVE. A high score means "confident", not "correct".

## 2. Level 2: tokenizer + model by hand

Same result, but each step is visible:
1. the tokenizer turns text into IDs (and an **attention mask** — 1 for real tokens, 0 for padding),
2. the model returns **logits** (raw scores),
3. softmax turns logits into probabilities."""),
        ("code", '''from transformers import AutoTokenizer, AutoModelForSequenceClassification

name = "distilbert-base-uncased-finetuned-sst-2-english"
tok = AutoTokenizer.from_pretrained(name)
model = AutoModelForSequenceClassification.from_pretrained(name)

inputs = tok(reviews, padding=True, return_tensors="pt")
print("input_ids shape:", tuple(inputs["input_ids"].shape), "(reviews, tokens incl. padding)")
print("first review tokens:", tok.convert_ids_to_tokens(inputs["input_ids"][0]))'''),
        ("md", "Now run the model. `torch.no_grad()` tells PyTorch we are not training, which saves memory and time."),
        ("code", '''with torch.no_grad():
    logits = model(**inputs).logits
probs = torch.softmax(logits, dim=-1)
print("labels:", model.config.id2label)
for r, l, p in zip(reviews, logits, probs):
    print(f"logits={l.numpy().round(2)}  probs={p.numpy().round(3)}  {r[:40]}")'''),
        ("md", """## 3. What is inside the model?

A model is a stack of layers holding **parameters** (learned numbers). Let's count them and look at the config, which is downloaded from the Hub with the weights."""),
        ("code", '''n_params = sum(p.numel() for p in model.parameters())
print(f"Parameters: {n_params/1e6:.1f} million")
cfg = model.config
print("layers:", cfg.n_layers, " heads:", cfg.n_heads, " hidden size:", cfg.dim, " vocab:", cfg.vocab_size)'''),
        ("md", """## 4. Text generation with a tiny model

`HuggingFaceTB/SmolLM2-135M-Instruct` is a **decoder-only** model (it writes text left to right) with 135 million parameters. It is tiny compared with chat models, so expect mistakes. `max_new_tokens` limits how much it writes; `do_sample=False` means "always pick the most likely next token" (called **greedy decoding**)."""),
        ("code", '''# dtype=torch.float32: the weights are stored in bfloat16, which is very slow on most CPUs
gen = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-135M-Instruct", dtype=torch.float32)
out = gen("The three most useful Python libraries for data are", max_new_tokens=30, do_sample=False)
print(out[0]["generated_text"])'''),
        ("md", """## 5. Chat format

**Instruct** models were trained on conversations with roles: `system` (rules for the assistant), `user` (the person), `assistant` (the model). `apply_chat_template` wraps messages in the special markers the model expects. Let's print the wrapped text first so the markers are visible."""),
        ("code", '''from transformers import AutoModelForCausalLM

chat_name = "HuggingFaceTB/SmolLM2-135M-Instruct"
ctok = AutoTokenizer.from_pretrained(chat_name)
cmodel = AutoModelForCausalLM.from_pretrained(chat_name, dtype=torch.float32)
messages = [
    {"role": "system", "content": "You are a friendly teacher. Answer in one short sentence."},
    {"role": "user", "content": "What is sentiment analysis?"},
]
print(ctok.apply_chat_template(messages, add_generation_prompt=True, tokenize=False))'''),
        ("md", "Now generate the answer and decode only the new tokens (the prompt is part of the output IDs, so we slice it off)."),
        ("code", '''inputs = ctok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt", return_dict=True)
with torch.no_grad():
    new_ids = cmodel.generate(**inputs, max_new_tokens=40, do_sample=False)
print(ctok.decode(new_ids[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))'''),
        ("md", """## 6. Other pipeline tasks (to explore later)

The same pattern works for many tasks. Each needs its own model, so these are listed, not run, to keep downloads small:

| task string | what it does | example small model |
|---|---|---|
| `"ner"` | find names, places, organisations | `dslim/bert-base-NER` |
| `"zero-shot-classification"` | classify into labels you invent | `facebook/bart-large-mnli` (large) |
| `"summarization"` | shorten text | `sshleifer/distilbart-cnn-12-6` |
| `"translation_en_to_fr"` | translate | `t5-small` |
| `"feature-extraction"` | get embeddings | `sentence-transformers/all-MiniLM-L6-v2` |

Search the Hub by task: https://huggingface.co/models"""),
        ("md", "## 7. Batch sentiment on a small table\nA realistic use: score a column of customer comments with pandas and count the labels."),
        ("code", '''import pandas as pd

df = pd.DataFrame({"comment": [
    "Delivery was fast and the food was hot.",
    "Order arrived cold and late.",
    "Customer support solved my issue in minutes.",
    "The app keeps crashing when I pay.",
    "Decent value for the price.",
]})
results = clf(df["comment"].tolist())
df["label"] = [r["label"] for r in results]
df["score"] = [round(r["score"], 3) for r in results]
print(df)
print(df["label"].value_counts())'''),
        ("md", """## Try it yourself
1. Look at the table above. Did any plainly positive comment get NEGATIVE (when we built this notebook, "Customer support solved my issue in minutes." did)? Why might a model trained on movie reviews struggle with support tickets?
2. Write five tricky reviews (sarcasm, negation like "not bad", mixed feelings). Which ones fool the model?
3. Change `do_sample=False` to `do_sample=True, temperature=1.2` in section 4 and run it a few times. What changes? (Module 07 explains temperature.)
4. Open the model card for SmolLM2-135M-Instruct on the Hub. What licence does it have? What languages does it support?"""),
    ], NB / "03-hugging-face-pipelines.ipynb")


# ---------------------------------------------------------------------------
# 3. Slides
# ---------------------------------------------------------------------------
def build_slides():
    deck = {
        "title": "Module 06 - NLP and Transformers",
        "subtitle": "From text to tokens, embeddings, attention and Hugging Face",
        "slides": [
            {"title": "Why this module matters",
             "bullets": ["Every chatbot, search box and LLM starts by turning text into numbers",
                         "Today: tokens -> embeddings -> attention -> transformers",
                         "Then: use real models with Hugging Face on a laptop",
                         "Module 07 builds directly on this"],
             "notes": "Open by asking: how can a calculator understand the word 'cat'? It cannot. Everything in NLP is about turning text into numbers that keep the meaning. By the end of today students will have run real tokenizers, compared sentence meanings with numbers, and computed attention by hand."},
            {"title": "The NLP pipeline", "image": str(IMG / "nlp-pipeline.png"),
             "bullets": ["Text -> tokens -> IDs -> embeddings", "Transformer layers mix context", "Output: label, vector, or next token"],
             "notes": "Walk left to right. Tokens are pieces of text. IDs are their row numbers in a vocabulary. Embeddings are lists of numbers that carry meaning. The transformer lets every token look at the others. The output depends on the task."},
            {"title": "Tokens: LEGO bricks for text", "image": str(IMG / "tokenization.png"),
             "bullets": ["Token = a chunk the model treats as one unit", "Word tokens: vocab too big", "Character tokens: sequences too long", "Sub-words (BPE): the sweet spot"],
             "notes": "Use the LEGO analogy: special moulded bricks for every object (word level) versus only 1x1 bricks (character level) versus a sensible kit (sub-word). BPE starts from characters and repeatedly glues the most frequent pair together."},
            {"title": "Real tokenizer output",
             "bullets": ["BERT: token, ##ization, isn, ', t ...", "GPT-2: Token, ization, Ġisn, 't ...", "o200k_base: 12 tokens; cl100k_base: 15", "Ġ = 'space before me'; ## = 'glued to previous'"],
             "code": "import tiktoken\nenc = tiktoken.get_encoding('o200k_base')\nids = enc.encode(\"isn't magic\")\nprint(ids, [enc.decode([i]) for i in ids])",
             "notes": "Show notebook 01 live if you can. Point out that the same sentence gives different token counts for different tokenizers, and that you can never mix token IDs between models."},
            {"title": "Why tokens matter in practice",
             "bullets": ["You pay per token, not per word", "Context limits are in tokens", "~4 characters or ~0.75 English words per token", "Code, numbers, Hindi/Telugu: more tokens per word", "Letter-counting mistakes come from tokens"],
             "notes": "Ask students to guess how many tokens a Hindi sentence needs compared with English, then run section 4 of notebook 01. The strawberry letter-counting failure is a good memorable example."},
            {"title": "Embeddings: meaning as numbers",
             "bullets": ["Embedding = list of numbers (vector)", "Similar meaning -> similar numbers", "Fruit sliders analogy: sweetness, size, redness", "MiniLM: 384 numbers per sentence"],
             "notes": "Draw three sliders on the board. Strawberry and cherry get similar slider positions; watermelon differs in size. Real embeddings have hundreds of sliders that the model invented; nobody labels them."},
            {"title": "Cosine similarity", "image": str(IMG / "embedding-similarity.png"),
             "bullets": ["Do two arrows point the same way?", "1 = same, 0 = unrelated, -1 = opposite", "dot(a,b) / (|a| x |b|)", "Basis of semantic search and RAG"],
             "notes": "Point at the bright squares: password vs forgot login, cat vs kitten, price vs subscription. These pairs share almost no words, yet score high. That is search by meaning."},
            {"title": "From RNNs to attention", "image": str(IMG / "rnn-vs-attention.png"),
             "bullets": ["RNN: read one token at a time (whisper game)", "Forgets long-range context, slow to train", "Attention: every token sees every token", "2017: 'Attention Is All You Need'"],
             "notes": "Play the whisper game analogy. RNNs pass a running summary from token to token, so early words fade and the work cannot be done in parallel. Attention is a meeting where everyone hears everyone."},
            {"title": "Query, Key, Value: the library",
             "bullets": ["Query: what am I looking for?", "Key: the label on each book", "Value: what the book says", "Match query to keys, read values weighted by match"],
             "notes": "Library analogy. You arrive with a question. You compare it with every spine label. You spend more time reading the books whose labels match. Your understanding is a weighted blend."},
            {"title": "Attention in four steps", "image": str(IMG / "attention-heatmap.png"),
             "bullets": ["1. Scores = Q x K-transpose", "2. Divide by sqrt(d)", "3. Softmax: rows sum to 1", "4. Output = weights x V"],
             "notes": "This heatmap comes from notebook 02 with hand-made numbers. Read a row: 'sat' gives 0.58 of its attention to 'cat'. Emphasise each row sums to 1. Real models do exactly this with learned, much larger matrices."},
            {"title": "Multi-head, position, masking",
             "bullets": ["Multi-head: several attention 'editors' in parallel", "Positional encoding: tell the model word order", "Causal mask: generators cannot peek at the future", "GPT-2 small: 12 layers x 12 heads"],
             "notes": "Without positions, 'dog bites man' equals 'man bites dog'. Without the mask, a generator could cheat during training by looking at the answer. Multi-head lets different heads specialise."},
            {"title": "The transformer block", "image": str(IMG / "transformer-block.png"),
             "bullets": ["Attention: tokens share information", "Feed-forward: each token 'thinks'", "Residual + layer norm keep training stable", "Stack N blocks; final layer gives logits"],
             "notes": "Residual connection: like tracking changes instead of rewriting the document. Layer norm: volume control. At the end, the output head turns the last vector into one score per vocabulary token; softmax makes those probabilities."},
            {"title": "Encoder, decoder, both",
             "bullets": ["Encoder-only (BERT, MiniLM): understand, classify, embed", "Decoder-only (GPT, Llama, Claude): generate", "Encoder-decoder (T5, BART): translate, summarise", "Parameters = learned numbers; size is counted in them"],
             "notes": "A quick way to remember: encoders read, decoders write. Today we use an encoder for sentiment and embeddings, and a decoder (SmolLM2) for generation."},
            {"title": "Hugging Face: three levels", "image": str(IMG / "hf-levels.png"),
             "bullets": ["Hub: models + model cards + licences", "pipeline(): one line", "AutoTokenizer + AutoModel: see the numbers", "Raw tensors: attention, hidden states"],
             "notes": "Show the Hub website briefly and open a model card. Stress reading the card: what the model was trained on, licence, limitations."},
            {"title": "Code: sentiment in three lines",
             "bullets": ["Model: DistilBERT fine-tuned on SST-2", "Only POSITIVE / NEGATIVE", "Score = confidence, not correctness"],
             "code": "from transformers import pipeline\nclf = pipeline('sentiment-analysis',\n  model='distilbert-base-uncased-finetuned-sst-2-english')\nclf(['I love it!', 'Great, it broke on day one.'])",
             "notes": "Run it live. The sarcastic sentence is usually labelled POSITIVE with high confidence. Use it to discuss limits: fine-tuned models only know their training task."},
            {"title": "Common mistakes",
             "bullets": ["Mixing a tokenizer from one model with another model", "Treating token count = word count", "Trusting a confident score as correct", "Forgetting torch.no_grad() at inference", "Using a model without reading its card/licence"],
             "notes": "Go through each and ask who has done it. The tokenizer mismatch produces silent nonsense, which is the most dangerous kind of bug."},
            {"title": "Recap and exercises",
             "bullets": ["Tokens -> IDs -> embeddings -> attention -> output", "Cosine similarity compares meaning", "softmax(QK^T / sqrt(d)) V", "Exercises 1-4 now, 5-10 as homework"],
             "notes": "Ask three students to each explain one stage of the pipeline in their own words. Then hand out exercises.md. Easy ones in class, harder ones at home; solutions are in solutions/."},
        ],
    }
    slides(deck, HERE / "slides" / f"{MOD}.pptx")


# ---------------------------------------------------------------------------
# 4. Excel cheat sheet
# ---------------------------------------------------------------------------
def build_excel():
    glossary = [["Term", "Plain-English meaning", "Where you meet it"],
                ["Token", "A chunk of text the model treats as one unit", "tokenizer.tokenize()"],
                ["Token ID", "The number of a token in the vocabulary", "tokenizer(text)['input_ids']"],
                ["Vocabulary", "Fixed list of all tokens a tokenizer knows", "tokenizer.vocab_size"],
                ["BPE", "Builds sub-words by merging the most frequent pairs", "GPT-2, tiktoken"],
                ["WordPiece", "BERT's sub-word method; '##' marks a glued piece", "bert-base-uncased"],
                ["Embedding", "List of numbers that represents meaning", "SentenceTransformer.encode()"],
                ["Cosine similarity", "-1..1 score of how alike two vectors point", "util.cos_sim()"],
                ["Attention", "Each token weighs how much every other token matters", "output_attentions=True"],
                ["Query / Key / Value", "What I seek / my label / what I hand over", "W_q, W_k, W_v"],
                ["Softmax", "Turns scores into probabilities that sum to 1", "torch.softmax()"],
                ["Multi-head attention", "Several attention calculations in parallel", "config.n_heads"],
                ["Positional encoding", "Adds word-order information", "inside the model"],
                ["Causal mask", "Stops tokens looking at future tokens", "decoder models"],
                ["Logits", "Raw scores before softmax", "model(**inputs).logits"],
                ["Parameter", "One learned number inside the model", "model.parameters()"],
                ["Fine-tuning", "Extra training on a small task dataset", "...-finetuned-sst-2-english"],
                ["Pipeline", "One-line Hugging Face wrapper for a task", "pipeline('sentiment-analysis')"],
                ["Model card", "README on the Hub: data, licence, limits", "huggingface.co/<model>"]]
    tokcount = [["Text", "Words", "o200k_base tokens", "Tokens per word"]]
    try:
        import tiktoken
        enc = tiktoken.get_encoding("o200k_base")
        for s in ["The weather in Hyderabad is warm and sunny today.",
                  "for i in range(10): print(i ** 2)",
                  "Order 8473629104 costs 12345.67 rupees",
                  "Pneumonoultramicroscopicsilicovolcanoconiosis is a word."]:
            r = len(tokcount) + 1
            tokcount.append([s, len(s.split()), len(enc.encode(s)), f"=C{r}/B{r}"])
    except Exception:
        pass
    models = [["Model (Hugging Face Hub name)", "Type", "Size", "Used for in this module", "Link"],
              ["bert-base-uncased", "encoder", "~110M params", "tokenizer comparison", "https://huggingface.co/bert-base-uncased"],
              ["gpt2", "decoder", "~124M params", "tokenizer comparison", "https://huggingface.co/gpt2"],
              ["sentence-transformers/all-MiniLM-L6-v2", "encoder", "~22M params", "sentence embeddings", "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2"],
              ["distilbert-base-uncased-finetuned-sst-2-english", "encoder", "~66M params", "sentiment, attention", "https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english"],
              ["HuggingFaceTB/SmolLM2-135M-Instruct", "decoder", "~135M params", "text generation, chat", "https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct"]]
    workbook({"Glossary": glossary, "Tokens per word": tokcount, "Models used": models},
             HERE / "excel" / "06-nlp-cheatsheet.xlsx",
             col_widths={"Glossary": [24, 55, 34], "Tokens per word": [55, 10, 18, 16], "Models used": [48, 10, 14, 26, 60]})


if __name__ == "__main__":
    build_diagrams()
    build_plots()
    build_notebooks()
    build_slides()
    build_excel()
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / f"{MOD}-handout.pdf", title="Module 06 - NLP and Transformers")
    print("Module 06 built.")
