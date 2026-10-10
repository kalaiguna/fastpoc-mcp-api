"""
Tests for the GraphQL transport (app/graphql_schema.py).

Schema-level tests use schema.execute_sync (no server). A couple of HTTP tests
via TestClient verify the /graphql mount and that it requires the API key.
"""
import os

import pytest
from fastapi.testclient import TestClient

from app.db import SQLiteDB
import app.business as business_module
from app.graphql_schema import schema
from app.api import app


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    test_db_path = "test_graphql_products.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    test_db = SQLiteDB(test_db_path)
    original = business_module.db
    business_module.db = test_db
    yield test_db
    business_module.db = original
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


API_KEY_HEADER = {"X-API-Key": "dev-key-changeme"}


@pytest.fixture
def client():
    return TestClient(app)


# --- Query ---

def test_query_products():
    r = schema.execute_sync("{ products { id name price stock } }")
    assert r.errors is None
    assert len(r.data["products"]) == 30


def test_query_product():
    r = schema.execute_sync("{ product(id: 1) { id name } }")
    assert r.errors is None
    assert r.data["product"]["id"] == 1


def test_query_product_not_found():
    r = schema.execute_sync("{ product(id: 99999) { id } }")
    assert r.errors
    assert "99999" in r.errors[0].message


# --- Mutation ---

def test_create_product():
    r = schema.execute_sync(
        'mutation { createProduct(name: "GQL Test", price: 9.99, stock: 4) { id name price } }'
    )
    assert r.errors is None
    assert r.data["createProduct"]["name"] == "GQL Test"
    assert r.data["createProduct"]["id"] > 0


def test_create_product_validation_error():
    r = schema.execute_sync(
        'mutation { createProduct(name: "Bad", price: -1, stock: 4) { id } }'
    )
    assert r.errors


def test_update_product_partial():
    r = schema.execute_sync("mutation { updateProduct(id: 2, price: 50.0) { id price } }")
    assert r.errors is None
    assert r.data["updateProduct"]["price"] == 50.0


def test_update_product_not_found():
    r = schema.execute_sync("mutation { updateProduct(id: 99999, price: 1.0) { id } }")
    assert r.errors
    assert "99999" in r.errors[0].message


def test_delete_product():
    created = schema.execute_sync(
        'mutation { createProduct(name: "To Delete", price: 1.0, stock: 1) { id } }'
    )
    pid = created.data["createProduct"]["id"]
    deleted = schema.execute_sync(f"mutation {{ deleteProduct(id: {pid}) }}")
    assert deleted.errors is None
    assert deleted.data["deleteProduct"] is True
    gone = schema.execute_sync(f"{{ product(id: {pid}) {{ id }} }}")
    assert gone.errors


def test_delete_product_not_found():
    r = schema.execute_sync("mutation { deleteProduct(id: 99999) }")
    assert r.errors
    assert "99999" in r.errors[0].message


# --- HTTP mount + auth ---

def test_graphql_requires_api_key(client):
    r = client.post("/graphql", json={"query": "{ products { id } }"})
    assert r.status_code == 401


def test_graphql_with_api_key(client):
    r = client.post("/graphql", json={"query": "{ products { id } }"}, headers=API_KEY_HEADER)
    assert r.status_code == 200
    assert "data" in r.json()
    assert r.json()["data"]["products"]
