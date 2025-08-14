from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from app.services.stt_service import transcribe_audio, ALLOWED_EXTS
from app.utils.jwt_utils import get_current_user
import os

router = APIRouter(prefix="/stt", tags=["음성 인식"])

@router.post("/transcribe")
async def transcribe_speech(
    file: UploadFile = File(...),
    current_user_email: str = Depends(get_current_user)
):
    """음성 파일을 텍스트로 변환 (인증 필요)"""
    
    # 파일 확장자 검증
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(ALLOWED_EXTS)}"
        )
    
    # 파일 크기 검증 (10MB 제한)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="파일 크기는 10MB를 초과할 수 없습니다."
        )
    
    try:
        # 파일 내용 읽기
        file_content = await file.read()
        
        # STT 서비스 호출
        transcription = transcribe_audio(file_content, file.filename)
        
        return {
            "transcription": transcription,
            "filename": file.filename,
            "user": current_user_email
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"음성 인식 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/supported-formats")
async def get_supported_formats():
    """지원되는 오디오 파일 형식 조회"""
    return {
        "supported_formats": list(ALLOWED_EXTS),
        "max_file_size": "10MB"
    } 