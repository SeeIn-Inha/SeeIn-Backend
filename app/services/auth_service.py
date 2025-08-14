from app.models.user_model import UserCreate, UserLogin, UserInDB, UserResponse, Token
from app.models.database_models import User
from app.utils.password_utils import hash_password, verify_password
from app.utils.jwt_utils import create_access_token
from app.utils.email_utils import validate_email, sanitize_email
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

def register_user(db: Session, user: UserCreate) -> Optional[UserResponse]:
    """사용자 등록"""
    print(f"회원가입 시도: {user.email}")
    
    if not validate_email(user.email):
        print("이메일 검증 실패")
        raise ValueError("유효하지 않은 이메일 형식입니다.")
    
    cleaned_email = sanitize_email(user.email)
    if not cleaned_email:
        print("이메일 정리 실패")
        raise ValueError("이메일을 처리할 수 없습니다.")
    
    # 기존 사용자 확인
    existing_user = db.query(User).filter(User.email == cleaned_email).first()
    if existing_user:
        print("이미 존재하는 사용자")
        return None
    
    try:
        hashed = hash_password(user.password)
        print(f"비밀번호 해싱 성공: {hashed[:20]}...")
        
        # 데이터베이스에 사용자 저장
        db_user = User(
            email=cleaned_email,
            hashed_password=hashed,
            username=user.username
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        print(f"사용자 저장 완료: {cleaned_email}")
        
        return UserResponse(
            email=db_user.email,
            username=db_user.username,
            is_active=db_user.is_active,
            created_at=db_user.created_at
        )
    except Exception as e:
        db.rollback()
        print(f"사용자 등록 오류: {e}")
        return None

def authenticate_user(db: Session, user: UserLogin) -> Optional[Token]:
    """사용자 인증"""
    print(f"로그인 시도: {user.email}")
    
    try:
        if not validate_email(user.email):
            print("이메일 검증 실패")
            return None
        
        cleaned_email = sanitize_email(user.email)
        if not cleaned_email:
            print("이메일 정리 실패")
            return None
        
        print(f"정리된 이메일: {cleaned_email}")
        
        # 데이터베이스에서 사용자 조회
        db_user = db.query(User).filter(User.email == cleaned_email).first()
        if not db_user:
            print("사용자를 찾을 수 없음")
            return None
        
        print("사용자 찾음, 비밀번호 검증 중...")
        if not verify_password(user.password, db_user.hashed_password):
            print("비밀번호 검증 실패")
            return None
        
        print("비밀번호 검증 성공, 토큰 생성 중...")
        token_data = {"sub": cleaned_email}
        print(f"토큰 데이터: {token_data}")
        access_token = create_access_token(token_data)
        print(f"토큰 생성 성공: {access_token[:50]}...")
        
        return Token(access_token=access_token)
    except Exception as e:
        print(f"사용자 인증 오류: {e}")
        return None

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """이메일로 사용자 조회"""
    cleaned_email = sanitize_email(email)
    if not cleaned_email:
        return None
    return db.query(User).filter(User.email == cleaned_email).first()
