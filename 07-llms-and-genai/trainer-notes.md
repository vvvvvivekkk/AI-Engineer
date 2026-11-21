# Module 07 - Trainer notes

Read `concepts.md` once and run the three notebooks yourself before teaching. You do **not** need API keys to teach this module: every notebook has an offline fallback. If you do have one key (a free Gemini key is easiest), set it in Colab Secrets so you can show one real call live. That is very convincing for students.

## 1. What students should be able to do after the session

1. Explain in one sentence what an LLM does (predicts the next token) and why that leads to hallucinations.
2. Say what temperature, top-p and the context window are, and pick sensible settings for a task.
3. Describe pre-training → instruction tuning → RLHF/DPO with an analogy.
4. Write a call to OpenAI, Anthropic and Gemini with a system prompt and history, from memory or with the cheat sheet.
5. Store API keys safely and explain why they must never appear in code or git.
6. Handle API errors: know which ones to retry and use backoff.
7. Estimate monthly cost from tokens and official prices, using tiktoken and the Excel calculator.
8. Explain what Ollama is and when a local model is the right choice.

## 2. Session plan (2 hours)

Before the session: run all notebooks once in Colab (model downloads are cached), open the Excel calculator and fill in today's prices for two models from the official pages, open the slides.

| Time | Activity | Materials | Notes |
|---|---|---|---|
| 0:00-0:10 | **Hook**: type "The capital of France is" and ask students to guess the model's top 5 next tokens and probabilities. Reveal. | Slides 1-3, notebook 01 §1 | The 27% for " the" surprises people. Good start for "it ranks continuations". |
| 0:10-0:25 | **Generation loop, temperature, top-p** | Slides 4-5, notebook 01 §2-5 | Run §5 with three temperatures; let students vote on which output is "best". |
| 0:25-0:35 | **Context window** | Slide 6, notebook 01 §6 | Show the token count climbing each turn. Ask: what do we do when it overflows? |
| 0:35-0:45 | **Training stages** | Slide 7, notebook 01 §7 | Library / teacher / coach. Show the template text with `<|im_start|>`. |
| 0:45-0:55 | Break | | |
| 0:55-1:25 | **APIs hands-on**: keys and `.env`, roles, three SDKs, memory demo, streaming, JSON | Slides 8-11, notebook 02 §1-10 | Students run it in Colab. If you have a key, show one real call first. |
| 1:25-1:40 | **Errors and retries** | Slide 12, notebook 02 §11 | Run the closed-port demo: real SDK errors with no internet. Then the flaky-API backoff. |
| 1:40-1:50 | **Cost**: tiktoken, example prices, the Excel calculator with real prices you filled in | Slide 13, notebook 03 §1-4 | Change requests/day live and watch monthly cost update. |
| 1:50-1:57 | **Ollama + choosing a model** | Slides 14-15, notebook 03 §5-6 | Demo Ollama on your laptop if installed; otherwise show `code/ollama_rest.py`. |
| 1:57-2:00 | **Recap + exercises** | Slides 16-17 | Exercises 1-4 in class, 5-10 at home. |

**1-hour version:** hook (5), temperature (10), context window (5), APIs with the comparison table and memory demo (20), errors (8), cost with the Excel file (10), recap (2). Skip training stages (assign the reading) and Ollama (assign `code/ollama_commands.sh`).

## 3. Common student mistakes and fixes

| Mistake | What it looks like | Fix |
|---|---|---|
| Pasting an API key into a notebook or script | Key visible in a cell, or pushed to GitHub | Stop and rotate (revoke) the key in the provider console immediately. Teach `.env` + `.gitignore`, Colab Secrets. |
| Expecting the model to remember earlier calls | "I told it my name in the last message!" | Run notebook 02 §8. The API is stateless; the app must send history. |
| Wrong model name | 404 / `NotFoundError` | Copy the name from the provider's models page; keep it in `.env`. |
| Putting the system prompt in the wrong place | Anthropic error about roles, or ignored instructions | Use the table in notebook 02 §3: `instructions=` / `system=` / `system_instruction`. |
| Retrying every error | Infinite loop on a bad key | Only retry 429, 5xx, 529 and connection errors. 400/401/403/404 need a fix, not a retry. |
| Trusting JSON because it parsed | Totals of 0.0, wrong dates | Exercise 8: validation checks shape, not truth. Add value checks and tests. |
| Counting words instead of tokens; forgetting output tokens | Cost estimates far too low | Use tiktoken; output tokens usually cost several times more than input. |
| Hard-coding prices copied from a blog | Out-of-date numbers | Always use the official pricing page and write the date you checked (Excel column G). |
| Using `genai.Client().models.generate_content(...)` in one line | "client has been closed" error | Store the client in a variable first. |
| Loading SmolLM2 without `dtype=torch.float32` on CPU | Generation takes a minute | The weights are bfloat16, slow on most CPUs; load in float32. |
| Thinking temperature 0 makes answers correct | "It's deterministic, so it's right" | Temperature controls randomness, not truth. A greedy answer can be confidently wrong. |

## 4. Questions to check understanding (with answers)

1. **Why can an LLM state false facts confidently?** It produces likely text, not checked facts. Nothing in next-token prediction verifies truth.
2. **What happens to the probabilities as temperature goes from 0.2 to 1.5?** They flatten: the top token loses share and rare tokens become more likely, so output becomes more varied and more error-prone.
3. **Top-p = 0.9 — which tokens are kept?** The smallest set of most-likely tokens whose probabilities add up to at least 90%.
4. **A chatbot works for 10 turns, then starts forgetting the start of the conversation. Why?** The history exceeded the context window (or the app trims it). Old messages are being dropped.
5. **What is the difference between a base model and an instruct model?** A base model only continues text; an instruct model was further trained on conversations to follow instructions in a chat format.
6. **What does RLHF add?** Training on human preferences between answers, so the model favours helpful, honest, safe replies.
7. **Where does the system prompt go in each SDK?** OpenAI Responses: `instructions=`; Anthropic: `system=`; Gemini: `GenerateContentConfig(system_instruction=...)`.
8. **You get a 429. What should your code do?** Wait (honour `retry-after` if given), retry with exponential backoff and jitter, give up gracefully after a few attempts.
9. **You get a 401. What should your code do?** Not retry. Report a key/configuration problem.
10. **How do you estimate the monthly cost of a feature?** requests/day × days × (input tokens × input price + output tokens × output price) ÷ 1,000,000, with prices from the official page.
11. **Name two reasons to run a model locally with Ollama.** Privacy (data stays on your machine), offline use, no per-token cost, experimentation.
12. **Why test a cheap model first?** If it passes your test set, you save money and get lower latency; move up only when needed.

## 5. Adapting the session

**Faster groups**
- Exercise 9 (retry with full jitter and `retry_after`) and exercise 5 (memory manager) in class.
- Show the OpenAI-compatible endpoint idea: the same `openai` client pointed at Ollama with `base_url`.
- Discuss prompt caching and batch APIs as cost levers; ask them to find both on the official pricing pages.
- Compare token counts for the same text from `tiktoken` and from a provider's `count_tokens` (if a key is available).

**Slower groups**
- Spend longer on notebook 01 §1-3 and skip top-p maths; the bar charts carry the idea.
- In notebook 02, run only the Anthropic helper, the memory demo and the comparison table; leave streaming and JSON for homework.
- Do the cost calculation together on the board with round numbers before opening Excel.
- Skip Ollama in class; give `code/ollama_commands.sh` as optional homework for students with their own laptop.
- Pair students: one reads the markdown aloud, the other runs the cell and explains the output.
