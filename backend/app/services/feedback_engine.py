"""Feedback engine - 5 rounds of self-improvement."""
import json
from app.services.content_generator import _call_with_retry


FEEDBACK_PROMPTS = [
    # Round 1: Analyze
    """방금 생성한 위의 내용을 모두 분석 및 파악 후, 보완점, 제안점, 문제점 등을 찾아서 나열해 주세요.
JSON 형식으로 응답: {"improvements": ["항목1", "항목2"], "suggestions": [], "problems": []}""",
    # Round 2: Self-verify
    """지금까지의 피드백 히스토리(이전 라운드 결과)를 검토하여 중복된 내용이 없는지 확인하세요.
이상 없으면 {"status": "ok", "duplicates": []} 로 응답하세요. 중복이 있으면 duplicates 배열에 나열하세요.""",
    # Round 3: Apply
    """위에서 제시한 보완점, 제안점, 문제점을 모두 적용하여 완성도 높게 다시 모두 폼 양식에 맞추어 작성해 주세요.
JSON 형식으로만 응답: {"sections": [{"title": "...", "content": "..."}]}""",
    # Round 4: Re-analyze
    """개선된 내용을 다시 분석하여 추가 보완점이 있는지 확인하세요.
{"improvements": [], "status": "ok"} 형식으로 응답. 추가 보완점이 없으면 improvements를 빈 배열로.""",
    # Round 5: Final review
    """전체 문서의 일관성, 전문성, 완성도를 최종 검토하세요.
최종 문서를 JSON으로 출력: {"sections": [{"title": "...", "content": "..."}]}""",
]


def _extract_json(text: str) -> dict | None:
    """Extract JSON from model response."""
    text = text.strip()
    for marker in ["```json", "```"]:
        if marker in text:
            try:
                part = text.split(marker)[1].split("```")[0].strip()
                return json.loads(part)
            except (IndexError, json.JSONDecodeError):
                pass
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


async def run_feedback_loop(content: dict, structure: dict, round_num: int) -> dict | None:
    """Run one feedback round. Returns updated content or None."""
    import asyncio

    sections = content.get("sections", [])
    if not sections:
        return content

    prompt_idx = min(round_num - 1, len(FEEDBACK_PROMPTS) - 1)
    base_prompt = FEEDBACK_PROMPTS[prompt_idx]

    doc_text = "\n\n".join(
        f"## {s.get('title', '')}\n{s.get('content', '')}" for s in sections
    )

    full_prompt = f"""다음은 지원과제 문서 초안입니다:

{doc_text}

---

{base_prompt}
"""

    try:
        text = await asyncio.to_thread(_call_with_retry, full_prompt)
        data = _extract_json(text)
        if not data:
            return content

        if "sections" in data:
            return data
        # Rounds 1, 2, 4: analysis only, keep content, merge feedback for next round
        return content
    except Exception:
        return content
