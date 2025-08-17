from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.test_receipt_analyze import call_clova, extract_text, analyze_receipt
import os
from dotenv import load_dotenv

# main.py 에서 라우터 등록해야 합니다

router = APIRouter()
load_dotenv()

CLOVA_OCR_URL = os.getenv("CLOVA_OCR_URL")
CLOVA_OCR_SECRET = os.getenv("CLOVA_OCR_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@router.post("/analyze-receipt/")
async def test_analyze_receipt(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        print(image.content_type)
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드")
    
    contents = await image.read()
    clova_res = await call_clova(contents, CLOVA_OCR_SECRET, CLOVA_OCR_URL)
    if clova_res == None:
        print("CLOVA 텍스트 추출 에러 발생으로 진행 불가")
        return
    
    extracted_text = extract_text(clova_res)

    result = await analyze_receipt(extracted_text, OPENAI_API_KEY)
    if result == None:
        print("OPEN AI 텍스트 분석 에러 발생으로 진행 불가")
        return
    
    return result