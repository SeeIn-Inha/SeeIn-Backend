# your_project/main.py

import uuid
import os
import shutil
import json

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

#상품분석라우터
from app.routers import product_router
 


# .env 파일 로드 (이곳이 유일한 load_dotenv 호출 지점)
# load_dotenv() # 기존 라인 (삭제 또는 주석 처리)
load_dotenv(dotenv_path='.env')  # <--- 이 라인으로 변경합니다.

# 환경 변수에서 API 키 로드 (main.py에서 직접 로드)
CLOVA_OCR_URL = os.getenv("CLOVA_OCR_URL")
CLOVA_OCR_SECRET = os.getenv("CLOVA_OCR_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# API 키들이 제대로 로드되었는지 확인 (앱 시작 전 필수 점검)
if not all([CLOVA_OCR_URL, CLOVA_OCR_SECRET, OPENAI_API_KEY]):
    print("FATAL ERROR: 필수 API 키(CLOVA_OCR_URL, CLOVA_OCR_SECRET, OPENAI_API_KEY)가 .env 파일에 설정되지 않았습니다.")
    print("FastAPI 애플리케이션 시작을 중단합니다.")
    raise ValueError("필수 API 키가 .env 파일에 설정되지 않았습니다.")

# services 폴더에서 receipt_analyzer 모듈 임포트
# 프로젝트 구조에 따라 'app.services'로 임포트합니다.
from app.services.receipt_analyzer import call_clova_ocr, extract_texts_from_clova, extract_receipt_info_with_gpt

# FastAPI 앱 인스턴스 생성
app = FastAPI()


#상품분석 라우터
app.include_router(product_router.router)


# 임시 파일 저장을 위한 디렉토리 설정
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def read_root():
    return {"message": "SeeIn Backend API - Welcome!"}


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