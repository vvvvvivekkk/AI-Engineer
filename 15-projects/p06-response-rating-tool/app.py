"""
app.py - the Streamlit rating app.

**Streamlit** - a Python library that turns a script into a web page. Every time
you click a button, Streamlit re-runs this whole file from top to bottom; values
we want to keep between runs live in `st.session_state` (a dictionary that
survives re-runs, like a sticky note on the fridge).

Run:  streamlit run app.py      then open the link it prints (http://localhost:8501)
"""
import os
from pathlib import Path

import streamlit as st

from src.ratings import CRITERIA, DATA, append_jsonl, export_preferences, load_candidates, make_record, \
    next_unrated, read_jsonl

# RATINGS_FILE lets tests write somewhere temporary instead of the real data file.
RATINGS = Path(os.getenv("RATINGS_FILE", DATA / "ratings.jsonl"))

st.set_page_config(page_title="Response rating tool", layout="wide")
st.title("Which answer is better?")
st.caption("Read the prompt, compare the two answers, score each one, then pick the winner.")

items = load_candidates()                               # the 100 prompts + answer pairs
rater = st.sidebar.text_input("Your rater name", value=st.session_state.get("rater", ""))
st.session_state["rater"] = rater

ratings = read_jsonl(RATINGS)                           # everything saved so far
mine = [r for r in ratings if r["rater"] == rater.strip()]
st.sidebar.metric("Rated by you", f"{len(mine)} / {len(items)}")
st.sidebar.markdown("**Rubric** (1 = poor, 5 = excellent)\n\n- correct\n- complete\n- safe\n- clear")

if st.sidebar.button("Export preference JSONL"):        # turn ratings into chosen/rejected pairs
    n = export_preferences(items, ratings, DATA / "preferences_hh.jsonl", rater=rater.strip() or None)
    st.sidebar.success(f"Wrote {n} pairs to data/preferences_hh.jsonl")

if not rater.strip():
    st.info("Type your rater name in the sidebar to start.")
    st.stop()                                           # stop drawing the page here

item = next_unrated(items, ratings, rater.strip())
if item is None:
    st.success("You have rated every pair. Thank you! Export your preferences from the sidebar.")
    st.stop()

st.subheader(f"{item['id']} · {item['category']}")
st.markdown(f"**Prompt:** {item['prompt']}")

scores = {}
cols = st.columns(2)
for col, side in zip(cols, ["A", "B"]):                 # draw answer A on the left, B on the right
    with col:
        st.markdown(f"### Answer {side}")
        st.markdown(item[f"answer_{side.lower()}"])
        scores[side] = {c: st.slider(f"{c} ({side})", 1, 5, 3, key=f"{item['id']}-{side}-{c}") for c in CRITERIA}

choice = st.radio("Overall, which is better?", ["A", "B", "tie"], horizontal=True, key=f"{item['id']}-choice")
note = st.text_area("Note (why?)", key=f"{item['id']}-note")

if st.button("Save and next", type="primary"):
    try:
        record = make_record(item, rater, choice, scores["A"], scores["B"], note)
    except ValueError as e:                             # friendly message instead of a crash
        st.warning(str(e))
    else:
        append_jsonl(RATINGS, record)                   # one new line in data/ratings.jsonl
        st.rerun()                                      # redraw the page with the next item
