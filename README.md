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
- 사용자 관리 (회원가입, 로그인, 프로필 조회, 정보 수정, 회원 탈퇴)

## API 엔드포인트

### 인증 관련 (`/auth`)
- `POST /auth/register` - 회원가입
- `POST /auth/login` - 로그인
- `GET /auth/me` - 현재 사용자 정보 (인증 필요)
- `GET /auth/profile/{email}` - 사용자 프로필 조회
- `PUT /auth/update` - 사용자 정보 수정 (닉네임, 이메일) (인증 필요)
- `PUT /auth/change-password` - 비밀번호 변경 (인증 필요)
- `DELETE /auth/delete` - 회원 탈퇴 (인증 필요)

### 음성 인식 관련 (`/stt`)
- `POST /stt/transcribe` - 음성 파일을 텍스트로 변환 (인증 필요)
- `GET /stt/supported-formats` - 지원되는 오디오 형식 조회

## 사용자 관리 기능 상세

### 1. 사용자 정보 수정
- **엔드포인트**: `PUT /auth/update`
- **인증**: JWT 토큰 필요
- **기능**: 닉네임과 이메일 수정 가능
- **요청 예시**:
```json
{
  "username": "새로운닉네임",
  "email": "newemail@example.com"
}
```

### 2. 비밀번호 변경
- **엔드포인트**: `PUT /auth/change-password`
- **인증**: JWT 토큰 필요
- **기능**: 현재 비밀번호 확인 후 새 비밀번호로 변경
- **요청 예시**:
```json
{
  "current_password": "현재비밀번호",
  "new_password": "새비밀번호"
}
```

### 3. 회원 탈퇴
- **엔드포인트**: `DELETE /auth/delete`
- **인증**: JWT 토큰 필요
- **기능**: 비밀번호 확인 후 계정 비활성화
- **요청 예시**:
```json
{
  "password": "현재비밀번호"
}
```

## 테스트
테스트 스크립트를 실행하여 모든 기능을 테스트할 수 있습니다:
```bash
python test_user_management.py
```