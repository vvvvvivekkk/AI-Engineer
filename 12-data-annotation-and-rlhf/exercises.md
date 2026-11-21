# Module 12 - Exercises

Graded from easy (1) to hard (12). Full worked solutions are in `solutions/solutions.md` and `solutions/solutions.py`. Try each one before looking.

## Easy

**1. Name the annotation type.** For each job, write the annotation type (classification, NER, bounding boxes, segmentation, ranking, preference pair, demonstration):
a) Draw a box around every helmet in construction-site photos.
b) Read two chatbot replies and pick the better one.
c) Highlight every medicine name in a doctor's note.
d) Write the ideal reply to "How do I open a bank account?".
e) Tag each tweet as "complaint", "question" or "praise".

**2. Pick the tool.** Which tool from the module would you choose, and why (one sentence each)?
a) A team labelling 10,000 dashcam video frames with tracked cars.
b) A student doing quick NER on 300 news sentences for a class project.
c) A start-up collecting preference pairs on its chatbot's answers, wanting to push the data to the Hugging Face Hub.

**3. Kappa by hand.** Two annotators labelled 10 emails as SPAM (S) or HAM (H):
```
A: S H H H S H H H H S
B: S H H S S H S H H H
```
Compute p_o, p_e and Cohen's kappa by hand. Then check with `cohen_kappa_score`.

**4. Read the number.** A project reports 94% raw agreement and a kappa of 0.18. In two or three sentences, explain what is probably going on and whether you would trust the labels.

## Medium

**5. Write guidelines.** Open `data/reviews_to_label.csv` (headphone reviews). Write a one-page guideline for POS / NEG / NEU using the template sheet in `excel/annotation-toolkit.xlsx`. Include at least three edge cases with decisions and reasons. Then label all 20 reviews.

**6. Agreement with a partner.** Swap labels from exercise 5 with a partner (or with the "simulated partner" in `solutions/solutions.py`). Compute kappa, list the disagreements, and propose one guideline change that would have prevented each.

**7. Preference pairs in JSONL.** Write 5 preference pairs in the format `{"prompt": ..., "chosen": ..., "rejected": ...}` on one topic you know well. At least two must be *close calls* (both answers decent, one slightly better). Validate the file with a short Python script that checks every line is valid JSON with exactly those three keys and non-empty strings.

**8. DPO loss by hand.** With beta = 0.2, policy log-probs chosen = -20, rejected = -25, reference log-probs chosen = -22, rejected = -22:
a) Compute the implicit rewards, the margin, and the loss by hand.
b) Confirm with `code/dpo_loss.py`.
c) What would the loss be if the policy were identical to the reference?

**9. Rubric design.** Write a rubric (4-5 binary criteria plus a combining rule) for grading a chatbot that answers customer questions for a train ticket website. For each criterion, give one answer that passes and one that fails.

## Hard

**10. Break the reward model.** In `notebooks/02-reward-model.ipynb`, the reward model was fooled by word stuffing. Change the training data so the hacked answer scores *lower* than the honest one (hint: add rejected answers that are lists of positive-sounding words). Retrain and show the before/after scores. Explain why this is a cat-and-mouse game and why PPO still needs a KL penalty.

**11. Position-bias experiment.** Write a function that runs a pairwise judge on N pairs in both orders and reports: (a) how often the judge picks the first position, (b) the consistency rate (same winner in both orders). Run it on the biased stand-in judge from notebook 04 with at least 8 pairs. If you have an API key, also run it with Claude and compare.

**12. Mock qualification test.** Do this timed (30 minutes). For each of the 3 prompts below, two model answers are given. Pick the better one, rate each on the rubric from exercise 9 (or the one in notebook 04), and write a 2-4 sentence justification that cites specific evidence. Then swap with a partner and compute your agreement.
- Prompt 1: "What year did India become independent?" A: "1947, on 15 August." B: "India became independent in 1950 when the constitution came into force."
- Prompt 2: "Write a Python function that returns the largest number in a list." A: `def largest(xs): return sorted(xs)[-1]` B: `def largest(xs): return max(xs) if xs else None`
- Prompt 3: "Is it okay to give honey to a 6-month-old baby?" A: "Yes, honey is natural and healthy." B: "No - doctors advise against honey for babies under 12 months because of the risk of infant botulism. Please ask your paediatrician."
