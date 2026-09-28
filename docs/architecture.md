# Architecture

## Overview

This project exposes a single Product database through two interfaces: a REST API (FastAPI) and an MCP Server (Model Context Protocol). Both share the same business logic — no duplication. An Agent layer demonstrates the A2A (Agent-to-Agent) communication pattern on top of the REST API.

```
app/
├── models.py           # Pydantic schemas (shared by API and MCP)
├── db.py               # SQLite data access layer
├── business.py         # Domain logic (the single source of truth)
├── api.py              # REST endpoints — thin wrappers over business.py
├── mcp.py              # MCP tool definitions — thin wrappers over business.py
├── service.py          # Wires the MCP server instance (used by mcp_entry.py)
├── auth.py             # API key dependency
├── limiter.py          # Shared rate limiter instance
└── agents/
    ├── models.py       # Agent schemas: requests, results, task lifecycle, agent cards
    ├── pricing.py      # PricingAgent logic (pure functions)
    ├── cards.py        # Agent Card factories (A2A discovery)
    ├── task_store.py   # Thread-safe in-memory task store
    └── router.py       # Agent HTTP endpoints: sync /run, async /submit, poll /tasks
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

### Agent-to-Agent (A2A) communication

`ProductAgent` calls `PricingAgent` via HTTP using `httpx`. In the default setup both agents run in the same FastAPI process — `ProductAgent` is effectively calling itself on the same port. This is intentional for the demo: it keeps the setup simple while demonstrating the communication pattern.

**What is already implemented:**
- `PricingAgent` is a plain authenticated HTTP endpoint — any external system with a valid `X-API-Key` can call it today, no changes needed.
- `ProductAgent` reads `PRICING_AGENT_URL` from an environment variable. Point it at a remote host and it calls a remote `PricingAgent` with zero code changes.
- Agent Cards (`/.well-known/agent.json`, `/agents/pricing/card`, `/agents/product/card`) — each agent is self-describing: name, skills, endpoint URLs, auth requirements, and async `submitEndpoint`.
- Async task lifecycle — `POST /agents/{agent}/submit` returns a task ID immediately; background execution happens in a thread pool; `GET /agents/tasks/{id}` polls for `submitted → working → completed / failed`.
- `examples/a2a_client.py` — standalone caller demonstrating the full flow: read Agent Card for discovery, submit a task, poll for result, display output.

**What is not yet implemented (full A2A spec):**
- Capability negotiation — agents cannot describe what they can do to each other dynamically at runtime.
- Push notifications — callback URL on submit instead of polling (caller must expose an HTTP endpoint to receive the callback).
- These remain in the backlog.

The pricing logic lives in pure functions in `pricing.py`, keeping it testable without a running server.

## Entry Points

| File | Purpose |
|---|---|
| `main.py` | Starts the FastAPI server (REST API) |
| `mcp_entry.py` | Starts the MCP server in stdio mode (for AI clients like Claude Desktop) |

## Extending the Project

**Add a new endpoint:** add a function in `business.py`, then a route in `api.py`.

**Add a new MCP tool:** add a function in `business.py`, then a `@mcp.tool()` in `mcp.py`.

**Add a new agent:** add logic functions in `app/agents/`, register a route in `agents/router.py`. Point `PRICING_AGENT_URL` (or a new env var) to a separate host to run it as a true remote agent.

**Change the database:** only `db.py` needs to change; nothing else depends on SQLite directly.
