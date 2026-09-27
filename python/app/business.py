"""
Shared Business Logic Module
Contains core business operations that are reused by both FastAPI and MCP.
"""
from typing import List, Optional
from app.models import Product, ProductCreate, ProductUpdate
from app.db import db, ProductNotFoundError


def list_all_products() -> List[Product]:
    """Shared logic: List all products."""
    return db.get_all()


def get_product_by_id(product_id: int) -> Product:
    """Shared logic: Get a product by ID.
    
    Raises:
        ProductNotFoundError: If product doesn't exist
    """
    return db.get_by_id(product_id)


def create_product_logic(name: str, description: str, price: float, stock: int) -> Product:
    """Shared logic: Create a new product."""
    product_data = ProductCreate(name=name, description=description, price=price, stock=stock)
    return db.create(product_data)


def update_product_logic(product_id: int, name: Optional[str] = None, 
                          description: Optional[str] = None, 
                          price: Optional[float] = None, 
                          stock: Optional[int] = None) -> Product:
    """Shared logic: Update a product.
    
    Raises:
        ProductNotFoundError: If product doesn't exist
    """
    product_data = ProductUpdate(name=name, description=description, price=price, stock=stock)
    return db.update(product_id, product_data)


def delete_product_logic(product_id: int) -> None:
    """Shared logic: Delete a product.
    
    Raises:
        ProductNotFoundError: If product doesn't exist
    """
    db.delete(product_id)
