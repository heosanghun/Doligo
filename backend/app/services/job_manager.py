"""Job manager for async document generation."""
import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class JobStatusEnum(str, Enum):
    """Job status values."""

    PENDING = "pending"
    PARSING = "parsing"
    DRAFTING = "drafting"
    FEEDBACK_1 = "feedback_1"
    FEEDBACK_2 = "feedback_2"
    FEEDBACK_3 = "feedback_3"
    FEEDBACK_4 = "feedback_4"
    FEEDBACK_5 = "feedback_5"
    IMAGES = "images"
    BUILDING = "building"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Document generation job."""

    job_id: str
    status: JobStatusEnum = JobStatusEnum.PENDING
    progress: int = 0
    message: str = ""
    error: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    upload_path: Path | None = None
    output_path: Path | None = None
    result: dict[str, Any] = field(default_factory=dict)
    cancelled: bool = False


_jobs: dict[str, Job] = {}


def create_job(upload_path: Path | None = None) -> Job:
    """Create a new job."""
    job_id = str(uuid.uuid4())
    job = Job(job_id=job_id, upload_path=upload_path)
    _jobs[job_id] = job
    return job


def get_job(job_id: str) -> Job | None:
    """Get job by ID."""
    return _jobs.get(job_id)


def update_job(
    job_id: str,
    status: JobStatusEnum | None = None,
    progress: int | None = None,
    message: str | None = None,
    error: str | None = None,
    output_path: Path | None = None,
    result: dict | None = None,
) -> Job | None:
    """Update job fields."""
    job = _jobs.get(job_id)
    if not job:
        return None
    if status is not None:
        job.status = status
    if progress is not None:
        job.progress = min(100, max(0, progress))
    if message is not None:
        job.message = message
    if error is not None:
        job.error = error
    if output_path is not None:
        job.output_path = output_path
    if result is not None:
        job.result.update(result)
    return job


def cancel_job(job_id: str) -> bool:
    """Cancel a job."""
    job = _jobs.get(job_id)
    if not job:
        return False
    job.cancelled = True
    job.status = JobStatusEnum.CANCELLED
    job.message = "취소됨"
    return True
