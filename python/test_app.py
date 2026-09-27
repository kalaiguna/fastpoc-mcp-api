"""
Test suite for verifying API endpoints and application logic.
Uses a temporary SQLite database to ensure tests runs are isolated and deterministic.
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.api import app
from app.db import SQLiteDB, ProductNotFoundError
import app.db as app_db_module
import app.api as app_api_module
import app.agents.router as agents_router_module


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
    agents_router_module.db = test_db

    yield test_db

    # Restore original references
    app_db_module.db = original_db_app
    app_api_module.db = original_db_api
    agents_router_module.db = test_db
    
    # Cleanup test database file
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


API_KEY_HEADER = {"X-API-Key": "dev-key-changeme"}


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
    response = test_client.get("/api/v1/products", headers=API_KEY_HEADER)
    assert response.status_code == 200
    # The test DB initializes with 30 sample items
    assert len(response.json()) == 30


def test_get_product_by_id(test_client):
    """Test getting a specific product by ID."""
    response = test_client.get("/api/v1/products/1", headers=API_KEY_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data
    assert "price" in data


def test_get_product_not_found(test_client):
    """Test 404 response for non-existent product."""
    response = test_client.get("/api/v1/products/99999", headers=API_KEY_HEADER)
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "NOT_FOUND"


def test_auth_rejected_without_key(test_client):
    """Test that product endpoints reject requests without an API key."""
    response = test_client.get("/api/v1/products")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_create_product(test_client):
    """Test creating a new product."""
    response = test_client.post(
        "/api/v1/products",
        json={"name": "Test Product", "price": 10.5, "stock": 100},
        headers=API_KEY_HEADER,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert "id" in data

    product_id = data["id"]

    # Verify it can be retrieved
    response = test_client.get(f"/api/v1/products/{product_id}", headers=API_KEY_HEADER)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"


def test_create_product_validation(test_client):
    """Test input validation for product creation."""
    # Test negative price
    response = test_client.post(
        "/api/v1/products",
        json={"name": "Invalid Product", "price": -10.5, "stock": 100},
        headers=API_KEY_HEADER,
    )
    assert response.status_code == 422

    # Test negative stock
    response = test_client.post(
        "/api/v1/products",
        json={"name": "Invalid Product", "price": 10.5, "stock": -5},
        headers=API_KEY_HEADER,
    )
    assert response.status_code == 422

    # Test empty name
    response = test_client.post(
        "/api/v1/products",
        json={"name": "", "price": 10.5, "stock": 100},
        headers=API_KEY_HEADER,
    )
    assert response.status_code == 422


def test_update_product(test_client):
    """Test updating an existing product."""
    create_response = test_client.post(
        "/api/v1/products",
        json={"name": "Update Test", "price": 20.0, "stock": 50},
        headers=API_KEY_HEADER,
    )
    product_id = create_response.json()["id"]

    update_response = test_client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "Updated Name", "price": 25.0},
        headers=API_KEY_HEADER,
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
        headers=API_KEY_HEADER,
    )
    assert response.status_code == 404


def test_delete_product(test_client):
    """Test deleting a product."""
    create_response = test_client.post(
        "/api/v1/products",
        json={"name": "Delete Test", "price": 15.0, "stock": 30},
        headers=API_KEY_HEADER,
    )
    product_id = create_response.json()["id"]

    delete_response = test_client.delete(f"/api/v1/products/{product_id}", headers=API_KEY_HEADER)
    assert delete_response.status_code == 200
    assert "message" in delete_response.json()

    # Verify it's deleted
    get_response = test_client.get(f"/api/v1/products/{product_id}", headers=API_KEY_HEADER)
    assert get_response.status_code == 404


def test_delete_product_not_found(test_client):
    """Test 404 response when deleting non-existent product."""
    response = test_client.delete("/api/v1/products/99999", headers=API_KEY_HEADER)
    assert response.status_code == 404


def test_mcp_logic():
    """Test MCP module imports correctly after refactor."""
    from app.business import list_all_products, get_product_by_id, create_product_logic
    assert callable(list_all_products)
    assert callable(get_product_by_id)
    assert callable(create_product_logic)


# --- A2A Agent tests ---

def test_pricing_agent(test_client):
    """PricingAgent returns a pricing recommendation for a valid product."""
    response = test_client.post(
        "/api/v1/agents/pricing/run",
        json={"product_id": 1},
        headers=API_KEY_HEADER,
    )
    assert response.status_code == 200
    data = response.json()
    assert "suggested_min" in data
    assert "suggested_max" in data
    assert "discount_eligible" in data
    assert "reasoning" in data


def test_pricing_agent_not_found(test_client):
    """PricingAgent returns 404 for a non-existent product."""
    response = test_client.post(
        "/api/v1/agents/pricing/run",
        json={"product_id": 99999},
        headers=API_KEY_HEADER,
    )
    assert response.status_code == 404


def test_product_agent(test_client):
    """ProductAgent returns combined analysis by calling PricingAgent via HTTP (mocked)."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "suggested_min": 9.5,
        "suggested_max": 10.5,
        "discount_eligible": False,
        "reasoning": "Stock levels are healthy — hold current price.",
    }
    mock_response.raise_for_status = MagicMock()

    with patch("app.agents.router.httpx.post", return_value=mock_response):
        response = test_client.post(
            "/api/v1/agents/product/run",
            json={"product_id": 1},
            headers=API_KEY_HEADER,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == 1
    assert "name" in data
    assert "current_price" in data
    assert "pricing" in data
    assert data["pricing"]["discount_eligible"] is False


def test_pricing_logic_low_stock():
    """PricingAgent recommends premium price when stock is low."""
    from app.agents.pricing import analyze_pricing
    result = analyze_pricing(price=100.0, stock=10)
    assert result.suggested_min > 100.0
    assert result.discount_eligible is False


def test_pricing_logic_high_stock():
    """PricingAgent recommends discount when stock is high."""
    from app.agents.pricing import analyze_pricing
    result = analyze_pricing(price=100.0, stock=90)
    assert result.suggested_max < 100.0
    assert result.discount_eligible is True


# --- Agent Card tests ---

def test_service_agent_card(test_client):
    """/.well-known/agent.json is public and returns a valid service card."""
    response = test_client.get("/.well-known/agent.json")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "FastPOC Agent Service"
    assert "skills" in data
    assert len(data["skills"]) == 2
    assert data["authentication"]["schemes"] == ["apiKey"]
    assert data["capabilities"]["streaming"] is False


def test_pricing_agent_card(test_client):
    """PricingAgent card returns correct metadata."""
    response = test_client.get("/api/v1/agents/pricing/card")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "PricingAgent"
    assert len(data["skills"]) == 1
    assert data["skills"][0]["id"] == "pricing-analysis"


def test_product_agent_card(test_client):
    """ProductAgent card returns correct metadata."""
    response = test_client.get("/api/v1/agents/product/card")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ProductAgent"
    assert len(data["skills"]) == 1
    assert data["skills"][0]["id"] == "product-analysis"


# --- Task lifecycle tests ---

def test_submit_pricing_task(test_client):
    """Submitting a pricing task returns a task ID with submitted status."""
    response = test_client.post(
        "/api/v1/agents/pricing/submit",
        json={"product_id": 1},
        headers=API_KEY_HEADER,
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "submitted"


def test_poll_pricing_task_completes(test_client):
    """Polling a submitted pricing task eventually returns completed with a result."""
    submit = test_client.post(
        "/api/v1/agents/pricing/submit",
        json={"product_id": 1},
        headers=API_KEY_HEADER,
    )
    task_id = submit.json()["task_id"]

    # TestClient runs background tasks synchronously before returning,
    # so the task should already be completed by the time we poll.
    poll = test_client.get(f"/api/v1/agents/tasks/{task_id}", headers=API_KEY_HEADER)
    assert poll.status_code == 200
    data = poll.json()
    assert data["status"] == "completed"
    assert data["result"] is not None
    assert "suggested_min" in data["result"]


def test_poll_task_not_found(test_client):
    """Polling a non-existent task returns 404."""
    response = test_client.get(
        "/api/v1/agents/tasks/00000000-0000-0000-0000-000000000000",
        headers=API_KEY_HEADER,
    )
    assert response.status_code == 404


def test_submit_pricing_task_invalid_product(test_client):
    """Submitting a task for a non-existent product results in a failed task."""
    submit = test_client.post(
        "/api/v1/agents/pricing/submit",
        json={"product_id": 99999},
        headers=API_KEY_HEADER,
    )
    task_id = submit.json()["task_id"]

    poll = test_client.get(f"/api/v1/agents/tasks/{task_id}", headers=API_KEY_HEADER)
    assert poll.status_code == 200
    data = poll.json()
    assert data["status"] == "failed"
    assert data["error"] is not None
