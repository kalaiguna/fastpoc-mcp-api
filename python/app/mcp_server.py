# mcp_server.py
"""
MCP Server implementation exposing Product management tools.
"""
from mcp.server.fastmcp import FastMCP
from app.db import db, ProductNotFoundError
from app.models import ProductCreate, ProductUpdate

# Initialize FastMCP server
mcp = FastMCP("Product MCP Server")

@mcp.tool()
def list_products() -> str:
    """List all products in the database."""
    products = db.get_all()
    return str([p.model_dump() for p in products])

@mcp.tool()
def get_product(product_id: int) -> str:
    """Get a product by its ID."""
    try:
        product = db.get_by_id(product_id)
        return str(product.model_dump())
    except ProductNotFoundError:
        return f"Error: Product with id {product_id} not found"

@mcp.tool()
def create_product(name: str, price: float, stock: int, description: str = None) -> str:
    """Create a new product."""
    product_in = ProductCreate(name=name, price=price, stock=stock, description=description)
    new_product = db.create(product_in)
    return f"Created product: {new_product.model_dump()}"

@mcp.tool()
def update_product(product_id: int, name: str = None, price: float = None, stock: int = None, description: str = None) -> str:
    """Update an existing product."""
    product_in = ProductUpdate(name=name, price=price, stock=stock, description=description)
    try:
        updated_product = db.update(product_id, product_in)
        return f"Updated product: {updated_product.model_dump()}"
    except ProductNotFoundError:
        return f"Error: Product with id {product_id} not found"

@mcp.tool()
def delete_product(product_id: int) -> str:
    """Delete a product by its ID."""
    try:
        db.delete(product_id)
        return f"Deleted product with id {product_id}"
    except ProductNotFoundError:
        return f"Error: Product with id {product_id} not found"
