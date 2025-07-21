# your_project/services/receipt_analyzer.py

import requests
import uuid
import time
import json
import os
import openai

# --- [1] CLOVA OCR API 호출 ---
# API URL과 SECRET KEY를 함수 인자로 받도록 변경
def call_clova_ocr(image_path: str, api_url: str, secret_key: str) -> dict | None:
    """
    클로바 OCR API를 호출하여 영수증 이미지에서 텍스트를 추출합니다.

    Args:
        image_path (str): 분석할 영수증 이미지의 파일 경로.
        api_url (str): 클로바 OCR Invoke URL.
        secret_key (str): 클로바 OCR Secret Key.

    Returns:
        dict | None: OCR API 응답 JSON (성공 시) 또는 None (실패 시).
    """
    if not api_url or not secret_key:
        print("❗ DEBUG: [receipt_analyzer.py] 클로바 OCR API URL 또는 Secret Key가 함수 인자로 전달되지 않았습니다.")
        return None

    request_json = {
        'images': [{'format': 'jpg', 'name': 'receipt_image'}], # 이미지 형식 확인 (jpg, png 등)
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    try:
        # 이미지 파일이 실제로 존재하는지 확인하는 디버깅 코드 추가
        if not os.path.exists(image_path):
            print(f"❗ DEBUG: [receipt_analyzer.py] 이미지 파일이 존재하지 않습니다: {image_path}")
            return None

        with open(image_path, 'rb') as f:
            files = [('file', f)]
            headers = {'X-OCR-SECRET': secret_key} # secret_key 인자 사용
            payload = {'message': json.dumps(request_json)}

            print(f"DEBUG: [receipt_analyzer.py] 클로바 OCR API URL: {api_url}")
            # 보안을 위해 Secret Key는 앞부분만 출력
            print(f"DEBUG: [receipt_analyzer.py] 클로바 OCR Secret Key (일부): {secret_key[:5]}...")
            print(f"DEBUG: [receipt_analyzer.py] 이미지 파일 경로: {image_path}")
            print(f"DEBUG: [receipt_analyzer.py] 클로바 OCR API로 요청 전송 시도...")

            response = requests.post(api_url, headers=headers, data=payload, files=files)

            # --- 핵심 디버깅 부분 ---
            print(f"DEBUG: [receipt_analyzer.py] 클로바 OCR API 응답 상태 코드: {response.status_code}")
            print(f"DEBUG: [receipt_analyzer.py] 클로바 OCR API 응답 내용: {response.text}") # 응답 전체를 출력하여 자세한 오류 확인
            # --- 여기까지 ---

        response.raise_for_status() # HTTP 4xx/5xx 에러 발생 시 여기서 예외 발생

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"❗ [receipt_analyzer.py] 클로바 OCR API 호출 중 네트워크 또는 요청 관련 오류 발생: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❗ [receipt_analyzer.py] 클로바 OCR API 응답 JSON 파싱 중 오류 발생: {e}")
        print(f"응답 내용: {response.text}") # 파싱 실패 시 원본 응답 다시 출력
        return None
    except Exception as e:
        print(f"❗ [receipt_analyzer.py] OCR 처리 중 예상치 못한 오류 발생: {type(e).__name__}: {e}")
        return None

# --- [2] OCR 텍스트 추출 ---
def extract_texts_from_clova(ocr_json: dict | None) -> str:
    """
    클로바 OCR JSON 응답에서 모든 추출된 텍스트를 하나의 문자열로 결합합니다.

    Args:
        ocr_json (dict | None): 클로바 OCR API의 JSON 응답.

    Returns:
        str: 추출된 모든 텍스트를 공백으로 연결한 문자열.
    """
    texts = []
    if ocr_json and 'images' in ocr_json:
        for image in ocr_json['images']:
            for field in image.get('fields', []):
                texts.append(field['inferText'])
    return ' '.join(texts)

