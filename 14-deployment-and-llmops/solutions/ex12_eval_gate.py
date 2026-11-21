"""
Exercise 12 solution - an eval gate for CI.
Exits with code 1 when the mean score is below EVAL_THRESHOLD, which makes the CI job fail.
Run from anywhere:  python ex12_eval_gate.py      (or EVAL_THRESHOLD=0.9 python ex12_eval_gate.py)
"""
import os
import pathlib
import sys

CODE_DIR = pathlib.Path(__file__).resolve().parents[1] / "code"
sys.path.insert(0, str(CODE_DIR))                 # so "import app" finds code/app
os.environ.pop("ANTHROPIC_API_KEY", None)         # CI evals use the offline model: free and repeatable

from fastapi.testclient import TestClient         # noqa: E402
from app.main import app                          # noqa: E402

# Each case: a question and the words a good answer must contain.
# With the offline echo model these keywords come from the question itself; with a real model
# you would write keywords from a reference answer.
CASES = [
    ("What is Docker?", ["docker"]),
    ("Explain a container image", ["container", "image"]),
    ("What is FastAPI used for?", ["fastapi"]),
    ("Why monitor p95 latency?", ["p95", "latency"]),
    ("What does CI mean?", ["ci"]),
]


def score(answer: str, keywords: list[str]) -> float:
    answer = answer.lower()
    return sum(k in answer for k in keywords) / len(keywords)


def main() -> int:
    threshold = float(os.getenv("EVAL_THRESHOLD", "0.7"))
    client = TestClient(app)
    scores = []
    print(f"{'score':>5}  question")
    for q, kws in CASES:
        r = client.post("/chat", json={"message": q})
        s = score(r.json().get("reply", ""), kws) if r.status_code == 200 else 0.0
        scores.append(s)
        print(f"{s:5.2f}  {q}")
    mean = sum(scores) / len(scores)
    print(f"mean score {mean:.2f} (threshold {threshold})")
    return 0 if mean >= threshold else 1          # non-zero exit code = failed step in CI


if __name__ == "__main__":
    sys.exit(main())
