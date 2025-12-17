# api.py 
"""
FastAPI application defining REST endpoints for Product management.
"""
from fastapi import FastAPI, HTTPException
from typing import List
from app.models import Product, ProductCreate, ProductUpdate
from app.db import db, ProductNotFoundError

app = FastAPI(title="Product API", description="CRUD API for Products", version="1.0.0")

@app.get("/products", response_model=List[Product])
def list_products():
    return db.get_all()

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    try:
        return db.get_by_id(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/products", response_model=Product, status_code=201)
def create_product(product: ProductCreate):
    return db.create(product)

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductUpdate):
    try:
        return db.update(product_id, product)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    try:
        db.delete(product_id)
        return {"message": "Product deleted successfully"}
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
