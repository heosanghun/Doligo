"""FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import generate, parse, templates, chat, health_ext
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown."""
    # Create dirs
    from pathlib import Path
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="지원과제 AI 작성 서비스",
    description="키워드와 양식을 입력받아 AI로 문서를 생성합니다.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.log_level == "debug" else None,
    redoc_url="/redoc" if settings.log_level == "debug" else None,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더 - API 키 등 민감정보가 클라이언트에 노출되지 않도록."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router)
app.include_router(parse.router)
app.include_router(templates.router)
app.include_router(chat.router)
app.include_router(health_ext.router)


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok"}
