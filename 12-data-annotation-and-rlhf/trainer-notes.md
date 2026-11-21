# Module 12 - Trainer notes

Read `concepts.md` fully and run all four notebooks yourself before teaching. Have `excel/annotation-toolkit.xlsx` open; the kappa calculator is a great live demo.

## 1. What students should be able to do after the session

- Explain "garbage in, garbage out" with an example, and name six annotation types.
- Pick a sensible labelling tool for images, text, or chatbot preference data.
- Compute Cohen's kappa by hand on a 10-item example and interpret it.
- Draw RLHF's three stages and explain what the reward model and the KL penalty do.
- Compute the DPO loss on toy numbers and explain why DPO is simpler than PPO.
- Write a rubric with observable, binary criteria and name two LLM-judge biases.
- Describe what AI trainer work looks like and give three tips for qualification tests.

## 2. Teaching sequence (2-hour session)

| Time | Activity | Details |
|---|---|---|
| 0:00-0:10 | Hook | Ask: "Who taught ChatGPT to be polite?" Answer: thousands of human annotators. Tell the cookbook / tasting-notes analogy. |
| 0:10-0:25 | Annotation types and tools | Slides 3-5. Show the Label Studio config in `code/label_studio_config.xml`. Quick quiz: exercise 1 aloud. |
| 0:25-0:45 | Live labelling activity | Everyone labels the 20 reviews in `data/reviews_to_label.csv` *without guidelines* for 5 minutes. Collect two students' labels. |
| 0:45-1:05 | Agreement and kappa | Compute kappa on the two students' labels in the Excel calculator. Then show the guidelines, relabel, recompute. Kappa usually rises - powerful moment. Do the 10-item example on the board. |
| 1:05-1:10 | Break | |
| 1:10-1:30 | RLHF and reward models | Slides 10-11 with the cooking-competition analogy. Run notebook 02 live; end on the reward hacking cell. |
| 1:30-1:45 | DPO | Slide 13: toy numbers on the board. Run notebook 03 steps 2-6. |
| 1:45-1:55 | Evals and AI trainer jobs | Slides 15-16. Show the job tracker. Do prompt 3 of exercise 12 (honey) together - a safety-failure example. |
| 1:55-2:00 | Recap and homework | Exercises 5-12 as homework; exercise 12 timed. |

For a 1-hour version: skip the live relabelling (use notebook 01 instead), and skip notebook 03 (show the toy-number slide only).

## 3. Common student mistakes and fixes

1. **Thinking 90% agreement means good labels.** Fix: show the lazy-annotators cell (notebook 01 step 11) and the bar chart slide. Agreement must be corrected for chance.
2. **Computing p_e from the combined label counts instead of each annotator's own counts.** Fix: write two separate tally columns on the board, one per annotator, then multiply.
3. **Forgetting that kappa needs the same items, in the same order.** Fix: in pandas, always align by item ID (merge on `item`) before computing.
4. **Mixing up chosen/rejected order in the loss.** `-logsigmoid(r_rejected - r_chosen)` trains the model backwards. Fix: say "chosen minus rejected" every time; check that loss falls *and* pair accuracy rises.
5. **Believing the reward model *is* human preference.** Fix: notebook 02 step 10. It is an approximation that can be gamed, hence the KL penalty.
6. **Thinking DPO needs no reference model.** Standard DPO needs a frozen reference (usually the SFT model). Some variants (ORPO, SimPO) drop it - that is a separate idea.
7. **Treating log-probabilities like probabilities.** Students expect positive numbers. Fix: log of a number between 0 and 1 is negative; closer to 0 = more likely; the sum over tokens gets more negative for longer answers.
8. **Vague rubric levels ("5 = great").** Fix: ask "could two strangers agree on this?" Rewrite as observable yes/no checks.
9. **Trusting an LLM judge without checking.** Fix: always compute agreement between the judge and a human-labelled sample; always swap positions.
10. **Expecting fixed, guaranteed pay from AI trainer platforms.** Fix: say clearly that pay and availability vary; projects pause; never pay to join.

## 4. Questions to check understanding (with answers)

1. *Why is raw percent agreement misleading?* It ignores agreement that happens by chance, which is high when one label dominates.
2. *Kappa is 0. What does that mean?* The annotators agree exactly as often as chance would predict - no real agreement.
3. *What does a gold question do?* It has a known answer, so it measures each annotator's accuracy without them knowing which item is a test.
4. *What are the three stages of RLHF?* SFT on demonstrations; reward model on preference pairs; PPO against the reward model with a KL penalty.
5. *What is reward hacking?* The policy finds outputs that score high on the reward model but are not actually good (for example very long or flattering answers).
6. *Name two reasons DPO is simpler than PPO.* No separate reward model; no text generation during training; only two models in memory; behaves like ordinary supervised training.
7. *In DPO, what is the loss when the policy equals the reference?* ln 2 ≈ 0.693, because the margin is 0.
8. *What does beta control?* How strongly the policy is kept near the reference; bigger beta = smaller allowed drift.
9. *Name two LLM-judge biases and their fixes.* Position bias (swap order); verbosity bias (instruct against length, check correlation); self-preference (use a different judge family, compare to humans).
10. *Three tips for a qualification test?* Read instructions twice; justify with specific evidence; fact-check every claim; stay consistent; no AI-written answers.

## 5. Adapting for faster / slower groups

**Faster groups**
- Exercise 10 (break the reward model) and exercise 11 (position-bias experiment) in class.
- Compute Fleiss' kappa with `code/kappa.py` for the whole class labelling the same 20 reviews.
- Read the DPO paper's abstract and discuss why the reward is "implicit".
- Install Label Studio and run a real A/B labelling project with `code/label_studio_config.xml`.

**Slower groups**
- Spend more time on the live labelling and kappa; skip the PyTorch details of notebooks 02-03 and show only outputs.
- Use the Excel kappa calculator instead of code.
- Teach DPO only as "make the winner more likely and the loser less likely, without drifting far" plus the diagram.
- Focus the jobs section on the practical: guidelines, justifications, fact-checking.
