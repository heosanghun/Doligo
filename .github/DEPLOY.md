# Cloudflare Pages 배포 가이드

## 사전 준비

1. **GitHub 푸시**: 이 저장소를 GitHub에 푸시
2. **Cloudflare Pages**: [Cloudflare Dashboard](https://dash.cloudflare.com) → Pages → Create project → Connect to Git

## 배포 구성

### 프론트엔드 (정적 사이트)

- **Build command**: `cd frontend && npm ci && npm run build`
- **Build output directory**: `frontend/dist`
- **Root directory**: `/` (프로젝트 루트)

### 환경 변수 (Cloudflare Pages)

- `VITE_API_URL`: 백엔드 API URL (예: `https://your-backend.workers.dev`)

### 백엔드 (별도 배포)

백엔드는 FastAPI이므로 Cloudflare Workers 또는 별도 서버(Vercel, Railway 등)에 배포 필요.

- **환경 변수**: `GOOGLE_API_KEY` 등 `.env.example` 참고

## 참고

- `.env` 파일은 절대 커밋하지 마세요.
- API 키는 Cloudflare/배포 플랫폼의 환경 변수로 설정하세요.
