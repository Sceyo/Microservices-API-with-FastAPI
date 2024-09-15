from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# In-memory store for customers
customers: Dict[int, Dict] = {}
next_customer_id = 1

class Customer(BaseModel):
    name: str
    email: str

@app.post("/customers", status_code=201)
def create_customer(customer: Customer):
    global next_customer_id
    customer_id = next_customer_id
    customers[customer_id] = customer.dict()
    next_customer_id += 1
    return {"customer_id": customer_id}

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    if customer_id in customers:
        return customers[customer_id]
    else:
        raise HTTPException(status_code=404, detail="Customer not found")

@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer: Customer):
    if customer_id in customers:
        customers[customer_id] = customer.dict()
        return {"msg": "Customer updated"}
    else:
        raise HTTPException(status_code=404, detail="Customer not found")

@app.delete("/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: int):
    if customer_id in customers:
        del customers[customer_id]
        return
    else:
        raise HTTPException(status_code=404, detail="Customer not found")
