from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth_router, protected_router

app = FastAPI(
    title="SeeIn Backend API",
    description="JWT 기반 인증과 STT 기능을 제공하는 API",
    version="1.0.0"
)

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
