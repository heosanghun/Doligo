"""이미지 생성 - Gemini 이미지 생성 또는 기본 이미지 사용."""
import io
import asyncio
from pathlib import Path

from app.config import settings


def _generate_image(prompt: str) -> bytes | None:
    """Gemini로 이미지 생성 시도. 지원 안 하면 None."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.google_api_key)
        model = genai.GenerativeModel(settings.gemini_model_image)
        # Gemini 텍스트 모델은 이미지 생성 미지원. Imagen API 사용 시 확장 가능.
        return None
    except Exception:
        return None


def _create_placeholder_image(section_title: str = "") -> bytes:
    """전문적인 플레이스홀더 이미지 생성 (초록 사각형 대체)."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        w, h = 400, 250
        img = Image.new("RGB", (w, h), color=(245, 247, 250))
        draw = ImageDraw.Draw(img)

        # 테두리
        draw.rectangle([(2, 2), (w - 3, h - 3)], outline=(200, 210, 220), width=2)

        # 텍스트 (이미지 영역 표시)
        text = "이미지 영역" if not section_title else section_title[:20]
        font = ImageFont.load_default()
        try:
            for name in ["malgun.ttf", "arial.ttf", "DejaVuSans.ttf"]:
                for base in ["C:/Windows/Fonts", "/usr/share/fonts"]:
                    p = Path(base) / name
                    if p.exists():
                        font = ImageFont.truetype(str(p), 20)
                        break
        except Exception:
            pass

        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((w - tw) // 2, (h - th) // 2 - 10), text, fill=(150, 160, 170), font=font)
        draw.text(((w - 140) // 2, (h - th) // 2 + 20), "(나노 바나나 등)", fill=(180, 190, 200), font=font)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        # Pillow 없을 때 최소 투명 PNG (녹색 아님)
        import base64
        return base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )


def _load_default_image() -> bytes | None:
    """backend/images/ 기본 이미지 로드 (나노 바나나 등)."""
    candidates = [
        Path(__file__).resolve().parent.parent.parent / "images" / "default.png",
        Path(__file__).resolve().parent.parent.parent / "images" / "nano-banana.png",
    ]
    for p in candidates:
        if p.exists():
            return p.read_bytes()
    return None


async def generate_images_for_sections(content: dict, structure: dict) -> dict[int, bytes]:
    """각 섹션별 이미지 생성. 실패 시 전문적 플레이스홀더 또는 기본 이미지 사용."""
    sections = content.get("sections", [])
    images = {}
    default_img = _load_default_image()

    for i, sec in enumerate(sections):
        title = sec.get("title", "")
        text_snippet = (sec.get("content", ""))[:200]
        prompt = f"Document section: {title}. Context: {text_snippet}. Professional illustration."
        try:
            img_bytes = await asyncio.to_thread(_generate_image, prompt)
            if img_bytes:
                images[i] = img_bytes
            elif default_img:
                images[i] = default_img
            else:
                images[i] = _create_placeholder_image(title)
        except Exception:
            images[i] = default_img or _create_placeholder_image(title)
    return images
