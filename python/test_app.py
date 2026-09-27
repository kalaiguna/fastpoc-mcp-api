"""
Test suite for verifying API endpoints and application logic.
Uses a temporary SQLite database to ensure tests runs are isolated and deterministic.
"""
import pytest
import os
from fastapi.testclient import TestClient
from app.api import app
from app.db import SQLiteDB, ProductNotFoundError
import app.db as app_db_module
import app.api as app_api_module


# Fixture to setup a temporary database for testing
@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Initialize test database and patch global instances."""
    test_db_path = "test_products.db"
    
    # Ensure a clean slate
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize test DB
    test_db = SQLiteDB(test_db_path)
    
    # Save original references
    original_db_app = app_db_module.db
    original_db_api = app_api_module.db
    
    # Patch the global db instances
    app_db_module.db = test_db
    app_api_module.db = test_db
    
    yield test_db
    
    # Restore original references
    app_db_module.db = original_db_app
    app_api_module.db = original_db_api
    
    # Cleanup test database file
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def test_client():
    """Create test client for API requests."""
    return TestClient(app)


def test_health_endpoint(test_client):
    """Test health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_readiness_endpoint(test_client):
    """Test readiness check endpoint."""
    response = test_client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_read_main(test_client):
    """Test listing all products."""
    response = test_client.get("/api/v1/products")
    assert response.status_code == 200
    # The test DB initializes with 30 sample items
    assert len(response.json()) == 30


def test_get_product_by_id(test_client):
    """Test getting a specific product by ID."""
    response = test_client.get("/api/v1/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data
    assert "price" in data


def test_get_product_not_found(test_client):
    """Test 404 response for non-existent product."""
    response = test_client.get("/api/v1/products/99999")
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "NOT_FOUND"


def test_create_product(test_client):
    """Test creating a new product."""
    response = test_client.post(
        "/api/v1/products",
        json={"name": "Test Product", "price": 10.5, "stock": 100},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert "id" in data
    
    product_id = data["id"]
    
    # Verify it can be retrieved
    response = test_client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"


def test_create_product_validation(test_client):
    """Test input validation for product creation."""
    # Test negative price
    response = test_client.post(
        "/api/v1/products",
        json={"name": "Invalid Product", "price": -10.5, "stock": 100},
    )
    assert response.status_code == 422
    
    # Test negative stock
    response = test_client.post(
        "/api/v1/products",
        json={"name": "Invalid Product", "price": 10.5, "stock": -5},
    )
    assert response.status_code == 422
    
    # Test empty name
    response = test_client.post(
        "/api/v1/products",
        json={"name": "", "price": 10.5, "stock": 100},
    )
    assert response.status_code == 422


def test_update_product(test_client):
    """Test updating an existing product."""
    # First create a product
    create_response = test_client.post(
        "/api/v1/products",
        json={"name": "Update Test", "price": 20.0, "stock": 50},
    )
    product_id = create_response.json()["id"]
    
    # Update the product
    update_response = test_client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "Updated Name", "price": 25.0},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Name"
    assert data["price"] == 25.0
    assert data["stock"] == 50  # Unchanged


def test_update_product_not_found(test_client):
    """Test 404 response when updating non-existent product."""
    response = test_client.put(
        "/api/v1/products/99999",
        json={"name": "Non-existent"},
    )
    assert response.status_code == 404


def test_delete_product(test_client):
    """Test deleting a product."""
    # First create a product
    create_response = test_client.post(
        "/api/v1/products",
        json={"name": "Delete Test", "price": 15.0, "stock": 30},
    )
    product_id = create_response.json()["id"]
    
    # Delete the product
    delete_response = test_client.delete(f"/api/v1/products/{product_id}")
    assert delete_response.status_code == 200
    assert "message" in delete_response.json()
    
    # Verify it's deleted
    get_response = test_client.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 404


def test_delete_product_not_found(test_client):
    """Test 404 response when deleting non-existent product."""
    response = test_client.delete("/api/v1/products/99999")
    assert response.status_code == 404


def test_mcp_logic():
    """Test MCP module imports correctly after refactor."""
    from app.business import list_all_products, get_product_by_id, create_product_logic
    assert callable(list_all_products)
    assert callable(get_product_by_id)
    assert callable(create_product_logic)
