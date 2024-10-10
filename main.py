

from fastapi import FastAPI
from Routers import products
from Routers import orders
from Routers import customers
from Middleware import authentication
app = FastAPI()

app.include_router(authentication.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(customers.router)
