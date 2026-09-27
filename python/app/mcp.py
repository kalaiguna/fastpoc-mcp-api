""" mcp.py
MCP Tools Module
Defines MCP tools as thin wrappers around business logic.
Returns dictionaries for JSON serialization safety.
"""
from typing import List
from mcp.server.fastmcp import FastMCP
from app.business import (
    list_all_products,
    get_product_by_id,
    create_product_logic,
    update_product_logic,
    delete_product_logic
)
from app.db import ProductNotFoundError

# Initialize FastMCP
mcp = FastMCP("Product MCP Server")


@mcp.tool()
def list_products_tool() -> List[dict]:
    """List all products in the database."""
    products = list_all_products()
    return [{"id": p.id, "name": p.name, "description": p.description, 
             "price": p.price, "stock": p.stock} for p in products]


@mcp.tool()
def get_product_tool(product_id: int) -> dict:
    """Get a product by its ID.
    
    Args:
        product_id: The ID of the product to retrieve
    """
    try:
        product = get_product_by_id(product_id)
        return {"id": product.id, "name": product.name, "description": product.description, 
                "price": product.price, "stock": product.stock}
    except ProductNotFoundError as e:
        return {"error": str(e)}


@mcp.tool()
def create_product_tool(name: str, price: float, stock: int, description: str = "") -> dict:
    """Create a new product.
    
    Args:
        name: Product name
        price: Product price
        stock: Product stock quantity
        description: Product description (optional)
    """
    desc = description if description else None
    product = create_product_logic(name=name, description=desc, price=price, stock=stock)
    return {"id": product.id, "name": product.name, "description": product.description, 
            "price": product.price, "stock": product.stock}


@mcp.tool()
def update_product_tool(product_id: int, name: str = "", description: str = "", 
                        price: float = -1, stock: int = -1) -> dict:
    """Update an existing product.
    
    Args:
        product_id: The ID of the product to update
        name: New product name (leave empty to keep current)
        description: New product description (leave empty to keep current)
        price: New product price (use -1 to keep current)
        stock: New product stock (use -1 to keep current)
    """
    try:
        # Convert sentinel values to None for optional updates
        update_name = name if name else None
        update_desc = description if description else None
        update_price = price if price >= 0 else None
        update_stock = stock if stock >= 0 else None
        
        product = update_product_logic(product_id, name=update_name, description=update_desc, 
                                        price=update_price, stock=update_stock)
        return {"id": product.id, "name": product.name, "description": product.description, 
                "price": product.price, "stock": product.stock}
    except ProductNotFoundError as e:
        return {"error": str(e)}


@mcp.tool()
def delete_product_tool(product_id: int) -> dict:
    """Delete a product by its ID.
    
    Args:
        product_id: The ID of the product to delete
    """
    try:
        delete_product_logic(product_id)
        return {"message": f"Product {product_id} deleted successfully"}
    except ProductNotFoundError as e:
        return {"error": str(e)}
