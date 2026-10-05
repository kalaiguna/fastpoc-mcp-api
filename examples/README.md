# Examples

Standalone scripts that demonstrate the FastPOC agent service from a caller's perspective.

See [docs/llm-integration.md](../docs/llm-integration.md) for the full guide on connecting an LLM to this service.

## openapi_tool_codegen.py

Reads the FastAPI OpenAPI spec and generates Gemini and OpenAI tool definitions automatically. Eliminates hand-maintaining tool schemas — re-run whenever the API changes.

### Prerequisites

```bash
pip install httpx
```

The server must be running:

```bash
cd python && python main.py
```

### Run

```bash
# Gemini + OpenAI JSON (default)
python examples/openapi_tool_codegen.py

# OpenAI only
python examples/openapi_tool_codegen.py --format openai

# Gemini only
python examples/openapi_tool_codegen.py --format gemini

# Python snippet — ready to paste into a client
python examples/openapi_tool_codegen.py --output python

# Custom server URL
python examples/openapi_tool_codegen.py --url http://my-host/openapi.json
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--url` | `$AGENT_BASE_URL/openapi.json` | OpenAPI spec URL |
| `--format` | `both` | `gemini`, `openai`, or `both` |
| `--output` | `json` | `json` or `python` |
| `--skip` | `/health,/ready,/openapi,/docs,/redoc,/.well-known` | Path prefixes to exclude |

### Expected output (stderr)

```
Fetching spec from http://localhost:8081/openapi.json ...
Extracted 14 tool(s): run_pricing_agent, run_product_agent, ..., list_products, create_product, get_product, update_product, delete_product
```

---

## gemini_tool_client.py

Demonstrates programmatic LLM tool use (Track 3 of the LLM integration guide). Gemini Flash receives a user prompt and a set of tool definitions that map to the FastPOC REST API. When Gemini decides a tool is needed it returns a structured `function_call`. The script executes the call, feeds the result back, and repeats until Gemini produces a final text answer — the core agentic loop pattern.

### Prerequisites

```bash
pip install google-generativeai httpx
```

Get a free Gemini API key (no credit card) at [https://aistudio.google.com/](https://aistudio.google.com/)

Start the server:

```bash
cd python && python main.py
```

### Run

```bash
GEMINI_API_KEY=your-key python examples/gemini_tool_client.py
```

### Environment variables

| Variable        | Default                                              | Description                  |
|-----------------|------------------------------------------------------|------------------------------|
| `GEMINI_API_KEY`| *(required)*                                         | Gemini API key               |
| `AGENT_BASE_URL`| `http://localhost:8081`                              | FastPOC base URL             |
| `API_KEY`       | `dev-key-changeme`                                   | FastPOC API key              |
| `PROMPT`        | `List all products and tell me which ones have low stock.` | Question for Gemini |

## a2a_client.py

Demonstrates the full Agent-to-Agent (A2A) flow in four steps:

1. **Discovery** — `GET /.well-known/agent.json` reads the service Agent Card to find available agents and their endpoint URLs. No hardcoded URLs.
2. **Submit** — `POST` to the `submitEndpoint` from the card to create an async task. The server returns a `task_id` immediately.
3. **Poll** — `GET /api/v1/agents/tasks/{task_id}` until the task reaches `completed` or `failed`.
4. **Result** — displays the combined product + pricing analysis.

### Prerequisites

```bash
pip install httpx
```

The server must be running (see `python/README.md`):

```bash
cd python && uvicorn main:app --port 8081
```

### Run

```bash
python examples/a2a_client.py
```

### Environment variables

| Variable        | Default                   | Description                  |
|-----------------|---------------------------|------------------------------|
| `AGENT_BASE_URL`| `http://localhost:8081`   | Base URL of the agent service |
| `API_KEY`       | `dev-key-changeme`        | API key for authenticated endpoints |
| `PRODUCT_ID`    | `1`                       | ID of the product to analyse |

### Expected output

```
=======================================================
  FastPOC A2A Client — full discovery-to-result flow
=======================================================
  Service : http://localhost:8081
  Product : 1

[1. DISCOVER] GET http://localhost:8081/.well-known/agent.json
    Service : FastPOC Agent Service v1.4.0
    Skills  : ['PricingAgent', 'ProductAgent']

[2. SUBMIT] POST http://localhost:8081/api/v1/agents/product/submit
    Task ID : <uuid>
    Status  : submitted

[3. POLL] GET http://localhost:8081/api/v1/agents/tasks/<uuid>
    Attempt  1: working
    Attempt  2: completed

[4. RESULT]
    Product        : Widget A (ID 1)
    Current price  : $19.99
    Stock          : 45 units
    Suggested range: $18.99 - $20.99
    Discount       : No
    Reasoning      : Stock level is within normal range. Hold current pricing.

=======================================================
```
