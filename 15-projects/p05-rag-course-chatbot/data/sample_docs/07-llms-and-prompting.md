# Module 07/08 - LLMs and prompting

## What an LLM is
A **large language model** (LLM) is a transformer trained to predict the next token on a huge amount of text. Instruction-tuned models are then trained further to follow requests and chat.

## Temperature
**Temperature** controls randomness when the model picks the next token. Low temperature (0 to 0.3) gives focused, repeatable answers; high temperature (0.8 and above) gives more varied, creative text.

## Context window
The **context window** is the maximum number of tokens the model can read at once, including your prompt, any documents and its own answer. Text beyond the window is simply not seen.

## Hallucination
A **hallucination** is a fluent answer that is false or made up. Reduce it by giving the model the relevant facts in the prompt (retrieval), asking it to cite sources, and allowing it to answer "I don't know".

## Prompt patterns
Good prompts give a role, clear instructions, the needed context, the output format, and a few examples (**few-shot prompting**). Ask for step-by-step reasoning on hard problems.
