import openai
from fastapi import UploadFile
import io
import os
import base64
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

async def analyze_product_image(file: UploadFile) -> dict:
    try:
        # 이미지 바이트 읽기
        image_bytes = await file.read()

        # Pillow로 이미지 열기
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")  # JPEG을 위해 RGB로 변환
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        jpeg_bytes = buffer.getvalue()

        # base64 인코딩
        image_base64 = base64.b64encode(jpeg_bytes).decode("utf-8")

        # GPT API 요청
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "이 이미지 속 문구를 바탕으로 상품명과 브랜드를 추출해서 한국어로 JSON 형태로 알려줘. "
                                "상품에 대한 간단한 요약 설명도 덧붙여줘. "
                                "예시: {\"상품명\": \"진라면\", \"브랜드\": \"오뚜기\", \"요약\": \"매운맛 라면입니다.\"}"
                            )
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

        content = response.choices[0].message.content
        return {"success": True, "result": content}

    except Exception as e:
        return {"success": False, "error": str(e)}
