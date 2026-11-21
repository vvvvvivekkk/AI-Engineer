# Module 07 - Solutions

Runnable code for all ten exercises is in [`solutions.py`](solutions.py). Everything runs without API keys; where a key would be used, the code shows the real call and falls back to a fake or local answer. The outputs below come from a run with no keys set. Small models can give slightly different numbers on other machines.

---

## 1. Next-token detective

```
I drank a cup of               -> ' coffee' 0.484, ' tea' 0.204, ' black' 0.168, ' green' 0.006, ' the' 0.006
The opposite of hot is         -> ' cold' 0.874, ' cool' 0.039, ' dry' 0.008, ' warm' 0.005, ' also' 0.004
My favourite programming language is -> ' Python' 0.407, ' Java' 0.102, ':' 0.059, '?' 0.057, '\n' 0.035
```

Most sure: "The opposite of hot is" (87% on " cold") — there is basically one right answer in the training text. Least sure: the programming-language prompt — it is an opinion, so many continuations are plausible (even punctuation). The coffee/tea prompt sits in between. **Lesson:** the probability spread tells you how open-ended a prompt is.

## 2. Temperature by hand

```
T=0.1: cat 1.000, dog 0.000, fish 0.000, bird 0.000   -> almost greedy: always "cat"
T=1.0: cat 0.631, dog 0.232, fish 0.085, bird 0.052   -> the model's own preferences
T=5.0: cat 0.323, dog 0.264, fish 0.217, bird 0.196   -> nearly uniform: "bird" is picked a fifth of the time
```

Code: `softmax(logits / T)`. Dividing by a small T multiplies the gaps between logits, so the winner takes everything; a large T shrinks the gaps.

## 3. Safe key loading

```python
def get_key(name):
    load_dotenv()
    value = os.getenv(name)
    if not value:
        print(f"{name} not set - using offline fallback")
        return None
    print(f"{name} found ({len(value)} characters)")   # presence only
    return value
```

Points students miss: never `print(value)`, never put the key in an f-string that gets logged, and never store it in a notebook cell — notebook outputs are saved to the file and pushed to GitHub.

## 4. Top-p from scratch

```
p=0.6:  keep [0, 1]       -> [0.714, 0.286, 0, 0, 0]
p=0.8:  keep [0, 1, 2]    -> [0.588, 0.235, 0.176, 0, 0]
p=0.95: keep [0, 1, 2, 3] -> [0.526, 0.211, 0.158, 0.105, 0]
1000 samples (T=1, top_p=0.8): [569, 249, 182, 0, 0]
```

Method: sort descending, take a running total (`cumsum`), keep tokens up to the first position where the total reaches p, zero the rest, divide by the new total. In `sample`, temperature is applied first (on log-probabilities), then top-p, then one random draw. Tokens 3 and 4 never appear with top_p = 0.8 — the "long tail" is cut off.

## 5. Conversation memory manager

```
full tokens: 711 | trimmed messages: 16 | trimmed tokens: 291 | first kept: Question 12: ...
```

Key ideas: walk backwards from the newest message adding messages while they fit; always keep the system prompt; drop a leading assistant message so the history starts with `user` (Anthropic requires this, and it reads more naturally for all models). A real app would also summarise dropped turns (Module 08).

## 6. One function, three providers

The important differences, all visible in `ask()`:

| | OpenAI | Anthropic | Gemini |
|---|---|---|---|
| Call | `client.responses.create` | `client.messages.create` | `client.models.generate_content` |
| System prompt | `instructions=` | `system=` | `config=GenerateContentConfig(system_instruction=)` |
| Assistant role | `assistant` | `assistant` | `model` |
| Required extra | — | `max_tokens` | history as `Content(parts=[Part(text=)])` |
| Answer text | `.output_text` | join `.content[i].text` | `.text` |
| Tokens | `.usage.input_tokens/output_tokens` | `.usage.input_tokens/output_tokens` | `.usage_metadata.prompt_token_count/candidates_token_count` |

