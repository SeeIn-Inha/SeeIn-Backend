from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str
    username: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserInDB(BaseModel):
    email: str
    hashed_password: str
    username: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

class UserResponse(BaseModel):
    email: str
    username: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None