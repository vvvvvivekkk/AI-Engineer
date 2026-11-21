# Module 08 — Exercises

Graded from easy (1) to hard (12). Solutions are in [solutions/solutions.md](solutions/solutions.md) and runnable code in [solutions/solutions.py](solutions/solutions.py). All exercises work offline; where a model is needed, use `call_llm()` from `code/llm_client.py`.

---

### Exercise 1 — Label the anatomy (easy, 10 min)
Here is a prompt:

> You are a friendly chef. Suggest one dinner recipe using only the ingredients below. Reply as a numbered list of steps, at most 6 steps. If the ingredients are not enough for a meal, say "Not enough ingredients". Ingredients: """eggs, spinach, cheese"""

Label each part with one of the seven building blocks (role, task, context, examples, format, constraints, input). Which block is missing? Write one line that adds it.

### Exercise 2 — Fix a vague prompt (easy, 15 min)
Rewrite this prompt so a program can use the answer: *"Tell me what you think of this review: 'The boots leaked on the first walk.'"* Your version must specify the task, the allowed outputs (positive / neutral / negative), the format, and separate the input with delimiters.

### Exercise 3 — Zero-shot to few-shot (easy, 20 min)
Using `call_llm()`, build a prompt that turns product names into URL slugs (`"Trail Runner 2 GTX"` → `trail-runner-2-gtx`). First try zero-shot on 5 names, then add 3 examples as chat turns (`examples=[...]`). Record how many of the 5 are exactly right each time.

### Exercise 4 — Template with a safety check (easy–medium, 20 min)
Write a `PromptTemplate` (see `code/prompt_templates.py`) called `summarise_review` with blanks `{product}` and `{review}`. Add it to a registry as `v1`. Then add a `v2` that also limits the summary to 20 words. Print both fingerprints and show that rendering with a missing blank raises an error.

### Exercise 5 — Pydantic schema and validator (medium, 30 min)
Write a Pydantic model `ReturnRequest` with: `order_id` (string starting with "BL-"), `reason` (one of `damaged`, `wrong_size`, `changed_mind`, `other`), `days_since_delivery` (integer 0–365). Validate the three JSON strings below and print which ones fail and why.
```
{"order_id": "BL-1001", "reason": "damaged", "days_since_delivery": 3}
{"order_id": "1002", "reason": "too big", "days_since_delivery": 3}
{"order_id": "BL-1003", "reason": "other", "days_since_delivery": 400}
```
Hint: use `Field(pattern=...)` or a `@field_validator`.

### Exercise 6 — Validate-and-retry with a scripted model (medium, 30 min)
Write `get_return_request(llm, text, max_tries=3)` that asks for JSON, validates it with your `ReturnRequest` model, sends the validation error back on failure, and returns `None` after `max_tries`. Test it with a scripted fake model whose replies are: (1) not JSON at all, (2) JSON with a bad reason, (3) valid JSON. Print each attempt.

### Exercise 7 — Context budget packer (medium, 40 min)
You have a 200-token budget. Pieces: system prompt (30 tokens), question (15), three documents (60, 90, 120 tokens, relevance 0.9, 0.4, 0.7), and chat history (80). Write code that keeps the system prompt and question always, then adds documents in order of relevance, then history if there is room. Print what was kept. Then change the rule so history is summarised to 30 tokens when it does not fit (fake the summary by cutting words).

### Exercise 8 — Break and defend a summariser (medium–hard, 40 min)
Write three indirect-injection attacks hidden in a fake email (e.g. in a signature, in "white text", in another language). Run them through the scanner in `code/injection_guard.py`. Which ones evade it? Add one new regex pattern that catches one evader without flagging the normal email `"Please ignore the previous invoice, a corrected one is attached."` Explain in two sentences why the scanner still is not enough.

### Exercise 9 — Analyse a real system prompt (hard, 45 min)
Open one product folder from the [system-prompts repo](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools) that is **not** discussed in detail in `system-prompt-analysis.md` (for example Junie, Warp.dev, Trae or Replit). Without copying any sentences, write a half-page analysis in your own words: which of the 12 building blocks it uses, which are missing, one design choice you would copy, one you would not, and why. (Remember: authenticity is unverified; treat it as a case study.)

### Exercise 10 — Write your own system prompt (hard, 60 min)
Using `templates/system-prompt-template.md`, write a full system prompt for **"StudyBuddy"**, an assistant that answers students' questions about a course syllabus (which you provide as a `<documents>` block). It must cite the syllabus section, refuse to write graded assignments for students, and say "Ask your instructor" when the syllabus lacks the answer.

### Exercise 11 — Test set for your system prompt (hard, 60 min)
Write 12 test cases for StudyBuddy in the Tests sheet of `excel/prompt-test-tracker.xlsx` (or a CSV with the same columns): 6 typical, 3 edge, 3 attack. For each, write the expected behaviour as a checkable rule (e.g. "contains `[section`", "does not contain an essay", "contains `Ask your instructor`"). Write a Python function that applies these rules to a reply and returns pass/fail.

### Exercise 12 — Improve by measurement (hard, 60–90 min)
Run your 12 cases against StudyBuddy v1 with `call_llm()` (offline or with an API key). Record the pass rate. Read the failures, change **one** section of the prompt, save it as v2, rerun, and record again. Write a short note (5 lines): what failed, what you changed, what improved, what got worse, and whether you would ship v2.
