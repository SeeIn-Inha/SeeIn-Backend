# app/services/stt_service.py
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
from typing import BinaryIO

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI SDK v1
from openai import OpenAI
client = None

if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    print("Warning: OPENAI_API_KEY가 설정되지 않았습니다. STT 기능을 사용하려면 .env 파일에 API 키를 설정하세요.")

ALLOWED_EXTS = {".wav", ".mp3", ".m4a", ".ogg", ".webm"}

def _ext(path: str) -> str:
    return os.path.splitext(path)[1].lower()

def _to_wav_if_needed(fileobj: BinaryIO, filename: str) -> str:
    """
    업로드된 파일을 ffmpeg로 WAV(16k)로 변환한 임시 파일 경로 반환.
    Whisper는 다양한 포맷을 지원하지만, WAV로 통일하면 안정적.
    """
    ext = _ext(filename)
    with NamedTemporaryFile(suffix=ext, delete=False) as src:
        src.write(fileobj.read())
        src.flush()
        src_path = src.name

    # 이미 WAV면 그대로 반환
    if ext == ".wav":
        return src_path

    # 그 외는 pydub로 wav 변환
    audio = AudioSegment.from_file(src_path)
    with NamedTemporaryFile(suffix=".wav", delete=False) as dst:
        audio.set_frame_rate(16000).set_channels(1).export(dst.name, format="wav")
        return dst.name

def transcribe_audio(file_content: bytes, filename: str) -> str:
    """
    파일 내용을 받아 Whisper API로 전사하고 텍스트 반환
    """
    if not client:
        raise ValueError("OpenAI API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 설정하세요.")
    
    from io import BytesIO
    
    # BytesIO 객체로 변환
    fileobj = BytesIO(file_content)
    wav_path = _to_wav_if_needed(fileobj, filename)
    
    try:
        with open(wav_path, "rb") as f:
            # OpenAI Whisper Transcriptions
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                # language="ko",  # 한국어 고정 원하면 주석 해제
                # prompt="로그인 이메일과 비밀번호가 포함될 수 있습니다.",
                response_format="json"
            )
        return result.text.strip()
    finally:
        # 임시 파일 정리
        try:
            os.unlink(wav_path)
        except:
            pass
