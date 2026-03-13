# DOLIGO 채팅 - Cloudflare Worker 배포 가이드

채팅 기능만 Cloudflare Worker로 배포하여 Railway/Render 없이 사용할 수 있습니다.

> **참고**: 문서 생성(PDF/PPT/HWP)은 Python 백엔드가 필요합니다. 채팅만 사용하려면 이 Worker로 충분합니다.

---

## 1. Worker 배포

### 방법 A: Wrangler CLI (권장)

```bash
cd worker-doligo-chat
npm install
npx wrangler login   # Cloudflare 로그인 (최초 1회)
npx wrangler deploy
```

### 방법 B: Cloudflare 대시보드

1. **Workers & Pages** → **응용 프로그램 생성** → **Worker 만들기**
2. 이름: `doligo-chat` (또는 원하는 이름)
3. **배포** 클릭
4. **설정** → **편집**에서 `worker-doligo-chat/src/index.js` 내용 붙여넣기
5. **저장 후 배포**

---

## 2. Secrets 설정 (API 키)

배포 후 Worker URL이 생성됩니다. 예: `https://doligo-chat.wwwhunycom07.workers.dev`

**GEMINI_API_KEY** 설정:

1. Worker 선택 → **설정** → **변수 및 암호**
2. **암호 추가** → 이름: `GEMINI_API_KEY`, 값: (Google AI Studio에서 발급한 API 키)
3. 저장

> `fashion-agentic-api`에 `BEMINI_API_KEV` 오타로 저장되어 있다면, `GEMINI_API_KEY`로 새로 추가하세요.

---

## 3. Cloudflare Pages 환경 변수

1. **Cloudflare Dashboard** → **Workers & Pages** → **doligo** (프론트엔드)
2. **설정** → **환경 변수**
3. **VITE_API_URL** 추가:
   - **이름**: `VITE_API_URL`
   - **값**: `https://doligo-chat.wwwhunycom07.workers.dev` (본인 Worker URL로 변경)
4. **다시 배포** 실행

---

## 4. CORS

Worker는 `Access-Control-Allow-Origin: *`로 설정되어 있어 `doligo.pages.dev`에서 호출 가능합니다.

---

## 5. 확인

1. https://doligo.pages.dev 접속
2. "AI와 대화하기"에서 메시지 전송
3. 응답이 오면 성공

---

## 제한사항

| 기능 | Worker | Python 백엔드 |
|------|--------|---------------|
| 채팅 | ✅ | ✅ |
| URL 맥락 | ✅ | ✅ |
| 이미지 첨부 | ❌ (추후 추가 가능) | ✅ |
| 문서 생성 (PDF/PPT/HWP) | ❌ | ✅ |

문서 생성이 필요하면 Railway/Render에 Python 백엔드를 배포하세요.
