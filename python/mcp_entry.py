"""
Entry point for running the MCP Server (Stdio mode).
"""
# Accept any protocol version the client requests, including post-2025-06-18 versions.
import mcp.types as _mcp_types
import mcp.shared.version as _mcp_version
_mcp_types.LATEST_PROTOCOL_VERSION = "2025-11-25"
_mcp_version.SUPPORTED_PROTOCOL_VERSIONS = [
    "2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"
]

from app.service import mcp

if __name__ == "__main__":
    mcp.run()
