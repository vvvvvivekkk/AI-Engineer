"""
solutions.py - runnable solutions for Module 06 exercises 1-10.

Run all:          python solutions.py
Run one (e.g. 8): python solutions.py 8
Needs: numpy, pandas, tiktoken, transformers, torch, sentence-transformers
"""
import sys
import numpy as np


def ex1():
    """Count tokens three ways."""
    import tiktoken
    from transformers import AutoTokenizer
    text = "Hyderabad's biryani is world-famous!"
    for name in ["gpt2", "bert-base-uncased"]:
        tok = AutoTokenizer.from_pretrained(name)          # load the tokenizer for this model
        pieces = tok.tokenize(text)
        print(f"{name:<18} {len(pieces):>2} {pieces}")
    enc = tiktoken.get_encoding("o200k_base")
    ids = enc.encode(text)
    print(f"{'o200k_base':<18} {len(ids):>2} {[enc.decode([i]) for i in ids]}")


def ex2():
    """Round trip with tiktoken."""
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    text = "Tokens are not words."
    ids = enc.encode(text)                                  # text -> IDs
    print("IDs:", ids)
    print("Decoded:", enc.decode(ids), "| same:", enc.decode(ids) == text)
    print("Pieces:", [repr(enc.decode([i])) for i in ids])  # repr shows the leading spaces


def cosine(a, b):
    """Cosine similarity using only NumPy."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def ex3():
    print(cosine([1, 2, 3], [2, 4, 6]))   # 1.0
    print(cosine([1, 0], [0, 1]))         # 0.0
    print(cosine([1, 1], [-1, -1]))       # -1.0


def tokens_per_word(text, encoding="o200k_base"):
    import tiktoken
    enc = tiktoken.get_encoding(encoding)
    return len(enc.encode(text)) / len(text.split())       # tokens divided by space-separated words


def ex4():
    import pandas as pd
    rows = {
        "English": "Where is the nearest railway station?",
        "Hindi": "सबसे नज़दीकी रेलवे स्टेशन कहाँ है?",
        "Telugu": "దగ్గరలో ఉన్న రైల్వే స్టేషన్ ఎక్కడ ఉంది?",
    }
    df = pd.DataFrame([{"language": k, "text": v, "tokens_per_word": round(tokens_per_word(v), 2)}
                       for k, v in rows.items()])
    print(df)


def ex5():
    from sentence_transformers import SentenceTransformer
    sents = ["The train to Chennai is delayed.", "My flight to Delhi was cancelled.",
             "The bus arrived two hours late.", "I baked a chocolate cake yesterday.",
             "Our metro service stopped due to rain."]
    v = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2").encode(sents, normalize_embeddings=True)
    sim = v @ v.T                                           # with normalised vectors, dot product = cosine
    avg = (sim.sum(axis=1) - 1) / (len(sents) - 1)          # remove the self-similarity of 1, average the rest
    for s, a in zip(sents, avg):
        print(f"{a:.3f}  {s}")
    print("Odd one out:", sents[int(np.argmin(avg))])


def softmax(s):
    s = np.asarray(s, dtype=float)
    e = np.exp(s - s.max())
    return e / e.sum()


def ex6():
    scores = np.array([2.0, 1.0, 0.1])
    for T in [0.5, 1, 2]:
        print(f"T={T}:", np.round(softmax(scores / T), 3))


def ex7():
    import pandas as pd
    from transformers import pipeline
    clf = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    data = [("The food was delicious and the staff were kind.", "POSITIVE"),
            ("Best purchase I have made this year!", "POSITIVE"),
            ("The room was dirty and smelled bad.", "NEGATIVE"),
            ("I want a refund, this is useless.", "NEGATIVE"),
            ("Oh wonderful, my parcel is lost again.", "NEGATIVE"),
            ("Great job, the app deleted all my notes.", "NEGATIVE"),
            ("The movie was not bad at all.", "POSITIVE"),
            ("The service was not great.", "NEGATIVE")]
    res = clf([t for t, _ in data])
    df = pd.DataFrame({"text": [t for t, _ in data], "expected": [e for _, e in data],
                       "model": [r["label"] for r in res], "score": [round(r["score"], 3) for r in res]})
    df["correct"] = df.expected == df.model
    print(df.to_string())
    print("Wrong:", int((~df.correct).sum()), "of", len(df))


def ex8():
    X = np.array([[1, 0], [0, 1], [1, 1]], dtype=float)
    Q = K = V = X @ np.eye(2)                               # identity matrices leave X unchanged
    scores = Q @ K.T / np.sqrt(2)
    print("scores:\n", np.round(scores, 3))
    W = np.apply_along_axis(softmax, 1, scores)             # softmax each row
    print("weights:\n", np.round(W, 3))
    print("output:\n", np.round(W @ V, 3))
    mask = np.triu(np.ones((3, 3)), k=1).astype(bool)
    Wc = np.apply_along_axis(softmax, 1, np.where(mask, -np.inf, scores))
    print("causal weights:\n", np.round(Wc, 3))
    print("causal output:\n", np.round(Wc @ V, 3))


def ex9():
    from sentence_transformers import SentenceTransformer
    faq = {
        "How do I reset my password?": "Click 'Forgot password' on the login page.",
        "What are your opening hours?": "We are open 9am to 6pm, Monday to Saturday.",
        "Do you deliver to Secunderabad?": "Yes, delivery to Secunderabad takes 1-2 days.",
        "How can I cancel my order?": "Go to My Orders and click Cancel within 1 hour.",
    }
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    questions = list(faq)
    q_vecs = model.encode(questions, normalize_embeddings=True)   # embed FAQ once, up front

    def answer(question, threshold=0.4):
        v = model.encode(question, normalize_embeddings=True)
        scores = q_vecs @ v                                       # cosine with every FAQ question
        best = int(np.argmax(scores))
        if scores[best] < threshold:                              # not confident enough -> hand over to a human
            return f"Sorry, I don't know. A human will reply soon. (best score {scores[best]:.2f})"
        return f"{faq[questions[best]]} (matched '{questions[best]}', score {scores[best]:.2f})"

    for q in ["I forgot my password", "when do you open?", "can I stop my order?",
              "do you ship to Secunderabad", "what is the capital of Peru?", "tell me a joke"]:
        print(q, "->", answer(q))


def ex10():
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    name = "HuggingFaceTB/SmolLM2-135M-Instruct"
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float32)   # float32 is much faster than bfloat16 on CPU
    ids = tok("The capital of France is", return_tensors="pt")["input_ids"]
    start = ids.shape[1]
    with torch.no_grad():
        for step in range(10):
            logits = model(input_ids=ids).logits[0, -1]           # scores for the next token only
            next_id = int(torch.argmax(logits))                   # greedy: take the best one
            ids = torch.cat([ids, torch.tensor([[next_id]])], dim=1)   # append and go again
            print(step + 1, repr(tok.decode(ids[0])))
        ref = model.generate(tok("The capital of France is", return_tensors="pt")["input_ids"],
                             max_new_tokens=10, do_sample=False)
    print("Matches generate():", torch.equal(ref[0][start:], ids[0][start:]))


if __name__ == "__main__":
    chosen = [int(a) for a in sys.argv[1:]] or range(1, 11)
    for n in chosen:
        print(f"\n===== Exercise {n} =====")
        globals()[f"ex{n}"]()
