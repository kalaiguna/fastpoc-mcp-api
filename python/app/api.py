# api.py 
"""
FastAPI application defining REST endpoints for Product management.
"""
import os
import logging
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models import Product, ProductCreate, ProductUpdate, ErrorResponse
from app.db import db, ProductNotFoundError

_STATUS_TO_CODE = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    422: "VALIDATION_ERROR",
    429: "TOO_MANY_REQUESTS",
    500: "INTERNAL_SERVER_ERROR",
    503: "SERVICE_UNAVAILABLE",
}

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


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = _STATUS_TO_CODE.get(exc.status_code, "ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": str(exc.detail)}},
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


@app.get(f"/api/{API_VERSION}/products", response_model=List[Product], tags=["Products"],
         responses={401: {"model": ErrorResponse}, 429: {"model": ErrorResponse}})
def list_products():
    """List all products in the database.
    
    Returns:
        List of all products with their details.
    """
    logger.info("Fetching all products")
    return db.get_all()


@app.get(f"/api/{API_VERSION}/products/{{product_id}}", response_model=Product, tags=["Products"],
         responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 429: {"model": ErrorResponse}})
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


@app.post(f"/api/{API_VERSION}/products", response_model=Product, status_code=201, tags=["Products"],
          responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}, 429: {"model": ErrorResponse}})
def create_product(product: ProductCreate):
    """Create a new product.
    
    Args:
        product: Product data including name, description, price, and stock.
        
    Returns:
        The created product with assigned ID.
    """
    logger.info(f"Creating new product: {product.name}")
    return db.create(product)


@app.put(f"/api/{API_VERSION}/products/{{product_id}}", response_model=Product, tags=["Products"],
         responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 429: {"model": ErrorResponse}})
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


@app.delete(f"/api/{API_VERSION}/products/{{product_id}}", tags=["Products"],
            responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 429: {"model": ErrorResponse}})
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
