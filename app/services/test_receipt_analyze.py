import requests
import uuid
import time
import json
import openai

async def call_clova(contents: bytes, secret_key: str, api_url: str):
    if contents == None:
        print("[call_clova] : 이미지 없음")
        return
    
    if not secret_key or not api_url :
        print("[call_clova] : OCR SECRET KEY 또는 API_URL 부재")
        return
    
    request_json = {
        'images': [{'format': 'jpg', 'name': 'receipt_image'}],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }
    try:
        headers = {'X-OCR-SECRET': secret_key}
        payload = {'message': json.dumps(request_json)}
        files = [('file', contents)]

        res = requests.post(api_url, headers=headers, data=payload, files=files)

        print(f"응답 상태: {res.status_code}")
        print(f"텍스트 내용: {res.text}")

    except requests.exceptions.RequestException as e:
        print(f"[call_clova] - CLOVA 호출 중 네트워크 에러: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"[call_clova] - CLOVA Json 파싱 에러: {e}")
        return None
    except OSError as e:
        print(f"[call_clova] - 파일 처리 오류: {e}")
        return None
    except Exception as e:
        print(f"[call_clova] - 기타 에러: {e}")
        return None
    
    if not 'images' in res.json():
        print("image tag is not exists")
        return
    
    return res.json()

def extract_text(clova_json):
    texts = []
    if clova_json:
        for image in clova_json['images']:
            for field in image.get('fields', []):
                texts.append(field['inferText'])

    return ' '.join(texts)

async def analyze_receipt(text_data: str, open_ai_key: str):
    if not open_ai_key:
        print("[analyze_receipt] : API KEY 전달 받지 못함")
        return

    client = openai.OpenAI(api_key=open_ai_key)

    prompt = f"""
    다음은 영수증에서 OCR로 추출된 텍스트입니다.
    이 텍스트에서 다음 정보를 추출하여 **반드시 JSON 형식으로** 반환해주세요.
    정보를 찾을 수 없는 경우 해당 필드는 **null**로 처리해주세요.

    필요한 정보는 다음과 같습니다:
    - **구매처 (store_name)**: 영수증 발행 상점의 이름
    - **결제 날짜 (transaction_date)**: 거래가 발생한 날짜 (YYYY-MM-DD 형식)
    - **결제 시간 (transaction_time)**: 거래가 발생한 시간 (HH:MM 형식)
    - **총 결제 금액 (total_amount)**: 최종 결제된 금액 (숫자만, 소수점 가능)
    - **결제 항목 (items)**: 구매한 각 항목의 목록. 각 항목은 다음을 포함합니다:
        - **이름 (name)**: 상품 또는 서비스의 이름
        - **가격 (price)**: 해당 항목의 단가 또는 총 가격 (숫자만)
        - **수량 (quantity)**: 해당 항목의 수량 (숫자만). 수량이 불분명하면 1로 가정.
    - **결제 수단 (payment_method)**: 사용된 결제 방식 (예: 신용카드, 현금, 페이, 상품권 등)

    예시 JSON 형식:
    {{
        "구매처": "ABC 마트",
        "결제 날짜": "2024-07-20",
        "결제 시간": "15:30",
        "총 결재 금액": 25500.0,
        "결제 항목": [
            {{"name": "바나나", "price": 3000.0, "quantity": 2}},
            {{"name": "사과", "price": 5000.0, "quantity": 1}}
        ],
        "결제 수단": "신용카드"
    }}

    영수증 텍스트:
    {text_data}
    """

    try:
        res = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a highly accurate assistant specialized in extracting structured information from receipt texts. Always respond in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={'type': 'json_object'},
            max_tokens=1500
        )

        return json.loads(res.choices[0].message.content)

    except openai.APIError as e:
        print(f"[APIError] - OPEN AI 호출 에러 발생 : {e}")
        return None
    
    except json.JSONDecodeError as e:
        print(f"[JSONDecodeError] - OPEN AI JSON Parsing 에러 발생 : {e}")
        return None

    except Exception as e:
        print(f"[Exception] - 기타 에러 발생 : {e}")
        return None