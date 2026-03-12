"""URL 컨텍스트 추출 - 지원과제 성격 파악."""
import re
import logging
import httpx

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


async def fetch_url_content(url: str, max_chars: int = 15000) -> str:
    """URL에서 텍스트 추출 (지원과제 공고 등)."""
    if not url or not url.strip().startswith(("http://", "https://")):
        return ""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            r = await client.get(url.strip(), headers={"User-Agent": USER_AGENT})
            r.raise_for_status()
            text = r.text
    except Exception as e:
        logger.warning("URL fetch 실패 %s: %s", url, e)
        return ""

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
    except ImportError:
        text = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", text, flags=re.I)
        text = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", text, flags=re.I)
        text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars] if text else ""
