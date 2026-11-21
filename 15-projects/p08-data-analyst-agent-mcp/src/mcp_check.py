"""
mcp_check.py - prove the MCP server works, with no desktop app needed.

Two checks:
  1. in-process: connect the SDK's `Client` straight to the server object
     (fast; this is what the tests use)
  2. stdio: start `python -m src.mcp_server` as a real subprocess and talk to it
     over stdin/stdout - exactly what Claude Desktop or Claude Code would do

Run:  python -m src.mcp_check
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

ROOT = Path(__file__).resolve().parents[1]


def _text(result) -> str:
    """Pull the text out of an MCP tool result."""
    return " ".join(getattr(c, "text", "") for c in result.content)


async def check(client_target) -> None:
    async with Client(client_target) as client:
        listed = await client.list_tools()
        print("tools:", [t.name for t in listed.tools])
        ok = await client.call_tool("sql_query", {"query": "SELECT COUNT(*) AS n FROM orders"})
        print("sql_query ->", " ".join(_text(ok).split())[:120])
        bad = await client.call_tool("sql_query", {"query": "DROP TABLE orders"})
        print("blocked write -> is_error =", bad.is_error, "|", _text(bad)[:100])


def main():
    from .mcp_server import mcp
    print("== in-process ==")
    asyncio.run(check(mcp))
    print("== stdio subprocess ==")
    params = StdioServerParameters(command=sys.executable, args=["-m", "src.mcp_server"], cwd=str(ROOT))
    asyncio.run(check(params))


if __name__ == "__main__":
    main()
