from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routers import auth_router, protected_router, stt_router
from app.core.init_db import init_db       

app = FastAPI(
    title="SeeIn Backend API",
    description="JWT 기반 인증과 STT 기능을 제공하는 API",
    version="1.0.0"
)

# 애플리케이션 시작 시 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    init_db()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth_router.router)
app.include_router(protected_router.router)
app.include_router(stt_router.router)

@app.get("/")
def root():
    return {
        "message": "SeeIn Backend API",
        "version": "1.0.0",
        "features": ["JWT Authentication", "STT (Speech Recognition)"]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/debug/jwt")
def debug_jwt():
    """JWT 설정 디버깅 정보"""
    from app.utils.jwt_utils import SECRET_KEY, ALGORITHM, EXPIRE_MINUTES, check_dependencies
    return {
        "SECRET_KEY": SECRET_KEY[:10] + "..." if len(SECRET_KEY) > 10 else SECRET_KEY,
        "ALGORITHM": ALGORITHM,
        "EXPIRE_MINUTES": EXPIRE_MINUTES,
        "dependencies": check_dependencies()
    }


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # 인증이 필요하지 않은 엔드포인트들
    public_endpoints = [
        "/",
        "/health",
        "/auth/register",
        "/auth/login"
    ]
    
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method in ["get", "post", "put", "delete", "patch"]:
                # 공개 엔드포인트가 아닌 경우에만 보안 적용
                if path not in public_endpoints:
                    openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi_schema = custom_openapi()