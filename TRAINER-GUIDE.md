# TRAINER GUIDE — how a team of trainers splits and runs this course

This guide is for the **lead trainer** and the **team of trainers** delivering the course. It explains how to learn the material yourself, how to split the work, and how to run each week.

## 1. The two jobs every trainer has

1. **Learn it yourself first.** Study a module the same way a student would: README → concepts.md → notebooks → exercises (attempt them before opening solutions/) → trainer-notes.md. Plan on about **1.5× the student time** the first time you learn a module.
2. **Teach it.** Use the module's `slides/*.pptx` (speaker notes are written for you to read aloud), the session plan in `trainer-notes.md`, and the notebooks for live coding. Hand out `pdf/*-handout.pdf`.

> **Rule of thumb:** do not teach a module you have not finished the exercises for. Students can tell.

## 2. Team roles

| Role | How many | Responsibilities |
|---|---|---|
| **Lead trainer** | 1 | Owns the ROADMAP and calendar, runs the weekly trainer sync, reviews content changes, handles escalations |
| **Module owner** | 1 per 2–3 modules | Becomes the expert on those modules: rehearses the session, keeps links fresh, updates notebooks when libraries change, and coaches other trainers before they teach it |
| **Session trainer** | Rotating | Delivers the live 1–2 hour session from the slides and session plan |
| **Lab assistant / TA** | 1 per ~12 students | Helps during hands-on time, triages setup problems, answers questions in the chat channel |
| **Project mentor** | 1 per ~8 students | Reviews project work from 15-projects, runs code reviews and mock interviews (16-careers) |

### Suggested split for a team of 5 trainers

| Trainer | Owns modules | Why grouped |
|---|---|---|
| A (lead) | 00-setup, 16-careers, 15-projects coordination | Start and end of the journey; logistics |
| B | 01-python-basics, 02-python-for-data, 03-math-for-ai | Foundations; same teaching style |
| C | 04-machine-learning, 05-deep-learning, 06-nlp-and-transformers | Classic ML → DL → NLP build on each other |
| D | 07-llms-and-genai, 08-prompt-and-context-engineering, 09-rag | The LLM core; same APIs and tools |
| E | 10-agentic-ai, 11-ai-automation, 12-data-annotation-and-rlhf, 13-fine-tuning, 14-deployment-and-llmops | Advanced engineering; can pair with D on 13–14 |

With 3 trainers: merge B+C and D+E. With 8+: give every pair of modules its own owner and add a dedicated setup/IT trainer for week 1.

## 3. Ramp-up plan for a brand-new trainer team (before the cohort starts)

| Week | Everyone | Module owners |
|---|---|---|
| −4 | Do 00-setup and 01 as students | Pick modules; read their trainer-notes.md |
| −3 | Do 02–03 | Learn your modules fully, run every notebook, attempt every exercise |
| −2 | Skim 04–09 concepts.md | Rehearse your first session in front of 2 other trainers; fix anything unclear in the repo (open a PR) |
| −1 | Skim 10–16 concepts.md | Dry-run the week-1 setup session with real laptops on Windows, macOS and Linux |

## 4. Running a week

- **Monday:** students read concepts.md and start notebook 1 (async).
- **Mid-week live session (1–2 h):** follow the session plan in `trainer-notes.md`: hook/analogy → concept with slides → live coding from the notebook → paired exercise → recap and questions.
- **Lab hours (1 h, TA-led):** debug help, exercises.
- **Friday:** students submit exercises (a GitHub repo link); the checkpoint in ROADMAP.md is the pass bar.
- **Weekly trainer sync (30 min):** what confused students, which notebook broke, which links are stale. The module owner fixes the repo.

## 5. Teaching principles for this course

1. **Analogy first, then the term, then the code.** Every concepts.md is written in this order. Keep it.
2. **Define jargon out loud** the first time you say it, even if it's on the slide.
3. **Live-code, don't paste.** Type the notebook code during the session and make mistakes on purpose. Reading a traceback together is one of the most valuable things you can show.
4. **Run notebooks in Colab during class** unless the module README says otherwise. It removes install problems. Use local VS Code for modules 00, 11 and 14, where the local tools are the point.
5. **Keys and secrets:** never show a real API key on a projected screen. Use Colab Secrets or a `.env` file, and show the `.env.example` instead.
6. **Check understanding** with the questions in trainer-notes.md before moving on, not at the end.

## 6. Assessment

| What | Weight | Where |
|---|---|---|
| Weekly exercises | 30% | `exercises.md` in each module (solutions are for trainers and self-checking) |
| Projects 1–9 | 40% | `15-projects/` — use each project README's "how to explain it in an interview" section as the oral check |
| Capstone (Project 10) + demo | 20% | 5-minute demo + Q&A |
| Mock interview | 10% | `16-careers/` question bank |

## 7. Keeping the repo healthy

- Each module has a `build.py`. After editing concepts.md or the notebook source, run `python NN-module/build.py` to regenerate slides, PDF, notebooks and Excel files.
- Before committing, run `python tools/check_module.py NN-module --run`. It must print `[PASS]`.
- Model names, prices and library APIs change often. Module owners review links and versions **once a month** (see `resources.md` and `RESOURCES-MASTER.xlsx`).
- Never commit `.env` files or keys. `.gitignore` blocks `.env`, and the checker scans for key-shaped strings.

## 8. Common cohort problems and fixes

| Problem | Fix |
|---|---|
| Half the class stuck on installs in week 1 | Move everyone to Colab for the session; fix local installs in lab hours using the 00-setup troubleshooting sheet |
| Wide skill gap | Use the "faster/slower groups" section in each trainer-notes.md; pair strong with new students |
| Students copy solutions | Grade by oral explanation ("walk me through line 12") rather than by output |
| API costs | Use the offline fallbacks in notebooks and local models (Ollama); give each student a capped key, or use free tiers |
| Library update breaks a notebook | The module owner pins the version in requirements.txt and re-runs `check_module --run` |
