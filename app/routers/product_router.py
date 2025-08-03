from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.product_analysis_service import analyze_product_image

router = APIRouter()


@router.post("/analyze-product/")
async def analyze_product(file: UploadFile = File(...)):
    """
    상품 이미지 분석 (GPT Vision 사용)
    """
    result = await analyze_product_image(file)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return result
