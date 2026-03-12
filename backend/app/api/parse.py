"""Document parse API."""
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.models import ParseResponse, ParseSection
from app.services.document_parser import parse_document

router = APIRouter(prefix="/api", tags=["parse"])

ALLOWED_EXTENSIONS = {".pdf", ".pptx", ".hwp", ".hwpx"}


@router.post("/parse", response_model=ParseResponse)
async def parse_file(file: UploadFile = File(...)):
    """Parse document structure (sections, titles)."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            f"지원하지 않는 형식입니다. 허용: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(413, f"파일 크기 제한 초과 (최대 {settings.max_file_size_mb}MB)")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    temp_path = upload_dir / f"parse_{id(file)}{ext}"
    temp_path.write_bytes(content)

    try:
        structure = parse_document(temp_path)
        if not structure:
            raise HTTPException(400, "문서 구조를 추출할 수 없습니다")

        sections = [
            ParseSection(
                index=i + 1,
                title=s.get("title", f"섹션 {i+1}"),
                has_image_placeholder=s.get("has_image_placeholder", False),
            )
            for i, s in enumerate(structure.get("sections", []))
        ]
        return ParseResponse(
            format=structure.get("format", ext[1:]),
            sections=sections,
            raw_text_preview=structure.get("raw_text_preview", "")[:500],
        )
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
