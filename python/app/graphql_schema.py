"""
GraphQL transport for FastPOC.

A fourth interface alongside REST, MCP, and gRPC, wired into the same shared
business logic. Exposes Query (list/get) and Mutation (create/update/delete).
Domain exceptions propagate as GraphQL errors.
"""
from typing import List, Optional

import strawberry

from app.business import (
    list_all_products,
    get_product_by_id,
    create_product_logic,
    update_product_logic,
    delete_product_logic,
)


@strawberry.type
class Product:
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int


def _to_gql(p) -> "Product":
    return Product(
        id=p.id,
        name=p.name,
        description=p.description,
        price=p.price,
        stock=p.stock,
    )


@strawberry.type
class Query:
    @strawberry.field(description="List all products.")
    def products(self) -> List[Product]:
        return [_to_gql(p) for p in list_all_products()]

    @strawberry.field(description="Get a single product by ID.")
    def product(self, id: int) -> Product:
        # ProductNotFoundError propagates as a GraphQL error.
        return _to_gql(get_product_by_id(id))


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Create a new product.")
    def create_product(
        self,
        name: str,
        price: float,
        stock: int,
        description: Optional[str] = None,
    ) -> Product:
        # Pydantic ValidationError propagates as a GraphQL error.
        return _to_gql(create_product_logic(
            name=name, description=description, price=price, stock=stock,
        ))

    @strawberry.mutation(description="Update an existing product. Only provided fields change.")
    def update_product(
        self,
        id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        stock: Optional[int] = None,
    ) -> Product:
        return _to_gql(update_product_logic(
            id, name=name, description=description, price=price, stock=stock,
        ))

    @strawberry.mutation(description="Delete a product by ID. Returns true on success.")
    def delete_product(self, id: int) -> bool:
        delete_product_logic(id)
        return True


schema = strawberry.Schema(query=Query, mutation=Mutation)
