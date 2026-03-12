"""Pydantic schemas for API."""
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request for document generation."""

    keywords: str = Field(..., description="키워드 목록 (쉼표 또는 줄바꿈 구분)")


class GenerateResponse(BaseModel):
    """Response after starting generation job."""

    job_id: str
    message: str = "문서 생성 시작됨"


class JobStatus(BaseModel):
    """Job status response."""

    job_id: str
    status: str  # pending, parsing, drafting, feedback_1..5, images, building, completed, failed, cancelled
    progress: int = 0  # 0-100
    message: str = ""
    error: str | None = None


class ParseSection(BaseModel):
    """Section from parsed document."""

    index: int
    title: str
    has_image_placeholder: bool = False


class ParseResponse(BaseModel):
    """Response from parse API."""

    format: str  # pdf, ppt, hwp
    sections: list[ParseSection]
    raw_text_preview: str = ""
