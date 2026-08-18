# api.py 
"""
FastAPI application defining REST endpoints for Product management.
"""
import os
import logging
from typing import List
from fastapi import FastAPI, HTTPException
from app.models import Product, ProductCreate, ProductUpdate
from app.db import db, ProductNotFoundError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
API_VERSION = os.getenv("API_VERSION", "v1")
PORT = int(os.getenv("PORT", 8081))
HOST = os.getenv("HOST", "0.0.0.0")

app = FastAPI(
    title="Product API",
    description="CRUD API for Products with full validation and error handling",
    version="1.0.0",
    openapi_tags=[
        {"name": "Products", "description": "Product management operations"},
        {"name": "Health", "description": "Health check endpoints"}
    ]
)


@app.get("/health", tags=["Health"], summary="Health Check")
def health_check():
    """Health check endpoint for container orchestration and monitoring."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/ready", tags=["Health"], summary="Readiness Check")
def readiness_check():
    """Readiness check to verify the application is ready to serve requests."""
    try:
        # Verify database connectivity
        db.get_all()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@app.get(f"/api/{API_VERSION}/products", response_model=List[Product], tags=["Products"])
def list_products():
    """List all products in the database.
    
    Returns:
        List of all products with their details.
    """
    logger.info("Fetching all products")
    return db.get_all()


@app.get(f"/api/{API_VERSION}/products/{{product_id}}", response_model=Product, tags=["Products"])
def get_product(product_id: int):
    """Get a specific product by ID.
    
    Args:
        product_id: The unique identifier of the product.
        
    Returns:
        The requested product details.
        
    Raises:
        HTTPException: 404 if product not found.
    """
    try:
        logger.info(f"Fetching product with id: {product_id}")
        return db.get_by_id(product_id)
    except ProductNotFoundError as e:
        logger.warning(f"Product not found: {product_id}")
        raise HTTPException(status_code=404, detail=str(e))


@app.post(f"/api/{API_VERSION}/products", response_model=Product, status_code=201, tags=["Products"])
def create_product(product: ProductCreate):
    """Create a new product.
    
    Args:
        product: Product data including name, description, price, and stock.
        
    Returns:
        The created product with assigned ID.
    """
    logger.info(f"Creating new product: {product.name}")
    return db.create(product)


@app.put(f"/api/{API_VERSION}/products/{{product_id}}", response_model=Product, tags=["Products"])
def update_product(product_id: int, product: ProductUpdate):
    """Update an existing product.
    
    Args:
        product_id: The unique identifier of the product to update.
        product: Fields to update (name, description, price, stock).
        
    Returns:
        The updated product details.
        
    Raises:
        HTTPException: 404 if product not found.
    """
    try:
        logger.info(f"Updating product with id: {product_id}")
        return db.update(product_id, product)
    except ProductNotFoundError as e:
        logger.warning(f"Product not found for update: {product_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid update data: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.delete(f"/api/{API_VERSION}/products/{{product_id}}", tags=["Products"])
def delete_product(product_id: int):
    """Delete a product by ID.
    
    Args:
        product_id: The unique identifier of the product to delete.
        
    Returns:
        Success message.
        
    Raises:
        HTTPException: 404 if product not found.
    """
    try:
        logger.info(f"Deleting product with id: {product_id}")
        db.delete(product_id)
        return {"message": "Product deleted successfully"}
    except ProductNotFoundError as e:
        logger.warning(f"Product not found for deletion: {product_id}")
        raise HTTPException(status_code=404, detail=str(e))
