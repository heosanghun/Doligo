"""채팅 및 URL 컨텍스트 API."""
import asyncio
import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.chat_service import chat
from app.services.url_context import fetch_url_content

router = APIRouter(prefix="/api", tags=["chat"])


class UrlContextRequest(BaseModel):
    url: str


class UrlContextResponse(BaseModel):
    content: str
    success: bool


@router.post("/chat")
async def chat_endpoint(
    messages: str = Form(...),
    url: str = Form(""),
    images: list[UploadFile] | None = File(default=None),
):
    """AI 전문 비서 채팅. 이미지 첨부 지원."""
    from app.config import settings

    if not settings.google_api_key or not settings.google_api_key.strip():
        raise HTTPException(503, "Gemini API 키가 설정되지 않았습니다. backend/.env에 GOOGLE_API_KEY를 설정하세요.")

    try:
        msg_list = json.loads(messages)
    except json.JSONDecodeError:
        raise HTTPException(400, "messages 형식 오류")

    url_context = ""
    if url and url.strip().startswith(("http://", "https://")):
        url_context = await fetch_url_content(url.strip())

    image_data_list = []
    for img in (images or []):
        if img.content_type and img.content_type.startswith("image/"):
            data = await img.read()
            image_data_list.append({"mime_type": img.content_type or "image/jpeg", "data": data})

    try:
        reply, keywords = await asyncio.to_thread(chat, msg_list, url_context, image_data_list)
        return {
            "reply": reply or "응답을 생성하지 못했습니다.",
            "keywords": keywords,
        }
    except Exception as e:
        err_msg = str(e)
        if "API_KEY_INVALID" in err_msg or "invalid" in err_msg.lower():
            raise HTTPException(503, "Gemini API 키가 유효하지 않습니다. Google AI Studio에서 키를 확인하세요.")
        if "quota" in err_msg.lower() or "429" in err_msg:
            raise HTTPException(503, "API 사용량 한도 초과. 잠시 후 다시 시도하세요.")
        raise HTTPException(500, f"채팅 오류: {err_msg}")


@router.post("/url-context", response_model=UrlContextResponse)
async def fetch_url(req: UrlContextRequest):
    """URL에서 지원과제 맥락 추출."""
    if not req.url or not req.url.strip().startswith(("http://", "https://")):
        raise HTTPException(400, "유효한 URL을 입력하세요")
    content = await fetch_url_content(req.url)
    return UrlContextResponse(content=content, success=bool(content))
