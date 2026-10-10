"""
Tests for the gRPC transport (app/grpc_server.py).

Servicers are tested directly with a fake context — no network server needed.
The fake context's abort() raises, mirroring real grpc behaviour so NOT_FOUND
and INVALID_ARGUMENT paths can be asserted.
"""
import os

import grpc
import pytest

from app.db import SQLiteDB
import app.business as business_module
from app.grpc_server import ProductServicer, PricingServicer
from app.grpc_gen import product_pb2 as pb


class _Aborted(Exception):
    pass


class _FakeContext:
    """Minimal grpc.ServicerContext stand-in; abort() records and raises."""
    def __init__(self):
        self.code = None
        self.details = None

    def abort(self, code, details):
        self.code = code
        self.details = details
        raise _Aborted(details)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    test_db_path = "test_grpc_products.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    test_db = SQLiteDB(test_db_path)
    original = business_module.db
    business_module.db = test_db
    yield test_db
    business_module.db = original
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def ctx():
    return _FakeContext()


@pytest.fixture
def products():
    return ProductServicer()


@pytest.fixture
def pricing():
    return PricingServicer()


# --- ProductService ---

def test_list_products(products, ctx):
    resp = products.ListProducts(pb.Empty(), ctx)
    assert len(resp.products) == 30
    assert resp.products[0].id == 1


def test_get_product(products, ctx):
    product = products.GetProduct(pb.ProductId(id=1), ctx)
    assert product.id == 1
    assert product.name


def test_get_product_not_found(products, ctx):
    with pytest.raises(_Aborted):
        products.GetProduct(pb.ProductId(id=99999), ctx)
    assert ctx.code == grpc.StatusCode.NOT_FOUND


def test_create_product(products, ctx):
    created = products.CreateProduct(pb.CreateProductRequest(
        name="Test Widget", description="desc", price=9.99, stock=5,
    ), ctx)
    assert created.id > 0
    assert created.name == "Test Widget"


def test_create_product_invalid(products, ctx):
    with pytest.raises(_Aborted):
        products.CreateProduct(pb.CreateProductRequest(
            name="Bad", description="", price=-5.0, stock=5,
        ), ctx)
    assert ctx.code == grpc.StatusCode.INVALID_ARGUMENT


def test_update_product_partial(products, ctx):
    updated = products.UpdateProduct(pb.UpdateProductRequest(
        id=2, price=42.0, has_price=True,
    ), ctx)
    assert updated.id == 2
    assert updated.price == 42.0


def test_update_product_not_found(products, ctx):
    with pytest.raises(_Aborted):
        products.UpdateProduct(pb.UpdateProductRequest(
            id=99999, price=1.0, has_price=True,
        ), ctx)
    assert ctx.code == grpc.StatusCode.NOT_FOUND


def test_delete_product(products, ctx):
    created = products.CreateProduct(pb.CreateProductRequest(
        name="To Delete", description="", price=1.0, stock=1,
    ), ctx)
    resp = products.DeleteProduct(pb.ProductId(id=created.id), ctx)
    assert "deleted" in resp.message.lower()
    with pytest.raises(_Aborted):
        products.GetProduct(pb.ProductId(id=created.id), ctx)


def test_delete_product_not_found(products, ctx):
    with pytest.raises(_Aborted):
        products.DeleteProduct(pb.ProductId(id=99999), ctx)
    assert ctx.code == grpc.StatusCode.NOT_FOUND


# --- PricingService ---

def test_get_pricing(pricing, ctx):
    result = pricing.GetPricing(pb.ProductId(id=1), ctx)
    assert result.suggested_min > 0
    assert result.suggested_max >= result.suggested_min
    assert result.reasoning


def test_get_pricing_not_found(pricing, ctx):
    with pytest.raises(_Aborted):
        pricing.GetPricing(pb.ProductId(id=99999), ctx)
    assert ctx.code == grpc.StatusCode.NOT_FOUND


def test_stream_pricing_analysis(pricing, ctx):
    events = list(pricing.StreamPricingAnalysis(pb.ProductId(id=1), ctx))
    assert events[0].status == "working"
    assert events[-1].status == "completed"
    assert events[-1].result.suggested_min > 0


def test_stream_pricing_not_found(pricing, ctx):
    events = list(pricing.StreamPricingAnalysis(pb.ProductId(id=99999), ctx))
    assert events[0].status == "working"
    assert events[-1].status == "failed"
    assert "99999" in events[-1].error
