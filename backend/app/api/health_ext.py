"""확장 헬스체크 - API 키 상태."""
from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/api/health/gemini")
async def health_gemini():
    """Gemini API 키 설정 여부 확인."""
    key = settings.google_api_key or ""
    return {
        "ok": bool(key.strip()),
        "message": "API 키 설정됨" if key.strip() else "backend/.env에 GOOGLE_API_KEY를 설정하세요.",
    }
