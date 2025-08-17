# /main.py

import uuid
import os
import shutil
import json

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv

from app.routers import auth_router, protected_router, stt_router, product_router
from app.core.init_db import init_db
from app.services.receipt_analyzer import call_clova_ocr, extract_texts_from_clova, extract_receipt_info_with_gpt


# .env 파일 로드
load_dotenv(dotenv_path='.env')

# 환경 변수에서 API 키 로드
CLOVA_OCR_URL = os.getenv("CLOVA_OCR_URL")
CLOVA_OCR_SECRET = os.getenv("CLOVA_OCR_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# API 키들이 제대로 로드되었는지 확인
if not all([CLOVA_OCR_URL, CLOVA_OCR_SECRET, OPENAI_API_KEY]):
    print("FATAL ERROR: 필수 API 키(CLOVA_OCR_URL, CLOVA_OCR_SECRET, OPENAI_API_KEY)가 .env 파일에 설정되지 않았습니다.")
    print("FastAPI 애플리케이션 시작을 중단합니다.")
    raise ValueError("필수 API 키가 .env 파일에 설정되지 않았습니다.")


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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth_router.router)
app.include_router(protected_router.router)
app.include_router(stt_router.router)
app.include_router(product_router.router)

# 임시 파일 저장을 위한 디렉토리 설정
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
                if path not in public_endpoints:
                    openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi_schema = custom_openapi()

@app.post("/analyze-receipt/")
async def analyze_receipt_endpoint(image: UploadFile = File(...)):
    """
    영수증 이미지를 받아 클로바 OCR과 OpenAI GPT를 사용하여 정보를 분석합니다.
    """
    allowed_extensions = {"jpg", "jpeg", "png"}
    file_extension = image.filename.split(".")[-1].lower() if image.filename else ""
    if not file_extension or file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="허용되지 않는 이미지 형식입니다. (jpg, jpeg, png만 허용)")

    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    temp_image_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        print(f"INFO: 이미지 파일이 임시 저장되었습니다: {temp_image_path}")

        print("INFO: 클로바 OCR API 호출 중...")
        ocr_result = call_clova_ocr(temp_image_path, CLOVA_OCR_URL, CLOVA_OCR_SECRET)

        if not ocr_result:
            print("ERROR: OCR 처리 중 오류 발생: 클로바 OCR 응답 없음 또는 오류 발생.")
            raise HTTPException(status_code=500, detail="영수증 OCR 처리 중 오류가 발생했습니다.")

        ocr_text = extract_texts_from_clova(ocr_result)
        print("INFO: OCR 텍스트 추출 완료.")

        print("INFO: OpenAI GPT로 영수증 정보 추출 중...")
        receipt_info = extract_receipt_info_with_gpt(ocr_text, OPENAI_API_KEY)

        if not receipt_info:
            print("ERROR: GPT를 통한 영수증 정보 추출 실패.")
            raise HTTPException(status_code=500, detail="영수증 정보 추출 중 오류가 발생했습니다. (GPT 응답 문제)")

        print("INFO: 영수증 정보 추출 완료.")

        return JSONResponse(content=receipt_info)

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"FATAL: 서버 내부 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"서버 내부 오류 발생: {type(e).__name__}")
    finally:
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
            print(f"INFO: 임시 파일 삭제 완료: {temp_image_path}")