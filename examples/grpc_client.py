#!/usr/bin/env python3
"""
gRPC Client Example
===================
Demonstrates the FastPOC gRPC transport — the same business logic the REST API
and MCP server expose, now over gRPC.

Shows:
  1. Unary calls    - ListProducts, GetProduct, CreateProduct
  2. Server stream  - StreamPricingAnalysis yields progress events then a result

Start the gRPC server first:
  cd python && python grpc_entry.py

Then run:
  python examples/grpc_client.py

Environment variables:
  GRPC_TARGET   host:port of the gRPC server (default: localhost:50051)
  PRODUCT_ID    Product ID to analyse        (default: 1)
"""
import os
import sys
from pathlib import Path

import grpc

# The generated stubs import each other as app.grpc_gen.* — put python/ on the path.
PYTHON_DIR = Path(__file__).resolve().parent.parent / "python"
sys.path.insert(0, str(PYTHON_DIR))

from app.grpc_gen import product_pb2 as pb          # noqa: E402
from app.grpc_gen import product_pb2_grpc as pb_grpc  # noqa: E402

TARGET = os.getenv("GRPC_TARGET", "localhost:50051")
PRODUCT_ID = int(os.getenv("PRODUCT_ID", "1"))


def step(label: str, detail: str = "") -> None:
    print(f"\n[{label}]", detail)


def main() -> None:
    print("=" * 55)
    print("  FastPOC gRPC Client")
    print("=" * 55)
    print(f"  Target  : {TARGET}")
    print(f"  Product : {PRODUCT_ID}")

    with grpc.insecure_channel(TARGET) as channel:
        products = pb_grpc.ProductServiceStub(channel)
        pricing = pb_grpc.PricingServiceStub(channel)

        step("1. LIST", "ProductService.ListProducts")
        resp = products.ListProducts(pb.Empty())
        print(f"    {len(resp.products)} products; first: "
              f"{resp.products[0].name} (${resp.products[0].price})")

        step("2. GET", f"ProductService.GetProduct(id={PRODUCT_ID})")
        product = products.GetProduct(pb.ProductId(id=PRODUCT_ID))
        print(f"    {product.name}: ${product.price}, stock {product.stock}")

        step("3. CREATE", "ProductService.CreateProduct")
        created = products.CreateProduct(pb.CreateProductRequest(
            name="gRPC Demo Widget",
            description="Created via gRPC",
            price=29.99,
            stock=15,
        ))
        print(f"    Created id={created.id}: {created.name}")

        step("4. STREAM", f"PricingService.StreamPricingAnalysis(id={PRODUCT_ID})")
        for event in pricing.StreamPricingAnalysis(pb.ProductId(id=PRODUCT_ID)):
            if event.status == "working":
                print(f"    working : {event.step}")
            elif event.status == "completed":
                r = event.result
                print(f"    done    : ${r.suggested_min} - ${r.suggested_max} "
                      f"(discount: {r.discount_eligible})")
                print(f"              {r.reasoning}")
            elif event.status == "failed":
                print(f"    failed  : {event.error}")

    print("\n" + "=" * 55)


if __name__ == "__main__":
    try:
        main()
    except grpc.RpcError as e:
        print(f"\ngRPC error: {e.code()} - {e.details()}", file=sys.stderr)
        sys.exit(1)
