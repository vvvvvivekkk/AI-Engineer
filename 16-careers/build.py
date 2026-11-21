import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "code"))
from notebook_sources import NOTEBOOKS          # noqa: E402
from question_bank_data import QUESTIONS, MCQS  # noqa: E402
from skills_data import ROLES, SKILLS           # noqa: E402

import csv  # noqa: E402

IMG = HERE / "images"
DATA = HERE / "data"
MOD = "16-careers"

# ---------------------------------------------------------------------------
# 1. Diagrams
# ---------------------------------------------------------------------------
DIAGRAMS = {
    "role_map": """
flowchart LR
    subgraph Data and evaluation
    T[AI trainer / annotator]
    EV[Evaluation specialist]
    end
    subgraph Build with models
    P[Prompt engineer]
    AE[AI engineer]
    end
    subgraph Build and run models
    ML[ML engineer]
    OPS[MLOps / LLMOps]
    end
    subgraph Product and customers
    PM[AI product manager]
    SE[Solutions engineer / DevRel]
    end
    T --> EV
    T --> P
    P --> AE
    AE --> ML
    AE --> OPS
    AE --> SE
    EV --> PM
    AE --> PM
""",
    "portfolio_project": """
flowchart TD
    P[Strong portfolio project] --> A[Real problem<br/>and real user]
    P --> B[Runs: live demo<br/>or 2-min video]
    P --> C[Clean code: tests,<br/>pinned deps, no keys]
    P --> D[Evaluation with<br/>numbers]
    P --> E[README: diagram,<br/>results, how to run]
    P --> F[Your decisions<br/>and trade-offs]
""",
    "job_search_funnel": """
flowchart TD
    A[Applications and outreach<br/>e.g. 100] --> B[Replies / screens<br/>e.g. 10-20]
    B --> C[Technical interviews<br/>e.g. 4-8]
    C --> D[Final rounds<br/>e.g. 2-3]
    D --> E[Offer<br/>1]
    A -.few replies?.-> F[Fix resume, targeting,<br/>use referrals]
    C -.not converting?.-> G[Practise interviews,<br/>system design]
""",
    "interview_loop": """
flowchart LR
    R[Recruiter screen<br/>20-30 min] --> TS[Technical screen<br/>coding or ML/LLM theory]
    TS --> TH[Take-home<br/>sometimes]
    TH --> O[Final loop]
    TS --> O
    O --> O1[Coding]
    O --> O2[LLM system design]
    O --> O3[Project deep-dive]
    O --> O4[Behavioural - STAR]
    O1 --> OF[Offer and negotiation]
    O2 --> OF
    O3 --> OF
    O4 --> OF
""",
    "system_design_framework": """
flowchart TD
    A[1. Requirements<br/>users, scale, latency, privacy] --> B[2. High-level boxes<br/>client, API, model, storage]
    B --> C[3. Data and retrieval<br/>chunking, index, hybrid, access]
    C --> D[4. Model and prompting<br/>hosted vs open, structured output]
    D --> E[5. Evaluation<br/>offline set, online feedback, CI]
    E --> F[6. Production<br/>latency, cost, reliability, safety, tracing]
    F --> G[7. Trade-offs<br/>MVP first, then improvements]
""",
}


def build_diagrams():
    for name, src in DIAGRAMS.items():
        mermaid(src, IMG / f"{name}.png")


