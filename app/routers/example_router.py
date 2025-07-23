"""
이 모듈은 API 라우터(엔드포인트)를 정의합니다.
예시:
- 상품 요약 API 엔드포인트
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
async def example_route():
    return {"message": "테스트"}
