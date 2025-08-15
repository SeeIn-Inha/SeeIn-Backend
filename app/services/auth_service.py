from app.models.user_model import UserCreate, UserLogin, UserInDB, UserResponse, Token, UserUpdate, UserPasswordUpdate, DeleteResponse
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

def update_user_info(db: Session, email: str, user_update: UserUpdate) -> Optional[UserResponse]:
    """사용자 정보 수정 (닉네임, 이메일)"""
    print(f"사용자 정보 수정 시도: {email}")
    
    try:
        # 현재 사용자 조회
        current_user = get_user_by_email(db, email)
        if not current_user:
            print("사용자를 찾을 수 없음")
            return None
        
        # 이메일 변경이 있는 경우
        if user_update.email and user_update.email != current_user.email:
            if not validate_email(user_update.email):
                print("새 이메일 검증 실패")
                raise ValueError("유효하지 않은 이메일 형식입니다.")
            
            cleaned_new_email = sanitize_email(user_update.email)
            if not cleaned_new_email:
                print("새 이메일 정리 실패")
                raise ValueError("새 이메일을 처리할 수 없습니다.")
            
            # 새 이메일이 이미 사용 중인지 확인
            existing_user = db.query(User).filter(User.email == cleaned_new_email).first()
            if existing_user:
                print("새 이메일이 이미 사용 중")
                raise ValueError("이미 사용 중인 이메일입니다.")
            
            current_user.email = cleaned_new_email
            print(f"이메일 변경: {email} -> {cleaned_new_email}")
        
        # 닉네임 변경이 있는 경우
        if user_update.username is not None:
            current_user.username = user_update.username
            print(f"닉네임 변경: {current_user.username}")
        
        db.commit()
        db.refresh(current_user)
        print("사용자 정보 수정 완료")
        
        return UserResponse(
            email=current_user.email,
            username=current_user.username,
            is_active=current_user.is_active,
            created_at=current_user.created_at
        )
    except Exception as e:
        db.rollback()
        print(f"사용자 정보 수정 오류: {e}")
        raise e

def update_user_password(db: Session, email: str, password_update: UserPasswordUpdate) -> bool:
    """사용자 비밀번호 변경"""
    print(f"비밀번호 변경 시도: {email}")
    
    try:
        # 현재 사용자 조회
        current_user = get_user_by_email(db, email)
        if not current_user:
            print("사용자를 찾을 수 없음")
            return False
        
        # 현재 비밀번호 검증
        if not verify_password(password_update.current_password, current_user.hashed_password):
            print("현재 비밀번호 검증 실패")
            return False
        
        # 새 비밀번호 해싱
        new_hashed_password = hash_password(password_update.new_password)
        current_user.hashed_password = new_hashed_password
        
        db.commit()
        print("비밀번호 변경 완료")
        return True
    except Exception as e:
        db.rollback()
        print(f"비밀번호 변경 오류: {e}")
        return False

def delete_user(db: Session, email: str, password: str) -> bool:
    """사용자 회원 탈퇴"""
    print(f"회원 탈퇴 시도: {email}")
    
    try:
        # 현재 사용자 조회
        current_user = get_user_by_email(db, email)
        if not current_user:
            print("사용자를 찾을 수 없음")
            return False
        
        # 비밀번호 검증
        if not verify_password(password, current_user.hashed_password):
            print("비밀번호 검증 실패")
            return False
        
        # 사용자 삭제 (실제 삭제 또는 비활성화)
        # 보안상 실제 삭제 대신 비활성화하는 것을 권장
        current_user.is_active = False
        # 만약 실제 삭제를 원한다면: db.delete(current_user)
        
        db.commit()
        print("회원 탈퇴 완료")
        return True
    except Exception as e:
        db.rollback()
        print(f"회원 탈퇴 오류: {e}")
        return False
