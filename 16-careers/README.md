<!-- nav:start -->
> [🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 15 Projects](../15-projects/README.md)  
> **💼 Module 16 · Careers**  
> [📖 Lesson](concepts.md) · [📄 PDF handout](pdf/16-careers-handout.pdf) · [🎞️ Slides](slides/16-careers.pptx) · [📓 Notebooks](notebooks/) · [✍️ Exercises](exercises.md) · [✅ Solutions](solutions/) · [🧑‍🏫 Trainer notes](trainer-notes.md) · [🔗 Resources](resources.md)
<!-- nav:end -->

# Module 16 — Careers in AI (week 24)

Turn the skills from this course into a job: understand the roles, close your skill gaps, build a portfolio, write a resume and LinkedIn profile, find openings (including AI-trainer work) and prepare for interviews.

## Learning goals

After this module you can:

1. Describe six AI role families — AI trainer/annotator, prompt engineer, AI engineer, ML engineer, MLOps/LLMOps, AI product roles — and what each does day to day.
2. Assess your skills against a role with the skills matrix and turn gaps into a weekly plan.
3. Plan and present 2–3 portfolio projects with strong READMEs, demos and evaluation numbers.
4. Write a one-page, ATS-friendly resume with impact bullets, and a keyword-rich LinkedIn profile.
5. Run a tracked job search across job boards, referrals, outreach and AI-trainer platforms, and spot scams.
6. Prepare for recruiter, technical, LLM system design and behavioural (STAR) interviews using a 137-question bank.

## Prerequisites

None strictly — but the module is most useful after modules 07–15, because your portfolio and interview answers draw on them. Notebooks need only basic Python (module 01) and pandas (module 02).

## Time estimate

- Reading `concepts.md`: about 1.5 hours
- Notebooks: about 1.5 hours (three notebooks)
- Templates and exercises: 4–8 hours (writing your real resume and stories takes time)
- Ongoing: interview practice and applications over 90 days (see the plan in `concepts.md`)
- Classroom session: 2 hours (see `trainer-notes.md`)

## Which tool and why

| Task | Tool | Why |
|---|---|---|
| Notebooks 01–03 | **Google Colab** or local Jupyter | Run offline in seconds; Colab needs no setup |
| Typing practice answers (`quiz_runner.py`) | **VS Code** terminal | Interactive `input()` prompts work best in a terminal |
| Resume and LinkedIn writing | Google Docs / Word + the `templates/` | Easy formatting and PDF export |
| Skills matrix, question bank, job tracker | **Excel** or Google Sheets | Live formulas; filter and sort |

## File map

| Path | Contents |
|---|---|
| `concepts.md` | the main lesson (roles, skills, portfolio, resume, LinkedIn, job search, AI-trainer platforms, interviews, salaries, 90-day plan) |
| `interview-question-bank.md` | 137 questions with model answers + 33 MCQs (generated from `code/question_bank_data.py`) |
| `notebooks/01-resume-keyword-matcher.ipynb` | skill matching with synonyms, TF-IDF, missing phrases, optional embeddings |
| `notebooks/02-mock-interview-quiz.ipynb` | explore the bank, MCQ quiz, open-question self-check, mock interview builder, spaced repetition |
| `notebooks/03-skills-gap-self-assessment.ipynb` | heatmap, readiness per role, radar chart, role similarity, weekly plan |
| `code/` | `resume_matcher.py`, `quiz_runner.py`, `skills_gap.py` (command-line versions) + the data sources `question_bank_data.py`, `skills_data.py` |
| `data/` | sample resume, two sample job descriptions, CSVs generated from `code/` |
| `templates/` | resume, LinkedIn, project README, outreach messages, STAR worksheet, cover letter |
| `excel/skills-matrix.xlsx` | skills × roles matrix, self-assessment with live gap and readiness formulas, role profiles |
| `excel/interview-question-bank.xlsx` | all questions with a confidence column, MCQs, summary formulas |
| `excel/job-search-tracker.xlsx` | applications log, funnel rates, job boards and AI-trainer resources, salary research links |
| `slides/16-careers.pptx` | 18-slide deck with speaker notes |
| `pdf/16-careers-handout.pdf` | printable handout of `concepts.md` |
| `exercises.md` / `solutions/` | 12 exercises with worked solutions |
| `trainer-notes.md` | session plan, common mistakes, check questions |
| `resources.md` | curated links |
| `build.py`, `notebook_sources.py` | regenerate everything |

Rebuild: `python 16-careers/build.py` from the repo root.

<!-- nav:start -->
---
[🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 15 Projects](../15-projects/README.md)
<!-- nav:end -->
