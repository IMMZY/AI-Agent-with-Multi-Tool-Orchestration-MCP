# MCP Integration

## What the MCP Server Does

`src/mcp_server.py` is a **stdio-based MCP server** built with FastMCP.  It exposes three tools over a standard protocol so the agent never touches the database directly.

| Tool | Arguments | Description |
|---|---|---|
| `save_research` | `title`, `summary`, `sources`, `timestamp` | Insert a research note into SQLite |
| `list_research` | — | List all saved notes (id, title, timestamp) |
| `search_research` | `keyword` | Search notes by keyword |

## How the Agent Connects

The `store_node` in `src/tools/text_tools.py` launches the server as a subprocess:

```python
server_params = StdioServerParameters(
    command=sys.executable,
    args=["src/mcp_server.py"],
)
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        await session.call_tool("save_research", {...})
```

## Verifying the Server

```bash
python test_mcp_server.py
```

## Using with Claude Desktop

Add to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "research-assistant": {
      "command": "python",
      "args": ["src/mcp_server.py"],
      "cwd": "/path/to/this/project"
    }
  }
}
```
