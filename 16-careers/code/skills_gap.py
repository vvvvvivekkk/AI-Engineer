"""
skills_gap.py - rate yourself on 22 skills and see your gap for each AI role.

Usage (from the 16-careers folder):
    python code/skills_gap.py              # asks you to rate each skill 0-3
    python code/skills_gap.py --demo       # uses example ratings, no typing
Rating scale: 0 = never used, 1 = basic awareness, 2 = can do it with docs, 3 = strong / could teach it.
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from skills_data import ROLES, SKILLS  # noqa: E402

DEMO = [3, 2, 2, 1, 2, 1, 2, 2, 2, 2, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 2, 1]   # an example learner


def ask_ratings():
    ratings = []
    for skill, module, _ in SKILLS:
        while True:
            raw = input(f"{skill:38s} (module {module}) rate 0-3: ").strip()
            if raw in {"0", "1", "2", "3"}:
                ratings.append(int(raw))
                break
            print("  please type 0, 1, 2 or 3")
    return ratings


def gaps(ratings):
    """For each role: total missing levels, readiness % and the biggest gaps."""
    out = []
    for r, role in enumerate(ROLES):
        need = [levels[r] for _, _, levels in SKILLS]
        missing = [max(0, n - have) for n, have in zip(need, ratings)]
        readiness = 1 - sum(missing) / sum(need)
        worst = sorted(((m, SKILLS[i][0], SKILLS[i][1]) for i, m in enumerate(missing) if m), reverse=True)[:4]
        out.append((role, readiness, worst))
    return sorted(out, key=lambda x: -x[1])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--demo", action="store_true")
    ratings = DEMO if p.parse_args().demo else ask_ratings()
    for role, readiness, worst in gaps(ratings):
        print(f"\n{role:24s} readiness {readiness:5.0%}")
        for m, skill, module in worst:
            print(f"   gap {m}: {skill} -> study module {module}")
