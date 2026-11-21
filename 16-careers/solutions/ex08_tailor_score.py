"""
Exercise 8 solution - score a resume before and after honest tailoring.
Run from anywhere:  python ex08_tailor_score.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]          # the 16-careers folder
sys.path.insert(0, str(ROOT / "code"))
from resume_matcher import report                            # noqa: E402

resume = (ROOT / "data" / "sample_resume.txt").read_text(encoding="utf-8")
jd = (ROOT / "data" / "sample_job_description.txt").read_text(encoding="utf-8")

# v2: only truthful additions (per the exercise's assumptions) - testing, an API, documentation.
resume_v2 = resume.replace(
    "- Deployed a Streamlit demo used by 120 students in the first week.",
    "- Deployed a Streamlit demo used by 120 students in the first week.\n"
    "- Exposed retrieval through a FastAPI REST API and covered it with 15 pytest unit tests.",
).replace(
    "- Ran weekly lab sessions for 40 students and wrote Python practice problems.",
    "- Ran weekly lab sessions for 40 students; wrote Python practice problems and their documentation, "
    "improving communication of technical ideas to beginners.",
)

for name, cv in [("v1", resume), ("v2", resume_v2)]:
    r = report(cv, jd)
    print(f"{name}: coverage {r['coverage']:.0%}  tf-idf {r['tfidf']:.3f}")
    print("    missing:", ", ".join(r["missing"]))
