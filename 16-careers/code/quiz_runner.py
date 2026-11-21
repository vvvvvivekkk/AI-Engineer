"""
quiz_runner.py - an interactive mock-interview quiz in the terminal, fully offline.

Two modes:
  mcq   multiple-choice questions, scored automatically
  open  open questions from the 137-question bank: you type an answer, then see the model answer,
        a keyword-overlap score, and rate yourself 0-2. Weak questions are saved to review later.

Usage (from the 16-careers folder):
    python code/quiz_runner.py mcq  --n 10
    python code/quiz_runner.py open --n 5 --category RAG
    python code/quiz_runner.py open --n 3 --auto        # demo mode: no typing, empty answers
Progress is appended to data/quiz_progress.csv (date, question, self-score).
"""
import argparse
import csv
import datetime
import pathlib
import random
import re

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE.parent / "data"
STOP = set("a an the and or of to in on for is are be with by it its as that this from at can you your use used using "
           "into than then so not no do does how what why when which who more most also each their they them".split())


def load(name):
    """Read a CSV from the data folder into a list of dicts."""
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def keywords(text):
    """Content words of a text: lower-case words of 4+ letters that are not stop words."""
    return {w for w in re.findall(r"[a-z][a-z0-9-]{3,}", text.lower()) if w not in STOP}


def overlap_score(answer, model_answer):
    """Share of the model answer's keywords that appear in your answer (a rough self-check, not a grade)."""
    target = keywords(model_answer)
    return len(target & keywords(answer)) / len(target) if target else 0.0


def run_mcq(n, category, auto):
    qs = [q for q in load("mcq.csv") if not category or q["category"] == category]
    random.shuffle(qs)
    score = 0
    for i, q in enumerate(qs[:n], 1):
        print(f"\nQ{i} [{q['category']}] {q['question']}")
        for letter in "ABCD":
            print(f"   {letter}) {q[letter]}")
        ans = random.choice("ABCD") if auto else input("Your answer (A-D): ").strip().upper()
        if ans == q["correct"]:
            score += 1
            print("   Correct!", q["explanation"])
        else:
            print(f"   Not quite - answer {q['correct']}. {q['explanation']}")
    total = min(n, len(qs))
    print(f"\nScore: {score}/{total}")


def run_open(n, category, level, auto):
    qs = [q for q in load("question_bank.csv")
          if (not category or q["category"] == category) and (not level or q["level"] == level)]
    random.shuffle(qs)
    log = DATA / "quiz_progress.csv"
    new_file = not log.exists()
    with open(log, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["date", "category", "question", "keyword_overlap", "self_score"])
        for i, q in enumerate(qs[:n], 1):
            print(f"\nQ{i} [{q['category']} / {q['level']}] {q['question']}")
            ans = "" if auto else input("Your answer (one paragraph, then Enter):\n> ")
            ov = overlap_score(ans, q["model_answer"])
            print(f"\nModel answer: {q['model_answer']}")
            print(f"Keyword overlap: {ov:.0%} (rough guide only - judge the meaning yourself)")
            raw = "0" if auto else input("Rate yourself: 0 = missed it, 1 = partly, 2 = nailed it: ").strip()
            self_score = int(raw) if raw in {"0", "1", "2"} else 0
            w.writerow([datetime.date.today().isoformat(), q["category"], q["question"], f"{ov:.2f}", self_score])
    print(f"\nSaved to {log}. Re-practise the questions you scored 0 or 1 in two days.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Offline mock-interview quiz")
    p.add_argument("mode", choices=["mcq", "open"])
    p.add_argument("--n", type=int, default=5, help="number of questions")
    p.add_argument("--category", default="", help="e.g. Python, RAG, Agents, Behavioural")
    p.add_argument("--level", default="", help="junior, mid or senior (open mode)")
    p.add_argument("--auto", action="store_true", help="demo mode with no typing")
    a = p.parse_args()
    if a.mode == "mcq":
        run_mcq(a.n, a.category, a.auto)
    else:
        run_open(a.n, a.category, a.level, a.auto)
