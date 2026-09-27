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
  - A2A agents: `PricingAgent` and `ProductAgent` with sync and async endpoints
  - Agent Cards (`/.well-known/agent.json`) for service discovery
  - Async task lifecycle: submit → poll → result
  - Docker support with health checks
  - GitHub Actions CI
  - Comprehensive test suite (25 tests)
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

## Documentation

- [Architecture](docs/architecture.md) - design decisions, module structure, and how to extend the project
- [Backlog](docs/backlog.md) - planned features and improvements, prioritised

## Testing

```bash
cd python
pytest
```
