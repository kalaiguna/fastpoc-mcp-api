# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Structured error responses — consistent `{"error": {"code": "...", "message": "..."}}` schema across all endpoints, documented in Swagger
- API key authentication via `X-API-Key` header — configurable through `API_KEY` environment variable, defaults to `dev-key-changeme` for local development; health endpoints remain public
- Rate limiting via `slowapi` — GET endpoints capped at 60 req/min, write endpoints (POST/PUT/DELETE) at 30 req/min; returns structured 429 error on breach
- GitHub Actions CI pipeline (`.github/workflows/ci.yml`) — runs the full test suite on every push to `main` and `feature/**` branches, and on all PRs targeting `main`

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

[Unreleased]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/kalaiguna/fastpoc-mcp-api/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/kalaiguna/fastpoc-mcp-api/releases/tag/v1.0.0
