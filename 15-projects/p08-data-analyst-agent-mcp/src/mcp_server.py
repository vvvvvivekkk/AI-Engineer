"""
mcp_server.py - expose the SAME tools through the Model Context Protocol (MCP).

**MCP** - an open standard for connecting AI apps to tools and data. Think of it
as "USB for AI tools": write a tool server once, and any MCP-capable client
(Claude Desktop, Claude Code, Cursor, VS Code agents, your own code) can plug it in.

Our server reuses the functions in tools.py, so the hand-written agent and MCP
clients get identical behaviour and identical safety checks.

This uses the official MCP Python SDK, version 2.x, where the high-level server
class is called `MCPServer` (in SDK 1.x the same idea was called `FastMCP`).

Run (stdio transport - the client starts this process and talks over stdin/stdout):
    python -m src.mcp_server
Check it without any client app:
    python -m src.mcp_check
"""
from __future__ import annotations

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError as MCPToolError

from . import tools

mcp = MCPServer(name="data-analyst", log_level="WARNING",
                instructions="Read-only tools over a fictional 2025 sales SQLite database "
                             "(tables regions, products, orders) plus internal notes.")


def _unwrap(result: dict) -> dict:
    """tools.call_tool returns {"error": ...} on failure. Raising the SDK's ToolError sends that message
    back to the client as an error result the model can read and correct (other exceptions are hidden)."""
    if isinstance(result, dict) and set(result) == {"error"}:
        raise MCPToolError(result["error"])
    return result


@mcp.tool(description=tools.TOOLS["get_schema"]["description"])
def get_schema() -> dict:
    return _unwrap(tools.call_tool("get_schema", {}))


@mcp.tool(description=tools.TOOLS["sql_query"]["description"])
def sql_query(query: str) -> dict:
    return _unwrap(tools.call_tool("sql_query", {"query": query}))


@mcp.tool(description=tools.TOOLS["python_calc"]["description"])
def python_calc(expression: str) -> dict:
    return _unwrap(tools.call_tool("python_calc", {"expression": expression}))


@mcp.tool(description=tools.TOOLS["make_chart"]["description"])
def make_chart(query: str, x: str, y: str, kind: str = "line", title: str = "") -> dict:
    return _unwrap(tools.call_tool("make_chart", {"query": query, "x": x, "y": y, "kind": kind, "title": title}))


@mcp.tool(description=tools.TOOLS["search_notes"]["description"])
def search_notes(query: str) -> dict:
    return _unwrap(tools.call_tool("search_notes", {"query": query}))


if __name__ == "__main__":
    mcp.run("stdio")
