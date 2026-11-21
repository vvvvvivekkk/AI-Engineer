"""
skills_data.py - the skills matrix used by build.py, skills_gap.py and notebook 03.

Levels: 0 = not needed, 1 = basic awareness, 2 = working knowledge, 3 = strong / expert.
These are our own judgement of typical entry-to-mid-level job adverts (late 2026);
real adverts vary, so always read the specific job description.
"""

ROLES = ["AI Trainer / Annotator", "Prompt Engineer", "AI Engineer", "ML Engineer", "MLOps / LLMOps", "AI Product Manager"]

# (skill, course module that teaches it, [level needed for each role in ROLES order])
SKILLS = [
    ("Python programming",                 "01, 02", [1, 2, 3, 3, 3, 1]),
    ("Git & GitHub",                       "00",     [0, 1, 3, 3, 3, 1]),
    ("Data handling (pandas, SQL)",        "02",     [1, 1, 2, 3, 2, 2]),
    ("Math & statistics intuition",        "03",     [1, 1, 2, 3, 1, 1]),
    ("Classic ML (scikit-learn, metrics)", "04",     [0, 1, 2, 3, 2, 1]),
    ("Deep learning (PyTorch)",            "05",     [0, 0, 1, 3, 2, 0]),
    ("NLP & transformers",                 "06",     [1, 2, 2, 3, 1, 1]),
    ("LLM APIs, tokens & cost",            "07",     [1, 3, 3, 2, 2, 2]),
    ("Prompt & context engineering",       "08",     [2, 3, 3, 2, 1, 2]),
    ("RAG & vector search",                "09",     [0, 2, 3, 2, 2, 1]),
    ("Agents, tool calling & MCP",         "10",     [0, 2, 3, 1, 1, 1]),
    ("Automation (n8n, webhooks)",         "11",     [0, 1, 2, 0, 1, 1]),
    ("Annotation, rubrics & RLHF",         "12",     [3, 2, 1, 2, 0, 2]),
    ("Evaluation design (evals)",          "12, 14", [2, 3, 3, 3, 2, 3]),
    ("Fine-tuning (LoRA/QLoRA)",           "13",     [0, 1, 2, 3, 2, 0]),
    ("APIs with FastAPI",                  "14",     [0, 1, 3, 2, 3, 0]),
    ("Docker & cloud deployment",          "14",     [0, 0, 2, 2, 3, 0]),
    ("Monitoring, tracing & cost control", "14",     [0, 1, 2, 2, 3, 2]),
    ("Guardrails, security & secrets",     "14",     [1, 2, 2, 1, 3, 2]),
    ("LLM system design",                  "14, 15", [0, 1, 3, 2, 3, 2]),
    ("Writing & communication",            "16",     [3, 3, 2, 2, 2, 3]),
    ("Domain expertise (law, code, ...)",  "-",      [3, 2, 1, 1, 0, 2]),
]
