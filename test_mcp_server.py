"""
test_mcp_server.py — Verify the MCP server starts and responds before connecting clients.

Run this standalone to confirm the server is healthy:
    python test_mcp_server.py
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MCP_SERVER = "src/mcp_server.py"


async def verify_mcp_server() -> bool:
    """
    Start the MCP server as a subprocess and list its available tools.

    Returns:
        True if the server started and responded correctly, False otherwise.
    """
    print(f"[test_mcp_server] Starting MCP server: {MCP_SERVER}")
    try:
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[MCP_SERVER],
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                tool_names = [t.name for t in tools.tools]
                print(f"[test_mcp_server] Server OK. Tools available: {tool_names}")

                expected = {"save_research", "list_research", "search_research"}
                missing = expected - set(tool_names)
                if missing:
                    print(f"[test_mcp_server] WARNING: missing tools: {missing}")
                    return False

                print("[test_mcp_server] All required tools present.")
                return True
    except Exception as exc:
        print(f"[test_mcp_server] FAILED: {exc}", file=sys.stderr)
        return False


if __name__ == "__main__":
    ok = asyncio.run(verify_mcp_server())
    sys.exit(0 if ok else 1)
