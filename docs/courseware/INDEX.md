# Courseware Index

This folder holds the **FastPOC Multi-Transport Course**, the training material built around this repository's own code.

The AI Engineer Conversion Course has moved to its own repository and is no longer kept here. See *Related training* below.

---

## FastPOC Multi-Transport Course

**Go to [`README.md`](README.md), [`syllabus.md`](syllabus.md), and [`test-map.md`](test-map.md).**

This is an advanced, engineering-focused walk through the `fastpoc` codebase. One business core is exposed through four transports (REST, MCP, gRPC, GraphQL), with layering, validation, auth, testing, and CI.

- **Audience:** engineers leveling up their API and architecture skills. They are already comfortable with Python and a single-file FastAPI app.
- **Use it two ways:**
  1. **As a standalone advanced course** on production API design and the "transport is not business logic" idea.
  2. **As an asset library for the AI Engineer course.** Its worked examples for FastAPI layering (`app/models.py`, `app/db.py`, `app/api.py`), MCP (`app/mcp.py`), and A2A agents (`app/agents/`) are referenced by that course's later phases.

---

## Related training

The **AI Engineer Conversion Course** lives in its own repository (`ai-engineer-course`). It turns IT professionals from adjacent backgrounds into AI Engineers (Python, FastAPI, SQLite, LLMs, RAG, agents with Google ADK, MCP, A2A, guardrails, evals, observability, deployment). It references `fastpoc` as its production-patterns asset.

---

*Draft courseware. No application code is changed by any document in this folder.*
