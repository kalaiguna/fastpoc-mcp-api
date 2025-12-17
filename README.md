# FastPOC - Multi-Language CRUD Prototype

This repository contains CRUD (Create, Read, Update, Delete) implementations for managing Products, organized by programming language.

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

## Available Implementations

### Python (FastAPI + MCP)
- **Location**: `python/`
- **Technologies**: FastAPI, MCP (Model Context Protocol), Pydantic
- **Features**: 
  - REST API with Swagger UI
  - MCP Server for AI tool integration
  - Shared codebase between API and MCP
  - In-memory database with 30 pre-populated records
  - Full CRUD operations

See `python/README.md` for detailed instructions.

## Future Implementations

This structure is designed to accommodate implementations in other languages:
- C# (planned)
- Java (planned)
- Node.js (planned)

Each implementation will have its own subdirectory with language-specific documentation.
