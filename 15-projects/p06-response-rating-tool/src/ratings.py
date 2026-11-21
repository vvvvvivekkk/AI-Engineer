"""
ratings.py - the plain-Python "brain" behind the Streamlit app.

Keeping this logic out of app.py means we can test it with pytest without
starting a web page.

Words used here:
  **JSONL** (JSON Lines) - a text file with one JSON object per line. Easy to
      append to, and easy to read line by line. Most training datasets use it.
  **rubric** - a fixed checklist of criteria a rater scores, so different raters
      judge the same things. Ours: correct, complete, safe, clear (1-5 each).
  **HH-RLHF format** - the layout of Anthropic's public "helpful and harmless"
      preference dataset: each line has a "chosen" and a "rejected" conversation,
      written as "\\n\\nHuman: ...\\n\\nAssistant: ...".
"""
from __future__ import annotations

import json
import time
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
CRITERIA = ["correct", "complete", "safe", "clear"]
CHOICES = ["A", "B", "tie"]          # a rater may say both answers are equally good/bad


def load_candidates(path: Path | None = None) -> list[dict]:
    """Read the prompts + candidate answers (data/candidates.json)."""
    return json.loads(Path(path or DATA / "candidates.json").read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    """Read a JSONL file into a list of dicts (empty list if the file is missing)."""
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_jsonl(path: Path, record: dict) -> None:
    """Add one record as a new line at the end of a JSONL file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def make_record(item: dict, rater: str, choice: str, scores_a: dict, scores_b: dict, note: str = "") -> dict:
    """Validate one rating and turn it into a dictionary ready to save.

    Raises ValueError for bad input, so the app can show a friendly warning.
    """
    if not rater.strip():
        raise ValueError("Please type your rater name first.")
    if choice not in CHOICES:
        raise ValueError(f"choice must be one of {CHOICES}")
    for scores in (scores_a, scores_b):
        for c in CRITERIA:
            if not 1 <= int(scores.get(c, 0)) <= 5:
                raise ValueError(f"score for '{c}' must be between 1 and 5")
    return {"id": item["id"], "category": item["category"], "rater": rater.strip(), "choice": choice,
            "scores_a": {c: int(scores_a[c]) for c in CRITERIA},
            "scores_b": {c: int(scores_b[c]) for c in CRITERIA},
            "note": note.strip(), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}


def next_unrated(items: list[dict], ratings: list[dict], rater: str) -> dict | None:
    """The first item this rater has not rated yet (None when they are finished)."""
    done = {r["id"] for r in ratings if r["rater"] == rater}
    return next((it for it in items if it["id"] not in done), None)


def to_hh(prompt: str, chosen: str, rejected: str) -> dict:
    """Write one preference pair in HH-RLHF style (plus plain fields that TRL's DPOTrainer reads)."""
    return {"chosen": f"\n\nHuman: {prompt}\n\nAssistant: {chosen}",
            "rejected": f"\n\nHuman: {prompt}\n\nAssistant: {rejected}",
            "prompt": prompt, "chosen_response": chosen, "rejected_response": rejected}


def export_preferences(items: list[dict], ratings: list[dict], out_path: Path, rater: str | None = None) -> int:
    """Turn ratings into chosen/rejected pairs. Ties are skipped (they teach nothing).

    If rater is None, every rater's labels are exported (one line per rating).
    Returns the number of pairs written.
    """
    by_id = {it["id"]: it for it in items}
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_path.open("w", encoding="utf-8") as fh:
        for r in ratings:
            if r["choice"] == "tie" or (rater and r["rater"] != rater) or r["id"] not in by_id:
                continue
            it = by_id[r["id"]]
            good, bad = (it["answer_a"], it["answer_b"]) if r["choice"] == "A" else (it["answer_b"], it["answer_a"])
            fh.write(json.dumps(to_hh(it["prompt"], good, bad), ensure_ascii=False) + "\n")
            n += 1
    return n
