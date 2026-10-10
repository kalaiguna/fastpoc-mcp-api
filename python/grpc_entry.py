"""
Entry point for running the gRPC server.

Exposes ProductService and PricingService on port 50051 (override with GRPC_PORT).
Backed by the same business logic as the REST API and MCP server.

  python grpc_entry.py
"""
import logging

from app.grpc_server import serve

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    serve()
