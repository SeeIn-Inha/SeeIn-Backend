# app/services/stt_service.py
import os
from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
from typing import BinaryIO

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 디버그 출력 추가
print(f"OpenAI API Key loaded: {'Yes' if OPENAI_API_KEY else 'No'}")
if OPENAI_API_KEY:
    print(f"API Key prefix: {OPENAI_API_KEY[:10]}...")

# OpenAI SDK v1
from openai import OpenAI
client = None

if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("OpenAI client initialized successfully")
else:
    print("Warning: OPENAI_API_KEY가 설정되지 않았습니다. STT 기능을 사용하려면 .env 파일에 API 키를 설정하세요.")

# 모든 오디오 형식 지원 (OpenAI Whisper가 직접 처리)
ALLOWED_EXTS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac", ".aac"}

def _ext(path: str) -> str:
    return os.path.splitext(path)[1].lower()

def transcribe_with_local_stt(file_content: bytes, filename: str) -> str:
    """
    로컬 STT를 사용한 음성 인식 (OpenAI API 대체)
    """
    try:
        import speech_recognition as sr
        from pydub import AudioSegment
        from io import BytesIO
        
        # pydub이 ffmpeg를 찾을 수 있도록 환경 변수 설정
        import os
        
        # 여러 가능한 ffmpeg 경로들 (Windows 전용)
        possible_ffmpeg_paths = [
            'C:\\ffmpeg-7.1.1-essentials_build\\bin',  # 로컬 개발 환경
            'C:\\ffmpeg\\bin',                         # 일반적인 설치 경로
            'C:\\Program Files\\ffmpeg\\bin',          # Program Files 설치 경로
            'C:\\Program Files (x86)\\ffmpeg\\bin',    # Program Files (x86) 설치 경로
        ]
        
        # PATH에 ffmpeg 경로 추가
        if 'PATH' not in os.environ:
            os.environ['PATH'] = ''
        
        for ffmpeg_path in possible_ffmpeg_paths:
            if os.path.exists(ffmpeg_path) and ffmpeg_path not in os.environ['PATH']:
                os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ['PATH']
                print(f"ffmpeg 경로 추가됨: {ffmpeg_path}")
                break
        
        # ffmpeg 설치 확인 (선택적)
        ffmpeg_available = False
        try:
            import subprocess
            # 먼저 PATH에서 ffmpeg 찾기 시도
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            ffmpeg_available = result.returncode == 0
        except FileNotFoundError:
            # PATH에서 찾을 수 없으면 직접 경로 시도
            try:
                result = subprocess.run(['C:\\ffmpeg-7.1.1-essentials_build\\bin\\ffmpeg.exe', '-version'], capture_output=True, text=True)
                ffmpeg_available = result.returncode == 0
                if ffmpeg_available:
                    print("ffmpeg를 직접 경로에서 찾았습니다.")
            except FileNotFoundError:
                ffmpeg_available = False
        
        if not ffmpeg_available:
            print("경고: ffmpeg가 설치되지 않았습니다. 일부 오디오 형식에서 문제가 발생할 수 있습니다.")
            
        # 오디오 파일을 WAV로 변환
        print(f"파일 확장자: {os.path.splitext(filename)[1].lower()}")
        print(f"파일 크기: {len(file_content)} bytes")
        print(f"ffmpeg 사용 가능: {ffmpeg_available}")
        
        try:
            audio = AudioSegment.from_file(BytesIO(file_content))
            print("오디오 파일 로드 성공")
        except Exception as audio_error:
            # 파일 확장자 확인
            file_ext = os.path.splitext(filename)[1].lower()
            
            # MP3와 WAV는 ffmpeg 없이도 처리 가능해야 함
            if file_ext in ['.mp3', '.wav'] and not ffmpeg_available:
                return f"오디오 파일 변환 오류: {audio_error}. MP3/WAV 파일인데도 변환에 실패했습니다. 파일이 손상되었거나 지원되지 않는 코덱일 수 있습니다."
            elif not ffmpeg_available:
                return f"오디오 파일 변환 오류: {audio_error}. 이 오디오 형식({file_ext})을 처리하려면 ffmpeg가 필요합니다. https://ffmpeg.org/download.html 에서 다운로드하거나, WAV 또는 MP3 형식으로 변환 후 다시 시도해보세요."
            else:
                return f"오디오 파일 변환 오류: {audio_error}"
        
        # 임시 WAV 파일 생성
        temp_path = None
        try:
            with NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                audio.export(temp_file.name, format="wav")
                temp_path = temp_file.name
            
            # SpeechRecognition 사용
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_path) as source:
                audio_data = recognizer.record(source)
                # Google Speech Recognition 사용 (무료)
                text = recognizer.recognize_google(audio_data, language="ko-KR")
                return text
        except sr.UnknownValueError:
            return "음성을 인식할 수 없습니다."
        except sr.RequestError as e:
            return f"음성 인식 서비스 오류: {e}"
        except Exception as e:
            return f"음성 인식 처리 오류: {e}"
        finally:
            # 임시 파일 정리
            if temp_path:
                try:
                    os.unlink(temp_path)
                except:
                    pass
    except Exception as e:
        return f"로컬 STT 오류: {e}"

def transcribe_audio(file_content: bytes, filename: str) -> str:
    """
    오디오 파일을 받아 Whisper API로 전사하고 텍스트 반환
    OpenAI API 할당량 초과 시 로컬 STT로 fallback
    """
    # 파일 확장자 확인
    ext = _ext(filename)
    if ext not in ALLOWED_EXTS:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {ext}. 지원 형식: {', '.join(ALLOWED_EXTS)}")
    
    # OpenAI API 사용 시도
    if client:
        try:
            # 임시 파일 생성 (원본 형식 유지)
            with NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file.flush()
                temp_path = temp_file.name
            
            try:
                with open(temp_path, "rb") as f:
                    # OpenAI Whisper Transcriptions - 원본 형식 그대로 전송
                    result = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        # language="ko",  # 한국어 고정 원하면 주석 해제
                        response_format="json"
                    )
                return result.text.strip()
            except Exception as e:
                error_msg = str(e)
                if "insufficient_quota" in error_msg or "429" in error_msg:
                    print("OpenAI API 할당량 초과, 로컬 STT로 fallback")
                    return transcribe_with_local_stt(file_content, filename)
                else:
                    print(f"Whisper API 오류: {e}")
                    # OpenAI API 오류 시에도 로컬 STT 시도
                    local_result = transcribe_with_local_stt(file_content, filename)
                    if "ffmpeg" in local_result or "오류" in local_result:
                        return f"OpenAI API 오류: {e}. 로컬 STT도 사용할 수 없습니다. ffmpeg를 설치하거나 OpenAI API 키를 확인하세요."
                    return local_result
            finally:
                # 임시 파일 정리
                try:
                    os.unlink(temp_path)
                except:
                    pass
        except Exception as e:
            print(f"OpenAI API 오류: {e}")
            return transcribe_with_local_stt(file_content, filename)
    else:
        # OpenAI API 키가 없으면 로컬 STT 사용
        print("OpenAI API 키 없음, 로컬 STT 사용")
        return transcribe_with_local_stt(file_content, filename)
