from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

app = FastAPI()

# In-memory store for products
products: Dict[int, Dict] = {}
next_product_id = 1
users_db = {
    "admin": {"username": "admin", "hashed_password": "$2b$12$wTfdEKCrxGquOKH9GVz2Xe2J6akfYfIpiIhvP9dOCqNVV4MIay.ae", "role": "admin"},
    "customer": {"username": "customer", "hashed_password": "$2b$12$YZbGVshj8G.CWRnUdqlhIufK2IjTdlGZ4VUPSRFM7Fk4WNjQ6QU.S", "role": "customer"}
}


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
