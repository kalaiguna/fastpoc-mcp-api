"""
Entry point for running the MCP Server (Stdio mode).
"""
from app.service import mcp

if __name__ == "__main__":
    mcp.run()
