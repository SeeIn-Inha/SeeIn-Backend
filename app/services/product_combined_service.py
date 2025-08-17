
import openai
import os
import base64
import io
import json
import re
from PIL import Image
from fastapi import UploadFile
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


async def analyze_and_recommend(file: UploadFile) -> dict:
    try:
        # 이미지 파일 → JPEG 변환
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        jpeg_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(jpeg_bytes).decode("utf-8")

        # GPT Vision으로 상품 정보 분석 요청
        vision_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "이 이미지 속 문구를 바탕으로 상품명과 브랜드를 추출해서 한국어로 JSON 형태로 알려줘. 상품에 대한 간단한 요약 설명도 덧붙여줘. 예시: {\"상품명\": \"진라면\", \"브랜드\": \"오뚜기\", \"요약\": \"매운맛 라면입니다.\"}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=800
        )

        product_json = vision_response.choices[0].message.content.strip()

        # ```json ... ``` 제거
        product_json_cleaned = re.sub(r"```json|```", "", product_json).strip()

        try:
            product_info = json.loads(product_json_cleaned)
        except Exception as e:
            return {
                "success": False,
                "error": "상품 정보 JSON 파싱 실패",
                "raw": product_json,
                "parsed_attempt": product_json_cleaned
            }

        name = product_info.get("상품명", "")
        brand = product_info.get("브랜드", "")
        summary = product_info.get("요약", "")

        if not name or not brand:
            return {
                "success": False,
                "error": "상품명 또는 브랜드 추출 실패",
                "raw": product_info
            }

        # 추천 요청 프롬프트 구성
        prompt = f"""
당신은 소비 조언 전문가입니다. 아래 상품에 대해 사용자가 구매를 고민하고 있습니다. 건강, 가격, 유사 제품과 비교 등 다양한 관점에서 분석해 간단한 한국어로 구매 추천 여부를 알려주세요.  
추천 여부는 "추천: 살 것 같음" 또는 "추천: 사지 말 것 같음" 중 하나로 시작하고, 이유는 짧게 설명해 주세요.  

상품 정보:
- 상품명: {name}
- 브랜드: {brand}
- 요약: {summary}
"""

        recommend_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )

        recommendation = recommend_response.choices[0].message.content.strip()

        return {
            "success": True,
            "product": {
                "name": name,
                "brand": brand,
                "summary": summary
            },
            "recommendation": recommendation
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
