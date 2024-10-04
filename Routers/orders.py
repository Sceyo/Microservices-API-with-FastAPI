import httpx
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pydantic import BaseModel, PositiveInt
from typing import Dict
from fastapi.security import OAuth2PasswordBearer
from Middleware.authentication import get_current_user
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
router = APIRouter()

# In-memory store for orders
orders: Dict[int, Dict] = {}
next_order_id = 1


class Order(BaseModel):
    customer_id: int
    product_id: int
    quantity: PositiveInt 

# OAuth2 scheme for getting the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Get current user and check role
async def get_current_user_and_role(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    return user

# Create a new order (Customer only)
@app.post("/orders", status_code=201)
async def create_order(order: Order, current_user: dict = Depends(get_current_user_and_role)):
    # Ensure the user is a customer
    if current_user['role'] != 'customer':
        logging.warning(f"Unauthorized access attempt by {current_user['username']}")
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    async with httpx.AsyncClient() as client:
        # Verify customer
        customer_response = await client.get(f'http://127.0.0.1:3005/customers/{order.customer_id}')
        if customer_response.status_code != 200:
            logging.error(f"Customer with ID {order.customer_id} not found.")
            raise HTTPException(status_code=400, detail="Customer not found")
        
        # Verify product
        product_response = await client.get(f'http://127.0.0.1:3004/products/{order.product_id}')
        if product_response.status_code != 200:
            logging.error(f"Product with ID {order.product_id} not found.")
            raise HTTPException(status_code=400, detail="Product not found")
    
    global next_order_id
    order_id = next_order_id
    orders[order_id] = order.dict()
    next_order_id += 1
    logging.info(f"Order created with ID: {order_id} by customer ID: {order.customer_id}")
    return {"order_id": order_id}

# Get an order by ID (Available to all users)
@app.get("/orders/{order_id}")
async def get_order(order_id: int, current_user: dict = Depends(get_current_user_and_role)):
    if order_id in orders:
        logging.info(f"Order {order_id} retrieved successfully.")
        return orders[order_id]
    else:
        logging.error(f"Order with ID {order_id} not found.")
        raise HTTPException(status_code=404, detail="Order not found")

# Update an order (Admin only)
@app.put("/orders/{order_id}")
async def update_order(order_id: int, order: Order, current_user: dict = Depends(get_current_user_and_role)):
    # Ensure the user is an admin
    if current_user['role'] != 'admin':
        logging.warning(f"Unauthorized access attempt by {current_user['username']} to update order {order_id}")
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    if order_id in orders:
        orders[order_id] = order.dict()
        logging.info(f"Order {order_id} updated by admin {current_user['username']}")
        return {"msg": "Order updated"}
    else:
        logging.error(f"Order with ID {order_id} not found for update.")
        raise HTTPException(status_code=404, detail="Order not found")

# Delete an order (Admin only)
@app.delete("/orders/{order_id}", status_code=204)
async def delete_order(order_id: int, current_user: dict = Depends(get_current_user_and_role)):
    # Ensure the user is an admin
    if current_user['role'] != 'admin':
        logging.warning(f"Unauthorized access attempt by {current_user['username']} to delete order {order_id}")
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    if order_id in orders:
        del orders[order_id]
        logging.info(f"Order {order_id} deleted by admin {current_user['username']}")
        return
    else:
        logging.error(f"Order with ID {order_id} not found for deletion.")
        raise HTTPException(status_code=404, detail="Order not found")

# Add the router to the app
app.include_router(router)