# --- [3] OpenAI (GPT) 활용하여 영수증 정보 추출 ---
# OPENAI_API_KEY를 함수 인자로 받도록 변경
def extract_receipt_info_with_gpt(ocr_text_content: str, openai_api_key: str) -> dict | None:
    """
    GPT 모델을 사용하여 OCR로 추출된 텍스트에서 영수증 정보를 추출합니다.

    Args:
        ocr_text_content (str): OCR로 추출된 영수증의 전체 텍스트 내용.
        openai_api_key (str): OpenAI API Key.

    Returns:
        dict | None: 추출된 영수증 정보 (JSON 형식) 또는 None (실패 시).
    """
    if not openai_api_key:
        print("❗ DEBUG: [receipt_analyzer.py] OpenAI API Key가 함수 인자로 전달되지 않았습니다.")
        return None

    client = openai.OpenAI(api_key=openai_api_key) # openai_api_key 인자 사용

    prompt = f"""
    다음은 영수증에서 OCR로 추출된 텍스트입니다.
    이 텍스트에서 다음 정보를 추출하여 **반드시 JSON 형식으로** 반환해주세요.
    정보를 찾을 수 없는 경우 해당 필드는 **null**로 처리해주세요.

    필요한 정보는 다음과 같습니다:
    - **상점명 (store_name)**: 영수증 발행 상점의 이름
    - **거래 날짜 (transaction_date)**: 거래가 발생한 날짜 (YYYY-MM-DD 형식)
    - **거래 시간 (transaction_time)**: 거래가 발생한 시간 (HH:MM 형식)
    - **총 결제 금액 (total_amount)**: 최종 결제된 금액 (숫자만, 소수점 가능)
    - **결제 항목 (items)**: 구매한 각 항목의 목록. 각 항목은 다음을 포함합니다:
        - **이름 (name)**: 상품 또는 서비스의 이름
        - **가격 (price)**: 해당 항목의 단가 또는 총 가격 (숫자만)
        - **수량 (quantity)**: 해당 항목의 수량 (숫자만). 수량이 불분명하면 1로 가정.
    - **결제 수단 (payment_method)**: 사용된 결제 방식 (예: 신용카드, 현금, 페이, 상품권 등)

    예시 JSON 형식:
    {{
        "store_name": "ABC 마트",
        "transaction_date": "2024-07-20",
        "transaction_time": "15:30",
        "total_amount": 25500.0,
        "items": [
            {{"name": "바나나", "price": 3000.0, "quantity": 2}},
            {{"name": "사과", "price": 5000.0, "quantity": 1}}
        ],
        "payment_method": "신용카드"
    }}

    영수증 텍스트:
    {ocr_text_content}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o", # 더 정확한 결과를 위해 gpt-4o 또는 gpt-4를 권장합니다.
            messages=[
                {"role": "system", "content": "You are a highly accurate assistant specialized in extracting structured information from receipt texts. Always respond in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}, # GPT가 JSON 형식으로 응답하도록 강제
            max_tokens=1500 # 응답 길이 조정 (필요에 따라)
        )
        extracted_info = json.loads(response.choices[0].message.content)
        return extracted_info

    except openai.APIError as e:
        print(f"❗ [receipt_analyzer.py] OpenAI API 호출 중 오류 발생: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❗ [receipt_analyzer.py] OpenAI 응답 JSON 파싱 중 오류 발생: {e}")
        print(f"응답 내용: {response.choices[0].message.content}") # 디버깅을 위해 응답 내용 출력
        return None
    except Exception as e:
        print(f"❗ [receipt_analyzer.py] GPT 정보 추출 중 알 수 없는 오류 발생: {type(e).__name__}: {e}")
        return None


# --- 메인 실행 로직 (이 파일 직접 실행 테스트 용도) ---
if __name__ == "__main__":
    # 이 __name__ == "__main__" 블록 안에서는 환경 변수를 다시 로드해야 합니다!
    # 왜냐하면 이 파일을 직접 실행할 때는 main.py가 환경 변수를 로드해주지 않기 때문입니다.
    from dotenv import load_dotenv # 여기서 다시 import 해줘야 합니다.
    load_dotenv() # 이 파일 자체를 테스트할 때는 여기서 다시 로드!

    # 환경 변수에서 API 키 로드 (여기서는 다시 os.getenv 사용)
    local_clova_ocr_url = os.getenv("CLOVA_OCR_URL")
    local_clova_ocr_secret = os.getenv("CLOVA_OCR_SECRET")
    local_openai_api_key = os.getenv("OPENAI_API_KEY")

    # 🔐 사용자 설정 필요: 실제 영수증 이미지 경로로 변경하세요.
    sample_image_path = 'sample_receipt.jpg' # 또는 'path/to/your/image.jpg'

    if not os.path.exists(sample_image_path):
        print(f"❗ 경고: 샘플 이미지 '{sample_image_path}'를 찾을 수 없습니다. 테스트를 위해 실제 이미지 경로로 수정해주세요.")
        # exit(1) # 테스트를 위해 주석 처리하거나, 필요에 따라 활성화

    if not all([local_clova_ocr_url, local_clova_ocr_secret, local_openai_api_key]):
        print("❗ API 키 설정이 완료되지 않았습니다. .env 파일을 확인해주세요.")
        exit(1) # 프로그램 종료

    print(f"📤 이미지 '{sample_image_path}'에서 OCR 텍스트 추출 중...")
    # 수정된 함수 시그니처에 맞게 인자 전달
    ocr_result_json = call_clova_ocr(sample_image_path, local_clova_ocr_url, local_clova_ocr_secret)

    if ocr_result_json:
        ocr_full_text = extract_texts_from_clova(ocr_result_json)
        print("\n📄 클로바 OCR 전체 텍스트:\n", ocr_full_text)

        print("\n✨ OpenAI GPT로 영수증 정보 추출 중...")
        # 수정된 함수 시그니처에 맞게 인자 전달
        receipt_info = extract_receipt_info_with_gpt(ocr_full_text, local_openai_api_key)

        if receipt_info:
            print("\n✅ 최종 추출된 영수증 정보:")
            print(json.dumps(receipt_info, ensure_ascii=False, indent=4))
        else:
            print("❗ GPT를 통해 영수증 정보를 추출하는 데 실패했습니다.")
    else:
        print("❗ 클로바 OCR 결과를 가져오는 데 실패했습니다. 이미지 경로 또는 API 설정을 확인하세요.")