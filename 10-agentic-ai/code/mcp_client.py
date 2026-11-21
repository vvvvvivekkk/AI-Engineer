"""
mcp_client.py - a tiny MCP client that starts mcp_server.py and talks to it.

This is what a host (Claude Desktop, VS Code, Cursor...) does behind the scenes:
  1. start the server as a child process (stdio transport)
  2. handshake ("initialize")
  3. list the tools / resources / prompts
  4. call a tool when the model asks for one

Written for mcp 2.x (uses mcp.Client). Run:  python mcp_client.py
"""
import asyncio                     # MCP clients are asynchronous (they wait on I/O)
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters   # Client = high-level client in mcp 2.x

SERVER = Path(__file__).with_name("mcp_server.py")


async def main() -> None:
    # Describe HOW to start the server: the same info you put in a host's config file.
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with Client(params) as client:                         # starts the process + handshake
        tools = await client.list_tools()
        print("Tools:", [t.name for t in tools.tools])
        print("Schema of 'add':", tools.tools[0].input_schema)    # auto-built JSON Schema

        result = await client.call_tool("add", {"a": 2, "b": 40})
        print("add(2, 40) ->", result.content[0].text)

        result = await client.call_tool("search_notes", {"keyword": "loop"})
        print("search_notes('loop') ->", result.content[0].text)

        index = await client.read_resource("notes://index")
        print("notes://index ->", index.contents[0].text)

        prompt = await client.get_prompt("quiz_me", {"topic": "mcp"})
        print("quiz_me prompt ->", prompt.messages[0].content.text)


if __name__ == "__main__":
    asyncio.run(main())
