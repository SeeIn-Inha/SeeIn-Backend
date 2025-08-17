# 서버 배포 가이드 (Windows 전용)

## 필수 요구사항

### 1. ffmpeg 설치

1. https://ffmpeg.org/download.html 에서 Windows builds 다운로드
2. `C:\ffmpeg-7.1.1-essentials_build\` 에 압축 해제
3. (선택사항) 시스템 PATH에 `C:\ffmpeg-7.1.1-essentials_build\bin` 추가

#### 설치 확인
```cmd
ffmpeg -version
```

### 2. Python 의존성 설치
```cmd
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env` 파일 생성:
```
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

### 4. 서버 실행
```cmd
python main.py
# 또는
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API 엔드포인트

### 공개 엔드포인트 (인증 불필요)
- `GET /` - API 정보
- `GET /health` - 서버 상태 확인
- `POST /auth/register` - 회원가입
- `POST /auth/login` - 로그인
- `POST /stt/transcribe` - 음성 인식 (STT)
- `GET /stt/supported-formats` - 지원 오디오 형식

### 보호된 엔드포인트 (인증 필요)
- `GET /auth/me` - 현재 사용자 정보
- `PUT /auth/update` - 사용자 정보 수정
- `PUT /auth/change-password` - 비밀번호 변경
- `DELETE /auth/delete` - 회원 탈퇴
- `GET /secure/me` - 보안 테스트

## 문제 해결

### ffmpeg 관련 오류
- `ffmpeg -version` 명령어로 설치 확인
- PATH 환경 변수에 ffmpeg 경로가 포함되어 있는지 확인
- 코드에서 자동으로 여러 경로를 시도하므로 대부분 자동 해결됨

### STT 관련 오류
- 오디오 파일 형식 확인 (WAV, MP3, M4A 등 지원)
- 파일 크기 제한: 10MB
- ffmpeg 설치로 모든 오디오 형식 지원 가능
