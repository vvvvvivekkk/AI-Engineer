"""
notebook_sources.py - cell-by-cell content of the module 16 notebooks.
build.py imports NOTEBOOKS and writes each list with build_kit.notebook().
"""


def M(text):
    return ("md", text)


def C(text):
    return ("code", text)


LOADER = r'''
import pathlib, urllib.request

RAW = "https://raw.githubusercontent.com/vvvvvivekkk/AI-Engineer/main/16-careers/data/"

def data_path(name: str) -> pathlib.Path:
    """Find a data file locally (repo checkout) or download it (Colab)."""
    for p in [pathlib.Path("../data") / name, pathlib.Path("data") / name, pathlib.Path(name)]:
        if p.exists():
            return p
    target = pathlib.Path(name)
    urllib.request.urlretrieve(RAW + name, target)      # works in Colab once the repo is public
    return target
print("loader ready")
'''

# ---------------------------------------------------------------------------
NB01 = [
    M(r'''
# 01 · Resume keyword matcher

Many companies first store and search applications in an **ATS** (Applicant Tracking System — software that lets recruiters filter resumes by keywords). In this notebook we build a small, honest version of that filter so you can check your own resume against a **JD** (job description).

**What you will learn**
1. Clean text and count words — and why raw word counts are noisy.
2. Match skills using a vocabulary with **synonyms** ("FAISS" counts as "vector database").
3. Measure overall similarity with **TF-IDF** and cosine similarity.
4. Find important JD phrases missing from your resume.
5. (Optional) match each JD requirement to your best resume bullet with sentence **embeddings**.

**Honesty rule:** only add a keyword to your resume if you really have the skill. Interviews will test it.
'''),
    M(r'''
## Step 1 — load a sample resume and job description

The files live in `16-careers/data/`. The helper looks for them locally and downloads them in Colab. Replace them with your own text later (paste into the variables).
'''),
    C(LOADER),
    M(r'''
Now read both files into Python strings and peek at the first lines.
'''),
    C(r'''
resume = data_path("sample_resume.txt").read_text(encoding="utf-8")
jd = data_path("sample_job_description.txt").read_text(encoding="utf-8")
print(resume[:400], "...\n")
print(jd[:400], "...")
'''),
    M(r'''
## Step 2 — normalise and split into words

**Normalising** text means making it uniform: lower-case, single spaces. Then a **regular expression** (a pattern for finding text) splits it into words. We keep characters like `/`, `+`, `-` inside words so "ci/cd" and "fine-tuning" survive.
'''),
    C(r'''
import re
from collections import Counter

def normalise(text):
    return re.sub(r"\s+", " ", text.lower())

def words(text):
    return re.findall(r"[a-z][a-z0-9+/.-]*[a-z0-9]", normalise(text))

print(words("Build RAG pipelines with FAISS, CI/CD and fine-tuning (LoRA)."))
'''),
    M(r'''
## Step 3 — naive overlap, and why it is misleading

Count the most common JD words and check which appear in the resume. Look at the top of the list: words like "and", "with", "you" dominate. These are **stop words** — very common words that carry little meaning.
'''),
    C(r'''
jd_counts = Counter(words(jd))
resume_words = set(words(resume))
for w, c in jd_counts.most_common(12):
    print(f"{c:3d}  {w:15s} {'in resume' if w in resume_words else '-'}")
'''),
    M(r'''
## Step 4 — remove stop words

scikit-learn ships a list of English stop words. Removing them leaves the words that describe the job.
'''),
    C(r'''
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

jd_content = Counter(w for w in words(jd) if w not in ENGLISH_STOP_WORDS)
for w, c in jd_content.most_common(15):
    print(f"{c:3d}  {w:15s} {'in resume' if w in resume_words else 'MISSING'}")
'''),
    M(r'''
## Step 5 — a skill vocabulary with synonyms

Single words still miss the point: the JD says "vector database", the resume says "FAISS" — the same skill. So we define **canonical skills** with the different ways people write them, and match whole words only (so "rag" does not match inside "storage").
'''),
    C(r'''
SKILLS = {
    "python": ["python"], "sql": ["sql", "postgres", "mysql"], "git": ["git", "github"],
    "pytest / testing": ["pytest", "unit test", "unit testing", "tests"],
    "pytorch": ["pytorch", "torch"], "transformers / hugging face": ["hugging face", "transformers", "distilbert"],
    "llm apis": ["openai api", "anthropic", "llm api", "llm apis"],
    "prompt engineering": ["prompt engineering", "prompting"],
    "structured outputs": ["structured output", "structured outputs", "json schema"],
    "rag": ["rag", "retrieval-augmented", "retrieval augmented"],
    "embeddings": ["embedding", "embeddings", "sentence-transformers", "minilm"],
    "vector database": ["vector database", "faiss", "qdrant", "pgvector", "chroma"],
    "hybrid search / reranking": ["hybrid search", "bm25", "reranking", "reranker"],
    "agents / tool calling": ["agent", "agents", "tool calling", "function calling"],
    "langgraph": ["langgraph"], "fastapi / rest apis": ["fastapi", "rest api", "rest apis"],
    "docker": ["docker", "container"], "kubernetes": ["kubernetes"], "ci/cd": ["ci/cd", "github actions"],
    "cloud": ["aws", "gcp", "azure", "cloud"],
    "evaluation / evals": ["evaluation", "evals", "evaluated", "hit rate"],
    "observability": ["observability", "langfuse", "monitoring"],
    "guardrails / security": ["guardrails", "pii", "prompt injection", "red-teaming"],
    "fine-tuning": ["fine-tuning", "fine-tuned", "lora"],
    "streamlit / gradio": ["streamlit", "gradio"],
    "rubrics / annotation": ["rubric", "rubrics", "annotation", "rated and ranked"],
    "communication": ["communication", "documentation", "written english"],
}

def find_skills(text):
    t = normalise(text)
    return {name for name, variants in SKILLS.items()
            if any(re.search(r"(?<![a-z0-9])" + re.escape(v) + r"(?![a-z0-9])", t) for v in variants)}

jd_skills, cv_skills = find_skills(jd), find_skills(resume)
matched, missing = sorted(jd_skills & cv_skills), sorted(jd_skills - cv_skills)
print(f"Coverage: {len(matched)}/{len(jd_skills)} = {len(matched)/len(jd_skills):.0%}")
print("Matched:", matched)
print("Missing:", missing)
'''),
    M(r'''
## Step 6 — TF-IDF similarity

**TF-IDF** ("term frequency – inverse document frequency") gives each word a weight: high if it appears often in *this* text but is not common everywhere. Each text becomes a vector of weights. **Cosine similarity** measures how much two vectors point the same way (0 = nothing shared, 1 = identical word use).

The number on its own means little; use it to **compare versions** of your resume against the same JD.
'''),
    C(r'''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
m = vec.fit_transform([resume, jd])
print(f"TF-IDF cosine similarity: {cosine_similarity(m[0], m[1])[0, 0]:.3f}")

terms = vec.get_feature_names_out()
jd_weights = m[1].toarray()[0]
top = jd_weights.argsort()[::-1][:12]
print("Most important JD terms:", [terms[i] for i in top])
'''),
    M(r'''
## Step 7 — frequent JD phrases missing from the resume

Two-word phrases ("vector database", "human-in-the-loop approval") often carry more meaning than single words. We count 1- and 2-word phrases in the JD and list the frequent ones that never appear in the resume.
'''),
    C(r'''
def missing_phrases(resume, jd, top=12):
    ws = [w for w in words(jd) if w not in ENGLISH_STOP_WORDS]
    grams = ws + [" ".join(p) for p in zip(ws, ws[1:])]
    r = normalise(resume)
    return [(g, c) for g, c in Counter(grams).most_common() if g not in r][:top]

for phrase, n in missing_phrases(resume, jd):
    print(f"{n}x  {phrase}")
'''),
    M(r'''
## Step 8 — visualise matched vs missing skills

A quick chart makes the gap obvious — useful when coaching students one-to-one.
'''),
    C(r'''
import matplotlib.pyplot as plt
labels = matched + missing
colors = ["#0f9d9a"] * len(matched) + ["#d1495b"] * len(missing)
plt.figure(figsize=(9, 0.35 * len(labels) + 1))
plt.barh(labels, [1] * len(labels), color=colors)
plt.xticks([]); plt.gca().invert_yaxis()
plt.title(f"JD skills: {len(matched)} matched (teal) vs {len(missing)} missing (red)")
plt.tight_layout(); plt.show()
'''),
    M(r'''
## Step 9 — an honest improvement

Suppose the candidate *really did* use FastAPI, Docker and pytest in the Campus Policy Assistant but forgot to say so, and *really did* write the evaluation set. We add one truthful bullet and re-score. (Never add skills you do not have.)
'''),
    C(r'''
resume_v2 = resume.replace(
    "- Deployed a Streamlit demo used by 120 students in the first week.",
    "- Deployed a Streamlit demo used by 120 students in the first week.\n"
    "- Served the retriever through a FastAPI REST API packaged with Docker; added pytest tests run by GitHub Actions CI/CD.")

def score(cv):
    s = find_skills(cv) & jd_skills
    m = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform([cv, jd])
    return len(s) / len(jd_skills), cosine_similarity(m[0], m[1])[0, 0]

for name, cv in [("v1", resume), ("v2", resume_v2)]:
    cov, sim = score(cv)
    print(f"{name}: skill coverage {cov:.0%}, TF-IDF similarity {sim:.3f}")
print("Still missing:", sorted(jd_skills - find_skills(resume_v2)))
'''),
    M(r'''
## Step 10 — which role fits this resume better?

Run the same resume against a second JD — a freelance **AI trainer (Python coding)** role. Comparing coverage across JDs helps choose where to apply first.
'''),
    C(r'''
jd_trainer = data_path("jd_ai_trainer.txt").read_text(encoding="utf-8")
for name, text in [("Junior AI Engineer", jd), ("AI Trainer - Python", jd_trainer)]:
    need = find_skills(text)
    have = need & cv_skills
    print(f"{name:22s} coverage {len(have)}/{len(need)} = {len(have)/len(need):.0%}   missing: {sorted(need - have)}")
'''),
    M(r'''
## Step 11 (optional) — match each requirement to your best bullet with embeddings

Keywords miss meaning: "evaluation datasets" and "hand-written questions" are related but share no words. **Sentence embeddings** turn each sentence into a vector so that similar meanings are close. We use the small `all-MiniLM-L6-v2` model (downloads ~90 MB from Hugging Face once). If it cannot load, the cell skips politely.
'''),
    C(r'''
reqs = [l.strip("- ").strip() for l in jd.splitlines() if l.strip().startswith("- ")]
bullets = [l.strip("- ").strip() for l in resume.splitlines() if l.strip().startswith("- ")]
try:
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    sims = util.cos_sim(model.encode(reqs), model.encode(bullets))
    for i, r in enumerate(reqs):
        j = int(sims[i].argmax())
        flag = "weak - add evidence?" if sims[i, j] < 0.35 else ""
        print(f"{float(sims[i, j]):.2f} | REQ: {r[:70]}\n     | BEST: {bullets[j][:70]} {flag}\n")
except Exception as e:
    print("Embedding model unavailable, skipping:", type(e).__name__)
'''),
    M(r'''
## Recap

- Raw word counts are noisy; remove stop words and match **skills with synonyms**.
- TF-IDF similarity is for comparing *versions* of your resume against one JD, not an absolute grade.
- Missing-phrase lists and requirement-to-bullet matching show where to add **truthful** evidence.
- The same code lives in `code/resume_matcher.py`: `python code/resume_matcher.py my_resume.txt jd.txt`.

**Try it yourself:** paste your own resume and a real JD you want, list the top three truthful additions, and re-score.
'''),
]

