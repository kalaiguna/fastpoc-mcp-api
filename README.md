# FastPOC - Python FastAPI + MCP Product CRUD

This repository contains a Product CRUD implementation using Python FastAPI with MCP (Model Context Protocol) integration.

## Project Structure

```
fastpoc/
├── python/          # Python implementation using FastAPI + MCP
│   ├── app/         # Application modules
│   ├── main.py      # FastAPI entry point
│   ├── mcp_entry.py # MCP server entry point
│   └── README.md    # Python-specific documentation
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
  - Docker support with health checks
  - Comprehensive test suite (12 tests)
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

See `.env.example` for reference.

## Testing

```bash
cd python
pytest
```
