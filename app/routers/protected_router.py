from fastapi import APIRouter, Depends
from app.utils.jwt_utils import get_current_user

router = APIRouter(prefix="/secure", tags=["secure"])

@router.get("/me")
def read_current_user(email: str = Depends(get_current_user)):
    return {"msg": f"현재 로그인된 사용자: {email}"}