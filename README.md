# FastPOC - FastAPI + MCP Integration POC

A demo repository for building AI-ready APIs. The goal is to explore and showcase how a REST API (FastAPI) and an MCP Server (Model Context Protocol) can share the same codebase and business logic — and to progressively extend it with other emerging concepts and new AI integration patterns.

Current focus: Python FastAPI + MCP with a simple Product CRUD domain as the working example.

## Project Structure

```
fastpoc/
├── python/          # Python implementation using FastAPI + MCP
│   ├── app/         # Application modules (REST, MCP, agents)
│   ├── main.py      # FastAPI entry point
│   ├── mcp_entry.py # MCP server entry point
│   └── README.md    # Python-specific documentation
├── examples/        # Standalone client scripts (A2A flow demo)
├── docs/            # Architecture and backlog
└── README.md        # This file
```

## Implementation

### Python (FastAPI + MCP) ✅ Production-Ready
- **Location**: `python/`
- **Technologies**: FastAPI, MCP (Model Context Protocol), Pydantic, SQLite
- **Features**: 
  - REST API with Swagger UI at `/api/v1/docs`
  - Versioned API endpoints (`/api/v1/products`)
  - MCP Server for AI tool integration
  - Shared codebase between API and MCP
  - SQLite database with automatic initialization
  - Full CRUD operations with input validation
  - Health check endpoints (`/health`, `/ready`)
  - API key authentication (`X-API-Key` header)
  - Rate limiting (60/min reads, 30/min writes)
  - Structured error responses (`{"error": {"code": "...", "message": "..."}}`)
  - A2A agents: `PricingAgent` and `ProductAgent` with sync, async, and streaming endpoints
  - Agent Cards (`/.well-known/agent.json`) for service discovery
  - Async task lifecycle: submit → poll → result
  - SSE streaming: live progress events via `text/event-stream`
  - Docker support with health checks
  - GitHub Actions CI
  - Comprehensive test suite (29 tests)
  - Environment-based configuration
  - Structured logging

See `python/README.md` for detailed instructions.

## Quick Start

### Using Docker (Recommended)
```bash
cd python
docker-compose up --build
```
Access the API at `http://localhost:8081` and Swagger UI at `http://localhost:8081/api/v1/docs`.

### Local Development
```bash
cd python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Configuration

Configure via environment variables or `.env` file:
- `PORT` - Server port (default: 8081)
- `HOST` - Server host (default: 0.0.0.0)
- `API_VERSION` - API version prefix (default: v1)
- `DB_PATH` - SQLite database path (default: auto-detected)
- `API_KEY` - API key for protected endpoints (default: `dev-key-changeme`)
- `PRICING_AGENT_URL` - Base URL of the PricingAgent; defaults to the same host (same-process call)

See `.env.example` for reference.

## Exploring the Layers

Start the server first:
```bash
cd python && python main.py
```

**REST API**
- Open `http://localhost:8081/api/v1/docs` — Swagger UI with all CRUD endpoints
- Click **Authorize**, enter `dev-key-changeme`, and all protected endpoints unlock for interactive testing

**MCP**
- Run `python mcp_entry.py` — starts the MCP server in stdio mode
- Connect via Claude Desktop using the config in `python/README.md`
- The five product tools (`list_products`, `get_product`, `create_product`, `update_product`, `delete_product`) appear as AI assistant tools

**A2A (Agent-to-Agent)**
- Open `http://localhost:8081/.well-known/agent.json` in a browser — the Agent Card describes what agents exist, what they can do, and where to call them
- Run `python examples/a2a_client.py` — walks through the full flow with printed output: discover → submit → poll → result
- Or call agents directly in Swagger: `POST /api/v1/agents/product/run` with `{"product_id": 1}`
- For live progress: `POST /api/v1/agents/product/stream` — returns `text/event-stream` with `working` events then the final `completed` result

**Reading the code**
- CRUD logic: `python/app/business.py` → `api.py`
- MCP tools: `python/app/mcp.py`
- A2A agents: `python/app/agents/router.py`, `pricing.py`, `cards.py`
- See [Architecture](docs/architecture.md) for design decisions and how the layers relate

## Documentation

- [Architecture](docs/architecture.md) - design decisions, module structure, and how to extend the project
- [Backlog](docs/backlog.md) - planned features and improvements, prioritised

## Testing

```bash
cd python
pytest
```
