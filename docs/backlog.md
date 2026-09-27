# Backlog

Prioritised list of planned improvements and features. Items within each priority tier are ordered by recommended implementation sequence.

## Medium Priority

### A2A: Streaming Responses
Agents stream incremental progress updates back to the caller via SSE (Server-Sent Events). FastAPI supports this natively via `StreamingResponse`. Useful for long-running agent tasks where the caller wants live feedback.

### A2A: Push Notifications
Instead of polling, the caller provides a callback URL when submitting a task. The agent calls back when the task completes. Requires background task execution (`FastAPI BackgroundTasks`) and basic retry logic.

### Authentication Upgrade
Replace the static API key with JWT tokens — short-lived, scoped per caller, revocable. More realistic for multi-agent scenarios where different callers need different permissions.

## Low Priority

### PostgreSQL Support
Add an optional PostgreSQL backend alongside SQLite, switchable via `DB_URL` environment variable. Relevant if the project is used as a template for services that need concurrent write support.

### Full A2A Spec Compliance
Align with the Google A2A specification fully — standard task schema, capability negotiation, multi-turn interactions. Builds on Agent Card + Task Lifecycle + Streaming + Push Notifications.
