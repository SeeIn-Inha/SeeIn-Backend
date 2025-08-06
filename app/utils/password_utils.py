try:
    from passlib.context import CryptContext  # type: ignore
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    PASSLIB_AVAILABLE = True
except ImportError:
    pwd_context = None
    PASSLIB_AVAILABLE = False

def hash_password(password: str) -> str:
    if not PASSLIB_AVAILABLE:
        raise ImportError("passlib 패키지가 필요합니다. pip install passlib[bcrypt]를 실행해주세요.")
    
    if not password:
        raise ValueError("비밀번호는 비어있을 수 없습니다.")
    
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not PASSLIB_AVAILABLE:
        raise ImportError("passlib 패키지가 필요합니다. pip install passlib[bcrypt]를 실행해주세요.")
    
    if not plain_password or not hashed_password:
        return False
    
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def check_dependencies() -> dict:
    status = {
        "passlib": PASSLIB_AVAILABLE,
        "bcrypt": PASSLIB_AVAILABLE
    }
    
    if not PASSLIB_AVAILABLE:
        print("passlib 패키지가 설치되지 않았습니다.")
        print("pip install passlib[bcrypt]를 실행해주세요.")
    else:
        print("passlib 패키지가 정상적으로 설치되어 있습니다.")
    
    return status
