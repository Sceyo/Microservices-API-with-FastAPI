from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, constr
import uvicorn
from slowapi import Limiter
from slowapi.util import get_remote_address
from prometheus_fastapi_instrumentator import Instrumentator  # Import this

# Create a Limiter instance
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter

# Initialize the Prometheus Instrumentator
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)  # Ensure metrics are exposed

# Step 6: Input Validation and Sanitization
class UserInput(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: str
    password: constr(min_length=8)

@app.post("/register/")
@limiter.limit("5/minute")  # Limit to 5 requests per minute for registration
async def register(user_input: UserInput, request: Request):
    return {"message": "User registered successfully", "user": user_input}

@app.get("/")
@limiter.limit("5/minute")  # Limit to 5 requests per minute for the root endpoint
async def root(request: Request):
    return {"message": "Hello, John Rey!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile="certs/private.key", ssl_certfile="certs/certificate.crt")
