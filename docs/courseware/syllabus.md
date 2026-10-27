# Syllabus, module by module

Each module lists its **Objective**, what to **Read** (files in the repo), what to **Notice** (the teaching points), an **Exercise** (hands-on), and a **Make it your own** stretch (optional). File paths are relative to `python/` unless noted.

Prerequisite for the whole course: you are comfortable with Python and a basic single-file FastAPI app.

---

## Module 0: Setup, and the leap from one file

**Objective:** Run the service, and understand why it is many files instead of one.

**Read:** `../README.md` (repo root), `python/README.md`, `requirements.txt`, `docs/architecture.md`.

**Notice:**
- In a typical first version, `main.py` holds the app, the models, the logic, and the AI call. Here those live in four files. Ask what you gained and what you paid.
- Dependency management: we use `pip install -r requirements.txt` for reproducible installs. Discuss how this compares with ad-hoc `pip install` and with tools like `uv`.
- The pinned version ranges in `requirements.txt`, and why a POC still pins them.

**Exercise:** Get the REST API running (`python main.py`), open `/api/v1/docs`, and create a product from the Swagger UI. It is the familiar click-to-test skill, now on a bigger app.

**Make it your own:** Draw the request flow for `POST /products` on paper: HTTP, auth, route, business, db, and back. You will fill in each box as the course goes on.

---

## Module 1: Pydantic for real

**Objective:** Move from "a model is a shape" to "a model is your validation layer."

**Read:** `app/models.py`.

**Notice:**
- Three models for one concept: `ProductCreate`, `ProductUpdate`, `Product`. Why not one? Create requires fields, Update makes them all optional, and Read adds `id`.
- `Field(..., gt=0, le=1000000)` writes constraints as declarations, not `if` statements.
- The custom `@field_validator` on `name` rejects whitespace-only input. This is when a constraint needs real code.
- `model_config = ConfigDict(from_attributes=True)` on `Product` lets it read from DB rows.

**Exercise:** Add a `sku` field (a string of exactly 8 alphanumeric characters) to the product. Decide which of the three models it belongs in, and add a validator. Don't wire it to the DB yet; just make the model enforce it.

**Make it your own:** Compare `ProductUpdate` here with a naive single model that tries to serve create, update, and read at once. Explain why update endpoints need all fields optional.

**Good fill-in-the-blank target:** the body of `validate_name`.

---

## Module 2: The data layer

**Objective:** Isolate persistence so the rest of the app never writes SQL.

**Read:** `app/db.py`.

**Notice:**
- The data layer returns and accepts Pydantic models, not raw tuples. Contrast that with a beginner `database.py` that passes dicts and tuples around.
- `ProductNotFoundError` is a domain exception, defined here, that upper layers catch and translate. The DB layer knows nothing about HTTP 404.
- Parameterized queries (the `?` placeholders) prevent SQL injection, stated here as a rule.

**Exercise:** Add a `get_by_name(name)` method that raises `ProductNotFoundError` when nothing matches. Keep the SQL in this file only.

**Make it your own:** The backlog has a "PostgreSQL support" item. Sketch which methods would change and which would not. That is proof the isolation pays off.

---

## Module 3: The business core (the heart of the course)

**Objective:** Understand why logic lives apart from every transport.

**Read:** `app/business.py`.

**Notice:**
- These functions take plain arguments and return models. No `Request`, no HTTP, no gRPC context. This is the single source of truth that every transport calls.
- `update_product_logic` builds `fields` from only the non-`None` arguments, then constructs `ProductUpdate(**fields)`. This is the partial-update pattern. Skipping a field must mean "leave it alone," not "set it to null."

**Exercise:** Add `adjust_stock(product_id, delta)` that loads a product, applies the delta, and rejects a result below zero (raise `ValueError`). Notice you write it once, and all four transports can call it.

**Make it your own:** Trace one business function outward into all four transport files (Module 7). Confirm that none of them re-implement the logic.

**Good fill-in-the-blank target:** the `fields = {...}` dict comprehension in `update_product_logic`. It is a classic "why is my update nulling other columns?" bug for students to discover.

---

## Module 4: REST with FastAPI

**Objective:** Build a full resource, not just one endpoint.

**Read:** `app/api.py`.

**Notice:**
- The five CRUD routes, compared with a single-endpoint app.
- `dependencies=[Depends(require_api_key)]` is dependency injection, a concept a single-file beginner app never needed.
- The `@app.exception_handler(HTTPException)` plus the `_STATUS_TO_CODE` map give every error one structured shape: `{"error": {"code", "message"}}`. Contrast that with returning raw exceptions.
- Path, query, and body parameters across the five routes.

**Exercise:** Add `GET /api/v1/products/search?name=...`, wired to the `get_by_name` you wrote in Module 2, returning a proper 404 through the structured error path.

**Make it your own:** Add OpenAPI `responses=` documentation to your new route so it shows up correctly in `/docs`.

---

