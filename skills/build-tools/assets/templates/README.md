# My MCP Server

A Level-3 external MCP server for Innovium, built with [FastMCP](https://github.com/jlowin/fastmcp) + [uv](https://docs.astral.sh/uv/). Scaffolded from the `build-tools` skill.

## Fill it in

1. Rename `my-mcp-server` / `my_mcp_server` to your own id (lowercase kebab for the id, snake_case for the Python package) in `innovium.json`, `pyproject.toml`, and the `src/` folder.
2. In `src/<pkg>/server.py`, replace the `echo` tool with your own `@mcp.tool()` functions. Type hints + docstrings become the tool schema.
3. Edit `innovium.json`: set `name`, `description`, `category`, and — if your server shells out to a binary or another runtime — declare it under `dependencies.runtime` (Innovium auto-injects `uv`/`npx`/`node`/`bun`/`docker`/`python`, but nothing else).

## Verify (the same gates Innovium's Packaging & Testing runs)

```bash
uv run python scripts/validate_innovium.py   # manifest is well-formed
uv run python scripts/test_innovium.py       # server spawns + answers initialize + tools/list
```

## Ship it

- Push the repo to GitHub with `innovium.json` at the root — Innovium's scan lists it in the marketplace.
- Or add it directly in **Settings → Tools → Import Tool** (local `command`) for a private/local one.
