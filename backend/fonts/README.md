# 한글 폰트 (선택)

PDF에 한글이 정상 표시되려면 한글 TTF 폰트가 필요합니다.

## 자동 감지 순서

1. `backend/fonts/NotoSansKR-Regular.ttf`
2. `backend/fonts/NanumGothic.ttf`
3. Windows: `C:\Windows\Fonts\malgun.ttf` (맑은 고딕)
4. Windows: `C:\Windows\Fonts\gulim.ttc` (굴림)
5. Linux: `/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc`
6. Linux: `/usr/share/fonts/truetype/nanum/NanumGothic.ttf`

## Windows 사용자

맑은 고딕(malgun.ttf)이 기본 설치되어 있어 **별도 설정 없이** 한글이 표시됩니다.

## Linux / macOS 사용자

이 폴더에 한글 폰트를 넣어 주세요:

- **Noto Sans KR**: https://fonts.google.com/noto/specimen/Noto+Sans+KR
- **나눔고딕**: https://github.com/naver/nanumfont

다운로드 후 `NotoSansKR-Regular.ttf` 또는 `NanumGothic.ttf`로 저장하세요.
