import logging
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pydantic import BaseModel, PositiveFloat
from typing import Dict
from fastapi.security import OAuth2PasswordBearer
from Middleware.authentication import get_current_user 

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
router = APIRouter()

# In-memory store for products
products: Dict[int, Dict] = {}
next_product_id = 1

class Product(BaseModel):
    name: str
    price: PositiveFloat
    description: str

# OAuth2 scheme for getting the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Get current user and check role
async def get_current_user_and_role(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    return user 

# Create a new product (Admin only)
@router.post("/products", status_code=201)
async def create_product(product: Product, current_user: dict = Depends(get_current_user_and_role)):
    logging.info(f"Current user: {current_user}")
    
    if current_user['role'] != 'admin':
        logging.warning(f"Unauthorized access attempt by {current_user['username']} to create a product.")
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    logging.info(f"User {current_user['username']} has admin privileges. Proceeding with product creation.")
    
    global next_product_id
    product_id = next_product_id
    products[product_id] = product.dict()
    next_product_id += 1
    logging.info(f"Product created with ID: {product_id} by admin: {current_user['username']}")
    
    return {"product_id": product_id}

# Get a product by ID (Available to all)
@app.get("/products/{product_id}")
async def get_product(product_id: int):
    if product_id in products:
        logging.info(f"Product {product_id} retrieved successfully.")
        return products[product_id]
    else:
        logging.error(f"Product with ID {product_id} not found.")
        raise HTTPException(status_code=404, detail="Product not found")

# Update a product (Admin only)
@app.put("/products/{product_id}")
async def update_product(product_id: int, product: Product, current_user: dict = Depends(get_current_user_and_role)):
    if current_user['role'] != 'admin':
        logging.warning(f"Unauthorized access attempt by {current_user['username']} to update product {product_id}.")
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    if product_id in products:
        products[product_id] = product.dict()
        logging.info(f"Product {product_id} updated by admin: {current_user['username']}")
        return {"msg": "Product updated"}
    else:
        logging.error(f"Product with ID {product_id} not found for update.")
        raise HTTPException(status_code=404, detail="Product not found")

# Delete a product (Admin only)
@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, current_user: dict = Depends(get_current_user_and_role)):
    if current_user['role'] != 'admin':
        logging.warning(f"Unauthorized access attempt by {current_user['username']} to delete product {product_id}.")
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    if product_id in products:
        del products[product_id]
        logging.info(f"Product {product_id} deleted by admin: {current_user['username']}")
        return
    else:
        logging.error(f"Product with ID {product_id} not found for deletion.")
        raise HTTPException(status_code=404, detail="Product not found")

# Add the router to the app
app.include_router(router)
