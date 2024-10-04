from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import httpx

app = FastAPI()

# In-memory store for orders
orders: Dict[int, Dict] = {}
next_order_id = 1

class Order(BaseModel):
    customer_id: int
    product_id: int
    quantity: int

@app.post("/orders", status_code=201)
async def create_order(order: Order):
    async with httpx.AsyncClient() as client:
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

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    if order_id in orders:
        return orders[order_id]
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.put("/orders/{order_id}")
def update_order(order_id: int, order: Order):
    if order_id in orders:
        orders[order_id] = order.dict()
        return {"msg": "Order updated"}
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: int):
    if order_id in orders:
        del orders[order_id]
        return
    else:
        raise HTTPException(status_code=404, detail="Order not found")
