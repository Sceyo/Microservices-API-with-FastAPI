import http
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict
from fastapi.security import OAuth2PasswordBearer
from Middleware.authentication import get_current_user  

app = FastAPI()

# In-memory store for orders
orders: Dict[int, Dict] = {}
next_order_id = 1

class Order(BaseModel):
    customer_id: int
    product_id: int
    quantity: int

# OAuth2 scheme for getting the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# get current user and check role
async def get_current_user_and_role(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    return user  

# create a new order (Customer only)
@app.post("/orders", status_code=201)
async def create_order(order: Order, current_user: dict = Depends(get_current_user_and_role)):
    # Ensure the user is a customer
    if current_user['role'] != 'customer':
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    async with http.AsyncClient() as client:
        # Verify customer
        customer_response = await client.get(f'http://127.0.0.1:3005/customers/{order.customer_id}')
        if customer_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Customer not found")
        
        # Verify product
        product_response = await client.get(f'http://127.0.0.1:3004/products/{order.product_id}')
        if product_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Product not found")
    
    global next_order_id
    order_id = next_order_id
    orders[order_id] = order.dict()
    next_order_id += 1
    return {"order_id": order_id}

# get an order by ID (Available to all users)
@app.get("/orders/{order_id}")
async def get_order(order_id: int, current_user: dict = Depends(get_current_user_and_role)):
    if order_id in orders:
        return orders[order_id]
    else:
        raise HTTPException(status_code=404, detail="Order not found")

# update an order (Admin only)
@app.put("/orders/{order_id}")
async def update_order(order_id: int, order: Order, current_user: dict = Depends(get_current_user_and_role)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    if order_id in orders:
        orders[order_id] = order.dict()
        return {"msg": "Order updated"}
    else:
        raise HTTPException(status_code=404, detail="Order not found")

# delete an order (Admin only)
@app.delete("/orders/{order_id}", status_code=204)
async def delete_order(order_id: int, current_user: dict = Depends(get_current_user_and_role)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    if order_id in orders:
        del orders[order_id]
        return
    else:
        raise HTTPException(status_code=404, detail="Order not found")
