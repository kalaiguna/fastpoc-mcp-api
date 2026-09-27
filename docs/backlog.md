# Backlog

Prioritised list of planned improvements and features. Items within each priority tier are ordered by recommended implementation sequence.

## High Priority

### ~~A2A: Agent Card~~ ✅ Done (v1.5.0)
~~Serve `/.well-known/agent.json` for each agent — describes the agent's name, capabilities, endpoint URL, and auth requirements. This is the discovery layer that makes agents self-describing to any caller.~~

### A2A: Task Lifecycle
Replace synchronous request/response with an async task model. Client submits a task, receives a task ID, and polls `GET /tasks/{id}` for status (submitted → working → completed/failed). Requires a task store (SQLite is sufficient).
- Effort: 2-3 days
- Unlocks: agents can handle long-running operations; callers are decoupled from execution time

### A2A: Client Example
Add `examples/a2a_client.py` — a standalone script that reads the Agent Card, submits a task to ProductAgent, and polls for the result. Demonstrates the full A2A flow from a caller's perspective without requiring a separate repository.
- Effort: half a day (depends on Agent Card and Task Lifecycle being done first)
- Unlocks: runnable end-to-end demo

## Medium Priority

### A2A: Streaming Responses
Agents stream incremental progress updates back to the caller via SSE (Server-Sent Events). FastAPI supports this natively via `StreamingResponse`. Useful for long-running agent tasks where the caller wants live feedback.
- Effort: 1-2 days

### A2A: Push Notifications
Instead of polling, the caller provides a callback URL when submitting a task. The agent calls back when the task completes. Requires background task execution (`FastAPI BackgroundTasks`) and basic retry logic.
- Effort: 1-2 days

### Authentication Upgrade
Replace the static API key with JWT tokens — short-lived, scoped per caller, revocable. More realistic for multi-agent scenarios where different callers need different permissions.
- Effort: 1 day

## Low Priority

### PostgreSQL Support
Add an optional PostgreSQL backend alongside SQLite, switchable via `DB_URL` environment variable. Relevant if the project is used as a template for services that need concurrent write support.
- Effort: 1-2 days

### Full A2A Spec Compliance
Align with the Google A2A specification fully — standard task schema, capability negotiation, multi-turn interactions. Builds on Agent Card + Task Lifecycle + Streaming + Push Notifications.
- Effort: 1+ weeks (after all Medium items are done)
