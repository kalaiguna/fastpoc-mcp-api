# Backlog

Prioritised list of planned improvements and features. Items within each priority tier are ordered by recommended implementation sequence.

## High Priority

### Authentication Upgrade
Replace the static API key with JWT tokens — short-lived, scoped per caller, revocable. More realistic for multi-agent scenarios where different callers need different permissions. Unblocks MCP OAuth and A2A Push Notifications.

### OpenAPI → LLM Tool Schema Codegen
Auto-generate Gemini / OpenAI function declarations from the existing FastAPI OpenAPI spec. Makes the bridge between REST and AI tool use explicit and keeps tool schemas in sync with the API automatically. Small effort, high payoff — directly extends the AI integration theme.

## Medium Priority

### MCP OAuth / Authentication
Implement the MCP 2025-03-26+ auth spec so the MCP server requires a bearer token. Makes the MCP transport production-ready and demonstrates how to scope tool access per caller — relevant for multi-agent scenarios. Depends on Authentication Upgrade above.

### A2A: Push Notifications
Instead of polling, the caller provides a callback URL when submitting a task. The agent calls back when the task completes. Requires background task execution (`FastAPI BackgroundTasks`) and basic retry logic.

### gRPC Layer
Add a gRPC transport alongside REST and MCP — the same business logic exposed three ways. Define `ProductService` and `PricingService` protos; implement server-streaming RPCs that map to the existing SSE streaming. Demonstrates typed contracts, binary efficiency, and service-to-service patterns vs. REST's human-friendly JSON.

### GraphQL Layer
Add a GraphQL endpoint using `strawberry-graphql` with FastAPI integration. Expose `Query` (list, get product), `Mutation` (create, update, delete), and a `Subscription` for real-time product updates. Demonstrates flexible field selection and nested queries vs. REST's fixed response shapes — same business logic, different query model.

## Low Priority

### WebSocket Layer
Bidirectional real-time channel using `fastapi-websockets`. SSE already covers the real-time streaming use case in this POC; WebSocket becomes relevant if a future scenario requires client-to-server messages mid-stream (e.g. cancellation, refinement).

### PostgreSQL Support
Add an optional PostgreSQL backend alongside SQLite, switchable via `DB_URL` environment variable. Relevant if the project is used as a template for services that need concurrent write support.

### Full A2A Spec Compliance
Align with the Google A2A specification fully — standard task schema, capability negotiation, multi-turn interactions. Builds on Agent Card + Task Lifecycle + Streaming + Push Notifications.
