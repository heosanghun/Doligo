# Cloudflare Pages 배포 가이드

## 사전 준비

1. **GitHub 푸시**: 이 저장소를 GitHub에 푸시
2. **Cloudflare Pages**: [Cloudflare Dashboard](https://dash.cloudflare.com) → Pages → Create project → Connect to Git

## 빌드 구성 (Build Configuration)

Cloudflare Pages **설정 → 빌드 구성**에서 아래와 같이 설정하세요.

| 항목 | 값 |
|------|-----|
| **프레임워크 미리 설정** | None (또는 Vue/Vite) |
| **빌드 명령** | `npm run build` |
| **빌드 출력 디렉터리** | `dist` |
| **루트 디렉터리 (고급)** | `frontend` |

### 상세 설명

- **루트 디렉터리**: `frontend`  
  - `package.json`이 `frontend/` 폴더에 있으므로 반드시 설정
- **빌드 명령**: `npm run build`  
  - 루트가 `frontend`이므로 해당 폴더에서 실행됨
- **빌드 출력 디렉터리**: `dist`  
  - Vite 빌드 결과가 `frontend/dist`에 생성됨 (루트 기준)

### 환경 변수 (Cloudflare Pages)

- `VITE_API_URL`: 백엔드 API URL (예: `https://your-backend.workers.dev`)

### 백엔드 (별도 배포)

백엔드는 FastAPI이므로 Cloudflare Workers 또는 별도 서버(Vercel, Railway 등)에 배포 필요.

- **환경 변수**: `GOOGLE_API_KEY` 등 `.env.example` 참고

## 참고

- `.env` 파일은 절대 커밋하지 마세요.
- API 키는 Cloudflare/배포 플랫폼의 환경 변수로 설정하세요.
