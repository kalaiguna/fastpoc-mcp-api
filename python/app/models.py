"""
Defines Pydantic models for Product data validation and serialization.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None

class Product(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
