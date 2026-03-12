# 보안 가이드 (API 키 보호)

## API 키 노출 방지

### 아키텍처 (클라이언트에 키가 전달되지 않음)

```
[브라우저 F12]          [백엔드 서버]           [Google Gemini API]
     |                        |                        |
     |  POST /api/generate    |                        |
     |  (키워드, 파일만)        |                        |
     |----------------------->|  GOOGLE_API_KEY 사용    |
     |                        |----------------------->|
     |                        |<-----------------------|
     |  job_id, 진행률만 반환   |                        |
     |<-----------------------|                        |
```

- **프론트엔드**: API 키를 절대 포함하지 않음. `/api/*` 요청만 전송.
- **백엔드**: `.env`의 `GOOGLE_API_KEY`는 서버 메모리에서만 사용. 응답에 포함되지 않음.

### 체크리스트

- [x] `.env`는 `.gitignore`에 포함 (git 커밋 제외)
- [x] `.env.example`에는 실제 키 없음 (플레이스홀더만)
- [x] 프론트엔드에 `VITE_` 접두사 없는 env는 번들에 포함되지 않음
- [x] API 응답에 `settings`, `config`, `api_key` 미포함
- [x] 보안 헤더 적용 (X-Content-Type-Options, X-Frame-Options 등)

### 운영 시 권장사항

1. **환경 변수**: 서버/컨테이너 환경 변수로만 API 키 설정. 파일로 두지 않을 것.
2. **Swagger 비활성화**: `LOG_LEVEL=info` 또는 `production` 시 `/docs`, `/redoc` 비활성화됨.
3. **CORS**: `CORS_ORIGINS`에 실제 프론트엔드 도메인만 허용.
4. **HTTPS**: 외부 배포 시 반드시 HTTPS 사용.

### 키가 노출된 경우

1. [Google AI Studio](https://aistudio.google.com/apikey)에서 해당 키 **즉시 삭제/재생성**
2. 새 키를 `.env`에 설정
3. `.env`가 git에 커밋되었다면 `git filter-branch` 또는 BFG로 히스토리에서 제거
