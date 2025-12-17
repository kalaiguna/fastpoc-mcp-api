# FastAPI + MCP Product CRUD Prototype

This project implements a simple Product CRUD application that exposes both a REST API (via FastAPI) and an MCP Server (via Model Context Protocol), sharing the same in-memory database.

## Prerequisites

- Python 3.10+

## Installation

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

## Running the API

To start the FastAPI server:

```bash
python main.py
```

The API will be available at `http://localhost:8081`.
You can access the interactive Swagger UI at `http://localhost:8081/docs`.

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
      "args": ["/absolute/path/to/fastpoc/mcp_entry.py"]
    }
  }
}
```

## Testing

### API Testing
You can use `curl` or the Swagger UI to test endpoints.

Example: Create a product
```bash
curl -X POST "http://localhost:8081/products" -H "Content-Type: application/json" -d '{"name": "Test Product", "price": 10.5, "stock": 100}'
```

### MCP Testing
You can verify the MCP server is running by inspecting it with an MCP inspector or connecting it to a client.

## Project Structure

- `app/`: Contains the application logic.
  - `models.py`: Pydantic models.
  - `db.py`: In-memory database and CRUD logic.
  - `api.py`: FastAPI application routes.
  - `mcp_server.py`: MCP server tools.
- `main.py`: Entry point for FastAPI.
- `mcp_entry.py`: Entry point for MCP server.
