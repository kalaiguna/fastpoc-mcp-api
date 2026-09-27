# Architecture

## Overview

This project exposes a single Product database through two interfaces: a REST API (FastAPI) and an MCP Server (Model Context Protocol). Both share the same business logic — no duplication.

```
app/
├── models.py       # Pydantic schemas (shared by API and MCP)
├── db.py           # SQLite data access layer
├── business.py     # Domain logic (the single source of truth)
├── api.py          # REST endpoints — thin wrappers over business.py
├── mcp.py          # MCP tools — thin wrappers over business.py
├── service.py      # Wires the MCP server instance (used by mcp_entry.py)
└── auth.py         # API key dependency
```

## Key Design Decisions

### Shared business layer
`business.py` holds all domain logic. `api.py` and `mcp.py` are intentionally thin — they handle transport concerns (HTTP status codes, MCP tool signatures) and delegate everything else. Adding a third interface (e.g. GraphQL) means writing another thin wrapper, not touching business logic.

### Auth as a FastAPI dependency, not middleware
Auth is applied per-endpoint via `dependencies=[Depends(require_api_key)]`. This makes it explicit which endpoints are protected, keeps health check endpoints public without special-casing, and makes the auth behaviour visible in Swagger. Middleware would silently apply to everything, which is harder to reason about and test.

### Rate limiting per endpoint
Different rate limits for reads (60/min) vs writes (30/min) reflect real-world API design. Applied via `@limiter.limit(...)` decorator so limits are visible at the call site, not hidden in middleware config.

### Structured error responses
All errors follow `{"error": {"code": "NOT_FOUND", "message": "..."}}`. A single `http_exception_handler` on the app handles this centrally — individual endpoints just raise `HTTPException` as normal. The schema is documented in Swagger via the `responses=` parameter on each endpoint.

## Entry Points

| File | Purpose |
|---|---|
| `main.py` | Starts the FastAPI server (REST API) |
| `mcp_entry.py` | Starts the MCP server in stdio mode (for AI clients like Claude Desktop) |

## Extending the Project

**Add a new endpoint:** add a function in `business.py`, then a route in `api.py`.

**Add a new MCP tool:** add a function in `business.py`, then a `@mcp.tool()` in `mcp.py`.

**Change the database:** only `db.py` needs to change; nothing else depends on SQLite directly.
