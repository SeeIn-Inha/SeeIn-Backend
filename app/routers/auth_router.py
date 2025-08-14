from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.user_model import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import register_user, authenticate_user, get_user_by_email
from app.utils.jwt_utils import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["인증"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """사용자 회원가입"""
    result = register_user(db, user)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    return result

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """사용자 로그인"""
    result = authenticate_user(db, user)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )
    return result

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자 정보 조회 (인증 필요)"""
    user = get_user_by_email(db, current_user_email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    return UserResponse(
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        created_at=user.created_at
    )

@router.get("/profile/{email}", response_model=UserResponse)
async def get_user_profile(email: str, db: Session = Depends(get_db)):
    """사용자 프로필 조회 (인증 불필요)"""
    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    return UserResponse(
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        created_at=user.created_at
    ) 