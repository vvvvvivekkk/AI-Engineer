"""
metrics_dashboard.py - simulate 7 days of traffic for an LLM app and draw a 4-panel dashboard.

Panels: requests + error rate, latency p50/p95, daily token cost, and a drift signal.
"Drift" = the inputs (or outputs) slowly changing compared with what the app was built and tested on.
Here we track average prompt length; a sudden jump is a warning sign.

Run:  python metrics_dashboard.py      -> saves dashboard.png next to this file
"""
import pathlib
import numpy as np                 # fast numeric arrays
import pandas as pd                # tables
import matplotlib
matplotlib.use("Agg")              # draw to a file, no window needed (works on servers)
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)    # fixed "seed" so the fake data is the same every run


def simulate(hours: int = 24 * 7) -> pd.DataFrame:
    """One row per hour with made-up but realistic numbers."""
    t = pd.date_range("2026-11-01", periods=hours, freq="h")
    daily = 1 + 0.6 * np.sin((t.hour - 8) / 24 * 2 * np.pi)          # more traffic in the daytime
    requests = rng.poisson(200 * daily)                                # Poisson = count of random events
    p50 = rng.normal(800, 60, hours)                                   # median latency in ms
    p95 = p50 * rng.normal(2.2, 0.15, hours)                           # slow tail is ~2x the median
    err = np.clip(rng.normal(0.01, 0.004, hours), 0, None)             # ~1% errors
    err[100:106] = 0.09                                                # an incident: provider outage
    p95[100:106] *= 2.5
    prompt_len = rng.normal(350, 25, hours)                            # tokens per prompt
    prompt_len[130:] += 180                                            # drift: users start pasting long docs
    cost = requests * (prompt_len * 1.0 + 150 * 5.0) / 1e6             # $ using example prices per 1M tokens
    return pd.DataFrame({"time": t, "requests": requests, "p50": p50, "p95": p95,
                         "error_rate": err, "prompt_tokens": prompt_len, "cost_usd": cost})


def draw(df: pd.DataFrame, out: pathlib.Path):
    fig, ax = plt.subplots(2, 2, figsize=(13, 7.5))
    a = ax[0, 0]
    a.bar(df.time, df.requests, width=0.04, color="#9fb3c8", label="requests/hour")
    a2 = a.twinx()                                                     # second y-axis on the right
    a2.plot(df.time, df.error_rate * 100, color="#d1495b", label="error rate %")
    a2.axhline(5, ls="--", color="#d1495b", lw=1)                     # alert threshold
    a.set_title("Traffic and error rate (dashed = 5% alert line)")
    a.set_ylabel("requests/hour"); a2.set_ylabel("error %")
    b = ax[0, 1]
    b.plot(df.time, df.p50, label="p50 (median)", color="#0f9d9a")
    b.plot(df.time, df.p95, label="p95 (slowest 5%)", color="#1b263b")
    b.axhline(3000, ls="--", color="grey", lw=1, label="SLO 3 s")
    b.set_title("Latency (ms)"); b.legend()
    c = ax[1, 0]
    daily_cost = df.set_index("time").cost_usd.resample("D").sum()
    c.bar(daily_cost.index.strftime("%b %d"), daily_cost.values, color="#0f9d9a")
    c.set_title("Token cost per day (USD, example prices)")
    d = ax[1, 1]
    d.plot(df.time, df.prompt_tokens, color="#5a6370", alpha=0.5, label="avg prompt tokens/hour")
    d.plot(df.time, df.prompt_tokens.rolling(12).mean(), color="#e07a5f", label="12-hour rolling mean")
    d.axhline(df.prompt_tokens[:72].mean() * 1.25, ls="--", color="#e07a5f", lw=1, label="baseline +25%")
    d.set_title("Drift signal: prompt length"); d.legend()
    for axis in ax.flat:
        axis.tick_params(axis="x", labelrotation=30, labelsize=8)
    fig.suptitle("LLM app monitoring dashboard (simulated week)", fontsize=14, weight="bold")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    df = simulate()
    out = pathlib.Path(__file__).with_name("dashboard.png")
    draw(df, out)
    print(df.describe().round(2))
    print("saved", out)
