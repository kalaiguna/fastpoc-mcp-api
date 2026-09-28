# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.9.0] - 2026-09-28

### Fixed
- SSE generators now emit a `failed` event on any unexpected exception instead of silently truncating the stream
- `_stream_product` previously caught only `httpx.HTTPError`, missing `ValidationError` and `JSONDecodeError` from PricingAgent responses — now catches all exceptions
- SSE responses now include `Cache-Control: no-cache` and `X-Accel-Buffering: no` headers to prevent proxy buffering
- `service_card()` PricingAgent skill was missing `submitEndpoint` and `streamEndpoint` — fixed to match per-agent card
- `AgentCapabilities.streaming` corrected from `False` to `True`
- Test teardown was restoring `agents_router_module.db` to the test DB instead of the original — fixed

### Changed
- Extracted `_call_pricing_agent()` helper, eliminating three copies of the same `httpx.post` block in `router.py`

## [1.8.0] - 2026-09-28

### Added
- SSE streaming endpoints for both agents — receive incremental progress events then the final result without polling:
  - `POST /api/v1/agents/pricing/stream` — emits `working` progress events then `completed` with pricing result
  - `POST /api/v1/agents/product/stream` — emits `working` progress events (fetch, pricing call, combine) then `completed` with full analysis
- `streamEndpoint` field added to `AgentSkill` model; populated on all skills in `cards.py` so callers can discover the stream URL from the Agent Card

### Changed
- CI runner pinned to `ubuntu-24.04` to avoid the upcoming `ubuntu-latest` migration to Ubuntu 26

## [1.7.0] - 2026-09-27

### Added
- `examples/a2a_client.py` — standalone script demonstrating the full A2A flow (discovery, submit, poll, result) against the live service; no hardcoded URLs, all resolved from the Agent Card
- `examples/README.md` — usage instructions and expected output for the client example
- `submitEndpoint` field added to `AgentSkill` model; populated on all agent skills in `cards.py`

## [1.6.0] - 2026-09-27

### Added
- Async task lifecycle for A2A agents — submit a task, get a task ID, poll for result:
  - `POST /api/v1/agents/pricing/submit` — submit pricing analysis task
  - `POST /api/v1/agents/product/submit` — submit product analysis task
  - `GET /api/v1/agents/tasks/{task_id}` — poll task status (`submitted` → `working` → `completed` / `failed`)
- `app/agents/task_store.py` — thread-safe in-memory task store (production note: swap for Redis or SQLite)
- `TaskStatus`, `Task`, `TaskSubmission` models added to `agents/models.py`

## [1.5.0] - 2026-09-27

### Added
- Agent Cards — each agent is now self-describing:
  - `GET /.well-known/agent.json` — service-level card listing all agents and their skills; public, no auth required
  - `GET /api/v1/agents/pricing/card` — PricingAgent card
  - `GET /api/v1/agents/product/card` — ProductAgent card
- `app/agents/cards.py` — card factory functions; URLs are derived from env vars so cards stay accurate across environments
- `AgentCard`, `AgentSkill`, `AgentAuthentication`, `AgentCapabilities` models added to `agents/models.py`

## [1.4.0] - 2026-09-27

### Added
- Agent-to-Agent (A2A) demo — two agents communicating via HTTP:
  - `PricingAgent` (`POST /api/v1/agents/pricing/run`) — rule-based pricing analysis for a product
  - `ProductAgent` (`POST /api/v1/agents/product/run`) — fetches product data, delegates to PricingAgent via HTTP, returns combined analysis
- `app/agents/` package: `models.py`, `pricing.py`, `router.py`
- `app/limiter.py` — shared rate limiter instance used across API and agent routes
- `docs/backlog.md` — prioritised feature backlog (Agent Card, Task Lifecycle, Streaming, Push Notifications, Auth upgrade, PostgreSQL)

## [1.3.0] - 2026-09-27

### Added
- Structured error responses — consistent `{"error": {"code": "...", "message": "..."}}` schema across all endpoints, documented in Swagger
- API key authentication via `X-API-Key` header — configurable through `API_KEY` environment variable, defaults to `dev-key-changeme` for local development; health endpoints remain public
- Rate limiting via `slowapi` — GET endpoints capped at 60 req/min, write endpoints (POST/PUT/DELETE) at 30 req/min; returns structured 429 error on breach
- GitHub Actions CI pipeline (`.github/workflows/ci.yml`) — runs the full test suite on every push to `main` and `feature/**` branches, and on all PRs targeting `main`
- `docs/architecture.md` — design decisions, module structure, and extension guide; linked from both READMEs

## [1.2.0] - 2026-09-27

### Changed
- Split monolithic `app/mcp_server.py` into three focused modules: `business.py` (domain logic), `service.py` (MCP wiring), `mcp.py` (tool definitions)
- Updated `mcp_entry.py` to import from the new service layer
- Updated `test_mcp_logic` test to reference new module structure
- Simplified README — removed Future Implementations section (C#, Java, Node.js), rewrote intro to reflect the POC's actual purpose

### Removed
- `python/app/mcp_server.py` — replaced by the modular three-file structure above
- Debug and analysis scripts: `check_endpoints.py`, `check_sse.py`, `check_sse_sig.py`, `check_mcp_count.py`, `debug_mcp.py`, `inspect_mcp.py`
- Temporary markdown files: `CHANGELOG.md`, `MCP_CLIENT_SETUP.md`, `MCP_TOOLS_REFACTOR.md`, `UTILITY_FILES_ANALYSIS.md`
- Stray database files (`products.db`, `test_products.db`) from repo root

## [1.1.0] - 2026-08-18

Production-ready hardening by Qwen AI on the initial CRUD skeleton.

### Added
- SQLite database with absolute path management and context managers
- Versioned REST API routes at `/api/v1/products`
- Health check endpoints: `/health` and `/ready`
- Pydantic field validators for all input models (name, price, stock)
- Structured logging throughout the application
- `Dockerfile` and `docker-compose.yml` with health checks
- `pytest.ini` and extended test suite (12 tests covering UPDATE, DELETE, 404, and validation cases)
- `python/.gitignore` and `.env.example`

### Changed
- `requirements.txt` — pinned dependency versions for reproducibility
- `README.md` and `python/README.md` — full installation, configuration, and usage documentation
- SQL injection prevention via column whitelist in `db.py`

## [1.0.0] - 2025-12-17

### Added
- `python/app/api.py` — FastAPI REST API with full CRUD endpoints for Products
- `python/app/mcp_server.py` — MCP Server exposing product tools via Model Context Protocol
- `python/app/db.py` — in-memory SQLite database with 30 pre-populated sample products
- `python/app/models.py` — Pydantic models: `Product`, `ProductCreate`, `ProductUpdate`
- `python/main.py` — unified entry point serving both API and MCP over SSE
- `python/mcp_entry.py` — standalone MCP stdio entry point
- `python/test_app.py` — initial test suite
- `python/requirements.txt`, `python/README.md`

[Unreleased]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.9.0...HEAD
[1.9.0]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/kalaiguna/fastpoc-mcp-api/releases/tag/v1.0.0
