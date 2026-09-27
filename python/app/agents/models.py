from typing import List, Optional, Any
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


# --- Agent Card models (A2A spec) ---

class AgentAuthentication(BaseModel):
    schemes: List[str]
    credentials: str


class AgentCapabilities(BaseModel):
    streaming: bool = False
    pushNotifications: bool = False
    stateTransitionHistory: bool = False


class AgentSkill(BaseModel):
    id: str
    name: str
    description: str
    endpoint: str
    inputModes: List[str] = ["application/json"]
    outputModes: List[str] = ["application/json"]
    examples: Optional[List[Any]] = None


class AgentCard(BaseModel):
    name: str
    description: str
    url: str
    version: str
    authentication: AgentAuthentication
    capabilities: AgentCapabilities
    skills: List[AgentSkill]
