"""
Agent-to-Agent (A2A) demo routes.

PricingAgent  — analyzes a product and returns pricing recommendations.
ProductAgent  — fetches product data, then delegates to PricingAgent via HTTP
                to get pricing, and returns a combined analysis.

The HTTP call from ProductAgent -> PricingAgent is the A2A pattern:
each agent is an independent endpoint that can be hosted on a separate service.
Change PRICING_AGENT_URL to point to a remote service and the pattern holds.
"""
import os
import httpx
from fastapi import APIRouter, HTTPException, Depends, Request
from app.agents.models import AgentRequest, PricingResult, ProductAnalysis
from app.agents.pricing import analyze_pricing
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
