"""
Test suite for verifying API endpoints and application logic.
Uses a temporary SQLite database to ensure tests runs are isolated and deterministic.
"""
import pytest
import os
import shutil
from fastapi.testclient import TestClient
from app.api import app
from app.db import SQLiteDB
import app.db as app_db_module
import app.api as app_api_module

# Fixture to setup a temporary database for testing
@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    print("\n[SETUP] Starting setup_test_db fixture")
    test_db_path = "test_products.db"
    
    # Ensure a clean slate
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass
    
    # Initialize test DB
    print(f"[SETUP] Initializing test DB at {test_db_path}")
    test_db = SQLiteDB(test_db_path)
    
    # Patch the global db instances
    # Save original references
    original_db_app = app_db_module.db
    original_db_api = app_api_module.db
    
    print(f"[SETUP] Patching app.db.db and app.api.db")
    app_db_module.db = test_db
    app_api_module.db = test_db
    
    yield test_db
    
    # Teardown
    print("\n[TEARDOWN] Restoring DB and cleaning up file")
    app_db_module.db = original_db_app
    app_api_module.db = original_db_api
    
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception as e:
            print(f"[WARNING] Could not remove {test_db_path}: {e}")

@pytest.fixture
def test_client():
    return TestClient(app)

def test_read_main(test_client):
    print("\n[TEST] Executing: test_read_main")
    try:
        response = test_client.get("/products")
        if response.status_code != 200:
            print(f"[DEBUG] Response content: {response.content}")
        assert response.status_code == 200
        # The test DB initializes with 30 sample items
        assert len(response.json()) == 30
        print("[TEST] Status: test_read_main PASSED")
    except AssertionError as e:
        print(f"[TEST] Status: test_read_main FAILED - Assertion Error: {e}")
        raise
    except Exception as e:
        print(f"[TEST] Status: test_read_main FAILED - Error: {e}")
        raise

def test_create_product(test_client):
    print("\n[TEST] Executing: test_create_product")
    try:
        # Create a new product
        response = test_client.post(
            "/products",
            json={"name": "Test Product", "price": 10.5, "stock": 100},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Product"
        assert "id" in data
        
        product_id = data["id"]
        
        # Verify it can be retrieved
        response = test_client.get(f"/products/{product_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Product"
        print("[TEST] Status: test_create_product PASSED")
    except AssertionError as e:
        print(f"[TEST] Status: test_create_product FAILED - Assertion Error: {e}")
        raise
    except Exception as e:
        print(f"[TEST] Status: test_create_product FAILED - Error: {e}")
        raise

def test_mcp_logic():
    print("\n[TEST] Executing: test_mcp_logic")
    try:
        # Basic import test for MCP server
        from app.mcp_server import list_products
        # Since mcp tools are decorated, we might check if they are callable or just exist
        assert callable(list_products)
        print("[TEST] Status: test_mcp_logic PASSED")
    except AssertionError as e:
        print(f"[TEST] Status: test_mcp_logic FAILED - Assertion Error: {e}")
        raise
    except Exception as e:
        print(f"[TEST] Status: test_mcp_logic FAILED - Error: {e}")
        raise
