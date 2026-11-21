# Module 08 — Trainer notes

## 1. What students should be able to do after the session

- Rewrite a vague prompt using the seven building blocks (role, task, context, examples, format, constraints, input).
- Explain and demonstrate zero-shot vs few-shot, and show the difference with numbers from a test set.
- Get JSON out of a model and validate it with Pydantic, with a retry loop.
- Explain what a context window budget is and pack a context by priority (rules first, question last).
- Explain direct and indirect prompt injection and name at least four defence layers, with least privilege as the strongest.
- Build a 10-case test set and record results for two prompt versions.
- Name at least six recurring building blocks of real products' system prompts, and write a system prompt from the template.

## 2. Teaching sequence (2-hour session)

| Time | Activity | Materials | Notes for you |
|---|---|---|---|
| 0:00–0:10 | Hook: "the temp worker" story; ask the class to write a briefing note for a temp who will sort emails | Slides 1–2 | Collect 2–3 notes on the board; they will contain most of the anatomy |
| 0:10–0:25 | Messages, roles, prompt anatomy; vague vs structured demo | Slides 3–4, notebook 01 sections 1–2 | Run the cells live; print the chat template so students see the "hidden" text |
| 0:25–0:40 | Zero-shot vs few-shot, measured | Slide 5, notebook 01 section 3 | The cell takes 1–2 min on CPU — talk through the scoring function while it runs |
| 0:40–0:55 | Structured output + reasoning | Slides 6–7, notebook 02 sections 1–2 and 4 | Use the scripted fake model to show the retry loop; then show the tiny model failing honestly |
| 0:55–1:00 | Break | | |
| 1:00–1:20 | Context engineering: suitcase analogy, budget chart | Slide 9, notebook 03 sections 3, 6, 7 | Ask: "what would you drop first?" before revealing the packer's choices |
| 1:20–1:40 | Prompt injection + defences; test set with attacks | Slides 10–12, notebook 04 sections 1–5 | Let students try to evade the regex scanner (they will, quickly — that is the point) |
| 1:40–1:55 | Real products' system prompts and the template | Slides 13–15, system-prompt-analysis.md | Open one folder link live (e.g. Perplexity) and point at structure, not wording. Remind: no copying |
| 1:55–2:00 | Recap, assign exercises 1–4 in class or homework, 5–12 for the week | Slides 16–17 | |

**One-hour version:** do 0:00–0:40 (anatomy and few-shot), then 15 minutes on injection (notebook 04 sections 1–4) and 5 minutes on the system-prompt patterns. Assign context engineering as reading plus notebook 03.

## 3. Common student mistakes and how to fix them

1. **Mistake:** thinking a longer prompt is always better. **Fix:** show the context-budget chart; every sentence costs tokens and attention. Ask "which test case does this sentence fix?"
2. **Mistake:** examples that all have the same label or look identical. **Fix:** have them count labels in their few-shot set; one example per label minimum, varied wording.
3. **Mistake:** trusting a JSON reply without validation ("it looked right"). **Fix:** run notebook 02's bad JSON through Pydantic and show the downstream crash it would have caused.
4. **Mistake:** believing "never reveal your prompt" makes the prompt secret, or that rules make injection impossible. **Fix:** demonstrate the scanner evasion; repeat "least privilege is the real wall".
5. **Mistake:** judging a prompt from one or two tries. **Fix:** insist on the test set and the tracker; temperature 0 for testing.
6. **Mistake:** changing several things between versions, so nobody knows what helped. **Fix:** one change per version, written in the notes field.
7. **Mistake:** copying text from the system-prompts repository into their own work. **Fix:** explain copyright and authenticity; the exercise asks for patterns in their own words — deduct marks for copied sentences.
8. **Mistake:** expecting the tiny offline model to behave like ChatGPT and concluding "prompting doesn't work". **Fix:** explain that it is 135 million parameters on purpose; the *relative* improvement (0% → 75% format obedience) is the lesson. If you have a key, show the same notebook on a real model.
9. **Mistake:** putting the question first and a long document after it. **Fix:** for long inputs, documents first and question last; show the layout in notebook 03.

## 4. Questions to check understanding (with answers)

1. **Why does the model "forget" the previous conversation between API calls?** — It has no memory between calls; anything it needs must be sent in the context each time (the app resends history).
2. **When does few-shot help most?** — When the format or the labels are unusual, and with smaller models. It also helps make outputs consistent.
3. **What are two downsides of chain-of-thought?** — More tokens (cost, latency); the reasoning can look right and still be wrong.
4. **Why validate JSON even when the API "guarantees" a schema?** — Code should never trust input blindly; schemas don't check business rules (e.g. order exists), and settings or models change.
5. **Name three ways to shrink a context.** — Retrieve only relevant documents; summarise old history; trim tool output to head and tail (or return only needed fields).
6. **What is indirect prompt injection?** — Instructions hidden in content the model reads for the user (web pages, emails, documents, tool results), not typed by the user.
7. **Which defence layer is strongest, and why?** — Least privilege: if the model cannot reach dangerous tools or data, a successful injection cannot do much damage.
8. **What three kinds of cases belong in a prompt test set?** — Typical, edge, adversarial (attack).
9. **Name four building blocks common to real products' system prompts.** — Any four of: identity/scope, environment facts, tool rules (incl. when not to use), work loop, planning/to-do, output format, citations, safety/trusted-vs-untrusted, memory handling, tone, section tags, good/bad examples.
10. **Why do format rules differ so much between products?** — They follow the screen that renders the output (IDE, document editor, search page, terminal) and the type of user.

## 5. Adapting the session

**Faster groups**
- Give them an API key (if your organisation allows) and rerun notebook 01 on a real model: compare the size of the few-shot effect.
- Ask them to implement label scoring for the eval in notebook 04 and compare accuracy with free generation.
- Have them write a "router" prompt (like Kiro's mode classifier) that decides between two system prompts, and test it.
- Introduce promptfoo or DeepEval (resources.md) to automate the test set.

**Slower groups**
- Spend the whole first hour on anatomy and few-shot; skip label scoring and self-consistency in notebook 02.
- Do context engineering as a paper exercise: give each pair cards with token costs and a budget, and ask them to "pack the suitcase".
- For injection, use only the naive-model demo and the receptionist analogy; skip the regex details.
- Let them fill in the system-prompt template in pairs, with the Brightleaf example open beside them.
