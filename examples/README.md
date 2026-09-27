# Examples

Standalone scripts that demonstrate the FastPOC agent service from a caller's perspective.

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
