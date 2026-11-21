# Module 16 — Exercises

Twelve exercises from easy to hard. Several produce real career documents — keep them. Solutions and worked examples are in `solutions/solutions.md` (and `solutions/ex08_tailor_score.py`, `solutions/ex09_quiz_weakest.py`).

Difficulty: ⭐ easy · ⭐⭐ medium · ⭐⭐⭐ hard

---

### 1. Match the day to the role ⭐
Which role is each person most likely in?
a) "I spent the morning ranking pairs of model answers on chemistry questions and writing justifications."
b) "I set up autoscaling for our vLLM GPUs and fixed an alert that kept firing at night."
c) "I added hybrid search to our support bot, then wrote an eval that runs in CI."
d) "I retrained the churn model with two new features and compared ROC-AUC with cross-validation."
e) "I interviewed five customers and wrote the success metrics for our new AI summary feature."

### 2. Rewrite weak bullets ⭐
Rewrite each as a strong resume bullet (action + what + how + result). Invent plausible numbers only for practice; on your real resume use true ones.
a) "Made a chatbot for my college."
b) "Did data cleaning in Python."
c) "Responsible for testing the model."
d) "Worked as an AI trainer."

### 3. Write your headline and About ⭐
Using `templates/linkedin-templates.md`, write a LinkedIn headline (under ~220 characters) and a three-paragraph About section for your target role.

### 4. Spot the scam ⭐
For each message, say whether it is a red flag and why:
a) "Congratulations! You're hired as an AI trainer. Pay the ₹2,000 onboarding fee to receive your laptop."
b) An email from a platform's official domain inviting you to take a 60-minute rubric assessment on their website.
c) "We pay weekly in gift cards. Reply in the next hour to secure your spot."
d) A platform asks you to upload ID through its own verified website after you passed its assessment.
e) "Please share your bank login so we can deposit your first payment."

### 5. Self-assessment ⭐⭐
Fill the **Self-assessment** sheet in `excel/skills-matrix.xlsx` (or `my_ratings` in notebook 03). Report: your top two roles by readiness, your three biggest gaps for your target role, and which modules you will revisit first.

### 6. Plan a portfolio ⭐⭐
For your target role, plan three portfolio projects (use module 15 for ideas). For each: the user and problem, the tech stack, the one evaluation number you will report, and how people can try it (demo link or video). Then draft the README for one of them with `templates/project-readme-template.md`.

### 7. STAR stories ⭐⭐
Write four STAR stories with `templates/star-story-worksheet.md`: a project you're proud of, a mistake, learning something fast, and working with someone difficult (or disagreeing). Time yourself telling each aloud: aim for about 2 minutes.

### 8. Tailor and score a resume ⭐⭐
Using notebook 01 or `code/resume_matcher.py`, score `data/sample_resume.txt` against `data/sample_job_description.txt`. Then write a **v2** that adds only skills the candidate plausibly has (assume she did use pytest and FastAPI in the Campus Policy Assistant, and wrote documentation as a TA). Report coverage and TF-IDF similarity before and after, and list which missing skills you deliberately did **not** add, and why.

### 9. Quiz analytics ⭐⭐
Extend notebook 02: run the MCQ quiz in demo mode with a fixed answer list for **all 33** questions, store whether each answer was correct, and print your accuracy **by category**, sorted from weakest to strongest. Which three categories should you practise first?

### 10. A mock system design ⭐⭐⭐
In 35 minutes, with a timer, design: *"An AI assistant that answers employees' HR-policy questions in a 5,000-person company, in English and Hindi."* Follow the 7-step framework in `concepts.md` and draw the diagram. Then compare with the support-chatbot model answer in the question bank and list three things you forgot.

### 11. Job-search sprint ⭐⭐⭐
Over two weeks: log at least 15 tailored applications and 6 outreach messages in `excel/job-search-tracker.xlsx`, publish one LinkedIn post about a project, and do two mock interviews with a partner using a script from notebook 02 step 7. At the end, read the Funnel sheet and write three sentences: which stage is weakest and what you will change.

### 12. Write three new bank questions ⭐⭐⭐
Add three new questions with model answers to `code/question_bank_data.py` (one LLM, one RAG, one system design), following the existing format and level tags, then run `python 16-careers/build.py` and check they appear in `interview-question-bank.md`, the Excel bank and notebook 02. Each model answer must be your own words, accurate, and answerable in about a minute.
