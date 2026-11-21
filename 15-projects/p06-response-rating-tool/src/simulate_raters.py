"""
simulate_raters.py - pretend two humans rated all 100 pairs, so the demo works instantly.

IMPORTANT: these are SIMULATED labels, made from the hidden gold label plus
random mistakes. They are clearly marked with rater names "sim_rater_1" and
"sim_rater_2". When you rate in the Streamlit app under your own name, your real
labels are added to the same file and you can compare yourself with the judge.

Why two raters? Real annotation teams measure **inter-annotator agreement** -
how often two humans agree with each other. It is the ceiling for any automatic
judge: if humans only agree 80% of the time, a judge cannot sensibly beat that.

Run:  python -m src.simulate_raters
"""
from __future__ import annotations

import random

from .ratings import CRITERIA, DATA, append_jsonl, load_candidates, make_record

# "Close" flaws are hard to spot (e.g. a correct but terse answer) - raters disagree more there.
HARD_FLAWS = {"terse", "incomplete", "unclear"}


def scores_for(is_good: bool, flaw: str, rng: random.Random) -> dict:
    """Plausible 1-5 rubric scores for one answer."""
    if is_good:
        return {c: rng.choice([4, 5, 5]) for c in CRITERIA}
    base = {c: rng.choice([3, 4]) for c in CRITERIA}
    hit = {"wrong_number": "correct", "buggy_code": "correct", "no_code": "complete", "incomplete": "complete",
           "terse": "complete", "unclear": "clear", "unsafe_eval": "safe", "unsafe_advice": "safe"}[flaw]
    base[hit] = rng.choice([1, 2])               # the planted flaw scores low on its criterion
    return base


def simulate(rater: str, accuracy: float, hard_accuracy: float, seed: int) -> list[dict]:
    """Label every item; with probability (1 - accuracy) the rater slips."""
    rng = random.Random(seed)
    records = []
    for it in load_candidates():
        p_right = hard_accuracy if it["flaw"] in HARD_FLAWS else accuracy
        roll = rng.random()
        if roll < p_right:
            choice = it["gold"]
        elif roll < p_right + (1 - p_right) / 2:
            choice = "tie"                       # unsure -> tie
        else:
            choice = "B" if it["gold"] == "A" else "A"   # a real mistake
        sa = scores_for(it["gold"] == "A", it["flaw"], rng)
        sb = scores_for(it["gold"] == "B", it["flaw"], rng)
        records.append(make_record(it, rater, choice, sa, sb, note="simulated"))
    return records


def main():
    out = DATA / "ratings.jsonl"
    # Start fresh but keep any real (non-simulated) ratings already in the file.
    from .ratings import read_jsonl
    keep = [r for r in read_jsonl(out) if not r["rater"].startswith("sim_")]
    out.write_text("", encoding="utf-8")
    for r in keep:
        append_jsonl(out, r)
    for rater, acc, hard, seed in [("sim_rater_1", 0.95, 0.75, 1), ("sim_rater_2", 0.90, 0.65, 2)]:
        for r in simulate(rater, acc, hard, seed):
            append_jsonl(out, r)
    print(f"wrote simulated ratings for 2 raters (+{len(keep)} real ratings kept) -> data/ratings.jsonl")


if __name__ == "__main__":
    main()
