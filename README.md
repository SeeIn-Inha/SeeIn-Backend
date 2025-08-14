# SeeIn Backend (FastAPI)
인하공전 해커톤 3팀 시인 프로젝트 백엔드

## 개발 환경 세팅

### 1. 가상환경 활성화
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here

# JWT 설정
JWT_SECRET_KEY=your_jwt_secret_key_here_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# 개발 환경 설정
ENVIRONMENT=development
DEBUG=true
```

### 4. 서버 실행
```bash
uvicorn main:app --reload
```

## API 문서
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 주요 기능
- JWT 기반 사용자 인증
- 음성 인식 (STT) - OpenAI Whisper API
- 사용자 관리 (회원가입, 로그인, 프로필 조회)

## API 엔드포인트
- `POST /auth/register` - 회원가입
- `POST /auth/login` - 로그인
- `GET /auth/me` - 현재 사용자 정보 (인증 필요)
- `GET /auth/profile/{email}` - 사용자 프로필 조회
- `POST /stt/transcribe` - 음성 파일을 텍스트로 변환 (인증 필요)
- `GET /stt/supported-formats` - 지원되는 오디오 형식 조회