Without keys every call returns `source="fake"` and nothing is sent.

## 7. Cost estimate for a real feature

Using **clearly fake** prices (small = $0.20 / $0.80, large = $5.00 / $25.00 per 1M input/output tokens):

```
small (FAKE prices): $13.92/month;  system prompt share 34%
large (FAKE prices): $402.00/month; system prompt share 30%
```

Working for the small model: per request input = 440 tokens, output = 180. Daily = 2,000 × (440 × 0.20 + 180 × 0.80) / 1,000,000 = $0.464. Monthly (30 days) = $13.92.

(c) The 400-token system prompt is about a third of the cost, because it is re-sent with every question. Ways to reduce: shorten it (remove repetition and examples that don't help), use **prompt caching** if the provider offers it (discounted repeated prefixes), and route easy questions to a smaller model.

(d) In the Excel calculator, put the fake prices into the EXAMPLE-ONLY row or a real row, set requests/day 2000, input tokens 440, output tokens 180, days 30: the monthly cell shows the same number. With real prices from the official pages the numbers will differ — that is the point of the exercise.

## 8. Robust structured extraction

With no key, the local model's first attempt usually fails (no JSON, or missing fields); the stricter second prompt then produced parseable JSON for all three texts:

```
Sri Ganesh Traders -> vendor='Sri Ganesh Traders' total=0.0 currency='INR' date='2026-10-02'
Amogha Sweets      -> vendor='Amogha Sweets' total=0.0 currency='INR' date='12/12/2026'
DigitalWave Ltd    -> vendor='DigitalWave Ltd' total=0.0 currency='USD' date='2026-09-30'
valid JSON: 3/3
```

**Look closer: valid is not the same as correct.** Every total is 0.0 (the model copied the placeholder from the prompt) and one date is wrong. Schema validation checks *shape*, not *truth*. In a real system add checks on values (total > 0, date parses and is not in the future) and test on labelled examples. With `ANTHROPIC_API_KEY` set, `messages.parse(..., output_format=Invoice)` uses the provider's native structured output, which is far more reliable.

## 9. Retry with backoff, properly

```
test 1: success [(1, 'temporary 500', 0.101), (2, 'temporary 429', 1.0), (3, 'ok', 0)]
test 2: failed fast with 401
test 3: gave up with 503
all tests passed
```

Design choices:
- **Full jitter**: `random.uniform(0, min(max_wait, base * 2**attempt))` spreads retries out better than a fixed doubling.
- **`retry_after`**: if the server says how long to wait (the 429 above says 1.0 s), obey it.
- **Permanent errors** (400/401/403/404) are re-raised immediately — retrying a bad key only wastes time.
- The `sleep` parameter lets tests run instantly (`sleep=lambda s: None`). This trick is called **dependency injection**.

## 10. Local vs hosted comparison

On the course machine (no Ollama, no key) the local column came from SmolLM2 and the hosted column was fake:

```
prompt                          local_s  local_answer
Summarise: the meeting moved t     8.20  The meeting was adjourned to Friday 3pm.
Translate 'good morning' to Hi    39.96  (nonsense Devanagari)
What is 17 * 3?                   27.70  17 * 3 is equal to 54.
```

(The machine was shared and busy, which explains the slow times.) Observations: the tiny model handles simple rephrasing, fails translation into Hindi and gets arithmetic wrong (17 × 3 = 51). A 1-3B model in Ollama does noticeably better; a hosted frontier model does better still.

Sample recommendation:
- **Private HR assistant** — data includes salaries and personal details, so prefer an open-weight model run locally or on company servers (Ollama), accepting lower quality, or a hosted provider only under a contract that covers data handling. Test it on real HR questions first.
- **Public marketing copy** — no private data, quality and creativity matter most, volume is low: a hosted model is the sensible choice; cost is small.
