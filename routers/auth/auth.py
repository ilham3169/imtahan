from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import jwt
from datetime import datetime, timedelta

from database import sessionLocal
from models import User
from schemas import UserCreate, UserLogin, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "your-secret-key" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str, db: db_dependency):
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: username not found")
        
        # Fetch the user from the database
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Create user
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user: UserCreate):
    user_email = db.query(User).filter(User.email == create_user.email).first()
    if user_email:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    user_username = db.query(User).filter(User.username == create_user.username).first()
    if user_username:
        raise HTTPException(status_code=400, detail="User with this username already exists")

    create_user_model = User(
        first_name=create_user.first_name,
        last_name=create_user.last_name,
        email=create_user.email,
        is_admin=create_user.is_admin,
        password=create_user.password,
        result=create_user.result,
        username=create_user.username
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    
    return {"message": "User created successfully", "user_id": create_user_model.id}

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(db: db_dependency, login_data: UserLogin):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or user.password != login_data.password:  # Plain text comparison
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},  
        expires_delta=access_token_expires
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "is_admin": user.is_admin,
            "result": user.result
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: User = Depends(get_current_user)):
    return user