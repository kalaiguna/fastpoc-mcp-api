# Backlog

Prioritised list of planned improvements and features. Items within each priority tier are ordered by recommended implementation sequence.

## Medium Priority

### A2A: Push Notifications
Instead of polling, the caller provides a callback URL when submitting a task. The agent calls back when the task completes. Requires background task execution (`FastAPI BackgroundTasks`) and basic retry logic.

### GraphQL: Subscription
Add a `Subscription` for real-time product updates over WebSocket, backed by an in-process pub/sub bus that mutations publish to. Rounds out the streaming story across transports. Follow-up to the Query + Mutation GraphQL layer already shipped.

## Low Priority

### Authentication Upgrade
Replace the static API key with JWT tokens — short-lived, scoped per caller, revocable. Deprioritised: static key is sufficient for a POC and JWT adds development/testing friction without proportional learning value.

### MCP OAuth / Authentication
Implement the MCP 2025-03-26+ auth spec so the MCP server requires a bearer token. Depends on Authentication Upgrade; deprioritised alongside it.

### WebSocket Layer
Bidirectional real-time channel using `fastapi-websockets`. SSE already covers the real-time streaming use case in this POC; WebSocket becomes relevant if a future scenario requires client-to-server messages mid-stream (e.g. cancellation, refinement).

### PostgreSQL Support
Add an optional PostgreSQL backend alongside SQLite, switchable via `DB_URL` environment variable. Relevant if the project is used as a template for services that need concurrent write support.

### Full A2A Spec Compliance
Align with the Google A2A specification fully — standard task schema, capability negotiation, multi-turn interactions. Builds on Agent Card + Task Lifecycle + Streaming + Push Notifications.
