# Module 12 - Solutions

Runnable code for exercises 3, 6, 7, 8, 10 and 11 is in `solutions.py` (run `python solutions/solutions.py` from the module folder).

## 1. Name the annotation type
a) Bounding boxes. b) Preference pair. c) Named entity recognition (NER). d) Demonstration (SFT data). e) Classification (single label, three classes).

## 2. Pick the tool
a) **CVAT** - built for images and video, including tracking objects across frames.
b) **doccano** - simplest to install and learn for text NER; enough for 300 sentences.
c) **Argilla** - designed for LLM feedback such as preference pairs, and integrates with the Hugging Face Hub. (Label Studio would also work.)

## 3. Kappa by hand
```
A: S H H H S H H H H S
B: S H H S S H S H H H
```
- Agreements: items 1, 2, 3, 5, 6, 8, 9 = 7 of 10 → **p_o = 0.7**.
- A uses S 3 times (0.3), H 7 times (0.7). B uses S 4 times (0.4), H 6 times (0.6).
- **p_e** = 0.3 × 0.4 + 0.7 × 0.6 = 0.12 + 0.42 = **0.54**.
- **kappa** = (0.7 - 0.54) / (1 - 0.54) = 0.16 / 0.46 ≈ **0.35** ("fair").
- `cohen_kappa_score(list("SHHHSHHHHS"), list("SHHSSHSHHH"))` → 0.348.

## 4. Read the number
High raw agreement with low kappa means most of the agreement is what you would expect by chance. Usually one label is very common (for example 95% "not toxic"), so annotators agree simply by choosing the common label, but they rarely agree on the rare, important label. Do not trust the labels for the rare class: review the guidelines for that class, add examples, and re-pilot.

## 5. Write guidelines (sample answer)
Definitions as in the template sheet (POS / NEG / NEU about the *product*). Sample edge cases:
1. **Sarcasm** ("Oh great, the left earbud fell apart. Fantastic quality.") → NEG. Label the meant opinion.
2. **Mixed with verdict** ("Comfortable, but the bass is weak. Still, I'd buy again.") → POS. The final verdict decides.
3. **About something else** ("Shipping took ages; the product itself is fine.") → NEU, because the only complaint is shipping and "fine" is not a clear opinion. (Some teams would choose POS - the point is to *decide and write it down*.)
4. **Vague** ("Decent.", "Meh, they're okay I guess.") → NEU unless clearly positive. Write the rule: single lukewarm words = NEU.

Sample labels (item: label): 0 POS, 1 NEG, 2 NEU, 3 NEG, 4 POS, 5 NEU, 6 POS, 7 NEG, 8 NEU, 9 NEG, 10 NEG, 11 POS, 12 NEU, 13 NEG, 14 NEU, 15 POS, 16 POS, 17 NEG, 18 NEU, 19 NEU.

## 6. Agreement with a partner
`solutions.py` compares the sample labels above with a simulated partner who treats "Decent." as POS, sarcasm as literal, and "Returned for a refund." as NEU. Kappa comes out around 0.77. Guideline fixes: (a) add a sarcasm rule with two examples; (b) state that one-word lukewarm reviews are NEU; (c) state that returning a product counts as NEG even without a reason.

## 7. Preference pairs in JSONL
Example close call:
```json
{"prompt": "How long should I boil an egg for a soft yolk?", "chosen": "About 6 minutes in boiling water, then cool it in cold water to stop cooking.", "rejected": "About 6 minutes."}
```
Both are correct; chosen is better because it adds the cooling step. The validator in `solutions.py` checks each line parses as JSON, has exactly the keys `prompt`, `chosen`, `rejected`, and that all values are non-empty strings and chosen ≠ rejected.

## 8. DPO loss by hand
a) chosen implicit reward = 0.2 × (-20 - (-22)) = 0.2 × 2 = **0.4**. Rejected = 0.2 × (-25 - (-22)) = 0.2 × (-3) = **-0.6**. Margin (already multiplied by beta) = 0.4 - (-0.6) = **1.0**. sigmoid(1.0) ≈ 0.731. Loss = -ln(0.731) ≈ **0.313**.
b) `dpo_loss(torch.tensor([-20.]), torch.tensor([-25.]), torch.tensor([-22.]), torch.tensor([-22.]), beta=0.2)` → 0.3133.
c) If policy = reference, both implicit rewards are 0, margin 0, loss = ln 2 ≈ **0.693**.

## 9. Rubric design (sample)
| Criterion | Pass example | Fail example |
|---|---|---|
| Correct policy/facts | "Tickets can be cancelled up to 4 hours before departure for a refund minus a fee." (matches policy) | "All tickets are fully refundable any time." |
| Answers the question | User asks about luggage → answer gives the luggage limit | Answer talks about seat upgrades |
| Safe and privacy-aware | Asks the user to log in to see booking details | Asks the user to paste their card number in chat |
| Actionable | Gives the steps or link name to complete the task | "Please check the website." only |
| Polite and concise | Two friendly sentences | Rude, or 200 words of filler |

Combining rule: FAIL if "Correct" or "Safe" fails; otherwise score = number of passes out of 5.

## 10. Break the reward model
Add rejected examples that are just strings of positive-sounding words (for example the top-weighted vocabulary words joined together), paired with real answers as chosen. After retraining, the stuffed answer's score drops below the honest one (see `solutions.py`: honest stays positive, stuffed becomes negative). But a new hack always exists (for example stuffing *different* words, or making answers very long), because a reward model is a learned approximation trained on limited data. That is why RLHF keeps a KL penalty: it limits how far the policy can wander into strange text that only exploits the reward model.

## 11. Position-bias experiment
`solutions.py` defines `position_bias_report(judge, pairs)`. On the biased stand-in with 8 pairs of similar-length answers it reports a first-position pick rate of 100% and a consistency rate of 0% - the judge's choice depends only on the order, which makes its verdicts worthless. A well-behaved judge should pick "first" about 50% of the time and be consistent on most pairs. With Claude, expect higher consistency, but still check.

## 12. Mock qualification test (model answers)
- **Prompt 1: A is better.** A gives the correct date (15 August 1947). B confuses independence with the constitution coming into force on 26 January 1950, so it is factually wrong.
- **Prompt 2: B is better.** Both return the largest number for non-empty lists, but A crashes with IndexError on an empty list and sorts the whole list (O(n log n)) when `max` is O(n). B handles the empty case explicitly. (A reviewer might note B returning `None` should be documented.)
- **Prompt 3: B is better.** A is unsafe and wrong: medical guidance advises no honey before 12 months due to infant botulism risk. B is correct, explains why, and refers to a professional. A fails the safety criterion, which fails the whole answer.
