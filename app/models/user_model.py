from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime

try:
    from pydantic import EmailStr
    EMAIL_STR_AVAILABLE = True
except ImportError:
    EmailStr = str
    EMAIL_STR_AVAILABLE = False

EmailType = Union[EmailStr, str] if EMAIL_STR_AVAILABLE else str

class UserCreate(BaseModel):
    email: EmailType
    password: str
    username: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailType
    password: str

class UserInDB(BaseModel):
    email: EmailType
    hashed_password: str
    username: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

class UserResponse(BaseModel):
    email: EmailType
    username: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None