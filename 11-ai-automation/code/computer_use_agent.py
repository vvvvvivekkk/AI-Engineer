"""
computer_use_agent.py - the shape of an Anthropic "computer use" agent loop.

Computer use = the model controls a whole desktop: it receives SCREENSHOTS and replies
with mouse/keyboard ACTIONS (click at x,y; type text; press a key; scroll...). Your
code performs each action on a real (virtual) screen and sends back a new screenshot.
It is the agent loop from module 10, where the tool is "a computer".

As of late 2026 the current tool type is "computer_toolset_20260801" (a single entry
that gives the model a set of member tools such as screenshot, left_click, type, key,
scroll, zoom, wait). Earlier versions ("computer_20251124", "computer_20250124") needed a
beta header. These names change - ALWAYS check the official page before running:
    https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool

IMPORTANT SAFETY RULES
----------------------
* Run it ONLY inside an isolated virtual machine or container (Anthropic publishes a
  Docker reference implementation - see the docs page). Never on your everyday computer.
* No logged-in accounts, passwords or personal files inside that machine.
* Keep a human watching; cap the number of steps; ask before any irreversible action.

What this file does
-------------------
* With no API key (default): runs a SIMULATED loop with a scripted "model" and a fake
  screen, so you can read the control flow safely. Nothing on your computer is touched.
* With ANTHROPIC_API_KEY and --real: sends ONE request and prints the actions the model
  wants. It deliberately does NOT execute them - you would connect an executor running
  inside your sandbox VM (e.g. xdotool + a screenshot tool) at the marked spot.
"""
import os
import sys

MAX_STEPS = 10


class FakeScreen:
    """Pretends to be a desktop. 'Executes' actions by updating a text description."""

    def __init__(self):
        self.state = "Desktop with a browser icon"

    def screenshot(self) -> str:
        return f"<screenshot: {self.state}>"           # a real one returns a base64 PNG image

    def do(self, action: dict) -> None:
        kind = action["action"]
        if kind == "left_click" and action.get("coordinate") == [40, 300]:
            self.state = "Browser open on a blank page with an address bar"
        elif kind == "type":
            self.state = f"Address bar contains '{action['text']}'"
        elif kind == "key" and action.get("text") == "Return":
            self.state = "Weather website showing: Taipei 24C sunny"


def scripted_model(step: int, screenshot: str) -> dict:
    """Stands in for Claude. Returns either a tool_use action or a final text answer."""
    plan = [
        {"action": "screenshot"},
        {"action": "left_click", "coordinate": [40, 300]},
        {"action": "type", "text": "weather taipei"},
        {"action": "key", "text": "Return"},
    ]
    if step < len(plan):
        return {"type": "tool_use", "input": plan[step]}
    return {"type": "text", "text": "The weather in Taipei is 24C and sunny."}


def simulated_loop() -> None:
    screen = FakeScreen()
    observation = screen.screenshot()
    for step in range(MAX_STEPS):                      # hard step limit
        reply = scripted_model(step, observation)      # 1. model sees screenshot, picks action
        if reply["type"] == "text":                    # 2. finished
            print("FINAL:", reply["text"])
            return
        action = reply["input"]
        print(f"step {step + 1}: model wants {action}")
        if action["action"] not in {"screenshot", "left_click", "type", "key", "scroll", "wait"}:
            print("  blocked: action not on the allow-list")
            continue
        if action["action"] != "screenshot":
            screen.do(action)                          # 3. execute on the (fake) computer
        observation = screen.screenshot()              # 4. new screenshot goes back to the model
        print("  ->", observation)
    print("Stopped: step limit reached")


def one_real_request() -> None:
    """Send one request and print the requested actions. Does NOT execute anything."""
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5"),
        max_tokens=1024,
        tools=[{"type": "computer_toolset_20260801"}],   # check the docs for the current type string
        messages=[{"role": "user", "content": "Take a screenshot and tell me what you see."}],
    )
    for block in response.content:
        if block.type == "tool_use":
            print("Model requested:", block.name, block.input)
            # >>> Here an executor INSIDE YOUR SANDBOX VM would perform the action,
            # >>> take a screenshot, and send it back as a tool_result image block.
        elif block.type == "text":
            print("Model said:", block.text)


if __name__ == "__main__":
    if "--real" in sys.argv and os.getenv("ANTHROPIC_API_KEY"):
        one_real_request()
    else:
        print("Running the SIMULATED computer-use loop (no API key used, nothing is clicked).\n")
        simulated_loop()
