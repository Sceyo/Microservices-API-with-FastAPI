from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import logging


fake_users_db = {
    "admin_user": {
        "username": "admin_user",
        "hashed_password": CryptContext(schemes=["bcrypt"], deprecated="auto").hash("admin_password"),
        "role": "admin"
    },
    "regular_user": {
        "username": "regular_user",
        "hashed_password": CryptContext(schemes=["bcrypt"], deprecated="auto").hash("user_password"),
        "role": "user"
    }
}

# Security scheme for OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key and algorithm
SECRET_KEY = "RajahHumabon"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Function to create a new access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to authenticate user
def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not CryptContext(schemes=["bcrypt"], deprecated="auto").verify(password, user['hashed_password']):
        return False
    return user 

# Dependency to get the current user
import logging

logger = logging.getLogger("my_logger")
logging.basicConfig(level=logging.INFO)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")  
        
        # Log the payload for debugging
        logger.info(f"Decoded payload: {payload}")
        
        # Check if username or role is None
        if username is None or role is None:
            logger.warning("Username or role is None.")
            raise credentials_exception
            
    except JWTError:
        logger.error("JWT Error: Could not decode token.")
        raise credentials_exception

    # Check if the user exists in the fake_users_db
    user = fake_users_db.get(username)
    if user is None:
        logger.error(f"User not found: {username}")
        raise credentials_exception

    logger.info(f"User authenticated: {username} with role {role}")
    return {"username": username, "role": role}

# Initialize the router
router = APIRouter()

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user['username'], "role": user['role']})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/admin-only")
async def admin_only_route(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return {"msg": "Welcome, Admin!"}
