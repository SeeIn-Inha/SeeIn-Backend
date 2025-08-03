from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.product_analysis_service import analyze_product_image
from app.services.product_recommendation_service import generate_product_recommendation
from pydantic import BaseModel
from app.services.product_combined_service import analyze_and_recommend

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
async def recommend_product(product: ProductInfo):
    try:
        print(f"[RECOMMEND] 입력 상품 - 이름: {product.name}, 브랜드: {product.brand}, 요약: {product.summary}")

        result = generate_product_recommendation(
            name=product.name,
            brand=product.brand,
            flavor=product.summary
        )

        if result and result.strip():
            return {"success": True, "result": result.strip()}
        else:
            return {"success": False, "error": "추천 응답이 비어 있습니다."}

    except Exception as e:
        print(f"[RECOMMEND ERROR] {e}")
        return {"success": False, "error": str(e)}

#
# @router.post("/recommend-product/")
# def recommend_product(product: ProductInfo):
#     try:
#         result = generate_product_recommendation(
#             name=product.name,
#             brand=product.brand,
#             flavor=product.summary  # 혹은 summary 그대로 넘겨도 OK
#         )
#         return {"success": True, "result": result}
#     except Exception as e:
#         return {"success": False, "error": str(e)}



@router.post("/analyze-and-recommend-product/")
async def analyze_and_recommend_product(file: UploadFile = File(...)):
    result = await analyze_and_recommend(file)
    return result