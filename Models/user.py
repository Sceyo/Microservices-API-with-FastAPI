from pydantic import BaseModel
from passlib.context import CryptContext

# User model for registration
class User(BaseModel):
    username: str
    password: str
    role: str  

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to verify passwords
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to get hashed password
def get_password_hash(password):
    return pwd_context.hash(password)

# In-memory user database with hashed passwords
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrator",
        "hashed_password": get_password_hash("puffdaddy"),  # Store hashed password
        "role": "admin",
    },
    "customer": {
        "username": "customer",
        "full_name": "Lemar Odom",
        "hashed_password": get_password_hash("Lakers"),  # Store hashed password
        "role": "customer",
    },
}

# function to register a new user 
def register_user(username: str, password: str, role: str):
    if username in fake_users_db:
        raise ValueError("Username already exists")
    
    hashed_password = get_password_hash(password)
    fake_users_db[username] = {
        "username": username,
        "full_name": username.capitalize(), 
        "hashed_password": hashed_password,
        "role": role,
}


