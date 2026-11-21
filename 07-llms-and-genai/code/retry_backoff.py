"""
retry_backoff.py - retry a flaky call with exponential backoff and jitter.

Run:  python retry_backoff.py
Needs: nothing beyond the standard library. A fake "API" fails at random so you can watch the retries.

The official OpenAI and Anthropic SDKs already retry for you (max_retries=2 by default). Write your own
loop when you need custom behaviour: logging, a different number of tries, or falling back to another model.
"""
import random
import time


class TemporaryError(Exception):
    """Errors worth retrying: rate limit (429), server errors (5xx), timeouts."""


class PermanentError(Exception):
    """Errors NOT worth retrying: bad request (400), bad key (401), wrong model name (404)."""


def flaky_api(prompt, fail_rate=0.6):
    """Pretend API: fails with a temporary error 60% of the time."""
    if random.random() < fail_rate:
        raise TemporaryError("429 rate limit (simulated)")
    return f"answer to {prompt!r}"


def call_with_retries(fn, *args, max_attempts=5, base_delay=0.5, max_delay=8.0, **kwargs):
    """Call fn; on TemporaryError wait base_delay * 2**attempt (+ jitter) and try again."""
    for attempt in range(max_attempts):
        try:
            return fn(*args, **kwargs)                  # success: return straight away
        except PermanentError:
            raise                                       # never retry these - fix the request instead
        except TemporaryError as e:
            if attempt == max_attempts - 1:             # out of attempts: give up
                raise
            delay = min(max_delay, base_delay * 2 ** attempt)   # 0.5, 1, 2, 4, 8 ... capped
            delay += random.uniform(0, delay / 2)       # jitter: spread out clients retrying together
            print(f"  attempt {attempt + 1} failed ({e}); waiting {delay:.2f}s")
            time.sleep(delay)


if __name__ == "__main__":
    random.seed(3)                                      # repeatable demo
    for q in ["What is a token?", "What is top-p?"]:
        try:
            print("OK:", call_with_retries(flaky_api, q, base_delay=0.2))
        except TemporaryError:
            print("Gave up after several attempts - show the user a friendly message")