## Module 5: Cross-cutting concerns

**Objective:** The things every real service needs but tutorials skip.

**Read:** `app/auth.py`, `app/limiter.py`, and the `/health` and `/ready` routes in `app/api.py`.

**Notice:**
- API-key auth as a reusable dependency. One line, `Depends(require_api_key)`, protects a route. In a typical beginner app, anyone who found the URL could call the LLM on your dime.
- Rate limiting with `@limiter.limit("60/minute")`, and why an AI-backed endpoint especially needs it.
- `/health` asks "is the process up?" while `/ready` asks "can it serve, for example is the DB reachable?" Explain why orchestrators need both.

**Exercise:** Add a stricter rate limit to your search endpoint, and verify the `429` structured error fires.

**Make it your own:** Read the backlog's "Authentication Upgrade (JWT)" entry and the note on why it is deprioritized. Argue for or against it for a real product.

---

## Module 6: Testing like a pro

**Objective:** Trust your code without clicking `/docs`.

**Read:** `test_app.py`. See `test-map.md` for the full test inventory.

**Notice:**
- Fixtures point the app at a temporary SQLite DB, so tests never touch real data.
- Patching `app.business.db` tests a layer in isolation.
- `TestClient` runs full HTTP round-trips, including auth-rejected (`401`) and validation (`422`) cases.
- Tests cover the unhappy paths (not found, bad input), not just the happy one.

**Exercise:** Write tests for your Module 3 `adjust_stock` (success, below-zero rejection, product-not-found), and run them to green.

**Make it your own:** Run `pytest --collect-only` to see the real count, then add one test that was missing for an existing endpoint.

---

## Module 7: One core, many faces (the main idea)

**Objective:** See the same business logic surfaced four ways.

**Read:** `app/mcp.py`, `grpc_server.py` with `protos/product.proto`, and `app/graphql_schema.py`, alongside `app/api.py` from Module 4. Also read `docs/architecture.md`.

**Notice:**
- Every transport is a thin adapter. It parses input, calls a `business.py` function, then translates the result or error into that transport's format.
- Error mapping per transport: HTTP `404`, gRPC `NOT_FOUND`, a GraphQL error, and an MCP error. One domain exception, four translations.
- What differs: REST and GraphQL are mounted in the FastAPI app, gRPC is a standalone server (`grpc_entry.py`, port 50051), and MCP runs over stdio (`mcp_entry.py`).
- The git history literally shows how a transport gets added, through the codegen, gRPC, then GraphQL commits. Read it as a walkthrough.

**Exercise:** Expose your `adjust_stock` logic through two transports, for example a REST route and a GraphQL mutation. You should add zero business logic, only adapters.

**Make it your own:** Pick the backlog's "GraphQL Subscription" and sketch the adapter for a transport that streams.

---

## Module 8: AI integration (the MCP way)

**Objective:** Make the service callable by an AI assistant, and meet agents.

**Read:** `app/mcp.py`, `app/service.py`, `app/agents/` (`router.py`, `pricing.py`, `cards.py`, `task_store.py`, `models.py`), and `examples/` for client demos.

**Notice:**
- In a typical AI app, your code calls the LLM. Here it is inverted: the LLM calls your code as tools, through MCP. This is the big conceptual flip, so spend time on it.
- The MCP tools (`list_products`, `create_product`, and so on) are just the business functions again, described so a model can invoke them.
- A2A agents offer a sync run, an async submit-and-poll task lifecycle, SSE streaming, and Agent Cards that advertise capabilities at `/.well-known/agent.json`.

**Exercise:** Add an MCP tool that wraps your `adjust_stock`. Confirm it shows up for an MCP client (or in the tests).

**Make it your own:** Compare the A2A submit-and-poll task lifecycle with a simple synchronous request and response. When is async worth the extra complexity?

---

## Module 9: Ship it

**Objective:** Everything between "works on my laptop" and "a team runs it."

**Read:** `Dockerfile`, `docker-compose.yml`, `.env.example`, `CHANGELOG.md`, and `.github/` (the CI workflow).

**Notice:**
- Config comes from environment variables (`.env.example`). Never hard-code the API key; keep secrets in `.env`.
- `CHANGELOG.md` follows Keep a Changelog, with SemVer tags. Explain why `v1.11.0` means what it means.
- CI runs the test suite on every push. That is the safety net that makes the multi-transport refactors in Module 7 safe.

**Exercise:** Add a CHANGELOG entry for the `sku`, `adjust_stock`, and search features you built through the course, and decide the correct SemVer bump.

**Make it your own:** Containerize and run the whole thing with `docker-compose up`, then hit `/health` from the host.

---

## Capstone options

Pull any item from `../backlog.md`. The best teaching capstones, in order:

1. **GraphQL Subscription.** It forces the streaming and transport lesson to stick.
2. **A2A Push Notifications.** Real async work and callback design.
3. **PostgreSQL support.** It proves the Module 2 data-layer isolation was worth it.
