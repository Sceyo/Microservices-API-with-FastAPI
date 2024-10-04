from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict
from fastapi.security import OAuth2PasswordBearer
from Middleware.authentication import get_current_user 

app = FastAPI()

# In-memory store for products
products: Dict[int, Dict] = {}
next_product_id = 1

# Define the Product model
class Product(BaseModel):
    name: str
    price: float
    description: str

# OAuth2 scheme for getting the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Get current user and check role
async def get_current_user_and_role(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    return user 

# Create a new product (Admin only)
@app.post("/products", status_code=201)
async def create_product(product: Product, current_user: dict = Depends(get_current_user_and_role)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    global next_product_id
    product_id = next_product_id
    products[product_id] = product.dict()
    next_product_id += 1
    return {"product_id": product_id}

# Get a product by ID (Available to all)
@app.get("/products/{product_id}")
async def get_product(product_id: int):
    if product_id in products:
        return products[product_id]
    else:
        raise HTTPException(status_code=404, detail="Product not found")

# Update a product (Admin only)
@app.put("/products/{product_id}")
async def update_product(product_id: int, product: Product, current_user: dict = Depends(get_current_user_and_role)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    if product_id in products:
        products[product_id] = product.dict()
        return {"msg": "Product updated"}
    else:
        raise HTTPException(status_code=404, detail="Product not found")

# Delete a product (Admin only)
@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, current_user: dict = Depends(get_current_user_and_role)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    if product_id in products:
        del products[product_id]
        return
    else:
        raise HTTPException(status_code=404, detail="Product not found")
