"""
mcp_server_solution.py - solution to exercise 9: the study-helper server plus
a word_count tool and a notes://count resource.

Run the check at the bottom:  python mcp_server_solution.py --test
Run as a real server:         python mcp_server_solution.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from mcp_server import NOTES, mcp   # reuse the original server object and its tools


@mcp.tool()
def word_count(text: str) -> int:
    """Count the words in a piece of text."""
    return len(text.split())


@mcp.resource("notes://count")
def notes_count() -> str:
    """How many notes exist."""
    return str(len(NOTES))


async def test() -> None:
    from mcp import Client                    # mcp 2.x in-memory client
    async with Client(mcp) as c:
        print("tools:", [t.name for t in (await c.list_tools()).tools])
        print("word_count ->", (await c.call_tool("word_count", {"text": "agents use tools in a loop"})).content[0].text)
        print("notes://count ->", (await c.read_resource("notes://count")).contents[0].text)


if __name__ == "__main__":
    if "--test" in sys.argv:
        asyncio.run(test())
    else:
        mcp.run()
