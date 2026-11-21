"""
main.py - trains/runs all models on the SAME reviews and compares them.

    python main.py                          # classic + neural + zero-shot (nli and sst2)
    python main.py --zero-shot nli          # only one zero-shot method
    python main.py --zero-shot none         # skip transformers (fast, no downloads)
    python main.py --zero-shot llm          # use src/llm.py (LLM_PROVIDER from .env)
Writes reports/comparison.md, comparison.csv, challenge_predictions.csv and accuracy.png.
"""
import argparse
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, f1_score

from src import classic, zero_shot
from src.data import load_challenge, load_split
from src.neural import NeuralSentiment

HERE = Path(__file__).resolve().parent
torch.set_num_threads(2)


def to_int(labels) -> list[int]:
    return [int(l == "positive") for l in labels]


def timed(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    return result, time.perf_counter() - start


def main() -> None:
    ap = argparse.ArgumentParser(description="Sentiment: classic vs neural vs zero-shot")
    ap.add_argument("--zero-shot", default="nli,sst2", help="comma list of nli, sst2, llm - or none")
    ap.add_argument("--out", default=str(HERE / "reports"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    train, test = load_split()
    challenge = load_challenge()
    y_train, y_test, y_ch = to_int(train.label), to_int(test.label), to_int(challenge.label)
    print(f"train {len(train)} | test {len(test)} | challenge {len(challenge)}")

    # Each entry: name -> (train seconds, predict function)
    models = {}
    m1, t1 = timed(lambda: classic.build().fit(train.text, y_train))
    models["tfidf_logreg"] = (t1, lambda xs: list(m1.predict(xs)))
    m2, t2 = timed(lambda: NeuralSentiment().fit(train.text, y_train))
    models["embedding_bag_nn"] = (t2, m2.predict)
    methods = [] if args.zero_shot == "none" else [m.strip() for m in args.zero_shot.split(",")]
    for m in methods:
        models[f"zero_shot_{m}"] = (0.0, lambda xs, m=m: zero_shot.classify(list(xs), m))

    rows, ch_preds = [], challenge[["text", "label", "kind"]].copy()
    for name, (train_s, predict) in models.items():
        pred_test, secs = timed(predict, list(test.text))
        pred_ch = predict(list(challenge.text))
        ch_preds[name] = ["positive" if p else "negative" for p in pred_ch]
        row = {"model": name,
               "test_accuracy": accuracy_score(y_test, pred_test),
               "test_f1": f1_score(y_test, pred_test),
               "challenge_accuracy": accuracy_score(y_ch, pred_ch),
               "train_seconds": train_s,
               "ms_per_review": 1000 * secs / len(test),
               # If this is near 0 or 1 the model is mostly guessing one label on unfamiliar text
               "challenge_share_predicted_positive": sum(pred_ch) / len(pred_ch)}
        # Accuracy on each kind of tricky review (sarcasm, unseen_words, negation, mixed)
        for kind, grp in challenge.groupby("kind"):
            idx = grp.index
            row[f"ch_{kind}"] = accuracy_score([y_ch[i] for i in idx], [pred_ch[i] for i in idx])
        rows.append(row)
        print(f"{name:20s} test acc {row['test_accuracy']:.3f} | challenge acc "
              f"{row['challenge_accuracy']:.3f} | {row['ms_per_review']:.2f} ms/review")

    table = pd.DataFrame(rows)
    table.round(3).to_csv(out / "comparison.csv", index=False)
    ch_preds.to_csv(out / "challenge_predictions.csv", index=False)

    # The test set has ~4% deliberately flipped labels, so ~96% is the realistic ceiling there.
    flipped = int(test.label_flipped.sum())
    words = classic.top_words(m1)
    md = ["# Sentiment comparison", "",
          f"Test set: {len(test)} template reviews ({flipped} have deliberately flipped labels, "
          f"so the best possible accuracy is about {1 - flipped / len(test):.3f}). "
          f"Challenge set: {len(challenge)} hand-written tricky reviews.", "",
          table.round(3).to_markdown(index=False), "",
          "## What the TF-IDF model relies on", "",
          f"- strongest positive signals: {', '.join(words['positive'])}",
          f"- strongest negative signals: {', '.join(words['negative'])}", "",
          f"The neural model had never seen {m2.unknown_rate(challenge.text):.0%} of the words "
          "in the challenge set (vs "
          f"{m2.unknown_rate(test.text):.0%} on the test set).", "",
          "![accuracy](accuracy.png)"]
    (out / "comparison.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    fig, ax = plt.subplots(figsize=(8, 4))
    x = range(len(table))
    ax.bar([i - 0.2 for i in x], table.test_accuracy, width=0.4, label="test (template reviews)")
    ax.bar([i + 0.2 for i in x], table.challenge_accuracy, width=0.4, label="challenge (hand-written)")
    ax.set_xticks(list(x), table.model, rotation=15)
    ax.set(ylim=(0, 1.05), ylabel="accuracy", title="Same data, three approaches")
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(out / "accuracy.png", dpi=110)
    plt.close(fig)
    print(f"\nwritten to {out}/comparison.md")


if __name__ == "__main__":
    main()