# ---------------------------------------------------------------------------
NB02 = [
    M(r'''
# 02 · Mock interview quiz runner

Practise with the module's **137-question interview bank** (model answers included) and **33 multiple-choice questions**, fully offline.

**What you will learn**
1. Load and explore the question bank with pandas.
2. Run a multiple-choice quiz (automatic marking).
3. Practise open questions and get a rough **self-check score** for your typed answer.
4. Build a balanced mock-interview set.
5. Schedule reviews with **spaced repetition** (Leitner boxes).

The notebook runs without typing (so it can be tested automatically). Set `INTERACTIVE = True` to answer with the keyboard. For a terminal version: `python code/quiz_runner.py mcq --n 10`.
'''),
    M(r'''
## Step 0 — settings and the data loader

`INTERACTIVE = False` uses pre-written demo answers. Switch it to `True` when practising for real.
'''),
    C(LOADER + r'''
INTERACTIVE = False      # set True to type your own answers
'''),
    M(r'''
## Step 1 — load and explore the bank

Each row has a category, a level (junior / mid / senior), the question and a model answer. `value_counts` counts rows per category.
'''),
    C(r'''
import pandas as pd
bank = pd.read_csv(data_path("question_bank.csv"))
mcq = pd.read_csv(data_path("mcq.csv"))
print(len(bank), "open questions,", len(mcq), "multiple-choice questions\n")
print(pd.crosstab(bank.category, bank.level))
'''),
    M(r'''
## Step 2 — a chart of the bank

Useful for planning: which areas have the most questions, and at which level.
'''),
    C(r'''
import matplotlib.pyplot as plt
pd.crosstab(bank.category, bank.level)[["junior", "mid", "senior"]].plot.barh(stacked=True, figsize=(8, 4.5),
                                                                             color=["#9fb3c8", "#0f9d9a", "#1b263b"])
plt.title("Interview question bank by category and level"); plt.xlabel("questions"); plt.tight_layout(); plt.show()
'''),
    M(r'''
## Step 3 — the multiple-choice quiz

`run_mcq` shows each question and its options, takes an answer, marks it and explains. In demo mode the "answers" come from a list, so the run is repeatable. `random_state` makes the question sample the same every run.
'''),
    C(r'''
def run_mcq(questions, answers=None):
    score = 0
    for i, (_, q) in enumerate(questions.iterrows()):
        print(f"Q{i+1} [{q.category}] {q.question}")
        for letter in "ABCD":
            print(f"    {letter}) {q[letter]}")
        ans = input("Answer A-D: ").strip().upper() if INTERACTIVE else answers[i]
        ok = ans == q.correct
        score += ok
        print(f"    you: {ans} -> {'correct' if ok else 'wrong, answer ' + q.correct}. {q.explanation}\n")
    print(f"Score {score}/{len(questions)}")
    return score

quiz = mcq.sample(5, random_state=3)
run_mcq(quiz, answers=list(quiz.correct.iloc[:3]) + ["A", "D"])   # demo: 3 right, then guesses
'''),
    M(r'''
## Step 4 — open questions and a rough self-check score

Real interviews are open-ended. We compare your answer with the model answer by **keyword overlap**: the share of the model answer's content words (4+ letters, not stop words) that your answer contains. It is a *rough guide* — a good answer in different words can score low — so always read the model answer and judge the meaning yourself.
'''),
    C(r'''
import re
STOP = set("a an the and or of to in on for is are be with by it its as that this from at can you your use used "
           "using into than then so not no do does how what why when which who more most also each their they them".split())

def keywords(text):
    return {w for w in re.findall(r"[a-z][a-z0-9-]{3,}", text.lower()) if w not in STOP}

def overlap(answer, model_answer):
    target = keywords(model_answer)
    return len(target & keywords(answer)) / len(target)

q = bank[bank.question.str.startswith("Precision vs recall")].iloc[0]
weak = "Precision and recall are metrics for models."
strong = ("Precision is the share of predicted positives that are really positive; recall is the share of real "
          "positives the model finds. For cancer screening recall matters most, for a spam filter precision. "
          "F1 balances both.")
print("Q:", q.question)
for label, ans in [("weak", weak), ("strong", strong)]:
    print(f"{label:6s} answer -> overlap {overlap(ans, q.model_answer):.0%}")
print("\nModel answer:", q.model_answer)
'''),
    M(r'''
## Step 5 — a second opinion with TF-IDF

**TF-IDF cosine similarity** (see notebook 01) weighs rare, meaningful words more than common ones. Comparing two scorers shows that both rank the strong answer higher — and that neither is a real grader. In real practice, a friend, a mentor, or an LLM given the model answer as a rubric gives better feedback.
'''),
    C(r'''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vec = TfidfVectorizer(stop_words="english").fit(bank.model_answer)    # learn word weights from the whole bank
def tfidf_sim(a, b):
    m = vec.transform([a, b])
    return cosine_similarity(m[0], m[1])[0, 0]

for label, ans in [("weak", weak), ("strong", strong)]:
    print(f"{label:6s} TF-IDF similarity {tfidf_sim(ans, q.model_answer):.2f}")
'''),
    M(r'''
## Step 6 — practise a few open questions

`practise` asks each question, collects an answer (typed, or from the demo list), and prints both scores plus the model answer. Use the feedback to rewrite your answer out loud.
'''),
    C(r'''
def practise(questions, demo_answers=None):
    results = []
    for i, (_, q) in enumerate(questions.iterrows()):
        print(f"\nQ{i+1} [{q.category} / {q.level}] {q.question}")
        ans = input("> ") if INTERACTIVE else demo_answers[i]
        o, t = overlap(ans, q.model_answer), tfidf_sim(ans, q.model_answer)
        print(f"   your answer: {ans[:100]}")
        print(f"   overlap {o:.0%} | tf-idf {t:.2f}")
        print(f"   model answer: {q.model_answer[:220]}...")
        results.append({"question": q.question, "overlap": round(o, 2), "tfidf": round(t, 2)})
    return pd.DataFrame(results)

picked = bank[bank.category.isin(["RAG", "LLMOps"])].sample(3, random_state=1)
demo = ["You search documents first and give the chunks to the model so it can answer with citations.",
        "I don't know.",
        "Use percentiles because the average hides slow requests."]
practise(picked, demo)
'''),
    M(r'''
## Step 7 — build a balanced mock interview

A real loop mixes areas. `mock_interview` picks questions per category in given proportions and prints a script a partner can read to you. `groupby(...).sample` draws from each group.
'''),
    C(r'''
PLAN = {"Python": 2, "Machine Learning": 1, "LLMs": 2, "RAG": 2, "Agents": 1, "LLM System Design": 1, "Behavioural": 2}

def mock_interview(plan, level=None, seed=7):
    pool = bank if level is None else bank[bank.level.isin(level)]
    parts = [pool[pool.category == c].sample(min(n, (pool.category == c).sum()), random_state=seed)
             for c, n in plan.items()]
    return pd.concat(parts).reset_index(drop=True)

script = mock_interview(PLAN, level=["junior", "mid"])
for i, row in script.iterrows():
    print(f"{i+1:2d}. ({row.category}) {row.question}")
print(f"\n{len(script)} questions - allow about 4 minutes each, 45 minutes in total.")
'''),
    M(r'''
## Step 8 — spaced repetition with Leitner boxes

**Spaced repetition** means reviewing a question just before you would forget it. The **Leitner system** uses boxes: every question starts in box 1 (review tomorrow). Answer well → move up a box (wait longer); answer badly → back to box 1. Below, we simulate two weeks of practice with made-up self-scores.
'''),
    C(r'''
import random, datetime
random.seed(0)
INTERVAL = {1: 1, 2: 3, 3: 7, 4: 14}          # box -> days until next review
start = datetime.date(2026, 12, 1)
cards = {q: {"box": 1, "due": start} for q in bank.question.sample(8, random_state=2)}

for day in range(14):
    today = start + datetime.timedelta(days=day)
    due = [q for q, c in cards.items() if c["due"] <= today]
    for qq in due:
        good = random.random() < 0.65 + 0.08 * cards[qq]["box"]     # easier the more you have practised
        cards[qq]["box"] = min(4, cards[qq]["box"] + 1) if good else 1
        cards[qq]["due"] = today + datetime.timedelta(days=INTERVAL[cards[qq]["box"]])

schedule = pd.DataFrame([{"question": q[:55], "box": c["box"], "next review": c["due"]} for q, c in cards.items()])
schedule.sort_values("next review")
'''),
    M(r'''
## Recap

- The bank has 137 open questions (with model answers) and 33 MCQs; filter by category and level.
- Automatic scores (keyword overlap, TF-IDF) are rough self-checks, not grades — read the model answer.
- Mix areas in mock interviews and practise aloud, ideally with a partner reading the script.
- Spaced repetition (Leitner boxes) puts your time on the questions you keep missing.

**Try it yourself:** set `INTERACTIVE = True`, run Step 6 with five questions from your weakest category, then rewrite your two lowest-scoring answers and try again.
'''),
]

