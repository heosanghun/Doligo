# 지원과제 AI 작성 서비스 (Doligo)

키워드와 PDF/HWP/PPT 양식을 입력받아, Google Gemini로 문서 내용을 작성하고 5회 이상 자동 피드백 루프를 거쳐 완성도를 높이는 웹 서비스입니다.

## 요구사항

- Python 3.11+
- Node.js 18+
- Google Gemini API 키

## 설치

### 1. 백엔드

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# .env에 GOOGLE_API_KEY 설정
```

### 2. 프론트엔드

```bash
cd frontend
npm install
```

## 실행

### 1. API 키 설정

```bash
cd backend
cp .env.example .env
# .env 파일을 열어 GOOGLE_API_KEY=your_key_here 로 설정
```

### 2. 개발 모드

```bash
# 터미널 1: 백엔드
cd backend
uvicorn app.main:app --reload --port 8000

# 터미널 2: 프론트엔드
cd frontend
npm run dev
```

브라우저에서 http://localhost:5173 접속

### Docker

```bash
# backend/.env에 GOOGLE_API_KEY 설정 후
docker-compose -f docker/docker-compose.yml up -d
```

## API

- `GET /api/health/gemini` - Gemini API 키 연결 확인
- `POST /api/chat` - AI 채팅 (전문 비서·전략기획실)
- `POST /api/generate` - 키워드 + 파일 업로드로 문서 생성 시작
- `GET /api/generate/{job_id}/stream` - SSE 진행률 스트림
- `GET /api/generate/{job_id}` - 작업 상태 조회
- `GET /api/generate/{job_id}/download` - 최종 문서 다운로드
- `DELETE /api/generate/{job_id}` - 작업 취소
- `POST /api/parse` - 파일 구조 미리보기

## 지원 형식

- PDF (.pdf)
- PowerPoint (.pptx)
- 한글 (.hwp, .hwpx)
- Markdown (.md) - 복붙·편집에 최적

**HWP 출력 시**: `pip install python-hwpx` 필요. 미설치 시 PDF로 대체됩니다.

## 보안 (API 키)

- **API 키는 백엔드에서만 사용**됩니다. 프론트엔드(F12 개발자 도구)에서 절대 노출되지 않습니다.
- `.env`는 `.gitignore`에 포함되어 git에 커밋되지 않습니다.
- `.env.example`에는 실제 키를 넣지 마세요. `.env`에만 설정하세요.
- 자세한 내용: [docs/SECURITY.md](docs/SECURITY.md)

## 채팅이 안 될 때

1. **백엔드 실행 확인**: `cd backend` 후 `uvicorn app.main:app --reload --port 8000` 실행
2. **개발 모드 사용**: `npm run dev`로 프론트 실행 (프록시 적용). 빌드 후 정적 서버만 쓰면 404 발생
3. **빌드 후 서빙 시**: `frontend/.env`에 `VITE_API_URL=http://localhost:8000` 추가 후 재빌드
4. **API 키 확인**: `backend/.env`에 `GOOGLE_API_KEY=실제키` 설정
5. **연결 테스트**: 브라우저에서 `http://localhost:8000/api/health/gemini` 접속 → `{"ok":true}` 이면 정상
