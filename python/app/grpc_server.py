"""
gRPC transport for FastPOC.

A third transport alongside REST (app/api.py) and MCP (app/mcp.py), wired into
the same shared business logic. ProductServicer handles CRUD; PricingServicer
mirrors the A2A PricingAgent, including a server-streaming RPC that maps to the
SSE streaming endpoint.
"""
import os
import logging
from concurrent import futures
from typing import Optional

import grpc
from pydantic import ValidationError

from app.business import (
    list_all_products,
    get_product_by_id,
    create_product_logic,
    update_product_logic,
    delete_product_logic,
)
from app.agents.pricing import analyze_pricing
from app.db import ProductNotFoundError
from app.grpc_gen import product_pb2 as pb
from app.grpc_gen import product_pb2_grpc as pb_grpc

logger = logging.getLogger(__name__)


def _to_proto(product) -> pb.Product:
    return pb.Product(
        id=product.id,
        name=product.name,
        description=product.description or "",
        price=product.price,
        stock=product.stock,
    )


class ProductServicer(pb_grpc.ProductServiceServicer):
    def ListProducts(self, request, context):
        products = list_all_products()
        return pb.ProductList(products=[_to_proto(p) for p in products])

    def GetProduct(self, request, context):
        try:
            return _to_proto(get_product_by_id(request.id))
        except ProductNotFoundError as e:
            context.abort(grpc.StatusCode.NOT_FOUND, str(e))

    def CreateProduct(self, request, context):
        try:
            product = create_product_logic(
                name=request.name,
                description=request.description or None,
                price=request.price,
                stock=request.stock,
            )
            return _to_proto(product)
        except ValidationError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

    def UpdateProduct(self, request, context):
        try:
            product = update_product_logic(
                request.id,
                name=request.name if request.has_name else None,
                description=request.description if request.has_description else None,
                price=request.price if request.has_price else None,
                stock=request.stock if request.has_stock else None,
            )
            return _to_proto(product)
        except ProductNotFoundError as e:
            context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except ValidationError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

    def DeleteProduct(self, request, context):
        try:
            delete_product_logic(request.id)
        except ProductNotFoundError as e:
            context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        return pb.DeleteResponse(message=f"Product {request.id} deleted successfully")


class PricingServicer(pb_grpc.PricingServiceServicer):
    def GetPricing(self, request, context):
        try:
            product = get_product_by_id(request.id)
        except ProductNotFoundError as e:
            context.abort(grpc.StatusCode.NOT_FOUND, str(e))
            return
        result = analyze_pricing(product.price, product.stock)
        return pb.PricingResult(
            suggested_min=result.suggested_min,
            suggested_max=result.suggested_max,
            discount_eligible=result.discount_eligible,
            reasoning=result.reasoning,
        )

    def StreamPricingAnalysis(self, request, context):
        yield pb.PricingProgress(status="working", step="Fetching product data...")
        try:
            product = get_product_by_id(request.id)
        except ProductNotFoundError as e:
            yield pb.PricingProgress(status="failed", error=str(e))
            return

        yield pb.PricingProgress(status="working", step="Analysing price and stock level...")
        result = analyze_pricing(product.price, product.stock)
        yield pb.PricingProgress(
            status="completed",
            result=pb.PricingResult(
                suggested_min=result.suggested_min,
                suggested_max=result.suggested_max,
                discount_eligible=result.discount_eligible,
                reasoning=result.reasoning,
            ),
        )


def serve(port: Optional[int] = None) -> None:
    if port is None:
        port = int(os.getenv("GRPC_PORT", 50051))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_ProductServiceServicer_to_server(ProductServicer(), server)
    pb_grpc.add_PricingServiceServicer_to_server(PricingServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info(f"gRPC server listening on port {port}")
    server.wait_for_termination()