# ---------------------------------------------------------------------------
NB03 = [
    M(r'''
# 03 · Skills gap self-assessment

Compare your skills with what six AI roles typically need, find your biggest gaps, and turn them into a week-by-week learning plan.

**What you will learn**
1. Read a **skills matrix** (skills × roles, levels 0–3) and visualise it as a heatmap.
2. Rate yourself and compute a **readiness score** per role.
3. Draw a **radar chart** comparing you with a target role.
4. Find which roles are similar (so skills transfer).
5. Generate a simple learning plan from your gaps.

Levels: **0** not needed · **1** basic awareness · **2** working knowledge · **3** strong / could teach it. The matrix is our judgement of typical entry-to-mid-level adverts (late 2026) — real JDs vary.
'''),
    M(r'''
## Step 1 — load the matrix

The CSV has one row per skill, the course module that teaches it, and one column per role.
'''),
    C(LOADER + r'''
import pandas as pd
matrix = pd.read_csv(data_path("skills_matrix.csv"))
ROLES = [c for c in matrix.columns if c not in ("skill", "module")]
print(ROLES)
matrix.head()
'''),
    M(r'''
## Step 2 — heatmap of what each role needs

Darker = higher level needed. Read down a column to see a role's profile; read across a row to see where a skill matters.
'''),
    C(r'''
import matplotlib.pyplot as plt
import numpy as np
fig, ax = plt.subplots(figsize=(9, 9))
im = ax.imshow(matrix[ROLES].values, cmap="Blues", vmin=0, vmax=3)
ax.set_xticks(range(len(ROLES)), ROLES, rotation=35, ha="right")
ax.set_yticks(range(len(matrix)), matrix.skill)
for i in range(len(matrix)):
    for j in range(len(ROLES)):
        ax.text(j, i, matrix[ROLES].iat[i, j], ha="center", va="center", fontsize=8)
fig.colorbar(im, shrink=0.5, label="level needed"); ax.set_title("Skills matrix: level needed by role")
plt.tight_layout(); plt.show()
'''),
    M(r'''
## Step 3 — rate yourself

Edit the numbers below honestly (0–3). The example is a learner who has finished the Python, data and LLM modules but not deployment yet. A rating of 3 means you could teach it.
'''),
    C(r'''
my_ratings = {
    "Python programming": 3, "Git & GitHub": 2, "Data handling (pandas, SQL)": 2, "Math & statistics intuition": 1,
    "Classic ML (scikit-learn, metrics)": 2, "Deep learning (PyTorch)": 1, "NLP & transformers": 2,
    "LLM APIs, tokens & cost": 2, "Prompt & context engineering": 2, "RAG & vector search": 2,
    "Agents, tool calling & MCP": 1, "Automation (n8n, webhooks)": 0, "Annotation, rubrics & RLHF": 1,
    "Evaluation design (evals)": 1, "Fine-tuning (LoRA/QLoRA)": 0, "APIs with FastAPI": 1,
    "Docker & cloud deployment": 0, "Monitoring, tracing & cost control": 0, "Guardrails, security & secrets": 1,
    "LLM system design": 0, "Writing & communication": 2, "Domain expertise (law, code, ...)": 1,
}
matrix["me"] = matrix.skill.map(my_ratings)
assert matrix.me.notna().all(), "rate every skill"
matrix[["skill", "me"]].T
'''),
    M(r'''
## Step 4 — readiness per role

For each skill, the **gap** is how many levels you are short (never negative — being above the need is fine). **Readiness** = 1 − (total gap ÷ total levels needed). 100% means you meet every requirement.
'''),
    C(r'''
rows = []
for role in ROLES:
    gap = (matrix[role] - matrix.me).clip(lower=0)
    rows.append({"role": role, "levels needed": int(matrix[role].sum()), "total gap": int(gap.sum()),
                 "readiness": 1 - gap.sum() / matrix[role].sum()})
readiness = pd.DataFrame(rows).sort_values("readiness", ascending=False)
readiness.style.format({"readiness": "{:.0%}"})
'''),
    M(r'''
## Step 5 — radar chart: you vs a target role

A **radar chart** puts each skill on its own spoke; the further out, the higher the level. Where the role's shape sticks out beyond yours, there is a gap.
'''),
    C(r'''
TARGET = "AI Engineer"
labels = matrix.skill.str.split(" \\(").str[0]            # shorter labels
angles = np.linspace(0, 2 * np.pi, len(matrix), endpoint=False).tolist()
angles += angles[:1]
fig = plt.figure(figsize=(8, 8)); ax = plt.subplot(polar=True)
for series, colour, name in [(matrix[TARGET], "#1b263b", TARGET), (matrix.me, "#0f9d9a", "me")]:
    vals = series.tolist() + series.tolist()[:1]
    ax.plot(angles, vals, color=colour, label=name); ax.fill(angles, vals, color=colour, alpha=0.15)
ax.set_xticks(angles[:-1], labels, fontsize=7); ax.set_yticks([1, 2, 3]); ax.set_ylim(0, 3)
ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1)); ax.set_title(f"Me vs {TARGET}")
plt.tight_layout(); plt.show()
'''),
    M(r'''
## Step 6 — the biggest gaps for your target role

Sort the skills by gap size and show which module teaches each one.
'''),
    C(r'''
matrix["gap"] = (matrix[TARGET] - matrix.me).clip(lower=0)
top_gaps = matrix[matrix.gap > 0].sort_values(["gap", TARGET], ascending=False)[["skill", "module", TARGET, "me", "gap"]]
top_gaps
'''),
    M(r'''
## Step 7 — which roles are similar?

If two roles need similar skills, moving between them is easier. **Cosine similarity** between the roles' requirement columns measures this (1 = identical profile).
'''),
    C(r'''
from sklearn.metrics.pairwise import cosine_similarity
sim = pd.DataFrame(cosine_similarity(matrix[ROLES].T.values), index=ROLES, columns=ROLES)
sim.round(2)
'''),
    M(r'''
## Step 8 — turn gaps into a weekly plan

A simple rule: each level of gap needs about **6 hours** of study and practice (a rough guess — adjust it). With a fixed number of hours per week we fill weeks in order of biggest gap first, and print the plan.
'''),
    C(r'''
HOURS_PER_LEVEL, HOURS_PER_WEEK = 6, 8
tasks = [(r.skill, r.module, int(r.gap) * HOURS_PER_LEVEL) for r in top_gaps.itertuples()]
plan, week, left = [], 1, HOURS_PER_WEEK
for skill, module, hours in tasks:
    while hours > 0:
        h = min(hours, left)
        plan.append({"week": week, "skill": skill, "module": module, "hours": h})
        hours -= h; left -= h
        if left == 0:
            week, left = week + 1, HOURS_PER_WEEK
plan = pd.DataFrame(plan)
print(f"About {plan.week.max()} weeks at {HOURS_PER_WEEK} h/week to close all gaps for {TARGET}.")
plan.groupby("week").agg(skills=("skill", lambda s: " + ".join(dict.fromkeys(s))), hours=("hours", "sum")).head(12)
'''),
    M(r'''
## Recap

- A skills matrix turns a vague goal ("get into AI") into specific gaps with modules to study.
- Readiness and radar charts show which role you are closest to *today* — a good first application target.
- Similar roles share skills, so a first job in one is a bridge to another.
- Save your plan: `plan.to_csv("my_plan.csv", index=False)` and re-run this notebook monthly.

The same calculation is in `excel/skills-matrix.xlsx` (Self-assessment sheet, with live formulas) and `code/skills_gap.py`.
'''),
]

NOTEBOOKS = {
    "01-resume-keyword-matcher.ipynb": NB01,
    "02-mock-interview-quiz.ipynb": NB02,
    "03-skills-gap-self-assessment.ipynb": NB03,
}