# ---------------------------------------------------------------------------
# 2. Data files (CSV) used by notebooks and code/
# ---------------------------------------------------------------------------
def build_data():
    DATA.mkdir(exist_ok=True)
    with open(DATA / "question_bank.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "category", "level", "question", "model_answer"])
        for i, (cat, lvl, q, a) in enumerate(QUESTIONS, 1):
            w.writerow([i, cat, lvl, q, a])
    with open(DATA / "mcq.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "question", "A", "B", "C", "D", "correct", "explanation"])
        for cat, q, opts, correct, expl in MCQS:
            w.writerow([cat, q, *opts, correct, expl])
    with open(DATA / "skills_matrix.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["skill", "module", *ROLES])
        for skill, module, levels in SKILLS:
            w.writerow([skill, module, *levels])


# ---------------------------------------------------------------------------
# 3. The markdown question bank
# ---------------------------------------------------------------------------
def build_question_bank_md():
    cats = list(dict.fromkeys(q[0] for q in QUESTIONS))
    lines = [f"# Interview question bank ({len(QUESTIONS)} questions with model answers)", "",
             "Generated from `code/question_bank_data.py` by `build.py` - edit the Python file, not this one.",
             "Levels: **junior** = expected of any entry-level candidate · **mid** = 1-3 years · **senior** = deeper design and judgement.",
             "", "How to practise: cover the answer, say yours out loud (about one minute), then compare. "
             "Notebook `02-mock-interview-quiz.ipynb` and `code/quiz_runner.py` run quizzes from the same questions.", "",
             "## Contents", ""]
    for c in cats:
        n = sum(q[0] == c for q in QUESTIONS)
        anchor = c.lower().replace(" & ", "--").replace(" ", "-")
        lines.append(f"- [{c}](#{anchor}) ({n})")
    num = 0
    for c in cats:
        lines += ["", f"## {c}", ""]
        for cat, lvl, q, a in QUESTIONS:
            if cat != c:
                continue
            num += 1
            lines += [f"**{num}. {q}** *({lvl})*", "", f"> {a}", ""]
    lines += ["", f"## Multiple-choice warm-up ({len(MCQS)} questions)", ""]
    for i, (cat, q, opts, correct, expl) in enumerate(MCQS, 1):
        opt_txt = " · ".join(f"{l}) {o}" for l, o in zip("ABCD", opts))
        lines += [f"**M{i}. ({cat})** {q}  ", f"{opt_txt}  ", f"*Answer: {correct} - {expl}*", ""]
    (HERE / "interview-question-bank.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 4. Notebooks
# ---------------------------------------------------------------------------
def build_notebooks():
    for name, cells in NOTEBOOKS.items():
        notebook(cells, HERE / "notebooks" / name)


# ---------------------------------------------------------------------------
# 5. Excel workbooks
# ---------------------------------------------------------------------------
def col(i):
    """1 -> A, 2 -> B ... (enough for our small sheets)."""
    return chr(ord("A") + i - 1)


def build_excel():
    # (a) skills matrix + self-assessment with live formulas + role profiles
    n = len(SKILLS)
    matrix = [["Skill", "Taught in module", *ROLES]]
    for skill, module, levels in SKILLS:
        matrix.append([skill, module, *levels])
    matrix.append([])
    matrix.append(["Levels: 0 = not needed, 1 = basic awareness, 2 = working knowledge, 3 = strong / could teach it"])

    self_rows = [["Skill", "Taught in module", "MY RATING (0-3) - edit this column", *[f"Gap: {r}" for r in ROLES]]]
    for i, (skill, module, _) in enumerate(SKILLS, start=2):
        gaps = [f"=MAX(0,'Skills matrix'!{col(3 + j)}{i}-$C{i})" for j in range(len(ROLES))]
        self_rows.append([skill, module, 0, *gaps])
    last = n + 1
    self_rows.append(["READINESS (1 - total gap / total needed)", "", "",
                      *[f"=1-SUM({col(4 + j)}2:{col(4 + j)}{last})/SUM('Skills matrix'!{col(3 + j)}2:{col(3 + j)}{last})"
                        for j in range(len(ROLES))]])

    profiles = [["Role", "What they do", "A typical day includes", "Main tools", "How people get in", "Course modules"]]
    profiles += [
        ["AI Trainer / Annotator", "Create and judge data that trains and evaluates models", "Rating and ranking answers against rubrics, writing gold answers, checking model code, red-teaming", "Annotation platforms, docs, spreadsheets", "Apply to platforms, pass assessment, keep quality high", "07, 08, 12"],
        ["Prompt Engineer", "Design and test prompts and context so LLMs work reliably", "Fixing failures from logs, building test sets, comparing prompt versions, working with domain experts", "LLM consoles, Python scripts, eval tools", "Usually grows out of another role; often merged into AI engineer / product roles", "07, 08, 09, 14"],
        ["AI Engineer", "Build products on top of AI models and run them in production", "RAG features, agents, debugging traces, writing evals, code review, API design", "Python, FastAPI, LLM APIs, vector DBs, LangGraph, Docker, Langfuse", "Portfolio of deployed LLM apps; software or data background", "07-11, 14, 15"],
        ["ML Engineer", "Train, evaluate and deploy ML models and data pipelines", "Investigating metric drops, feature pipelines, retraining, experiments, serving", "Python, SQL, scikit-learn, PyTorch, experiment tracking", "Strong ML projects, internships, research; often a CS/maths degree", "02-06, 12-14"],
        ["MLOps / LLMOps", "Keep model-based systems reliable, scalable, observable and secure", "CI/CD pipelines, GPU serving, dashboards and alerts, incident response, secrets", "Docker, Kubernetes, cloud, GitHub Actions, vLLM, Langfuse", "From DevOps, backend or data engineering", "00, 13, 14"],
        ["AI Product Manager", "Decide what AI features to build and how to measure success", "User research, writing requirements, defining evals and metrics, trade-offs with engineering", "Docs, analytics, prototypes, eval dashboards", "From product, engineering, consulting or domain expertise", "07-10, 12, 14, 16"],
    ]
    workbook({"Skills matrix": matrix, "Self-assessment": self_rows, "Role profiles": profiles},
             HERE / "excel" / "skills-matrix.xlsx",
             col_widths={"Skills matrix": [36, 12] + [16] * len(ROLES),
                         "Self-assessment": [40, 12, 18] + [16] * len(ROLES),
                         "Role profiles": [22, 40, 55, 40, 40, 14]})

    # (b) interview question bank
    allq = [["ID", "Category", "Level", "Question", "Model answer", "My confidence (0-2)", "Last practised"]]
    for i, (c, l, q, a) in enumerate(QUESTIONS, 1):
        allq.append([i, c, l, q, a, "", ""])
    mcq = [["Category", "Question", "A", "B", "C", "D", "Correct", "Explanation"]]
    for c, q, opts, correct, expl in MCQS:
        mcq.append([c, q, *opts, correct, expl])
    cats = list(dict.fromkeys(q[0] for q in QUESTIONS))
    last_row = len(QUESTIONS) + 1
    summary = [["Category", "Questions", "Junior", "Mid", "Senior", "Avg my confidence (fill column F first)"]]
    for k, c in enumerate(cats, start=2):
        summary.append([c, f"=COUNTIF('All questions'!B2:B{last_row},A{k})",
                        f"=COUNTIFS('All questions'!B2:B{last_row},A{k},'All questions'!C2:C{last_row},\"junior\")",
                        f"=COUNTIFS('All questions'!B2:B{last_row},A{k},'All questions'!C2:C{last_row},\"mid\")",
                        f"=COUNTIFS('All questions'!B2:B{last_row},A{k},'All questions'!C2:C{last_row},\"senior\")",
                        f"=IFERROR(AVERAGEIF('All questions'!B2:B{last_row},A{k},'All questions'!F2:F{last_row}),\"-\")"])
    workbook({"All questions": allq, "MCQ": mcq, "Summary": summary},
             HERE / "excel" / "interview-question-bank.xlsx",
             col_widths={"All questions": [6, 18, 9, 50, 90, 14, 14], "MCQ": [16, 50, 22, 22, 22, 22, 9, 50],
                         "Summary": [22, 11, 9, 9, 9, 22]})

    # (c) job-search tracker
    apps = [["Date applied", "Company", "Role", "Link", "Channel (cold / referral / outreach / recruiter / platform)",
             "Status (Applied / Replied / Interview / Final / Offer / Rejected)", "Next step", "Follow-up date", "Notes"]]
    examples = [
        ("2026-12-01", "Example AI Startup", "Junior AI Engineer", "", "referral", "Interview", "Prepare RAG system design", "Tailored resume v3"),
        ("2026-12-02", "Example Bank", "ML Engineer Intern", "", "cold", "Applied", "Wait", ""),
        ("2026-12-03", "Example Platform", "AI Trainer - Python", "", "platform", "Replied", "Take skills test", "Assessment due in 3 days"),
        ("2026-12-04", "Example SaaS", "AI Engineer", "", "outreach", "Rejected", "Ask for feedback", "Needed more Docker experience"),
    ]
    for r, (d, c, role, link, ch, st, nxt, notes) in enumerate(examples, start=2):
        apps.append([d, c, role, link, ch, st, nxt, f"=IF(A{r}=\"\",\"\",IFERROR(TEXT(DATEVALUE(A{r})+7,\"yyyy-mm-dd\"),TEXT(A{r}+7,\"yyyy-mm-dd\")))", notes])
    for r in range(len(examples) + 2, 202):
        apps.append(["", "", "", "", "", "", "", f"=IF(A{r}=\"\",\"\",IFERROR(TEXT(DATEVALUE(A{r})+7,\"yyyy-mm-dd\"),TEXT(A{r}+7,\"yyyy-mm-dd\")))", ""])
    rng = "Applications!F2:F201"
    funnel = [["Stage", "Count", "Rate vs applications", "What a low number suggests"],
              ["Applications", "=COUNTA(Applications!B2:B201)", "", "Apply more consistently (set a weekly target)"],
              ["Replied or further", f"=COUNTIF({rng},\"Replied\")+COUNTIF({rng},\"Interview\")+COUNTIF({rng},\"Final\")+COUNTIF({rng},\"Offer\")",
               "=IFERROR(B3/B2,0)", "Resume, keywords, targeting; use referrals and outreach"],
              ["Interview or further", f"=COUNTIF({rng},\"Interview\")+COUNTIF({rng},\"Final\")+COUNTIF({rng},\"Offer\")",
               "=IFERROR(B4/B2,0)", "Screening calls: practise your story and basics"],
              ["Final round or offer", f"=COUNTIF({rng},\"Final\")+COUNTIF({rng},\"Offer\")", "=IFERROR(B5/B2,0)",
               "Technical depth: system design, project deep-dives"],
              ["Offers", f"=COUNTIF({rng},\"Offer\")", "=IFERROR(B6/B2,0)", "Behavioural answers, negotiation, fit"],
              ["Referral applications", "=COUNTIF(Applications!E2:E201,\"referral\")", "=IFERROR(B7/B2,0)",
               "Network more: referrals usually convert much better"]]
    boards = [["Name", "Link", "Type", "Notes"],
              ["LinkedIn", "https://linkedin.com", "Job board + network", "Main platform; message hiring managers directly"],
              ["Internshala", "https://internshala.com", "Internships (India)", "Many AI/ML and GenAI internships"],
              ["Devpost hackathons", "https://devpost.com/hackathons", "Hackathons", "Ship portfolio projects under a deadline"],
              ["Major League Hacking (MLH)", "https://mlh.io/", "Hackathons / fellowship", "Student hackathon league"],
              ["Kaggle Competitions", "https://www.kaggle.com/competitions", "Competitions", "Public ranked record for ML roles"],
              ["Google Summer of Code", "https://summerofcode.withgoogle.com/", "Open source (paid stipend)", "Mentored open-source work"],
              ["Outreachy", "https://www.outreachy.org/", "Open source internships (paid)", "For people under-represented in tech"],
              ["Google STEP", "https://buildyourfuture.withgoogle.com/programs/step/", "Internship", "For early-year CS students"],
              ["GitHub Student Developer Pack", "https://education.github.com/pack", "Free tools", "Credits and tools for portfolio building"],
              ["aitrainer.work job board", "https://aitrainer.work", "AI-trainer listings", "Aggregator; filter by domain. The site earns referral fees - apply via each platform's official site"],
              ["AI-trainer platform comparison", "https://aitrainer.work/platforms", "AI-trainer guide", "Compare platforms (Mercor, Micro1, Turing, Alignerr, ...) before applying"],
              ["Is AI training legit or a scam?", "https://aitrainer.work/guides/is-ai-training-legit-scam-guide", "Guide", "Red flags to check before sharing ID or time"],
              ["AI training for developers", "https://aitrainer.work/guides/best-ai-training-platforms-developers-coders", "Guide", "Which platforms want coders"],
              ["Entry-level AI-trainer jobs", "https://aitrainer.work/jobs/entry-level", "AI-trainer listings", "Roles needing no prior experience"]]
    salary = [["Source", "Link", "Best for"],
              ["Levels.fyi", "https://www.levels.fyi", "Tech company levels and total compensation"],
              ["Glassdoor salaries", "https://www.glassdoor.com/Salaries/index.htm", "Self-reported pay by company and role"],
              ["LinkedIn Salary", "https://www.linkedin.com/salary/", "Pay ranges by title and location"],
              ["AmbitionBox", "https://www.ambitionbox.com/salaries", "India: salaries and company reviews"],
              ["Note", "", "Pay varies by country, city, company, role and experience - compare several sources and talk to people in your market"]]
    workbook({"Applications": apps, "Funnel": funnel, "Job boards & platforms": boards, "Salary research": salary},
             HERE / "excel" / "job-search-tracker.xlsx",
             col_widths={"Applications": [13, 22, 24, 30, 22, 24, 26, 14, 30], "Funnel": [24, 12, 18, 50],
                         "Job boards & platforms": [32, 55, 26, 60], "Salary research": [22, 50, 60]})


# ---------------------------------------------------------------------------
# 6. Slides
# ---------------------------------------------------------------------------
def build_slides():
    I = lambda n: str(IMG / f"{n}.png")  # noqa: E731
    deck = {
        "title": "Module 16 - Careers in AI",
        "subtitle": "Roles, portfolio, resume, job search and interviews",
        "slides": [
            {"title": "From skills to a job",
             "bullets": ["The chef wants to taste your cooking: portfolio", "Read where you have worked: resume and LinkedIn",
                         "Watch you cook under pressure: interviews", "Today: roles, proof, applications, interview practice"],
             "notes": "Open with the restaurant kitchen analogy. Earlier modules taught cooking; this one is about getting hired. Ask the room: what job title do you want in a year? Write the answers on the board and come back to them at the end."},
            {"title": "The map of AI roles", "image": I("role_map"),
             "bullets": ["Data and evaluation", "Building with models", "Building and running models", "Product and customers",
                         "Careers zig-zag: arrows are common moves"],
             "notes": "Walk the four groups. Stress that nobody needs to start at the top: AI trainer work or a junior AI engineer role are both valid entry points. The arrows show common moves people make after a year or two."},
            {"title": "AI trainer / data annotator",
             "bullets": ["Rates and ranks model answers against rubrics", "Writes gold answers, checks model code, red-teams",
                         "Remote, task-based, often freelance", "Domain expertise pays most", "Great side income and bridge into AI"],
             "notes": "This is the human side of RLHF from module 12. Explain rubrics with a quick example: two answers, one ignores a word limit. Mention that work comes in bursts and that real platforms never charge you to join."},
            {"title": "Prompt engineer and AI engineer",
             "bullets": ["Prompt engineering: now mostly a skill inside other roles", "AI engineer: builds products on top of models",
                         "  RAG, agents, APIs, evals, deployment, cost", "This course's main target role"],
             "notes": "As of late 2026 standalone prompt engineer titles are rarer; the skill lives inside AI engineer and product roles. Describe an AI engineer's day: stand-up, building a RAG feature, debugging a trace, writing an eval, reviewing a pull request."},
            {"title": "ML engineer, MLOps / LLMOps, product roles",
             "bullets": ["ML engineer: trains and deploys models; data and metrics", "MLOps / LLMOps: infrastructure, serving, monitoring, cost",
                         "AI PM: what to build and how to measure it", "Solutions engineer / DevRel: customers and teaching"],
             "notes": "Contrast ML engineers, who train their own models, with AI engineers, who mostly build on foundation models. LLMOps is module 14 as a job. Product roles suit people who like users and decisions more than writing most of the code."},
            {"title": "Skills matrix and self-assessment",
             "bullets": ["22 skills x 6 roles, levels 0-3", "Self-assessment sheet computes your gap per role",
                         "Notebook 03: readiness, radar chart, weekly plan", "Apply first where readiness is highest"],
             "notes": "Open excel/skills-matrix.xlsx and fill the self-assessment live for a volunteer, or use notebook 03. Point out that readiness is a guide, not a verdict, and that the matrix reflects typical adverts; real job descriptions vary."},
            {"title": "A portfolio beats certificates", "image": I("portfolio_project"),
             "bullets": ["Real problem and user", "Runs: demo link or video", "Tests, pinned deps, no keys",
                         "Evaluation with numbers", "README with diagram and results"],
             "notes": "A photographer is hired from photos, not course certificates. Show an example README from module 15. The evaluation-with-numbers point is what separates engineers from tutorial followers: hit rate went from 0.71 to 0.89 after hybrid search."},
            {"title": "GitHub, demos and writing",
             "bullets": ["Profile README + 4-6 pinned repos", "1-3 minute demo videos", "Blog posts explaining what you learned",
                         "Hackathons, Kaggle, open source (GSoC, Outreachy)", "Understand every line, even if AI helped write it"],
             "notes": "Live: show how a profile README works (a repository named like your username). Encourage one short blog post per project. Warn that interviewers ask candidates to explain or modify their own code live."},
            {"title": "Resumes that pass the first filter",
             "bullets": ["One page, one column, standard headings, PDF", "ATS = software that stores and keyword-filters resumes",
                         "Bullet: action + what + how + result", "Mirror the JD's words - only for skills you have"],
             "code": "Weak:  Worked on a chatbot.\n\nStrong: Built a RAG assistant over\n1,200 policy pages (FastAPI, FAISS,\nBM25); raised retrieval hit rate\nfrom 0.71 to 0.89 on a 60-question\neval set.",
             "notes": "Rewrite one weak bullet together with the class. Then run notebook 01 on the sample resume and job description: coverage, missing skills, then the honest improvement in step 9. Repeat the honesty rule."},
            {"title": "LinkedIn and networking",
             "bullets": ["Headline = role + focus + proof", "About: what you do, proof, what you want",
                         "Post weekly about what you build", "Short, specific outreach with one small ask",
                         "Referrals only after real conversations"],
             "notes": "Show templates/linkedin-templates.md and outreach-messages.md. Have each student write their headline in two minutes and read a few aloud. Explain why a referral moves an application up the pile."},
            {"title": "The job-search funnel", "image": I("job_search_funnel"),
             "bullets": ["Track every application", "Few replies: fix resume and targeting", "Interviews not converting: practise",
                         "Mix channels: referrals and outreach convert best"],
             "notes": "The numbers in the diagram are illustrative, not promises. Open excel/job-search-tracker.xlsx: the Funnel sheet computes reply and interview rates from the Applications sheet. Diagnose the weakest stage and fix that first."},
            {"title": "AI-trainer platforms: use them safely",
             "bullets": ["Read reviews and comparisons first", "Apply on each platform's official site", "Assessments test rubric-based rating",
                         "Pay varies widely - check current listings", "Red flags: fees, gift cards, pressure, password requests"],
             "notes": "Name some platforms from our catalogue such as Mercor, Turing, Alignerr and Micro1. Explain that the aggregator site earns referral fees, so we link to its guides but not referral links. Spend a minute on scam red flags; students get these messages."},
            {"title": "The interview loop", "image": I("interview_loop"),
             "bullets": ["Recruiter screen", "Technical screen", "Take-home (sometimes)", "Final loop: coding, system design, project, behavioural"],
             "notes": "Describe each stage and what it tests. Tell students to rehearse a 60 to 90 second introduction for the recruiter screen and to think aloud in coding rounds because reasoning is graded."},
            {"title": "LLM system design framework", "image": I("system_design_framework"),
             "bullets": ["Requirements first", "Boxes, then data and retrieval", "Model choice and prompting",
                         "Evaluation", "Production: latency, cost, safety, tracing", "Trade-offs and MVP"],
             "notes": "Do a 10-minute mini design together: a support chatbot over a help centre. Use the model answer in the question bank as your checklist. Emphasise asking about scale, latency and privacy before drawing anything."},
            {"title": "Behavioural answers with STAR",
             "bullets": ["Situation, Task, Action, Result", "Most time on Action: what YOU did", "Result with numbers and a lesson",
                         "Prepare 6-8 stories; each answers many questions", "Always ask them 2-3 questions"],
             "notes": "Read the filled example in templates/star-story-worksheet.md. Pair students up: each tells one story in two minutes, the partner checks all four parts are present."},
            {"title": "Practise with the question bank",
             "bullets": ["137 questions with model answers, 10 categories", "33 multiple-choice warm-ups",
                         "Notebook 02: quizzes, self-check scores, mock interview scripts", "Spaced repetition for weak questions"],
             "notes": "Open interview-question-bank.md and the Excel version. Run a quick MCQ round with the class using notebook 02. Explain that automatic scores are rough self-checks; the real value is saying answers aloud and comparing."},
            {"title": "Salaries and offers",
             "bullets": ["Pay varies by country, city, company and level", "Research: Levels.fyi, Glassdoor, LinkedIn Salary, AmbitionBox",
                         "Compare the total package", "Early career: weigh learning and mentoring highly"],
             "notes": "This course deliberately gives no salary numbers because they differ hugely by market and change every year. Show the Salary research sheet in the tracker workbook and how to compare several sources."},
            {"title": "Your 90-day plan and exercise",
             "bullets": ["Days 1-30: target role, gaps, 2 projects, resume + LinkedIn", "Days 31-60: tailored applications, outreach, a blog post, mocks",
                         "Days 61-90: third project, system design practice, iterate", "Exercise: tailor your resume to one real JD and score it"],
             "notes": "Return to the job titles written on the board at the start. Ask each student to pick one target role and commit to the first 30-day actions. Set exercises 1 to 5 in class, the rest as homework."},
        ],
    }
    slides(deck, HERE / "slides" / f"{MOD}.pptx")


if __name__ == "__main__":
    build_diagrams()
    build_data()
    build_question_bank_md()
    build_notebooks()
    build_excel()
    build_slides()
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / f"{MOD}-handout.pdf", title="Module 16 - Careers in AI")
    print("built", MOD)
