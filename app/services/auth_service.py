from app.models.user_model import UserCreate, UserLogin, UserInDB, UserResponse, Token
from app.utils.password_utils import hash_password, verify_password
from app.utils.jwt_utils import create_access_token
from app.utils.email_utils import validate_email, sanitize_email
from datetime import datetime
from typing import Optional

fake_user_db = {}

def register_user(user: UserCreate) -> Optional[UserResponse]:
    """사용자 등록"""
    if not validate_email(user.email):
        raise ValueError("유효하지 않은 이메일 형식입니다.")
    
    cleaned_email = sanitize_email(user.email)
    if not cleaned_email:
        raise ValueError("이메일을 처리할 수 없습니다.")
    
    if cleaned_email in fake_user_db:
        return None
    
    try:
        hashed = hash_password(user.password)
        user_in_db = UserInDB(
            email=cleaned_email,
            hashed_password=hashed,
            username=user.username,
            created_at=datetime.utcnow()
        )
        fake_user_db[cleaned_email] = user_in_db
        
        return UserResponse(
            email=user_in_db.email,
            username=user_in_db.username,
            is_active=user_in_db.is_active,
            created_at=user_in_db.created_at
        )
    except Exception as e:
        print(f"사용자 등록 오류: {e}")
        return None

def authenticate_user(user: UserLogin) -> Optional[Token]:
    """사용자 인증"""
    try:
        if not validate_email(user.email):
            return None
        
        cleaned_email = sanitize_email(user.email)
        if not cleaned_email:
            return None
        
        db_user = fake_user_db.get(cleaned_email)
        if not db_user:
            return None
        
        if not verify_password(user.password, db_user.hashed_password):
            return None
        
        access_token = create_access_token({"sub": cleaned_email})
        return Token(access_token=access_token)
    except Exception as e:
        print(f"사용자 인증 오류: {e}")
        return None

def get_user_by_email(email: str) -> Optional[UserInDB]:
    """이메일로 사용자 조회"""
    cleaned_email = sanitize_email(email)
    if not cleaned_email:
        return None
    return fake_user_db.get(cleaned_email)
