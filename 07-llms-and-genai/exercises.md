# Module 07 - Exercises

Ten exercises, easy to hard. All can be done **without API keys** (each says how). Solutions: [`solutions/solutions.md`](solutions/solutions.md) (explanations) and [`solutions/solutions.py`](solutions/solutions.py) (runnable: `python solutions.py 4` runs exercise 4).

---

## Easy

### 1. Next-token detective
Using `HuggingFaceTB/SmolLM2-135M-Instruct` (load it with `dtype=torch.float32`), print the top 5 next tokens and their probabilities for each prompt:
- `"I drank a cup of"`
- `"The opposite of hot is"`
- `"My favourite programming language is"`

Which prompt is the model most sure about? Which is least sure? Why does that make sense?

### 2. Temperature by hand
Given logits `[3.0, 2.0, 1.0, 0.5]` for tokens `["cat", "dog", "fish", "bird"]`, compute the softmax probabilities at temperatures 0.1, 1.0 and 5.0 with NumPy. Describe each result in one sentence.

### 3. Safe key loading
Write a function `get_key(name)` that reads an environment variable (after `load_dotenv()`), returns it if present, and otherwise returns `None` and prints `"<name> not set - using offline fallback"`. It must **never print the key itself**. Test it with `OPENAI_API_KEY` and a made-up name.

---

## Medium

### 4. Top-p from scratch
Write `top_p_filter(probs, p)` that returns the indices of tokens kept by nucleus sampling and the renormalised probabilities. Test it on `probs = [0.5, 0.2, 0.15, 0.1, 0.05]` with p = 0.6, 0.8 and 0.95. Then write `sample(probs, temperature, top_p, rng)` that applies temperature (to log-probabilities), then top-p, then draws one index.

### 5. Conversation memory manager
Write a class `Conversation` that stores a system prompt and a list of messages, with methods `add_user(text)`, `add_assistant(text)`, `token_count()` (use tiktoken `o200k_base`, +4 tokens per message) and `trimmed(max_tokens)` that returns the system prompt plus the most recent messages that fit, always starting with a `user` message. Test it with a 20-turn fake conversation and `max_tokens=300`.

### 6. One function, three providers
Write `ask(provider, system, messages)` that calls OpenAI, Anthropic or Gemini (official SDKs) and returns `{"text", "input_tokens", "output_tokens", "source"}`. If the key for that provider is missing, return a fake response with `source="fake"` instead of calling anything. Make sure each provider's system prompt goes in the right place.

### 7. Cost estimate for a real feature
A college wants a chatbot answering admissions questions. Expect 2,000 questions/day in peak month, average system prompt 400 tokens, average question 40 tokens, average answer 180 tokens.
(a) Write a function that computes monthly cost from prices per 1M tokens.
(b) Look up current prices for one small and one large model on official pricing pages (or, if you can't, use the clearly-fake prices small = (0.20, 0.80), large = (5.00, 25.00) and **say so**).
(c) What fraction of the cost comes from the system prompt? Suggest two ways to reduce it.
(d) Enter the same numbers in `excel/07-llm-cost-calculator.xlsx` and check they match.

---

## Hard

### 8. Robust structured extraction
Define a Pydantic model `Invoice(vendor: str, total: float, currency: str, date: str)`. Write `extract_invoice(text)` that:
1. if `ANTHROPIC_API_KEY` is set, uses `client.messages.parse(..., output_format=Invoice)`;
2. otherwise asks the local SmolLM2 for JSON, extracts the first `{...}` block, and validates with Pydantic;
3. on validation failure retries once with a stricter prompt, then returns `None` and logs why.
Test with three invoice texts. Report how often the local model produced valid JSON.

### 9. Retry with backoff, properly
Write `call_with_retry(fn, max_attempts=5, base=0.5, max_wait=8)` that retries only on "temporary" errors. Simulate errors with a fake API that raises exceptions carrying a `status_code` attribute (429, 500, 529 = temporary; 400, 401, 404 = permanent). Requirements: exponential wait with full jitter (`random.uniform(0, base * 2**attempt)`, capped at `max_wait`), honour a `retry_after` attribute if the exception has one, never retry permanent errors, and return a log of attempts. Write three tests: succeeds after 2 failures, fails fast on 401, gives up after max attempts.

### 10. Local vs hosted comparison plan (with Ollama)
Write a script that sends the same 5 prompts to (a) a local model and (b) any hosted model, recording answer, latency and tokens. Use Ollama's REST API at `http://localhost:11434/api/chat` if it is reachable; otherwise fall back to SmolLM2 via `transformers`. For the hosted model, fall back to a fake response if no key is set. Output a pandas table and a one-paragraph recommendation of which you would use for (i) a private HR assistant and (ii) a public marketing-copy generator, with reasons.
