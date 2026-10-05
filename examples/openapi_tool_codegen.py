#!/usr/bin/env python3
"""
OpenAPI → LLM Tool Schema Codegen
==================================
Reads a FastAPI OpenAPI spec and generates tool definitions for Gemini and OpenAI.

Eliminates hand-maintaining tool schemas when the API changes — re-run whenever
the API changes and paste the output into your LLM client.

Usage:
  python examples/openapi_tool_codegen.py                    # Gemini + OpenAI JSON
  python examples/openapi_tool_codegen.py --format openai    # OpenAI only
  python examples/openapi_tool_codegen.py --format gemini    # Gemini only
  python examples/openapi_tool_codegen.py --output python    # Python snippet
  python examples/openapi_tool_codegen.py --url http://host/openapi.json

Environment variables:
  AGENT_BASE_URL    FastPOC base URL (default: http://localhost:8081)
"""
import argparse
import json
import os
import sys

import httpx

BASE_URL = os.getenv("AGENT_BASE_URL", "http://localhost:8081").rstrip("/")

# Paths that are infrastructure/meta — not useful as LLM tools
_SKIP_PREFIXES = ("/health", "/ready", "/openapi", "/docs", "/redoc", "/.well-known")

_OPENAPI_TYPES = {"string", "integer", "number", "boolean", "array", "object"}


# ---------------------------------------------------------------------------
# Spec fetching and $ref resolution
# ---------------------------------------------------------------------------

def _fetch_spec(url: str) -> dict:
    r = httpx.get(url, timeout=5.0)
    r.raise_for_status()
    return r.json()


def _resolve(schema: dict, spec: dict) -> dict:
    if "$ref" in schema:
        parts = schema["$ref"].lstrip("#/").split("/")
        node = spec
        for p in parts:
            node = node[p]
        return _resolve(node, spec)
    return schema


# ---------------------------------------------------------------------------
# Schema conversion: OpenAPI → JSON Schema (compatible with both Gemini + OpenAI)
# ---------------------------------------------------------------------------

def _convert_schema(schema: dict, spec: dict) -> dict:
    schema = _resolve(schema, spec)
    typ = schema.get("type", "object")
    result: dict = {"type": typ if typ in _OPENAPI_TYPES else "string"}

    if schema.get("description"):
        result["description"] = schema["description"]
    if schema.get("enum"):
        result["enum"] = schema["enum"]

    if typ == "object":
        props = schema.get("properties", {})
        if props:
            result["properties"] = {k: _convert_schema(v, spec) for k, v in props.items()}
        if schema.get("required"):
            result["required"] = schema["required"]

    if typ == "array" and "items" in schema:
        result["items"] = _convert_schema(schema["items"], spec)

    return result


# ---------------------------------------------------------------------------
# Tool name: strip FastAPI's auto-generated path suffix from operationId
# e.g. "list_products_api_v1_products_get" → "list_products"
# ---------------------------------------------------------------------------

def _tool_name(operation_id: str, method: str, path: str) -> str:
    for marker in ("_api_v1_", "_api_"):
        idx = operation_id.find(marker)
        if idx != -1:
            return operation_id[:idx]
    if operation_id:
        return operation_id
    slug = path.replace("/", "_").replace("{", "").replace("}", "").strip("_")
    return f"{method}_{slug}"


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------

def extract_tools(spec: dict, skip_prefixes: tuple = _SKIP_PREFIXES) -> list[dict]:
    """Return a list of tool dicts (name, description, parameters JSON Schema)."""
    tools = []
    for path, methods in spec.get("paths", {}).items():
        if any(path.startswith(p) for p in skip_prefixes):
            continue
        for method, op in methods.items():
            if method not in ("get", "post", "put", "delete", "patch"):
                continue
            if op.get("deprecated"):
                continue

            name = _tool_name(op.get("operationId", ""), method, path)
            description = op.get("summary") or op.get("description") or f"{method.upper()} {path}"

            properties: dict = {}
            required: list = []

            for param in op.get("parameters", []):
                param = _resolve(param, spec)
                pname = param["name"]
                pschema = _convert_schema(param.get("schema", {"type": "string"}), spec)
                if param.get("description"):
                    pschema["description"] = param["description"]
                properties[pname] = pschema
                if param.get("required"):
                    required.append(pname)

            body = op.get("requestBody", {})
            if body:
                body_schema = (
                    body.get("content", {})
                    .get("application/json", {})
                    .get("schema", {})
                )
                if body_schema:
                    resolved = _convert_schema(body_schema, spec)
                    properties.update(resolved.get("properties", {}))
                    required.extend(r for r in resolved.get("required", []) if r not in required)

            parameters: dict = {"type": "object", "properties": properties}
            if required:
                parameters["required"] = required

            tools.append({"name": name, "description": description, "parameters": parameters})

    return tools


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def to_openai(tools: list[dict]) -> list[dict]:
    return [{"type": "function", "function": t} for t in tools]


