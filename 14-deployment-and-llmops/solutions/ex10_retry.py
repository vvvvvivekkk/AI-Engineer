"""
Exercise 10 solution - retries with exponential backoff and jitter.
Run:  python ex10_retry.py
"""
import random
import time


class RateLimitError(Exception):
    """Stands in for HTTP 429 from a provider."""


class ServerError(Exception):
    """Stands in for HTTP 5xx from a provider."""


RETRYABLE = (RateLimitError, ServerError)       # only temporary problems are worth retrying


def call_with_retries(fn, max_retries=3, base_delay=0.1):
    """Call fn(); on a retryable error wait base_delay * 2**attempt (+ jitter) and try again."""
    for attempt in range(max_retries + 1):       # attempt 0 is the first try
        try:
            return fn()
        except RETRYABLE as e:
            if attempt == max_retries:           # out of retries: give up and raise
                raise
            delay = base_delay * (2 ** attempt)  # 0.1, 0.2, 0.4 ...
            delay += random.uniform(0, delay / 2)  # jitter: spread retries so clients don't all retry at once
            print(f"  attempt {attempt + 1} failed with {type(e).__name__}; waiting {delay:.2f}s")
            time.sleep(delay)
        # any other exception (ValueError, a 400 bad request ...) is NOT caught, so it is raised at once


def make_flaky(failures):
    """Return a function that raises ServerError `failures` times, then succeeds."""
    state = {"calls": 0}

    def fn():
        state["calls"] += 1
        if state["calls"] <= failures:
            raise ServerError("503 from provider")
        return f"success after {state['calls']} calls"
    return fn


if __name__ == "__main__":
    print(call_with_retries(make_flaky(2)))                    # fails twice, then works
    try:
        call_with_retries(make_flaky(10), max_retries=2)       # never works -> raises after 3 tries
    except ServerError as e:
        print("gave up:", e)
    calls = {"n": 0}

    def bad_request():
        calls["n"] += 1
        raise ValueError("400: bad input")
    try:
        call_with_retries(bad_request)
    except ValueError:
        print("ValueError raised immediately, calls made:", calls["n"])   # 1, no retries
