from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.product_analysis_service import analyze_product_image
from app.services.product_recommendation_service import generate_product_recommendation
from pydantic import BaseModel

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


class ProductInfo(BaseModel):
    name: str
    brand: str
    summary: str = ""


@router.post("/recommend-product/")
def recommend_product(product: ProductInfo):
    try:
        result = generate_product_recommendation(
            name=product.name,
            brand=product.brand,
            flavor=product.summary  # 혹은 summary 그대로 넘겨도 OK
        )
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
