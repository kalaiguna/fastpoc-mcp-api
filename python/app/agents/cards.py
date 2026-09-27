import os
from app.agents.models import AgentCard, AgentSkill, AgentAuthentication, AgentCapabilities

_VERSION = "1.4.0"
_AUTH = AgentAuthentication(
    schemes=["apiKey"],
    credentials="X-API-Key request header. Set API_KEY env var on the server.",
)
_CAPABILITIES = AgentCapabilities(
    streaming=False,
    pushNotifications=False,
    stateTransitionHistory=False,
)


def _base_url() -> str:
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", "8081")
    # Normalize localhost variants
    if host in ("0.0.0.0", "127.0.0.1"):
        host = "localhost"
    return f"http://{host}:{port}"


def _api_prefix() -> str:
    version = os.getenv("API_VERSION", "v1")
    return f"/api/{version}"


def pricing_agent_card() -> AgentCard:
    base = _base_url()
    prefix = _api_prefix()
    return AgentCard(
        name="PricingAgent",
        description=(
            "Analyzes a product's current price and stock level and returns "
            "a pricing recommendation — suggested range, discount eligibility, and reasoning."
        ),
        url=f"{base}{prefix}/agents/pricing/run",
        version=_VERSION,
        authentication=_AUTH,
        capabilities=_CAPABILITIES,
        skills=[
            AgentSkill(
                id="pricing-analysis",
                name="Pricing Analysis",
                description="Returns suggested_min, suggested_max, discount_eligible, and reasoning for a product.",
                endpoint=f"{prefix}/agents/pricing/run",
                submitEndpoint=f"{prefix}/agents/pricing/submit",
                examples=[{"product_id": 1}],
            )
        ],
    )


def product_agent_card() -> AgentCard:
    base = _base_url()
    prefix = _api_prefix()
    return AgentCard(
        name="ProductAgent",
        description=(
            "Fetches full product details and delegates pricing analysis to PricingAgent via HTTP (A2A). "
            "Returns a combined product and pricing analysis."
        ),
        url=f"{base}{prefix}/agents/product/run",
        version=_VERSION,
        authentication=_AUTH,
        capabilities=_CAPABILITIES,
        skills=[
            AgentSkill(
                id="product-analysis",
                name="Product Analysis",
                description="Returns product details combined with a pricing recommendation sourced from PricingAgent.",
                endpoint=f"{prefix}/agents/product/run",
                submitEndpoint=f"{prefix}/agents/product/submit",
                examples=[{"product_id": 1}],
            )
        ],
    )


def service_card() -> AgentCard:
    """Combined card for the whole service — served at /.well-known/agent.json."""
    base = _base_url()
    prefix = _api_prefix()
    return AgentCard(
        name="FastPOC Agent Service",
        description=(
            "A demo FastAPI + MCP service exposing product CRUD and two A2A agents: "
            "PricingAgent and ProductAgent."
        ),
        url=base,
        version=_VERSION,
        authentication=_AUTH,
        capabilities=_CAPABILITIES,
        skills=[
            AgentSkill(
                id="pricing-analysis",
                name="PricingAgent",
                description="Rule-based pricing recommendations based on price and stock level.",
                endpoint=f"{prefix}/agents/pricing/run",
                examples=[{"product_id": 1}],
            ),
            AgentSkill(
                id="product-analysis",
                name="ProductAgent",
                description="Combined product + pricing analysis. Delegates pricing to PricingAgent via HTTP.",
                endpoint=f"{prefix}/agents/product/run",
                submitEndpoint=f"{prefix}/agents/product/submit",
                examples=[{"product_id": 1}],
            ),
        ],
    )
