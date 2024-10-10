from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pydantic import BaseModel, EmailStr
from typing import Dict
from fastapi.security import OAuth2PasswordBearer
from Middleware.authentication import get_current_user  

app = FastAPI()
router = APIRouter()

# In-memory store for customers
customers: Dict[int, Dict] = {}
next_customer_id = 1

class Customer(BaseModel):
    name: str
    email: EmailStr  

# OAuth2 scheme for getting the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Get current user and check role
async def get_current_user_and_role(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    return user  # This user object should include the 'role' attribute

# Customer Management Endpoints
@app.post("/customers", status_code=201)
async def create_customer(customer: Customer, current_user: dict = Depends(get_current_user_and_role)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    global next_customer_id
    customer_id = next_customer_id
    customers[customer_id] = customer.dict()
    next_customer_id += 1
    return {"customer_id": customer_id}

@app.get("/customers/{customer_id}")
async def get_customer(customer_id: int, current_user: dict = Depends(get_current_user_and_role)):
    if customer_id in customers:
        return customers[customer_id]
    else:
        raise HTTPException(status_code=404, detail="Customer not found")

@app.put("/customers/{customer_id}")
async def update_customer(customer_id: int, customer: Customer, current_user: dict = Depends(get_current_user_and_role)):
    if current_user['role'] != 'admin' and current_user['username'] != customers[customer_id]['email']:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    if customer_id in customers:
        customers[customer_id] = customer.dict()
        return {"msg": "Customer updated"}
    else:
        raise HTTPException(status_code=404, detail="Customer not found")

@app.delete("/customers/{customer_id}", status_code=204)
async def delete_customer(customer_id: int, current_user: dict = Depends(get_current_user_and_role)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not enough privileges")

    if customer_id in customers:
        del customers[customer_id]
        return
    else:
        raise HTTPException(status_code=404, detail="Customer not found")

# Include the router to the app
app.include_router(router)
