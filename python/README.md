# FastAPI + MCP Product CRUD Prototype

This project implements a simple Product CRUD application that exposes both a REST API (via FastAPI) and an MCP Server (via Model Context Protocol), sharing the same SQLite database.

## ✨ Key Features

- **Dual Interface**: REST API and MCP Server sharing the same business logic
- **Production-Ready**: Input validation, health checks, logging, and error handling
- **Versioned API**: `/api/v1/products` with Swagger UI at `/api/v1/docs`
- **Database**: SQLite with automatic initialization and proper path management
- **Docker Support**: Ready-to-use Dockerfile and docker-compose.yml
- **Comprehensive Tests**: 12 tests covering all CRUD operations and edge cases
- **Configuration**: Environment-based settings via `.env` file or variables

## Prerequisites

- Python 3.10+
- Docker (optional, for containerized deployment)

## Installation

### Option 1: Local Development

1. Clone the repository (if not already done).
2. Navigate to the python directory:
   ```bash
   cd python
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Docker (Recommended)

```bash
cd python
docker-compose up --build
```

## Configuration

Copy `.env.example` to `.env` and customize as needed:

```bash
cp .env.example .env
```

Available configuration options:
- `PORT` - Server port (default: 8081)
- `HOST` - Server host (default: 0.0.0.0)
- `API_VERSION` - API version prefix (default: v1)
- `DB_PATH` - SQLite database path (default: auto-detected in app directory)

## Running the API

To start the FastAPI server:

```bash
python main.py
```

The API will be available at `http://localhost:8081`.
- **Swagger UI**: `http://localhost:8081/api/v1/docs`
- **Health Check**: `http://localhost:8081/health`
- **Readiness Check**: `http://localhost:8081/ready`

## Running the MCP Server

To start the MCP server (Stdio mode):

```bash
python mcp_entry.py
```

This is typically used by an MCP client (like Claude Desktop or an IDE extension) which will spawn this process.

### Configuring for Claude Desktop

Add the following to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "fastpoc": {
      "command": "python",
      "args": ["/absolute/path/to/fastpoc/python/mcp_entry.py"]
    }
  }
}
```

## Testing

Run the comprehensive test suite:

```bash
pytest
```

This runs 12 tests covering:
- All CRUD operations (Create, Read, Update, Delete)
- Error handling (404 scenarios)
- Input validation (negative prices, empty names, etc.)
- Health check endpoints

## API Endpoints

All endpoints are prefixed with `/api/v1`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products` | List all products |
| GET | `/api/v1/products/{id}` | Get product by ID |
| POST | `/api/v1/products` | Create new product |
| PUT | `/api/v1/products/{id}` | Update product |
| DELETE | `/api/v1/products/{id}` | Delete product |
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |

### Example Requests

All product endpoints require an `X-API-Key` header. Set `API_KEY` in your `.env` file (defaults to `dev-key-changeme` locally).

**Create a product:**
```bash
curl -X POST "http://localhost:8081/api/v1/products" \
  -H "X-API-Key: dev-key-changeme" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product", "price": 10.5, "stock": 100}'
```

**Get all products:**
```bash
curl "http://localhost:8081/api/v1/products" \
  -H "X-API-Key: dev-key-changeme"
```

**Update a product:**
```bash
curl -X PUT "http://localhost:8081/api/v1/products/1" \
  -H "X-API-Key: dev-key-changeme" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Product", "price": 15.99, "stock": 50}'
```

**Delete a product:**
```bash
curl -X DELETE "http://localhost:8081/api/v1/products/1" \
  -H "X-API-Key: dev-key-changeme"
```

## Project Structure

```
python/
├── app/                      # Application modules
│   ├── models.py             # Pydantic schemas (shared by API and MCP)
│   ├── db.py                 # SQLite data access layer
│   ├── business.py           # Domain logic (single source of truth)
│   ├── api.py                # REST endpoints
│   ├── mcp.py                # MCP tool definitions
│   ├── service.py            # MCP server wiring
│   └── auth.py               # API key authentication dependency
├── main.py                   # FastAPI entry point
├── mcp_entry.py              # MCP server entry point (stdio mode)
├── requirements.txt          # Python dependencies (pinned versions)
├── pytest.ini                # Pytest configuration
├── .env.example              # Environment variables template
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # This file
```

See [Architecture](../docs/architecture.md) for design decisions and how to extend the project.

## Input Validation

The API enforces the following validation rules:
- **Name**: Required, 1-100 characters
- **Description**: Optional, max 500 characters
- **Price**: Required, must be positive (> 0)
- **Stock**: Required, must be non-negative (≥ 0)

Invalid requests return appropriate HTTP 422 errors with detailed messages.

## Logging

The application uses Python's logging module with structured output. Logs include:
- Application startup/shutdown events
- Request processing information
- Database operations
- Errors and warnings

## Docker Deployment

Build and run with Docker Compose:

```bash
docker-compose up --build
```

The container includes:
- Health checks every 30 seconds
- Automatic restart on failure
- Port mapping to host (8081:8081)
- Volume persistence for SQLite database

Stop with:
```bash
docker-compose down
```

## MCP Tools

The MCP server provides these tools for AI assistants:
- `list_products` - Retrieve all products
- `get_product` - Get a specific product by ID
- `create_product` - Add a new product
- `update_product` - Modify an existing product
- `delete_product` - Remove a product

## Troubleshooting

**Port already in use:**
```bash
# Change PORT in .env or export PORT=8082
export PORT=8082
python main.py
```

**Database issues:**
The SQLite database is automatically created in the app directory. To reset:
```bash
rm app/products.db
python main.py  # Database will be recreated
```

**Test failures:**
Ensure you're in the `python/` directory and dependencies are installed:
```bash
cd python
pip install -r requirements.txt
pytest -v
```
