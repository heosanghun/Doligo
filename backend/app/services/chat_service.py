"""채팅 서비스 - 전문 비서/전략기획실 역할."""
import re
from app.config import settings
from app.services.content_generator import _call_with_retry


SYSTEM_PROMPT = """당신은 DOLIGO의 AI 전문 비서이자 전략기획실 최고 전문가입니다.
사용자의 지원과제(정부사업, R&D, 과제 신청 등) 작성 요청에 대해:
1. 사용자의 의도와 맥락을 정확히 이해합니다.
2. 전문 비서처럼 핵심 요구사항을 명확히 정리합니다.
3. 전략기획실 전문가 관점으로 보완점과 제안을 제시합니다.
4. 사용자가 원하는 정확한 니즈를 파악해 문서 작성에 반영할 수 있도록 구체화합니다.
한국어로 응답하며, 친절하고 전문적인 톤을 유지합니다.

[중요] 응답 마지막에 반드시 새 줄 두 개 후 다음 형식으로 이 대화에서 문서 작성에 유용한 핵심 키워드 1~3개를 추출해 적어주세요:
___KEYWORDS___: 키워드1, 키워드2, 키워드3
(키워드가 없거나 추출할 수 없으면 ___KEYWORDS___: 만 적어주세요)"""


def _parse_keywords(text: str) -> list[str]:
    """응답에서 ___KEYWORDS___: 이후의 키워드 목록 추출."""
    match = re.search(r"___KEYWORDS___:\s*(.+)", text, re.DOTALL)
    if not match:
        return []
    raw = match.group(1).strip()
    if not raw:
        return []
    keywords = [k.strip() for k in re.split(r"[,，、\n]+", raw) if k.strip()]
    return keywords[:5]


def chat(messages: list[dict], url_context: str = "", image_data_list: list[dict] | None = None) -> tuple[str, list[str]]:
    """채팅 응답 생성. 이미지가 있으면 멀티모달로 전달."""
    conv_text = ""
    if url_context:
        conv_text += f"[참고: 지원과제 관련 URL 맥락]\n{url_context[:8000]}\n\n"
    for m in messages:
        role = "사용자" if m.get("role") == "user" else "AI"
        conv_text += f"{role}: {m.get('content', '')}\n\n"
    prompt = f"{SYSTEM_PROMPT}\n\n---\n\n대화 내용:\n{conv_text}\nAI:"

    if image_data_list:
        import google.generativeai as genai
        from app.config import settings
        genai.configure(api_key=settings.google_api_key)
        model = genai.GenerativeModel(settings.gemini_model_text)
        parts = [{"inline_data": img} for img in image_data_list]
        parts.append(prompt)
        try:
            raw = model.generate_content(parts).text or ""
        except Exception as e:
            return (f"이미지 분석 중 오류: {e}", [])
    else:
        try:
            raw = _call_with_retry(prompt)
        except Exception as e:
            return (f"응답 생성 중 오류가 발생했습니다: {e}", [])

    keywords = _parse_keywords(raw)
    reply = re.sub(r"\n*\s*___KEYWORDS___:.*$", "", raw, flags=re.DOTALL).strip()
    return reply or "응답을 생성하지 못했습니다.", keywords
