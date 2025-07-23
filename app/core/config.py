"""
이 모듈은 환경변수와 설정값을 로드합니다.
예시:
- OPENAI API KEY 불러오기
"""

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
