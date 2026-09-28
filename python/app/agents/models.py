from enum import Enum
from datetime import datetime
from typing import List, Optional, Any, Dict
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


# --- Task lifecycle models (A2A async pattern) ---

class TaskStatus(str, Enum):
    submitted = "submitted"
    working = "working"
    completed = "completed"
    failed = "failed"


class TaskSubmission(BaseModel):
    task_id: str
    status: TaskStatus
    message: str


class Task(BaseModel):
    id: str
    agent: str
    status: TaskStatus
    input: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


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
    submitEndpoint: Optional[str] = None  # async submit path; poll via /agents/tasks/{id}
    streamEndpoint: Optional[str] = None  # SSE stream path; yields progress + result events
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
