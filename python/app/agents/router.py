"""
Agent-to-Agent (A2A) demo routes.

Sync (request/response):
  PricingAgent  POST /agents/pricing/run
  ProductAgent  POST /agents/product/run  (calls PricingAgent via HTTP)

Async (task lifecycle):
  Submit        POST /agents/pricing/submit
                POST /agents/product/submit
  Poll          GET  /agents/tasks/{task_id}

Change PRICING_AGENT_URL to a remote host and the agents become independent services.
"""
import os
import uuid
import json
import httpx
from datetime import datetime, timezone
from typing import Generator
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.agents.models import (
    AgentRequest, PricingResult, ProductAnalysis, AgentCard,
    Task, TaskStatus, TaskSubmission,
)
from app.agents.pricing import analyze_pricing
from app.agents.cards import pricing_agent_card, product_agent_card
from app.agents.task_store import task_store
from app.auth import require_api_key
from app.db import db, ProductNotFoundError
from app.limiter import limiter

router = APIRouter(prefix="/agents", tags=["Agents"])

PRICING_AGENT_URL = os.getenv("PRICING_AGENT_URL", "http://localhost:8081")
API_VERSION = os.getenv("API_VERSION", "v1")


@router.post("/pricing/run", response_model=PricingResult,
             dependencies=[Depends(require_api_key)])
