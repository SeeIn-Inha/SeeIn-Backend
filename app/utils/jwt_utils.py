from datetime import datetime, timedelta
import os

try:
    from jose import JWTError, jwt
    from dotenv import load_dotenv
    load_dotenv()
    JOSE_AVAILABLE = True
except ImportError:
    JWTError = None
    jwt = None
    JOSE_AVAILABLE = False

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "seein_secret")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))

def create_access_token(data: dict) -> str:
    if not JOSE_AVAILABLE:
        raise ImportError("python-jose 패키지가 필요합니다. pip install python-jose[cryptography]를 실행해주세요.")
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    if not JOSE_AVAILABLE:
        raise ImportError("python-jose 패키지가 필요합니다. pip install python-jose[cryptography]를 실행해주세요.")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def check_dependencies() -> dict:
    status = {
        "python-jose": JOSE_AVAILABLE,
        "cryptography": JOSE_AVAILABLE
    }
    
    if not JOSE_AVAILABLE:
        print("python-jose 패키지가 설치되지 않았습니다.")
        print("pip install python-jose[cryptography]를 실행해주세요.")
    else:
        print("python-jose 패키지가 정상적으로 설치되어 있습니다.")
    
    return status