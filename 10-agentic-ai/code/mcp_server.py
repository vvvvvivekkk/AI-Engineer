"""
mcp_server.py - a minimal Model Context Protocol (MCP) server: "study-helper".

MCP in one sentence: a standard plug (like USB-C) that lets any AI app (the "host",
e.g. Claude Desktop or VS Code) connect to any tool provider (the "server") the same way.

This server exposes the three MCP building blocks:
  * tools     - functions the MODEL may call (it decides when):   add, search_notes, save_note
  * resources - read-only data the APP can attach as context:      notes://index, notes://{topic}
  * prompts   - reusable prompt templates the USER can pick:       quiz_me

Written for the official Python SDK `mcp` version 2.x (installed here: 2.3.0), where the
high-level server class is `MCPServer`. In mcp 1.x the same class was called `FastMCP`,
so the import below falls back automatically.

Run it
------
    pip install mcp
    python mcp_server.py                    # speaks MCP over stdio (standard input/output)

You normally do NOT run it by hand: a host app starts it for you. See
mcp_client.py (a test client) and concepts.md section "Connecting to Claude Desktop / VS Code".
Never print() to stdout in a stdio server - stdout is the protocol channel. Log to stderr.
"""
import sys
from pathlib import Path

try:                                                    # mcp 2.x
    from mcp.server.mcpserver import MCPServer
except ImportError:                                     # mcp 1.x used a different name
    from mcp.server.fastmcp import FastMCP as MCPServer

# Create the server. The name is what host apps show in their UI.
mcp = MCPServer("study-helper")

# Our tiny "database": a JSON-free dict of notes. A real server might use files or a DB.
NOTES = {
    "agents": "An agent is an LLM running in a loop, choosing tools until the goal is met.",
    "mcp": "MCP is an open protocol that connects AI apps to tools and data in a standard way.",
    "react": "ReAct means Reason + Act: think, call a tool, observe, repeat.",
}
NOTES_DIR = Path(__file__).with_name("saved_notes")    # where save_note writes files


# ----------------------------- TOOLS -------------------------------------
# @mcp.tool() reads the function name, type hints and docstring and builds the
# JSON Schema for the model automatically.
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b


@mcp.tool()
def search_notes(keyword: str) -> list[str]:
    """Return every study note whose text contains the keyword (case-insensitive)."""
    k = keyword.lower()
    return [f"{topic}: {text}" for topic, text in NOTES.items() if k in text.lower() or k in topic]


@mcp.tool()
def save_note(topic: str, text: str) -> str:
    """Save a new study note to disk. This WRITES data, so hosts usually ask the user first."""
    safe = "".join(ch for ch in topic if ch.isalnum() or ch in "-_")[:40] or "note"  # no path tricks
    NOTES_DIR.mkdir(exist_ok=True)
    (NOTES_DIR / f"{safe}.txt").write_text(text, encoding="utf-8")
    NOTES[safe] = text                                  # also keep it in memory
    print(f"saved note {safe}", file=sys.stderr)        # log to stderr, never stdout
    return f"Saved note '{safe}'."


# --------------------------- RESOURCES -----------------------------------
# Resources are addressed by a URI (like a web address). The app reads them; the model doesn't call them.
@mcp.resource("notes://index")
def notes_index() -> str:
    """A comma-separated list of all note topics."""
    return ", ".join(sorted(NOTES))


@mcp.resource("notes://{topic}")                        # {topic} makes this a *template*
def note_by_topic(topic: str) -> str:
    """The text of one note."""
    return NOTES.get(topic, f"No note called '{topic}'.")


# ---------------------------- PROMPTS ------------------------------------
@mcp.prompt()
def quiz_me(topic: str) -> str:
    """A ready-made prompt that asks the model to quiz the user on a topic."""
    return (f"Using the note on '{topic}' ({NOTES.get(topic, 'no note')}), ask me 3 short "
            "quiz questions one at a time and wait for my answer each time.")


if __name__ == "__main__":
    mcp.run()          # default transport is stdio; use mcp.run("streamable-http") for a web server
