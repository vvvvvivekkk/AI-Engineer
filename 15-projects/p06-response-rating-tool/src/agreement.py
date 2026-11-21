"""
agreement.py - how often does the judge agree with the humans?

**Cohen's kappa** - an agreement score between two raters that removes the
agreement you would get by pure luck. Plain accuracy can fool you: if two raters
both pick "A" 90% of the time, they agree a lot even when guessing. Kappa says:
   1.0 = perfect agreement, 0 = no better than chance, below 0 = worse than chance.
A rough guide: 0.41-0.60 moderate, 0.61-0.80 substantial, above 0.80 almost perfect.

This script compares, item by item:
  human vs human   (inter-annotator agreement - the realistic ceiling)
  judge vs each human
  everyone vs the hidden gold label (only possible because our data is synthetic)

Run:  python -m src.agreement            (uses data/judge_rule.jsonl)
      python -m src.agreement --judge llm
Writes data/agreement_report.json and prints a table.
"""
from __future__ import annotations

import argparse
import json

import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

from .ratings import DATA, load_candidates, read_jsonl

LABELS = ["A", "B", "tie"]


def pair_stats(x: pd.Series, y: pd.Series) -> dict:
    """Raw agreement + Cohen's kappa for two label columns (rows where both exist)."""
    both = pd.concat([x, y], axis=1).dropna()
    if both.empty:
        return {"n": 0, "agreement": None, "kappa": None}
    a, b = both.iloc[:, 0], both.iloc[:, 1]
    kappa = cohen_kappa_score(a, b, labels=LABELS)
    return {"n": int(len(both)), "agreement": round(float((a == b).mean()), 3), "kappa": round(float(kappa), 3)}


def build_table(judge: str = "rule") -> tuple[pd.DataFrame, dict]:
    """One row per item, one column per rater (plus gold); and a stats dict."""
    items = load_candidates()
    ratings = read_jsonl(DATA / "ratings.jsonl") + read_jsonl(DATA / f"judge_{judge}.jsonl")
    df = pd.DataFrame(ratings)
    if df.empty:
        raise SystemExit("No ratings yet. Run `python -m src.simulate_raters` or rate in the app.")
    # pivot: rows = item id, columns = rater, cells = their choice (last one wins if repeated)
    wide = df.drop_duplicates(["id", "rater"], keep="last").pivot(index="id", columns="rater", values="choice")
    wide["gold"] = pd.Series({it["id"]: it["gold"] for it in items})
    wide["category"] = pd.Series({it["id"]: it["category"] for it in items})

    judge_col = f"judge_{judge}"
    humans = [c for c in wide.columns if c not in ("gold", "category") and not c.startswith("judge_")]
    stats = {"judge": judge_col, "pairs": {}}
    for i, h1 in enumerate(humans):                      # every human vs every other human
        for h2 in humans[i + 1:]:
            stats["pairs"][f"{h1} vs {h2}"] = pair_stats(wide[h1], wide[h2])
    for h in humans:                                     # judge vs every human
        if judge_col in wide:
            stats["pairs"][f"{judge_col} vs {h}"] = pair_stats(wide[judge_col], wide[h])
    for r in humans + ([judge_col] if judge_col in wide else []):   # everyone vs gold
        stats["pairs"][f"{r} vs gold"] = pair_stats(wide[r], wide["gold"])
    if judge_col in wide and humans:                     # where does the judge disagree, by category?
        h = humans[0]
        stats["by_category_vs_" + h] = {cat: pair_stats(g[judge_col], g[h])
                                        for cat, g in wide.groupby("category")}
        both = wide[[judge_col, h]].dropna()
        stats["confusion_matrix"] = {"rows_judge_cols_" + h: confusion_matrix(both[judge_col], both[h],
                                                                              labels=LABELS).tolist(),
                                     "labels": LABELS}
    jfile = read_jsonl(DATA / f"judge_{judge}.jsonl")
    if jfile:
        stats["judge_position_consistency"] = round(sum(r["position_consistent"] for r in jfile) / len(jfile), 3)
    return wide, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", choices=["rule", "llm"], default="rule")
    args = ap.parse_args()
    _, stats = build_table(args.judge)
    print(f"{'pair':40s} {'n':>4s} {'agree':>6s} {'kappa':>6s}")
    for name, s in stats["pairs"].items():
        print(f"{name:40s} {s['n']:4d} {s['agreement']!s:>6s} {s['kappa']!s:>6s}")
    if "judge_position_consistency" in stats:
        print(f"judge gave the same verdict in both orders on {stats['judge_position_consistency']:.0%} of items")
    out = DATA / f"agreement_report_{args.judge}.json"
    out.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"saved -> data/{out.name}")


if __name__ == "__main__":
    main()