@limiter.limit("30/minute")
def run_pricing_agent(request: Request, body: AgentRequest):
    """PricingAgent: returns a pricing recommendation for a product."""
    try:
        product = db.get_by_id(body.product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return analyze_pricing(product.price, product.stock)


@router.post("/product/run", response_model=ProductAnalysis,
             dependencies=[Depends(require_api_key)])
@limiter.limit("30/minute")
def run_product_agent(request: Request, body: AgentRequest):
    """
    ProductAgent: fetches product details, then calls PricingAgent via HTTP (A2A),
    and returns a combined analysis.
    """
    try:
        product = db.get_by_id(body.product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # A2A call: ProductAgent delegates pricing analysis to PricingAgent
    api_key = os.getenv("API_KEY", "dev-key-changeme")
    try:
        response = httpx.post(
            f"{PRICING_AGENT_URL}/api/{API_VERSION}/agents/pricing/run",
            json={"product_id": body.product_id},
            headers={"X-API-Key": api_key},
            timeout=5.0,
        )
        response.raise_for_status()
        pricing = PricingResult(**response.json())
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"PricingAgent unavailable: {e}")

    return ProductAnalysis(
        product_id=product.id,
        name=product.name,
        current_price=product.price,
        stock=product.stock,
        pricing=pricing,
    )


@router.get("/pricing/card", response_model=AgentCard, tags=["Agent Cards"])
def get_pricing_agent_card():
    """Agent Card for PricingAgent — describes capabilities, endpoint, and auth."""
    return pricing_agent_card()


@router.get("/product/card", response_model=AgentCard, tags=["Agent Cards"])
def get_product_agent_card():
    """Agent Card for ProductAgent — describes capabilities, endpoint, and auth."""
    return product_agent_card()


# --- Async task lifecycle ---

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _run_pricing_task(task_id: str, product_id: int) -> None:
    task = task_store.get(task_id)
    task.status = TaskStatus.working
    task.updated_at = _now()
    task_store.save(task)
    try:
        product = db.get_by_id(product_id)
        result = analyze_pricing(product.price, product.stock)
        task.result = result.model_dump()
        task.status = TaskStatus.completed
    except Exception as e:
        task.error = str(e)
        task.status = TaskStatus.failed
    task.updated_at = _now()
    task_store.save(task)


def _run_product_task(task_id: str, product_id: int) -> None:
    task = task_store.get(task_id)
    task.status = TaskStatus.working
    task.updated_at = _now()
    task_store.save(task)
    try:
        product = db.get_by_id(product_id)
        api_key = os.getenv("API_KEY", "dev-key-changeme")
        response = httpx.post(
            f"{PRICING_AGENT_URL}/api/{API_VERSION}/agents/pricing/run",
            json={"product_id": product_id},
            headers={"X-API-Key": api_key},
            timeout=5.0,
        )
        response.raise_for_status()
        pricing = PricingResult(**response.json())
        analysis = ProductAnalysis(
            product_id=product.id,
            name=product.name,
            current_price=product.price,
            stock=product.stock,
            pricing=pricing,
        )
        task.result = analysis.model_dump()
        task.status = TaskStatus.completed
    except Exception as e:
        task.error = str(e)
        task.status = TaskStatus.failed
    task.updated_at = _now()
    task_store.save(task)


@router.post("/pricing/submit", response_model=TaskSubmission, tags=["Agents"],
             dependencies=[Depends(require_api_key)])
@limiter.limit("30/minute")
def submit_pricing_task(request: Request, body: AgentRequest, background_tasks: BackgroundTasks):
    """Submit a pricing analysis task. Returns a task ID to poll for the result."""
    now = _now()
    task = Task(
        id=str(uuid.uuid4()),
        agent="pricing",
        status=TaskStatus.submitted,
        input=body.model_dump(),
        created_at=now,
        updated_at=now,
    )
    task_store.save(task)
    background_tasks.add_task(_run_pricing_task, task.id, body.product_id)
    return TaskSubmission(task_id=task.id, status=task.status, message="Task submitted.")


@router.post("/product/submit", response_model=TaskSubmission, tags=["Agents"],
             dependencies=[Depends(require_api_key)])
@limiter.limit("30/minute")
def submit_product_task(request: Request, body: AgentRequest, background_tasks: BackgroundTasks):
    """Submit a product analysis task. Returns a task ID to poll for the result."""
    now = _now()
    task = Task(
        id=str(uuid.uuid4()),
        agent="product",
        status=TaskStatus.submitted,
        input=body.model_dump(),
        created_at=now,
        updated_at=now,
    )
    task_store.save(task)
    background_tasks.add_task(_run_product_task, task.id, body.product_id)
    return TaskSubmission(task_id=task.id, status=task.status, message="Task submitted.")


@router.get("/tasks/{task_id}", response_model=Task, tags=["Agents"],
            dependencies=[Depends(require_api_key)])
def get_task(task_id: str):
    """Poll task status. Result is populated when status is 'completed'."""
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


# --- SSE streaming ---

def _sse(data: dict) -> str:
    """Format a dict as a single SSE data line."""
    return f"data: {json.dumps(data)}\n\n"


def _stream_pricing(product_id: int) -> Generator[str, None, None]:
    yield _sse({"status": "working", "step": "Fetching product data..."})
    try:
        product = db.get_by_id(product_id)
    except ProductNotFoundError:
        yield _sse({"status": "failed", "error": f"Product {product_id} not found"})
        return
    yield _sse({"status": "working", "step": "Analysing price and stock level..."})
    result = analyze_pricing(product.price, product.stock)
    yield _sse({"status": "completed", "result": result.model_dump()})


def _stream_product(product_id: int) -> Generator[str, None, None]:
    yield _sse({"status": "working", "step": "Fetching product data..."})
    try:
        product = db.get_by_id(product_id)
    except ProductNotFoundError:
        yield _sse({"status": "failed", "error": f"Product {product_id} not found"})
        return
    yield _sse({"status": "working", "step": "Calling PricingAgent..."})
    api_key = os.getenv("API_KEY", "dev-key-changeme")
    try:
        response = httpx.post(
            f"{PRICING_AGENT_URL}/api/{API_VERSION}/agents/pricing/run",
            json={"product_id": product_id},
            headers={"X-API-Key": api_key},
            timeout=5.0,
        )
        response.raise_for_status()
        pricing = PricingResult(**response.json())
    except httpx.HTTPError as e:
        yield _sse({"status": "failed", "error": f"PricingAgent unavailable: {e}"})
        return
    yield _sse({"status": "working", "step": "Combining analysis..."})
    analysis = ProductAnalysis(
        product_id=product.id,
        name=product.name,
        current_price=product.price,
        stock=product.stock,
        pricing=pricing,
    )
    yield _sse({"status": "completed", "result": analysis.model_dump()})


@router.post("/pricing/stream", dependencies=[Depends(require_api_key)])
@limiter.limit("30/minute")
def stream_pricing_agent(request: Request, body: AgentRequest):
    """
    PricingAgent (SSE): streams progress events then the final result.
    Each event is a JSON object: {"status": "working"|"completed"|"failed", ...}
    """
    return StreamingResponse(
        _stream_pricing(body.product_id),
        media_type="text/event-stream",
    )


@router.post("/product/stream", dependencies=[Depends(require_api_key)])
@limiter.limit("30/minute")
def stream_product_agent(request: Request, body: AgentRequest):
    """
    ProductAgent (SSE): streams progress events then the final result.
    Each event is a JSON object: {"status": "working"|"completed"|"failed", ...}
    """
    return StreamingResponse(
        _stream_product(body.product_id),
        media_type="text/event-stream",
    )
