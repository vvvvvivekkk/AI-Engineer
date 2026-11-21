"""
python_automation.py - a scheduled Python automation: fetch -> filter -> summarise -> save.

The same job as n8n workflow 02 (RSS digest), written as plain Python, so you can
compare "visual workflow tool" with "a script on a server".

Libraries
---------
schedule : runs a function at set times ("every day at 08:00"), inside your program.
httpx    : makes HTTP requests. We add timeouts and retries, because networks fail.

Run
---
    pip install schedule httpx
    python python_automation.py --once        # run the job one time and exit
    python python_automation.py               # keep running, job fires daily at 08:00

For production, prefer the operating system's scheduler (cron on Linux/macOS, Task
Scheduler on Windows) or a cloud scheduler, so the job survives reboots.
"""
import csv
import os
import sys
import time
import xml.etree.ElementTree as ET   # built-in XML parser (RSS feeds are XML)
from datetime import datetime
from pathlib import Path

import httpx

FEED_URL = os.getenv("FEED_URL", "https://hnrss.org/frontpage")   # any RSS feed works
KEYWORDS = ["ai", "llm", "agent", "python"]                         # only keep matching items
OUT_CSV = Path(__file__).with_name("digest.csv")

# An offline sample so the script still works with no internet.
SAMPLE_RSS = """<rss><channel>
<item><title>New open-source LLM agent framework released</title><link>https://example.com/1</link></item>
<item><title>Gardening tips for winter</title><link>https://example.com/2</link></item>
<item><title>Python 3.14 performance improvements</title><link>https://example.com/3</link></item>
</channel></rss>"""


def fetch_with_retry(url: str, attempts: int = 3, backoff: float = 1.0) -> str:
    """GET a URL; on failure wait 1s, 2s, 4s... and try again (exponential backoff)."""
    for i in range(attempts):
        try:
            r = httpx.get(url, timeout=10, follow_redirects=True)
            r.raise_for_status()                      # turn 4xx/5xx status codes into errors
            return r.text
        except httpx.HTTPError as e:
            wait = backoff * 2 ** i
            print(f"attempt {i + 1} failed ({type(e).__name__}); retrying in {wait:.0f}s", file=sys.stderr)
            time.sleep(wait)
    print("all attempts failed - using the offline sample feed", file=sys.stderr)
    return SAMPLE_RSS


def parse_items(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    return [{"title": it.findtext("title", ""), "link": it.findtext("link", "")}
            for it in root.iter("item")]


def keep_relevant(items: list[dict]) -> list[dict]:
    """Keep items whose title contains a keyword as a whole word ('ai' must not match 'rain')."""
    kept = []
    for it in items:
        words = {w.strip(".,:;!?()").lower() for w in it["title"].split()}   # set of clean words
        if words & set(KEYWORDS):                                            # any overlap?
            kept.append(it)
    return kept


def summarise(title: str) -> str:
    """Where an LLM would go. Offline stand-in: shorten the title."""
    if os.getenv("ANTHROPIC_API_KEY"):
        import anthropic
        msg = anthropic.Anthropic().messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5"), max_tokens=60,
            messages=[{"role": "user", "content": f"Summarise in 12 words: {title}"}])
        return msg.content[0].text
    return title[:60]


def job() -> None:
    items = keep_relevant(parse_items(fetch_with_retry(FEED_URL)))[:5]
    new_file = not OUT_CSV.exists()
    with OUT_CSV.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["date", "title", "summary", "link"])           # header row once
        for it in items:
            w.writerow([datetime.now().date(), it["title"], summarise(it["title"]), it["link"]])
    print(f"{datetime.now():%H:%M} saved {len(items)} items to {OUT_CSV.name}")


if __name__ == "__main__":
    if "--once" in sys.argv:
        job()
    else:
        import schedule
        schedule.every().day.at("08:00").do(job)     # register the job
        print("Scheduler running. Ctrl+C to stop.")
        while True:
            schedule.run_pending()                    # run any job whose time has come
            time.sleep(30)                            # check twice a minute
