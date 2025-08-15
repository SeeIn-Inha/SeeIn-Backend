from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.user_model import UserCreate, UserLogin, UserResponse, Token, UserUpdate, UserPasswordUpdate, DeleteResponse, UserDelete
from app.services.auth_service import register_user, authenticate_user, get_user_by_email, update_user_info, update_user_password, delete_user
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



@router.put("/update", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 정보 수정 (닉네임, 이메일) - 인증 필요"""
    try:
        result = update_user_info(db, current_user_email, user_update)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 정보 수정 중 오류가 발생했습니다."
        )

@router.put("/change-password")
async def change_password(
    password_update: UserPasswordUpdate,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """비밀번호 변경 - 인증 필요"""
    success = update_user_password(db, current_user_email, password_update)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 올바르지 않거나 사용자를 찾을 수 없습니다."
        )
    
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}

@router.delete("/delete", response_model=DeleteResponse)
async def delete_user_account(
    user_delete: UserDelete,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """회원 탈퇴 - 인증 필요"""
    success = delete_user(db, current_user_email, user_delete.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호가 올바르지 않거나 사용자를 찾을 수 없습니다."
        )
    
    return DeleteResponse(message="회원 탈퇴가 완료되었습니다.") 