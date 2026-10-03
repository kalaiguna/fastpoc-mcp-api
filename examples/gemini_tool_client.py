#!/usr/bin/env python3
"""
Gemini Tool Client — Track 3 LLM Integration
=============================================
Demonstrates programmatic LLM tool use using Google Gemini Flash (free tier).

Gemini receives a user prompt and a set of tool definitions that map to the
FastPOC REST API. When Gemini decides a tool is needed it returns a structured
function_call. This script executes that call against the live API, feeds the
result back to Gemini, and repeats until Gemini produces a final text answer.

This is the engineering wiring an AI Engineer writes to connect an LLM to
any backend service.

Prerequisites:
  pip install google-generativeai httpx

Get a free API key (no credit card) at https://aistudio.google.com/

Run:
  GEMINI_API_KEY=your-key python examples/gemini_tool_client.py

Environment variables:
  GEMINI_API_KEY    Gemini API key (required)
  AGENT_BASE_URL    FastPOC base URL      (default: http://localhost:8081)
  API_KEY           FastPOC API key       (default: dev-key-changeme)
  PROMPT            Question for Gemini   (default: see below)
"""
import os
import sys
import json
import httpx
import google.generativeai as genai

BASE_URL   = os.getenv("AGENT_BASE_URL", "http://localhost:8081").rstrip("/")
API_KEY    = os.getenv("API_KEY", "dev-key-changeme")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
PROMPT     = os.getenv("PROMPT", "List all products and tell me which ones have low stock.")

HEADERS = {"X-API-Key": API_KEY}

# ---------------------------------------------------------------------------
# Step 1 — Define the tools
# ---------------------------------------------------------------------------
# These descriptions tell Gemini what each tool does and what arguments it
# accepts. Gemini uses them to decide when and how to call a tool.
# This is the equivalent of writing an MCP tool definition, but in the
# OpenAI-compatible function calling format that Gemini understands.

TOOL_DEFINITIONS = genai.types.Tool(
    function_declarations=[
        genai.types.FunctionDeclaration(
            name="list_products",
            description="Return all products in the catalog with their ID, name, price, and stock level.",
            parameters=genai.types.Schema(
                type=genai.types.Type.OBJECT,
                properties={},
            ),
        ),
        genai.types.FunctionDeclaration(
            name="get_product",
            description="Return a single product by its numeric ID.",
            parameters=genai.types.Schema(
                type=genai.types.Type.OBJECT,
                properties={
                    "product_id": genai.types.Schema(
                        type=genai.types.Type.INTEGER,
                        description="The numeric ID of the product.",
                    )
                },
                required=["product_id"],
            ),
        ),
        genai.types.FunctionDeclaration(
            name="get_pricing_recommendation",
            description=(
                "Ask PricingAgent for a pricing recommendation for a product. "
                "Returns suggested price range, discount eligibility, and reasoning."
            ),
            parameters=genai.types.Schema(
                type=genai.types.Type.OBJECT,
                properties={
                    "product_id": genai.types.Schema(
                        type=genai.types.Type.INTEGER,
                        description="The numeric ID of the product to analyse.",
                    )
                },
                required=["product_id"],
            ),
        ),
    ]
)


# ---------------------------------------------------------------------------
# Step 2 — Implement the tools
# ---------------------------------------------------------------------------
# When Gemini decides to call a tool, this function executes the actual HTTP
# request against the FastPOC REST API and returns the result as a string.

def execute_tool(name: str, args: dict) -> str:
    """Execute a tool call and return the result as a JSON string."""
    if name == "list_products":
        r = httpx.get(f"{BASE_URL}/api/v1/products", headers=HEADERS, timeout=5.0)
        r.raise_for_status()
        return json.dumps(r.json())

    if name == "get_product":
        pid = args["product_id"]
        r = httpx.get(f"{BASE_URL}/api/v1/products/{pid}", headers=HEADERS, timeout=5.0)
        r.raise_for_status()
        return json.dumps(r.json())

    if name == "get_pricing_recommendation":
        pid = args["product_id"]
        r = httpx.post(
            f"{BASE_URL}/api/v1/agents/pricing/run",
            json={"product_id": pid},
            headers=HEADERS,
            timeout=5.0,
        )
        r.raise_for_status()
        return json.dumps(r.json())

    return json.dumps({"error": f"Unknown tool: {name}"})


# ---------------------------------------------------------------------------
# Step 3 — The agentic loop
# ---------------------------------------------------------------------------
# This is the core pattern: send prompt → check for tool calls → execute →
# feed result back → repeat until Gemini returns a plain text answer.
# This same pattern applies regardless of which LLM or which backend you use.

def run(prompt: str) -> None:
    print("=" * 60)
    print("  FastPOC Gemini Tool Client")
    print("=" * 60)
    print(f"\nPrompt: {prompt}\n")

    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=[TOOL_DEFINITIONS],
    )
    chat = model.start_chat()

    response = chat.send_message(prompt)

    iteration = 0
    while True:
        iteration += 1
        tool_calls = [p for p in response.parts if p.function_call.name]

        if not tool_calls:
            # No more tool calls — Gemini has a final answer
            for part in response.parts:
                if part.text:
                    print("\nAnswer:")
                    print(part.text)
            break

        # Execute all tool calls in this round
        tool_responses = []
        for part in tool_calls:
            fn = part.function_call
            print(f"[Tool call {iteration}] {fn.name}({dict(fn.args)})")
            result = execute_tool(fn.name, dict(fn.args))
            print(f"[Tool result]  {result[:120]}{'...' if len(result) > 120 else ''}")
            tool_responses.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=fn.name,
                        response={"result": result},
                    )
                )
            )

        # Feed all results back to Gemini in one message
        response = chat.send_message(tool_responses)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    if not GEMINI_KEY:
        print("Error: GEMINI_API_KEY is not set.", file=sys.stderr)
        print("Get a free key at https://aistudio.google.com/", file=sys.stderr)
        sys.exit(1)
    run(PROMPT)
