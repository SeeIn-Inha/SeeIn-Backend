import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_product_recommendation(name: str, brand: str, flavor: str = "") -> str:
    prompt = f"""
당신은 소비자 조언가입니다. 아래 상품에 대해 사용자가 구매를 고민하고 있습니다.
다음 형식을 따라 간단하게 응답해 주세요.

형식:
추천: 살 것 같음 / 사지 말 것 같음
이유: (한문장 간단한 설명)

상품 정보:
- 상품명: {name}
- 브랜드: {brand}
- 특징 또는 요약: {flavor}
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )

        reply = response.choices[0].message.content

        if reply is None or not reply.strip():
            print("[GPT 응답 없음]")
            return "추천 결과를 가져오지 못했습니다."

        print(f"[GPT 추천 결과] {reply.strip()}")
        return reply.strip()

    except Exception as e:
        print(f"[GPT ERROR] {e}")
        raise RuntimeError("AI 추천 요청 중 오류 발생")

#     prompt = f"""
# 당신은 소비 조언 전문가입니다. 아래 상품에 대해 사용자가 구매를 고민하고 있습니다. 건강, 가격, 유사 제품과 비교 등 다양한 관점에서 분석해 간단한 한국어로 구매 추천 여부를 알려주세요. 추천 여부는 "살 것 같음" 또는 "사지 말 것 같음" 중 하나로 말해주고, 이유를 간단히 설명해 주세요.
#
# 상품 정보:
# - 상품명: {name}
# - 브랜드: {brand}
# - 맛: {flavor}
# """
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    return response.choices[0].message.content
