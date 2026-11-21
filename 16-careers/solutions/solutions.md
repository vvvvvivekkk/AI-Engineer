# Module 16 — Solutions and worked examples

Scripts: `ex08_tailor_score.py` and `ex09_quiz_weakest.py` run from this folder with no setup beyond pandas and scikit-learn. Many exercises produce personal documents, so the solutions below are **worked examples** you can compare against, not the only right answers.

---

## 1. Match the day to the role

a) AI trainer / data annotator (domain-expert rater). b) MLOps / LLMOps engineer. c) AI engineer. d) ML engineer. e) AI product manager.

## 2. Rewrite weak bullets (example numbers are for practice only)

a) "Built a RAG chatbot over 800 pages of college regulations (Python, FAISS, Streamlit); answered 84% of a 50-question test set correctly and was used by 120 students in its first week."
b) "Cleaned and merged 3 attendance datasets (48,000 rows) with pandas, removing 6% duplicate records and cutting report preparation from 2 hours to 10 minutes."
c) "Wrote 25 pytest tests and a 60-case evaluation set for a sentiment model; caught a label-mapping bug that had lowered F1 from 0.91 to 0.74."
d) "Rated and ranked 1,500+ LLM coding responses against detailed rubrics on a freelance AI-training platform, maintaining a top-quartile quality score."

What changed: a strong verb first, concrete objects, tools, and a number that shows impact.

## 3. Headline and About (example)

**Headline:** `Aspiring AI Engineer | RAG, Agents & LLM Evaluation | Built 2 deployed LLM apps · Python, FastAPI, FAISS`

**About:**
> I build practical LLM applications and measure whether they work. My Campus Policy Assistant answers students' questions over 800 pages of regulations, and evaluation-driven tuning raised its retrieval hit rate from 0.68 to 0.84.
>
> I work with Python, FastAPI, FAISS, Hugging Face, LangGraph and Docker, and I care about evaluation, clear documentation and shipping things people actually use. I also rate LLM coding answers as a freelance AI trainer.
>
> I'm looking for junior AI engineer roles or internships (remote or Bengaluru). Happy to talk about RAG evaluation or student-built AI tools — message me here.

Checklist: role + focus + proof in the headline; keywords from target JDs; a clear "what I want" line.

## 4. Spot the scam

a) **Red flag** — legitimate employers never charge onboarding or equipment fees.
b) **Normal** — an assessment on the platform's own site, from its official domain, is how real platforms screen.
c) **Red flag** — gift-card payment and artificial urgency are classic scam signs.
d) **Usually normal** — identity checks on the platform's verified site after you pass screening are common (still confirm the URL is the official domain).
e) **Red flag** — nobody needs your bank login to pay you; never share passwords or OTPs.

## 5. Self-assessment (worked example)

With the example ratings in notebook 03, readiness is highest for **AI Trainer / Annotator (68%)**, then **Prompt Engineer** and **AI Product Manager (63%)**, and lowest for **AI Engineer (54%)**. For the target **AI Engineer**, the biggest gap is *LLM system design* (3 levels), followed by a group of 2-level gaps: *APIs with FastAPI*, *agents/tool calling*, *Docker & deployment*, *monitoring & cost control*, *evaluation design*, *fine-tuning* and *automation*. So revisit modules 14, 10 and 15 first, then 12/13. A sensible strategy: apply for AI-trainer or prompt-focused work now (highest readiness) while closing AI-engineer gaps over the next 8–12 weeks (notebook 03 step 8 estimates the weeks).

## 6. Plan a portfolio (example for an AI-engineer target)

| Project | User and problem | Stack | Evaluation number | Try it |
|---|---|---|---|---|
| Policy Q&A with citations | Students can't find rules in long PDFs | FastAPI, MiniLM, FAISS + BM25, reranker, Streamlit | retrieval hit rate@5 and faithfulness on 60 questions | Streamlit Cloud link + video |
| Meeting-booking agent with approval | Small clinic receptionist books by chat | LangGraph, tool calling, human-in-the-loop, SQLite | task success rate on 30 scripted conversations | Gradio Space |
| Deployed LLM service with monitoring | Any of the above in production | Docker, GitHub Actions, Langfuse, guardrails | p95 latency and cost per 100 requests before/after caching | live API docs + dashboard screenshot |

The README draft should follow the template: one-line pitch, screenshot, architecture diagram, results table, run instructions, trade-offs, limitations.

## 7. STAR stories

Compare yours against the filled example in `templates/star-story-worksheet.md`. Check each story: Is the situation under 20 seconds? Is "Action" at least half the time and in the first person ("I")? Is there a number in "Result"? Is there a lesson? Could it answer at least two different questions?

## 8. Tailor and score a resume

Running `ex08_tailor_score.py`:

