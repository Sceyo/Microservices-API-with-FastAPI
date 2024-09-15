from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# In-memory store for products
products: Dict[int, Dict] = {}
next_product_id = 1

class Product(BaseModel):
    name: str
    price: float
    description: str

@app.post("/products", status_code=201)
def create_product(product: Product):
    global next_product_id
    product_id = next_product_id
    products[product_id] = product.dict()
    next_product_id += 1
    return {"product_id": product_id}

@app.get("/products/{product_id}")
def get_product(product_id: int):
    if product_id in products:
        return products[product_id]
    else:
        raise HTTPException(status_code=404, detail="Product not found")

@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product):
    if product_id in products:
        products[product_id] = product.dict()
        return {"msg": "Product updated"}
    else:
        raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int):
    if product_id in products:
        del products[product_id]
        return
    else:
        raise HTTPException(status_code=404, detail="Product not found")
