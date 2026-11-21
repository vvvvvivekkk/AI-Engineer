# Module 16 — Trainer notes

## 1. What students should be able to do after the session

- Name the six AI role families and describe a typical day in at least three of them.
- Rate themselves on the skills matrix and name their target role, their readiness and their top three gaps.
- Rewrite a weak resume bullet into an impact bullet and write a LinkedIn headline.
- Explain what an ATS is and use the keyword matcher honestly.
- List scam red flags for AI-trainer and remote job offers.
- Describe the interview loop, answer a behavioural question with STAR, and walk through the 7-step LLM system design framework.
- Leave with a 30-day action list.

## Before you teach

- Read `concepts.md` and skim `interview-question-bank.md`.
- Run the three notebooks (each takes seconds).
- Fill the Self-assessment sheet in `excel/skills-matrix.xlsx` for yourself — you will demo it.
- Prepare one weak resume bullet of your own (or use the ones in exercise 2) to rewrite live.
- Bring two real job descriptions from your local market (one AI engineer, one AI trainer) to replace the samples in notebook 01 — local examples are far more motivating.
- Sensitive topic: some students feel anxious about jobs. Keep the tone practical and encouraging; avoid promising outcomes or quoting salaries (the module deliberately gives none — use the research links).

## 2. Teaching sequence (2-hour session)

| Time | Segment | What you do | Materials |
|---|---|---|---|
| 0:00–0:08 | Hook | Kitchen analogy; each student writes the job title they want in a year. | Slide 1 |
| 0:08–0:30 | Roles | Role map; describe a day in each role; quick quiz (exercise 1 aloud). | Slides 2–5 |
| 0:30–0:45 | Skills gap | Demo the Self-assessment sheet or notebook 03; students rate themselves and find their top role. | Slide 6, `excel/skills-matrix.xlsx`, notebook 03 |
| 0:45–1:00 | Portfolio | What makes a strong project; show a good README; GitHub profile tips. | Slides 7–8, `templates/project-readme-template.md` |
| 1:00–1:05 | Break | — | — |
| 1:05–1:25 | Resume + LinkedIn | Rewrite a weak bullet together; run notebook 01 on the sample, then the honest v2; everyone writes a headline in 2 minutes. | Slides 9–10, notebook 01, templates |
| 1:25–1:35 | Job search | Funnel and tracker; channels; AI-trainer platforms and scam red flags (exercise 4 aloud). | Slides 11–12, `excel/job-search-tracker.xlsx` |
| 1:35–1:55 | Interviews | Loop; 10-minute group system design (support bot); STAR pairs (2 min each). | Slides 13–16, question bank |
| 1:55–2:00 | Wrap-up | Salaries: where to research; 90-day plan; each student commits to 3 actions for the next 30 days. | Slides 17–18 |

For a **1-hour** version: roles (15), skills gap (10), resume + LinkedIn (15), interviews with STAR (15), wrap-up (5). Assign notebooks 01–02 and exercises 5–8 as homework.

## 3. Common student mistakes and how to fix them

| Mistake | Why it hurts | Fix |
|---|---|---|
| Listing every tool ever touched ("expert in 40 technologies") | Recruiters distrust it; interviews expose shallow knowledge | List only what you can discuss for 5 minutes; group skills by category |
| Stuffing keywords for skills they don't have | Passes the ATS, fails the interview, damages trust | Honesty rule; close the gap by building, then add it (exercise 8) |
| Ten half-finished tutorial projects on GitHub | Looks unfocused; nothing proves depth | 2–3 finished projects with READMEs, demos and evaluation numbers; archive the rest |
| Projects they can't explain because AI wrote them | Interviewers ask to modify code live | Rewrite until you understand every line; practise explaining design decisions |
| Responsibility bullets ("responsible for testing") | Says nothing about impact | Action + what + how + result, with a number |
| Mass-applying with one generic resume | Very low reply rate | Tailor the top third for each important application; use referrals and outreach |
| Sending a resume as the first LinkedIn message to strangers | Ignored | Short, specific message with one small ask (templates) |
| Believing "too good to be true" AI-trainer offers | Lost money or identity theft | Red-flag checklist; apply only via official sites; never pay to work |
| Rambling behavioural answers, "we" instead of "I" | Interviewer cannot see their contribution | STAR, 2 minutes, most time on their own Action, finish with a number and lesson |
| Jumping straight into boxes in system design | Misses requirements and trade-offs | Spend the first 5 minutes on requirements; follow the 7-step framework |
| Not asking the interviewer questions | Looks uninterested | Prepare 2–3 questions (concepts.md 7.5) |

## 4. Questions to check understanding (with answers)

1. **What is the main difference between an AI engineer and an ML engineer?** — AI engineers mostly build products on top of existing foundation models (APIs, RAG, agents) and run them in production; ML engineers more often train and evaluate their own models and own the data pipelines.
2. **What is an ATS and how should it change your resume?** — Software that stores applications and lets recruiters filter by keywords; use a simple one-column layout and the JD's wording for skills you really have.
3. **Rewrite: "Worked on a RAG project."** — e.g. "Built a RAG assistant over 800 policy pages with FAISS and BM25; raised hit rate from 0.68 to 0.84 on a 50-question eval set."
4. **Name three scam red flags.** — Paying to join/train/get equipment; payment in gift cards or crypto; urgency pressure; requests for bank passwords/OTPs; contact only via personal accounts.
5. **What does STAR stand for and where should most of the time go?** — Situation, Task, Action, Result; most time on Action (what *you* did).
6. **What is the first step of an LLM system design interview?** — Clarify requirements: users, scale, latency, languages, privacy, budget.
7. **Your applications get almost no replies. What do you change?** — Resume, keywords and targeting; tailor the top third; shift effort to referrals and outreach.
8. **Why does this course not give salary numbers?** — Pay varies hugely by country, city, company, role and experience and changes yearly; research your own market with Levels.fyi, Glassdoor, LinkedIn Salary or local sources.
9. **What makes a portfolio project strong?** — A real problem, runs (demo/video), clean code with tests and no keys, evaluation numbers, a good README, and explained trade-offs.
10. **Why is AI-trainer work a reasonable first step?** — Lower entry barrier, remote, builds evaluation and rubric skills and AI familiarity; but work is uneven, so treat it as side income or a bridge.

## 5. Adapting for faster or slower groups

**Slower groups / earlier in the course**
- Focus on roles, the skills matrix and the AI-trainer path (most accessible); keep interviews to STAR and the MCQ quiz.
- Do notebook 01 together; skip the embeddings step.
- Exercises 1, 2, 4 and 5 in class.

**Faster groups / job-ready students**
- Replace the samples with each student's real resume and a real JD; run notebook 01 individually.
- Run full mock interviews in pairs using a script from notebook 02 step 7, with the partner using the model answers as a rubric.
- Timed system design (exercise 10) in small groups, then present to the class.
- Start the two-week job-search sprint (exercise 11) and review Funnel sheets together next session.
- Extension: have students add three questions to the bank (exercise 12) — writing model answers deepens their own understanding.
