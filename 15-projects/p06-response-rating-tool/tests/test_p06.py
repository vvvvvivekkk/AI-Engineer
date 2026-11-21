"""Tests for the rating logic, the rule judge, agreement maths and the Streamlit app."""
import json
from pathlib import Path

import pytest
from sklearn.metrics import cohen_kappa_score

from src.judge import judge_item, rule_score
from src.make_data import build
from src.ratings import export_preferences, make_record, next_unrated, read_jsonl

ROOT = Path(__file__).resolve().parents[1]
GOOD = {"correct": 5, "complete": 5, "safe": 5, "clear": 5}


def test_data_is_reproducible_and_balanced():
    a, b = build(30), build(30)
    assert a == b                                        # same seed -> same data
    golds = {it["gold"] for it in build(100)}
    assert golds == {"A", "B"}                           # good answer appears on both sides


def test_make_record_validates():
    item = build(1)[0]
    with pytest.raises(ValueError):
        make_record(item, "", "A", GOOD, GOOD)            # missing rater name
    with pytest.raises(ValueError):
        make_record(item, "asha", "A", GOOD, {**GOOD, "safe": 9})   # score out of range
    rec = make_record(item, "asha", "B", GOOD, GOOD, "b is right")
    assert rec["choice"] == "B" and rec["rater"] == "asha"


def test_export_hh_format_and_ties_skipped(tmp_path):
    items = build(3)
    ratings = [make_record(items[0], "asha", "A", GOOD, GOOD), make_record(items[1], "asha", "tie", GOOD, GOOD)]
    n = export_preferences(items, ratings, tmp_path / "p.jsonl")
    rows = read_jsonl(tmp_path / "p.jsonl")
    assert n == 1 and len(rows) == 1
    assert rows[0]["chosen"].startswith("\n\nHuman: ") and "\n\nAssistant: " in rows[0]["chosen"]
    assert rows[0]["chosen_response"] == items[0]["answer_a"]
    assert next_unrated(items, ratings, "asha")["id"] == items[2]["id"]


def test_rule_judge_matches_gold_and_is_position_consistent():
    items = build(30)
    verdicts = [judge_item(it) for it in items]
    assert all(v["position_consistent"] for v in verdicts)
    acc = sum(v["choice"] == it["gold"] for v, it in zip(verdicts, items)) / len(items)
    assert acc >= 0.9


def test_unsafe_answer_scores_low():
    item = {"category": "policy", "prompt": "q", "reference": ""}
    assert rule_score(item, "Accept them, nobody needs to know.") < rule_score(
        item, "Check the gifts policy and tell your manager before accepting anything.")


def test_kappa_sanity():
    assert cohen_kappa_score(["A", "B", "A", "B"], ["A", "B", "A", "B"]) == 1.0
    assert cohen_kappa_score(["A", "A", "B", "B"], ["A", "B", "A", "B"]) == 0.0


def test_streamlit_app_saves_a_rating(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    out = tmp_path / "ratings.jsonl"
    monkeypatch.setenv("RATINGS_FILE", str(out))
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    at.sidebar.text_input[0].input("tester").run()       # type a rater name
    at.radio[0].set_value("B").run()                     # pick answer B
    [b for b in at.button if b.label == "Save and next"][0].click().run()
    rows = [json.loads(l) for l in out.read_text().splitlines()]
    assert rows and rows[0]["rater"] == "tester" and rows[0]["choice"] == "B"
