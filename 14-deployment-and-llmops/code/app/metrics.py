"""
metrics.py - a tiny in-memory metrics store.

Real systems send metrics to tools such as Prometheus, Grafana, Datadog or Langfuse.
Here we keep them in a Python list so you can see the idea with zero setup.
"""
import statistics    # built-in module for median etc.
import threading     # a Lock stops two requests writing at the same moment

_lock = threading.Lock()
_records: list[dict] = []          # one dict per request


def record(latency_ms: float, ok: bool, input_tokens: int = 0, output_tokens: int = 0, cost_usd: float = 0.0):
    """Store one request's numbers."""
    with _lock:
        _records.append({"latency_ms": latency_ms, "ok": ok, "input_tokens": input_tokens,
                         "output_tokens": output_tokens, "cost_usd": cost_usd})


def percentile(values: list[float], p: float) -> float:
    """p-th percentile: the value that p% of requests are faster than."""
    if not values:
        return 0.0
    s = sorted(values)
    k = min(len(s) - 1, int(round(p / 100 * (len(s) - 1))))
    return s[k]


def summary() -> dict:
    """Return headline numbers: count, error rate, p50/p95 latency, total tokens and cost."""
    with _lock:
        recs = list(_records)
    if not recs:
        return {"requests": 0}
    lat = [r["latency_ms"] for r in recs]
    errors = sum(not r["ok"] for r in recs)
    return {
        "requests": len(recs),
        "error_rate": round(errors / len(recs), 4),
        "latency_p50_ms": round(statistics.median(lat), 2),
        "latency_p95_ms": round(percentile(lat, 95), 2),
        "total_tokens": sum(r["input_tokens"] + r["output_tokens"] for r in recs),
        "total_cost_usd": round(sum(r["cost_usd"] for r in recs), 6),
    }


def reset():
    """Clear everything (used by tests)."""
    with _lock:
        _records.clear()