def to_gemini(tools: list[dict]) -> list[dict]:
    return [{"function_declarations": [{"name": t["name"], "description": t["description"], "parameters": t["parameters"]} for t in tools]}]


def to_python(tools: list[dict]) -> str:
    lines = [
        "# Auto-generated by examples/openapi_tool_codegen.py — do not edit by hand.",
        "# Re-run whenever the FastPOC API changes.",
        "",
        "import google.generativeai as genai",
        "",
        "# --- Gemini ---",
        "GEMINI_TOOLS = genai.types.Tool(",
        "    function_declarations=[",
    ]
    for t in tools:
        props = t["parameters"].get("properties", {})
        req = t["parameters"].get("required", [])
        lines += [
            f"        genai.types.FunctionDeclaration(",
            f'            name="{t["name"]}",',
            f'            description="{t["description"]}",',
            f"            parameters=genai.types.Schema(",
            f"                type=genai.types.Type.OBJECT,",
        ]
        if props:
            lines.append("                properties={")
            for pname, pschema in props.items():
                ptype = pschema.get("type", "string").upper()
                pdesc = pschema.get("description", "")
                lines.append(f'                    "{pname}": genai.types.Schema(')
                lines.append(f"                        type=genai.types.Type.{ptype},")
                if pdesc:
                    lines.append(f'                        description="{pdesc}",')
                lines.append("                    ),")
            lines.append("                },")
        if req:
            lines.append(f"                required={req!r},")
        lines += ["            ),", "        ),"]
    lines += ["    ]", ")", ""]

    lines += ["", "# --- OpenAI ---", "OPENAI_TOOLS = ["]
    for t in tools:
        lines.append(f"    {{")
        lines.append(f'        "type": "function",')
        lines.append(f'        "function": {{')
        lines.append(f'            "name": "{t["name"]}",')
        lines.append(f'            "description": "{t["description"]}",')
        params_json = json.dumps(t["parameters"], indent=12)
        lines.append(f'            "parameters": {params_json},')
        lines.append(f"        }},")
        lines.append(f"    }},")
    lines.append("]")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LLM tool schemas from a FastAPI OpenAPI spec.")
    parser.add_argument("--url", default=f"{BASE_URL}/openapi.json", help="OpenAPI spec URL (default: $AGENT_BASE_URL/openapi.json)")
    parser.add_argument("--format", choices=["gemini", "openai", "both"], default="both", help="Output format (default: both)")
    parser.add_argument("--output", choices=["json", "python"], default="json", help="Output style: JSON or Python snippet (default: json)")
    parser.add_argument("--skip", default=",".join(_SKIP_PREFIXES), help="Comma-separated path prefixes to exclude")
    args = parser.parse_args()

    skip = tuple(s.strip() for s in args.skip.split(",") if s.strip())

    print(f"Fetching spec from {args.url} ...", file=sys.stderr)
    try:
        spec = _fetch_spec(args.url)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    tools = extract_tools(spec, skip_prefixes=skip)
    print(f"Extracted {len(tools)} tool(s): {', '.join(t['name'] for t in tools)}", file=sys.stderr)

    if args.output == "python":
        print(to_python(tools))
        return

    if args.format == "gemini":
        print(json.dumps(to_gemini(tools), indent=2))
    elif args.format == "openai":
        print(json.dumps(to_openai(tools), indent=2))
    else:
        print(json.dumps({"gemini": to_gemini(tools), "openai": to_openai(tools)}, indent=2))


if __name__ == "__main__":
    main()
