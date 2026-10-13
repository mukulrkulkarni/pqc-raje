"""My MCP server.

Replace the example `echo` tool below with your own. Each function decorated
with `@mcp.tool()` becomes a tool the agent can call; the type hints and
docstring become its schema and description. Keep `main()` and the stdio run.
"""

from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP("my-mcp-server")


@mcp.tool()
def echo(text: str) -> str:
    """Return the text you send. Replace this with your real tool(s)."""
    return text


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
