"""
Exercise 9 solution - MCQ accuracy by category, weakest first.
Run from anywhere:  python ex09_quiz_weakest.py
"""
import pathlib
import random

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
mcq = pd.read_csv(ROOT / "data" / "mcq.csv")

# Demo answers: a fixed random generator plays a learner who is right about 60% of the time.
rng = random.Random(42)
answers = [row.correct if rng.random() < 0.6 else rng.choice("ABCD") for row in mcq.itertuples()]

mcq["my_answer"] = answers
mcq["correct_flag"] = mcq.my_answer == mcq.correct           # True / False per question
by_cat = (mcq.groupby("category").correct_flag.agg(["mean", "size"])
          .rename(columns={"mean": "accuracy", "size": "questions"})
          .sort_values("accuracy"))
print(f"Overall accuracy: {mcq.correct_flag.mean():.0%}\n")
print(by_cat.assign(accuracy=by_cat.accuracy.map("{:.0%}".format)))
print("\nPractise first:", ", ".join(by_cat.index[:3]))
