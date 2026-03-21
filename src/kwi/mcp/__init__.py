"""kwi MCP server — expose work item operations to AI agents."""

from kwi.mcp.server import mcp


def main() -> None:
    """Entry point for the kwi-mcp command."""
    mcp.run()
