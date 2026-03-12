"""Content generator - 2단계 파이프라인: 초안 → 섹션별 전문 에이전트 병렬 개선."""
import json
import time
import asyncio
from app.config import settings


def _get_model():
    import google.generativeai as genai
    genai.configure(api_key=settings.google_api_key)
    return genai.GenerativeModel(settings.gemini_model_text)


def _call_with_retry(prompt: str, max_retries: int | None = None) -> str:
    max_retries = max_retries or settings.gemini_retry_count
    model = _get_model()
    last_err = None
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text or ""
        except Exception as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    raise last_err or RuntimeError("API call failed")


def _extract_json_sections(text: str) -> list[dict]:
    """응답에서 sections JSON 추출."""
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    data = json.loads(text)
    return data.get("sections", [])


# 섹션 유형별 전문 에이전트 역할
AGENT_ROLES = {
    "개요": "과제 개요·배경 전문가. 핵심 목표, 필요성, 기대효과를 명확하고 설득력 있게 작성합니다.",
    "범위": "과제 범위·세부과제 전문가. 구체적인 범위, 세부과제, 산출물을 상세히 정의합니다.",
    "일정": "일정·마일스톤 전문가. 단계별 일정, 마일스톤, 산출물 연계를 체계적으로 작성합니다.",
    "예산": "예산·재원 전문가. 항목별 예산, 재원조달, 집행계획을 구체적으로 작성합니다.",
    "기대효과": "기대효과·성과 전문가. 정량·정성적 기대효과, 성과지표를 명확히 제시합니다.",
    "기술": "기술·연구개발 전문가. 핵심 기술, 혁신성, 차별화 포인트를 전문적으로 서술합니다.",
    "default": "지원과제 작성 전문가. 해당 섹션의 목적에 맞는 전문적이고 구체적인 내용을 작성합니다.",
}


def _get_agent_role(title: str) -> str:
    for key, role in AGENT_ROLES.items():
        if key in title:
            return role
    return AGENT_ROLES["default"]


async def _generate_draft(
    keywords: str,
    structure: dict,
    context_block: str,
) -> list[dict]:
    """1단계: 전체 문서 맥락을 반영한 초안 일괄 생성 (1회 호출)."""
    sections = structure.get("sections", [])
    section_titles = "\n".join(f"- {s.get('title', '')}" for s in sections)

    prompt = f"""당신은 DOLIGO의 전략기획실 전문가입니다. 지원과제 문서의 초안을 작성합니다.

{context_block}

## 키워드
{keywords}

## 목차
{section_titles}

## 요청사항
- 위 맥락과 키워드를 반영하여 전체 문서의 일관된 초안을 작성하세요.
- 각 섹션별로 150~300자 이상의 기본 골격을 작성하세요 (세부 추후 개선 예정).
- 한국어로 작성하세요.
- JSON 형식으로만 응답하세요.

## 출력 (JSON만)
{{"sections": [{{"title": "섹션 제목", "content": "본문 내용"}}]}}
"""

    try:
        text = await asyncio.to_thread(_call_with_retry, prompt)
        return _extract_json_sections(text)
    except Exception:
        return []


async def _refine_section(
    section: dict,
    section_index: int,
    draft_sections: list[dict],
    keywords: str,
    context_block: str,
) -> dict:
    """2단계: 전문 에이전트가 해당 섹션만 세부 개선 (병렬 실행)."""
    title = section.get("title", f"섹션{section_index + 1}")
    draft_content = section.get("content", "")
    role = _get_agent_role(title)

    # 전체 초안 맥락 (전후 섹션 참고용)
    draft_context = "\n\n".join(
        f"### {s.get('title', '')}\n{s.get('content', '')[:200]}..."
        for i, s in enumerate(draft_sections) if i != section_index
    )[:2000]

    prompt = f"""당신은 DOLIGO의 {role}

## 전체 맥락
{context_block}

## 키워드
{keywords}

## 전체 초안의 다른 섹션 참고 (일관성 유지)
{draft_context}

## 담당 섹션 초안 (이 내용을 세부 개선)
제목: {title}
현재 내용:
{draft_content}

## 요청사항
- 위 초안을 기반으로 전문성·구체성을 높여 세부 개선하세요.
- 400~1000자 이상으로 풍부하고 구체적인 내용으로 확장하세요.
- 숫자, 사례, 근거, 실행 가능한 항목을 포함하세요.
- 다른 섹션과 중복·모순 없이 일관되게 작성하세요.
- 한국어로 작성하세요.
- JSON 형식으로만 응답하세요.

## 출력 (JSON만)
{{"title": "{title}", "content": "개선된 본문 내용"}}
"""

    try:
        text = await asyncio.to_thread(_call_with_retry, prompt)
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        data = json.loads(text)
        return {"title": data.get("title", title), "content": data.get("content", draft_content)}
    except Exception:
        return {"title": title, "content": draft_content}


async def generate_content(
    keywords: str,
    structure: dict,
    url_context: str = "",
    chat_summary: str = "",
) -> dict | None:
    """2단계 파이프라인: 초안 → 섹션별 전문 에이전트 병렬 개선."""
    sections = structure.get("sections", [])
    if not sections:
        return None

    context_parts = []
    if url_context:
        context_parts.append(f"## 지원과제 URL 맥락\n{url_context[:6000]}")
    if chat_summary:
        context_parts.append(f"## 사용자-AI 대화 요약 (정확한 니즈)\n{chat_summary[:3000]}")
    context_block = "\n\n".join(context_parts) if context_parts else "(맥락 없음)"

    # 1단계: 초안 일괄 생성 (1회 API 호출)
    draft_sections = await _generate_draft(keywords, structure, context_block)
    if not draft_sections:
        return {
            "sections": [
                {"title": s.get("title", f"섹션{i+1}"), "content": f"[{keywords} 기반 내용]"}
                for i, s in enumerate(sections)
            ]
        }

    # 초안과 구조 매칭 (섹션 수 맞추기)
    while len(draft_sections) < len(sections):
        draft_sections.append({"title": sections[len(draft_sections)].get("title", ""), "content": ""})
    draft_sections = draft_sections[: len(sections)]

    # 2단계: 섹션별 전문 에이전트가 병렬로 세부 개선
    tasks = [
        _refine_section(draft_sections[i], i, draft_sections, keywords, context_block)
        for i in range(len(sections))
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        "sections": [
            r if isinstance(r, dict) else {"title": sections[i].get("title", ""), "content": draft_sections[i].get("content", "")}
            for i, r in enumerate(results)
        ]
    }
