from fastapi import APIRouter, HTTPException, status
from app.models.user_model import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import register_user, authenticate_user, get_user_by_email

router = APIRouter(prefix="/auth", tags=["인증"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    """사용자 회원가입"""
    result = register_user(user)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    return result

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """사용자 로그인"""
    result = authenticate_user(user)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )
    return result

@router.get("/me", response_model=UserResponse)
async def get_current_user(email: str):
    """현재 사용자 정보 조회"""
    user = get_user_by_email(email)
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