# 백엔드 배포 가이드 (Railway / Render)

프론트엔드(doligo.pages.dev)에서 채팅·문서 생성이 동작하려면 백엔드 API를 배포해야 합니다.

## Railway로 배포 (권장)

1. [railway.app](https://railway.app) 가입 후 **New Project** → **Deploy from GitHub**
2. `heosanghun/Doligo` 저장소 선택
3. **Root Directory**: `backend` 지정
4. **Dockerfile** 자동 감지 (backend/Dockerfile)
5. **Variables**에 환경 변수 설정:
   - `GOOGLE_API_KEY`: Gemini API 키
   - `CORS_ORIGINS`: `https://doligo.pages.dev`
6. 배포 후 **Settings** → **Generate Domain**으로 URL 확인 (예: `https://xxx.railway.app`)

## Cloudflare Pages 환경 변수 설정

1. Cloudflare Dashboard → Pages → doligo → **설정** → **환경 변수**
2. **VITE_API_URL** 추가: `https://xxx.railway.app` (Railway에서 생성한 URL)
3. **다시 배포** 실행

## Render로 배포

1. [render.com](https://render.com) → **New** → **Web Service**
2. GitHub 연결 후 `heosanghun/Doligo` 선택
3. **Root Directory**: `backend`
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. 환경 변수: `GOOGLE_API_KEY`, `CORS_ORIGINS`
