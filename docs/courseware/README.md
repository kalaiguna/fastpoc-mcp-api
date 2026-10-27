# FastPOC Multi-Transport Course: From a One-File API to a Production Service

> This is the advanced multi-transport track (see **[`INDEX.md`](INDEX.md)**). The related **AI Engineer Conversion Course** lives in its own repository, `ai-engineer-course`, and reuses this course's code as an asset library.

This course takes you from a typical single-file FastAPI app to a production, multi-transport service. The domain is a small CRUD service, but it gains layering, validation, authentication, rate limiting, and automated tests. The headline idea is that one business core is exposed through four different transports: REST, MCP, gRPC, and GraphQL.

---

## Who this is for

Someone comfortable with Python and a basic single-file FastAPI app, who wants to learn how production API and AI-app code is actually structured.

This is not a Python-basics course. If variables, loops, and functions are new, start with a Python foundations course first.

## The bridge: from a first API to a production service

Most people's first API is one file that does everything. This course rebuilds that into production shape.

| A typical first version | What you build in this course |
|---|---|
| `main.py`, one file holding app, models, logic, and the AI call | A layered app: `models.py`, `db.py`, `business.py`, `api.py` |
| One endpoint that calls an LLM and returns its raw output | A full CRUD resource with validation and structured errors |
| `sqlite3.connect(...)` inline, passing dicts and tuples around | A data-access layer with a typed API and custom exceptions |
| "It works on my machine," tested by clicking `/docs` | 50+ automated `pytest` tests you run with one command |
| One API, called over HTTP | The same logic served over REST, MCP, gRPC, and GraphQL |
| An LLM endpoint your code calls directly | An MCP server and A2A agents that an AI assistant can call as tools |

The whole course builds toward one punchline: transport is not business logic. You write `create_product` once and surface it four ways.

## A note on project setup

Module 0 covers project structure and dependency management: why the code is split into layers, and why we use `pip install -r requirements.txt` for reproducible installs. It also explains that the AI integration here is MCP rather than a direct model call, and when each choice fits.

## How to use this courseware

Three documents make up the teaching spine for this multi-transport track:

1. **`README.md`** (this file): the why, the audience, and the bridge.
2. **`syllabus.md`**: module-by-module objectives, which files to read, which concepts to notice, and a hands-on exercise per module.
3. **`test-map.md`**: the existing test suite mapped to each module, so exercises can be run "to green" against tests that already exist.

The repository itself is the textbook. Every module points at real files and real tests, and nothing here duplicates the code.

### Suggested teaching formats

- **Guided read.** Walk the modules in order, reading the referenced files.
- **Fill-in-the-blank (recommended).** Create a `solution` branch (the current code) and a `student` branch where chosen function bodies are blanked out. Students then make the existing tests pass. See `syllabus.md` for which functions make the best blanks.
- **Extend it.** The backlog (`../backlog.md`) is a ready-made list of capstone projects, such as GraphQL subscriptions, push notifications, and PostgreSQL support.

## Course map (detail in `syllabus.md`)

| # | Module | Core idea | Primary files |
|---|--------|-----------|---------------|
| 0 | Setup, and the leap from one file | Project structure, dependency management, why layers | repo root, `python/README.md` |
| 1 | Pydantic for real | Validation, constraints, the Create/Update/Read split | `app/models.py` |
| 2 | The data layer | Isolating persistence, custom exceptions | `app/db.py` |
| 3 | The business core | Pure logic, the single source of truth | `app/business.py` |
| 4 | REST with FastAPI | Routing, dependencies, structured errors | `app/api.py` |
| 5 | Cross-cutting concerns | Auth, rate limiting, health and readiness | `app/auth.py`, `app/limiter.py` |
| 6 | Testing like a pro | Fixtures, patching the DB, `TestClient` | `test_app.py` |
| 7 | One core, many faces | The multi-transport idea | `app/mcp.py`, `grpc_server.py`, `graphql_schema.py` |
| 8 | AI integration | MCP server and A2A agents as callable tools | `app/mcp.py`, `app/agents/` |
| 9 | Ship it | Docker, config, CHANGELOG, SemVer, CI | `Dockerfile`, `CHANGELOG.md`, `.github/` |

---

*Draft teaching spine. No application code is changed by this courseware.*
