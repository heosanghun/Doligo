"""Document generation API."""
import asyncio
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from app.config import settings
from app.models import GenerateResponse, JobStatus
from app.services.job_manager import (
    JobStatusEnum,
    cancel_job,
    create_job,
    get_job,
    update_job,
)

router = APIRouter(prefix="/api/generate", tags=["generate"])

ALLOWED_EXTENSIONS = {".pdf", ".pptx", ".hwp", ".hwpx"}


def _validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            f"지원하지 않는 형식입니다. 허용: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    if file.size and file.size > settings.max_file_size_bytes:
        raise HTTPException(
            413,
            f"파일 크기 제한 초과 (최대 {settings.max_file_size_mb}MB)",
        )


async def _run_generation(
    job_id: str,
    keywords: str,
    file_path: Path,
    output_format: str = "",
    url_context: str = "",
    chat_summary: str = "",
) -> None:
    """Background task: run full generation pipeline."""
    from app.services.document_parser import parse_document
    from app.services.content_generator import generate_content
    from app.services.feedback_engine import run_feedback_loop
    from app.services.image_generator import generate_images_for_sections
    from app.services.document_builder import build_document

    job = get_job(job_id)
    if not job or job.cancelled:
        return

    try:
        # 1. Parse
        update_job(job_id, status=JobStatusEnum.PARSING, progress=5, message="양식 분석 중...")
        structure = await asyncio.to_thread(parse_document, file_path)
        if job.cancelled:
            return
        if not structure or not structure.get("sections"):
            update_job(
                job_id,
                status=JobStatusEnum.FAILED,
                progress=0,
                error="문서 구조를 추출할 수 없습니다.",
            )
            return

        # 2. Draft
        update_job(job_id, status=JobStatusEnum.DRAFTING, progress=15, message="초안 작성 중...")
        content = await generate_content(keywords, structure, url_context=url_context, chat_summary=chat_summary)
        if job.cancelled:
            return
        if not content:
            update_job(job_id, status=JobStatusEnum.FAILED, error="초안 생성 실패")
            return

        # 3. Feedback loop
        feedback_statuses = [
            JobStatusEnum.FEEDBACK_1,
            JobStatusEnum.FEEDBACK_2,
            JobStatusEnum.FEEDBACK_3,
            JobStatusEnum.FEEDBACK_4,
            JobStatusEnum.FEEDBACK_5,
        ]
        for i in range(settings.feedback_min_rounds):
            if get_job(job_id) and get_job(job_id).cancelled:
                return
            st = feedback_statuses[i] if i < len(feedback_statuses) else JobStatusEnum.FEEDBACK_5
            update_job(
                job_id,
                status=st,
                progress=15 + ((i + 1) * 12),
                message=f"피드백 {i+1}회차 적용 중...",
            )
            content = await run_feedback_loop(content, structure, round_num=i + 1)
            if not content:
                break

        if job.cancelled:
            return

        # 4. Images
        update_job(job_id, status=JobStatusEnum.IMAGES, progress=80, message="이미지 생성 중...")
        images = await generate_images_for_sections(content, structure)
        content["images"] = images

        # 5. Build
        update_job(job_id, status=JobStatusEnum.BUILDING, progress=90, message="문서 조립 중...")
        output_path = await asyncio.to_thread(
            build_document,
            file_path,
            content,
            structure,
            output_format=output_format or None,
        )
        if job.cancelled:
            return

        # 5b. Save content for Markdown 보기 API (항상 저장)
        import json
        content_path = Path(settings.output_dir) / f"{job_id}_content.json"
        content_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")

        update_job(
            job_id,
            status=JobStatusEnum.COMPLETED,
            progress=100,
            message="완료",
            output_path=output_path,
        )
    except Exception as e:
        update_job(
            job_id,
            status=JobStatusEnum.FAILED,
            error=str(e),
        )


@router.post("", response_model=GenerateResponse)
async def start_generation(
    background_tasks: BackgroundTasks,
    keywords: str = Form(...),
    output_format: str = Form("pdf"),
    url: str = Form(""),
    chat_summary: str = Form(""),
    file: UploadFile = File(...),
):
    """Start document generation job."""
    _validate_file(file)
    if output_format not in ("pdf", "ppt", "hwp", "md"):
        output_format = "pdf"

    url_context = ""
    if url and url.strip().startswith(("http://", "https://")):
        from app.services.url_context import fetch_url_content
        url_context = await fetch_url_content(url.strip())

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "file.pdf").suffix

    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(413, f"파일 크기 제한 초과 (최대 {settings.max_file_size_mb}MB)")

    job = create_job()
    save_path = upload_dir / f"{job.job_id}{ext}"
    save_path.write_bytes(content)
    job.upload_path = save_path

    background_tasks.add_task(
        _run_generation,
        job.job_id,
        keywords,
        save_path,
        output_format,
        url_context,
        chat_summary.strip(),
    )

    return GenerateResponse(job_id=job.job_id)


@router.get("/{job_id}/stream")
async def stream_job_status(job_id: str):
    """SSE stream for job progress."""
    import json

    async def event_generator():
        last_status = None
        while True:
            job = get_job(job_id)
            if not job:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break
            status_str = f"{job.status.value}|{job.progress}|{job.message}"
            if status_str != last_status:
                last_status = status_str
                yield f"data: {json.dumps({'status': job.status.value, 'progress': job.progress, 'message': job.message, 'error': job.error})}\n\n"
            if job.status in (JobStatusEnum.COMPLETED, JobStatusEnum.FAILED, JobStatusEnum.CANCELLED):
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get("/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job status (polling)."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "작업을 찾을 수 없습니다")
    return JobStatus(
        job_id=job.job_id,
        status=job.status.value,
        progress=job.progress,
        message=job.message,
        error=job.error,
    )


@router.get("/{job_id}/content")
async def get_job_content(job_id: str):
    """생성된 문서 내용을 Markdown으로 반환 (복붙용)."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "작업을 찾을 수 없습니다")
    if job.status != JobStatusEnum.COMPLETED:
        raise HTTPException(400, "아직 완료되지 않았습니다")
    content_path = Path(settings.output_dir) / f"{job_id}_content.json"
    if not content_path.exists():
        raise HTTPException(404, "내용을 찾을 수 없습니다")
    try:
        import json
        data = json.loads(content_path.read_text(encoding="utf-8"))
        sections = data.get("sections", [])
        lines = []
        for sec in sections:
            title = sec.get("title", "")
            text = sec.get("content", "").strip()
            if title:
                lines.append(f"# {title}\n\n")
            if text:
                lines.append(text)
                lines.append("\n\n")
        return {"markdown": "".join(lines).strip(), "format": "markdown"}
    except Exception as e:
        raise HTTPException(500, f"내용 로드 실패: {e}")


@router.get("/{job_id}/download")
async def download_result(job_id: str):
    """Download generated document."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "작업을 찾을 수 없습니다")
    if job.status != JobStatusEnum.COMPLETED:
        raise HTTPException(400, "아직 완료되지 않았습니다")
    if not job.output_path or not job.output_path.exists():
        raise HTTPException(404, "생성된 파일을 찾을 수 없습니다")
    return FileResponse(
        job.output_path,
        filename=job.output_path.name,
        media_type="application/octet-stream",
    )


@router.delete("/{job_id}")
async def cancel_generation(job_id: str):
    """Cancel generation job."""
    if not cancel_job(job_id):
        raise HTTPException(404, "작업을 찾을 수 없습니다")
    return {"message": "취소됨"}
