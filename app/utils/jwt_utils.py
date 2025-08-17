from datetime import datetime, timedelta
import os
import secrets

try:
    from jose import JWTError, jwt  # type: ignore
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
    JOSE_AVAILABLE = True
except ImportError:
    JWTError = None
    jwt = None
    JOSE_AVAILABLE = False

try:
    from fastapi import Depends, HTTPException, status
    from fastapi.security import OAuth2PasswordBearer
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# 더 안전한 기본 SECRET_KEY 생성
DEFAULT_SECRET_KEY = "seein_development_secret_key_2024"
SECRET_KEY = os.getenv("JWT_SECRET_KEY", DEFAULT_SECRET_KEY)
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

print(f"JWT 설정 로드됨 - SECRET_KEY: {SECRET_KEY[:10]}..., ALGORITHM: {ALGORITHM}, EXPIRE_MINUTES: {EXPIRE_MINUTES}")

if FASTAPI_AVAILABLE:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def create_access_token(data: dict) -> str:
    if not JOSE_AVAILABLE:
        raise ImportError("python-jose 패키지가 필요합니다. pip install python-jose[cryptography]를 실행해주세요.")
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    print(f"토큰 생성 데이터: {to_encode}")
    print(f"SECRET_KEY: {SECRET_KEY[:10]}...")
    print(f"ALGORITHM: {ALGORITHM}")
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"토큰 생성 완료: {encoded_jwt[:50]}...")
    
    return encoded_jwt

def verify_access_token(token: str):
    if not JOSE_AVAILABLE:
        raise ImportError("python-jose 패키지가 필요합니다. pip install python-jose[cryptography]를 실행해주세요.")
    
    try:
        print(f"토큰 디코딩 시도: {token[:20]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"토큰 디코딩 성공: {payload}")
        return payload
    except JWTError as e:
        print(f"토큰 디코딩 실패: {e}")
        return None
    except Exception as e:
        print(f"토큰 검증 중 예상치 못한 오류: {e}")
        return None

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI가 필요합니다.")
    
    print(f"토큰 검증 시작: {token[:20] if token else 'None'}...")
    
    if not token:
        print("토큰이 없습니다.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_access_token(token)
    if payload is None:
        print("토큰 검증 실패")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 정보입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    if not email:
        print("토큰에 이메일 정보가 없습니다.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에 사용자 정보가 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"토큰 검증 성공: {email}")
    return email

def check_dependencies() -> dict:
    status = {
        "python-jose": JOSE_AVAILABLE,
        "cryptography": JOSE_AVAILABLE,
        "fastapi": FASTAPI_AVAILABLE
    }
    
    if not JOSE_AVAILABLE:
        print("python-jose 패키지가 설치되지 않았습니다.")
        print("pip install python-jose[cryptography]를 실행해주세요.")
    else:
        print("python-jose 패키지가 정상적으로 설치되어 있습니다.")
    
    if not FASTAPI_AVAILABLE:
        print("FastAPI 패키지가 설치되지 않았습니다.")
    else:
        print("FastAPI 패키지가 정상적으로 설치되어 있습니다.")
    
    return status