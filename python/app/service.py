""" service.py
Unified Service Module
Integrates FastAPI and MCP into a single application.
This module acts as the orchestration layer.
"""
from app.api import app
from app.mcp import mcp
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://kngiafgkdnlkgmefdafaibkibegkcaef"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount MCP SSE endpoint to the FastAPI app
app.mount("/sse", mcp.sse_app())

# Add MCP tools endpoint
@app.get("/tools")
async def list_mcp_tools():
    return mcp.get_tools_info() 

# @app.get("/tools")
# async def list_mcp_tools():
#     """Expose MCP tools for discovery"""
#     tools = []
    
#     # Get all registered tools from the MCP instance
#     for tool_name, tool_info in mcp._tools.items():
#         tools.append({
#             "name": tool_name,
#             "description": tool_info.description or "",
#             "inputSchema": {
#                 "type": "object",
#                 "properties": {},
#                 "required": [],
#                 "title": f"{tool_name}Arguments"
#             }
#         })
    
#     return Response(
#         content=json.dumps({"tools": tools}),
#         media_type="application/json"
#     )

# Export the integrated app for use in main.py
__all__ = ["app"]
