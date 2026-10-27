# Test map: tests as the safety net for each module

The repository already ships a test suite. In a fill-in-the-blank course you don't write most of these. Instead, you blank out a function body and make the existing tests pass again. This file maps every test to the module it reinforces.

Run the authoritative count and list any time:

```bash
cd python
pytest --collect-only -q    # see every test id
pytest -v                   # run them all
pytest test_grpc.py -v      # run one transport's tests
```

Files: `test_app.py` (REST, MCP, A2A agents), `test_grpc.py` (gRPC transport), `test_graphql.py` (GraphQL transport).

---

## Module 1: Pydantic

| Test | File | Reinforces |
|------|------|-----------|
| `test_create_product_validation` | test_app.py | `Field` constraints and `validate_name` reject bad input (422) |
| `test_create_product_validation_error` | test_graphql.py | the same validation surfaced as a GraphQL error |
| `test_create_product_invalid` | test_grpc.py | the same validation surfaced as gRPC `INVALID_ARGUMENT` |

> One validation rule, verified through three transports. That is the main idea in test form.

## Module 2: Data layer

| Test | File | Reinforces |
|------|------|-----------|
| `test_get_product_not_found` | test_app.py | `ProductNotFoundError` raised by the db layer |
| `test_get_product_by_id` | test_app.py | round-tripping a model through the db |

## Module 3: Business core

| Test | File | Reinforces |
|------|------|-----------|
| `test_mcp_logic` | test_app.py | business functions called directly, with no transport |
| `test_update_product_partial` | test_grpc.py | the partial-update pattern (non-`None` fields only) |
| `test_update_product_partial` | test_graphql.py | the same partial-update rule via GraphQL |

> If a student breaks the `fields = {...}` comprehension in `business.py`, the two `test_update_product_partial` tests are what catch it.

## Module 4: REST

| Test | File | Reinforces |
|------|------|-----------|
| `test_read_main`, `test_client` | test_app.py | app boots, root responds |
| `test_create_product` | test_app.py | POST happy path (201) |
| `test_get_product_by_id` | test_app.py | GET by id |
| `test_update_product` / `test_update_product_not_found` | test_app.py | PUT success, plus 404 |
| `test_delete_product` / `test_delete_product_not_found` | test_app.py | DELETE success, plus 404 |

## Module 5: Cross-cutting concerns

| Test | File | Reinforces |
|------|------|-----------|
| `test_auth_rejected_without_key` | test_app.py | the auth dependency blocks unkeyed calls (401) |
| `test_graphql_requires_api_key` | test_graphql.py | the same dependency guards a mounted router |
| `test_graphql_with_api_key` | test_graphql.py | a valid key passes through |
| `test_health_endpoint`, `test_readiness_endpoint` | test_app.py | liveness vs. readiness |

## Module 6: Testing

All of the above are the material. Read how they:
- build a temp-DB fixture and patch `app.business.db`,
- use `TestClient` for real HTTP,
- assert on unhappy paths (`_not_found`, `_validation`, auth-rejected).

## Module 7: One core, many faces

Read the three files side by side. The same operations appear in each, with transport-specific error translation:

| Operation | REST (test_app) | gRPC (test_grpc) | GraphQL (test_graphql) |
|-----------|-----------------|------------------|------------------------|
| list | *(via agents/CRUD)* | `test_list_products` | `test_query_products` |
| get | `test_get_product_by_id` | `test_get_product` | `test_query_product` |
| get missing | `test_get_product_not_found` | `test_get_product_not_found` | `test_query_product_not_found` |
| create | `test_create_product` | `test_create_product` | `test_create_product` |
| create invalid | `test_create_product_validation` | `test_create_product_invalid` | `test_create_product_validation_error` |
| update partial | `test_update_product` | `test_update_product_partial` | `test_update_product_partial` |
| update missing | `test_update_product_not_found` | `test_update_product_not_found` | `test_update_product_not_found` |
| delete | `test_delete_product` | `test_delete_product` | `test_delete_product` |
| delete missing | `test_delete_product_not_found` | `test_delete_product_not_found` | `test_delete_product_not_found` |

> Reading a single row across all three columns is the clearest possible demonstration of "transport is not business logic."

## Module 8: AI integration (MCP and A2A agents)

| Test | File | Reinforces |
|------|------|-----------|
| `test_mcp_logic` | test_app.py | MCP tools wrap the business layer |
| `test_pricing_agent` / `test_pricing_agent_not_found` | test_app.py | sync agent run, plus error |
| `test_product_agent` | test_app.py | a second agent over the same domain |
| `test_pricing_logic_low_stock` / `_high_stock` | test_app.py | agent logic as pure functions |
| `test_service_agent_card`, `test_pricing_agent_card`, `test_product_agent_card` | test_app.py | Agent Cards and capability discovery |
| `test_submit_pricing_task`, `test_poll_pricing_task_completes`, `test_poll_task_not_found`, `test_submit_pricing_task_invalid_product` | test_app.py | async task lifecycle (submit, then poll) |
| `test_stream_pricing_agent`, `test_stream_pricing_agent_not_found`, `test_stream_product_agent`, `test_stream_agent_card_includes_stream_endpoint` | test_app.py | SSE streaming and its advertisement |
| `test_get_pricing`, `test_get_pricing_not_found` | test_grpc.py | pricing exposed over gRPC |
| `test_stream_pricing_analysis`, `test_stream_pricing_not_found` | test_grpc.py | **server-streaming** RPC |

## Module 9: Ship it

No unit tests here, by design. The lesson is the process. CI runs the whole suite above on every push (`.github/`), and that green run is what the CHANGELOG and SemVer release depend on. Exercise: watch CI run your branch, read the workflow file, and trace a failed test back to a blocked release.

---

## Fill-in-the-blank quick picks

The best function bodies to blank out, ranked by payoff against frustration:

| Blank this | File | Caught by |
|------------|------|-----------|
| `validate_name` | `app/models.py` | `test_create_product_validation` (plus the gRPC and GraphQL variants) |
| `update_product_logic` `fields` comprehension | `app/business.py` | both `test_update_product_partial` tests |
| `get_by_id`, plus the not-found raise | `app/db.py` | `test_get_product_not_found` across all three files |
| a transport's error mapping (for example `NOT_FOUND`) | `grpc_server.py` | `test_*_not_found` in test_grpc.py |