| Version | Skill coverage | TF-IDF similarity |
|---|---|---|
| v1 | 43% | 0.096 |
| v2 | 57% | 0.103 |

v2 adds pytest testing, a FastAPI REST API and documentation/communication — all things the exercise says she really did. Notice TF-IDF barely moves: it is a blunt instrument, useful only for comparing versions.

Deliberately **not** added: Docker, CI/CD, Kubernetes, cloud, LangGraph, agents, guardrails, observability, hybrid search, structured outputs — she has not used them. Adding them would pass the ATS but fail the technical interview. The right fix is to *learn and build* (e.g. containerise the policy assistant and add a GitHub Actions workflow, module 14), then add them truthfully.

## 9. Quiz analytics

`ex09_quiz_weakest.py` stores `my_answer`, compares with `correct`, then:

```python
by_cat = mcq.groupby("category").correct_flag.agg(["mean", "size"]).sort_values("mean")
```

With the demo learner (about 60% right) the weakest categories were LLMOps, AI Trainer & Data and RAG. With only 1–5 MCQs per category the numbers are noisy — follow up with the open questions for those categories in notebook 02.

## 10. Mock system design — HR-policy assistant (outline answer)

1. **Requirements:** 5,000 employees, peak maybe a few hundred questions/hour, answers in English and Hindi, under ~5 s, must cite policy sections, HR data is confidential, some policies differ by country/grade, escalate sensitive topics (harassment, medical) to humans.
2. **Boxes:** chat UI in the intranet → FastAPI service (SSO login) → guardrails → retrieval → LLM → response with citations; Langfuse tracing; admin page for HR.
3. **Data and retrieval:** ingest policy PDFs/wiki, chunk by section headings, store metadata (country, grade, effective date, language), multilingual embeddings so Hindi questions retrieve English policies, hybrid search for policy names and numbers, reranker, filter by the employee's country/grade, re-index when HR publishes changes.
4. **Model and prompting:** a hosted model with good Hindi, or a self-hosted open model if data must not leave the company; answer only from retrieved sections, cite them, say "I don't know — contact HR" otherwise; reply in the user's language.
5. **Evaluation:** 150 real questions written with HR in both languages, with correct sections; measure hit rate, faithfulness, language correctness; CI eval gate; monthly HR review of sampled answers; thumbs up/down.
6. **Production:** streaming, caching of frequent questions, PII redaction in logs, access control, rate limits, sensitive-topic classifier that routes to a human, cost dashboard, audit log.
7. **Trade-offs/MVP:** start with English policies for one country, citations and escalation; add Hindi, more countries and analytics later.

Commonly forgotten items: per-country/grade filtering, policy version dates, escalation of sensitive topics, multilingual retrieval, audit logs.

## 11. Job-search sprint (how to read the Funnel sheet)

- **Replies/applications low** (for example under ~10% after 15+ tailored applications): resume and targeting problem → re-run notebook 01 against the JDs, sharpen the top third of the resume, shift effort to referrals and outreach.
- **Interviews/replies low:** recruiter screens are not converting → practise your 60–90 second story and the "why this company" answer.
- **Finals/interviews low:** technical depth → system design practice, project deep-dives, coding drills.
- **Referral row:** if referral applications convert much better than cold ones, rebalance your week towards outreach.

These thresholds are rules of thumb for diagnosis, not benchmarks; markets differ.

## 12. Write three new bank questions (example entries)

```python
("LLMs", "mid", "What is prompt caching and when does it help?",
 "Some providers can store the processed form of a long, unchanging prompt prefix, such as a big system prompt or a document, so later requests that reuse it are cheaper and faster. It helps when many calls share the same long prefix; put the stable content first and the changing question last. Check your provider's documentation for how caching is enabled and priced."),
("RAG", "mid", "What is parent-child (small-to-big) retrieval?",
 "You index small chunks for precise matching but, when one matches, you pass its larger parent section to the model. This combines accurate retrieval with enough surrounding context for a good answer. It is useful when answers need the whole paragraph or table around the matching sentence."),
("LLM System Design", "senior", "Design a system that flags risky clauses in uploaded contracts.",
 "Clarify contract types, languages, volume and the list of risk categories with lawyers. Pipeline: secure upload, text extraction with OCR, clause segmentation, then for each clause retrieval of the company's playbook guidance and an LLM classification into risk categories with a structured output and quoted evidence. Show results in a review UI where lawyers accept or correct flags, and store corrections as evaluation and future fine-tuning data. Measure precision and recall per category, keep strict access control and audit logs, and never auto-approve contracts."),
```

After `python 16-careers/build.py`, the heading of `interview-question-bank.md` shows the new total automatically (it is computed from the list). The number 137 written in `concepts.md`, `README.md` and notebook 02's text is plain prose, so update it by hand.
