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

## 문제 해결

### ffmpeg 관련 오류
- `ffmpeg -version` 명령어로 설치 확인
- PATH 환경 변수에 ffmpeg 경로가 포함되어 있는지 확인
- 코드에서 자동으로 여러 경로를 시도하므로 대부분 자동 해결됨
