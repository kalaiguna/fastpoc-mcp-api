#!/usr/bin/env python3
"""
A2A Client Example
==================
Demonstrates the full Agent-to-Agent (A2A) flow against the FastPOC agent service.

Steps:
  1. Discovery  - read /.well-known/agent.json to find what agents exist and where to call them
  2. Submit     - POST a task to ProductAgent's async submit endpoint
  3. Poll       - GET /agents/tasks/{id} until the task reaches a terminal state
  4. Result     - display the combined product + pricing analysis

Run:
  python examples/a2a_client.py

Environment variables:
  AGENT_BASE_URL   Base URL of the agent service (default: http://localhost:8081)
  API_KEY          API key for authentication    (default: dev-key-changeme)
  PRODUCT_ID       Product ID to analyse         (default: 1)
"""
import os
import sys
import time
import httpx

BASE_URL   = os.getenv("AGENT_BASE_URL", "http://localhost:8081").rstrip("/")
API_KEY    = os.getenv("API_KEY", "dev-key-changeme")
PRODUCT_ID = int(os.getenv("PRODUCT_ID", "1"))

HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

POLL_INTERVAL  = 0.5   # seconds between polls
MAX_POLLS      = 20    # give up after this many attempts


def step(label: str, detail: str = "") -> None:
    print(f"\n[{label}]", detail)


def discover() -> dict:
    """
    Step 1 - Discovery
    Fetch the service Agent Card. This is how an external caller finds out
    what agents exist, what they can do, and where to call them.
    """
    step("1. DISCOVER", f"GET {BASE_URL}/.well-known/agent.json")
    response = httpx.get(f"{BASE_URL}/.well-known/agent.json")
    response.raise_for_status()
    card = response.json()
    print(f"    Service : {card['name']} v{card['version']}")
    print(f"    Skills  : {[s['name'] for s in card['skills']]}")
    return card


def find_submit_endpoint(card: dict, skill_id: str) -> str:
    """
    Extract the async submit endpoint for a named skill from the Agent Card.
    This is why Agent Cards matter — the client never hardcodes URLs.
    """
    for skill in card["skills"]:
        if skill["id"] == skill_id:
            endpoint = skill.get("submitEndpoint")
            if not endpoint:
                raise ValueError(f"Skill '{skill_id}' has no submitEndpoint in the Agent Card.")
            return endpoint
    raise ValueError(f"Skill '{skill_id}' not found in Agent Card.")


def submit_task(submit_path: str) -> str:
    """
    Step 2 - Submit
    POST the task to the agent. The agent returns immediately with a task ID.
    The actual work happens in the background.
    """
    url = f"{BASE_URL}{submit_path}"
    step("2. SUBMIT", f"POST {url}")
    response = httpx.post(url, json={"product_id": PRODUCT_ID}, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    task_id = data["task_id"]
    print(f"    Task ID : {task_id}")
    print(f"    Status  : {data['status']}")
    return task_id


def poll_task(task_id: str) -> dict:
    """
    Step 3 - Poll
    Poll GET /agents/tasks/{id} until the task reaches 'completed' or 'failed'.
    In production you might use push notifications instead of polling.
    """
    poll_url = f"{BASE_URL}/api/v1/agents/tasks/{task_id}"
    step("3. POLL", f"GET {poll_url}")

    for attempt in range(1, MAX_POLLS + 1):
        response = httpx.get(poll_url, headers=HEADERS)
        response.raise_for_status()
        task = response.json()
        status = task["status"]
        print(f"    Attempt {attempt:>2}: {status}")

        if status in ("completed", "failed"):
            return task

        time.sleep(POLL_INTERVAL)

    raise TimeoutError(f"Task {task_id} did not complete after {MAX_POLLS} polls.")


def display_result(task: dict) -> None:
    """Step 4 - Result"""
    step("4. RESULT")
    if task["status"] == "failed":
        print(f"    Task failed: {task['error']}")
        return

    result = task["result"]
    pricing = result["pricing"]
    print(f"    Product        : {result['name']} (ID {result['product_id']})")
    print(f"    Current price  : ${result['current_price']:.2f}")
    print(f"    Stock          : {result['stock']} units")
    print(f"    Suggested range: ${pricing['suggested_min']:.2f} - ${pricing['suggested_max']:.2f}")
    print(f"    Discount       : {'Yes' if pricing['discount_eligible'] else 'No'}")
    print(f"    Reasoning      : {pricing['reasoning']}")


def main() -> None:
    print("=" * 55)
    print("  FastPOC A2A Client — full discovery-to-result flow")
    print("=" * 55)
    print(f"  Service : {BASE_URL}")
    print(f"  Product : {PRODUCT_ID}")

    try:
        card          = discover()
        submit_path   = find_submit_endpoint(card, "product-analysis")
        task_id       = submit_task(submit_path)
        task          = poll_task(task_id)
        display_result(task)
    except httpx.HTTPStatusError as e:
        print(f"\nHTTP error: {e.response.status_code} - {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "=" * 55)


if __name__ == "__main__":
    main()
