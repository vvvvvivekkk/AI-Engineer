"""
browser_use_agent.py - an LLM-driven browser agent with the `browser-use` library.

Difference from playwright_basics.py
------------------------------------
Playwright script : YOU write every click.         Fast, cheap, predictable, breaks if the page changes.
Browser agent     : you write a GOAL in English; an LLM looks at the page (text of the
                    page structure and/or screenshots), decides the next click/type,
                    and repeats - the same agent loop as module 10, with browser actions as tools.
                    Flexible, but slower, costs tokens on every step, and can make mistakes.

NOT installed in the course environment. To try it on your own machine:
    python -m venv .venv && source .venv/bin/activate
    pip install browser-use
    playwright install chromium          # browser-use drives a Chromium browser
    export ANTHROPIC_API_KEY=your-key-here
    python browser_use_agent.py

The browser-use API changes quickly. As of late 2026 check https://docs.browser-use.com
for the current class names (the LLM wrapper classes have been renamed before).

Safety
------
* Use a SEPARATE browser profile with no saved passwords or logged-in accounts.
* Never let it complete purchases or submit forms with personal data without you watching.
* Web pages can contain hidden text that tries to give the agent instructions
  (prompt injection). Treat page content as untrusted.
"""
import asyncio
import os
import sys

try:
    from browser_use import Agent            # the agent loop that controls the browser
    from browser_use import ChatAnthropic    # browser-use's own wrapper around the Anthropic API
except ImportError:
    print("browser-use is not installed (see the setup steps at the top of this file).")
    sys.exit(0)

if not os.getenv("ANTHROPIC_API_KEY"):
    print("Set ANTHROPIC_API_KEY first.")
    sys.exit(0)

TASK = (
    "Go to https://news.ycombinator.com, find the three top stories, "
    "and return their titles and points as a bullet list. Do not log in or click ads."
)


async def main() -> None:
    llm = ChatAnthropic(model=os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5"))  # check the models page
    agent = Agent(task=TASK, llm=llm)       # goal + brain; browser-use adds the browser tools
    history = await agent.run(max_steps=15) # hard cap on loop iterations (cost + safety)
    print(history.final_result())           # the agent's final answer text


if __name__ == "__main__":
    asyncio.run(main())
