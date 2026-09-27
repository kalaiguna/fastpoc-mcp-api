from pydantic import BaseModel


class AgentRequest(BaseModel):
    product_id: int


class PricingResult(BaseModel):
    suggested_min: float
    suggested_max: float
    discount_eligible: bool
    reasoning: str


class ProductAnalysis(BaseModel):
    product_id: int
    name: str
    current_price: float
    stock: int
    pricing: PricingResult
