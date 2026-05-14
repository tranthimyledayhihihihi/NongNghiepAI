"""
Tavily Search API client.

Hai chức năng chính:
  1. search_prices()  — tìm giá nông sản thực tế từ web, trả về raw text để parser xử lý
  2. ask_price_qa()   — hỏi-đáp định giá: Tavily tổng hợp câu trả lời có nguồn trích dẫn
"""
import logging
import os
import re
from datetime import date
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ─── Truy vấn tìm kiếm giá ───────────────────────────────────────────────────
_PRICE_QUERIES = [
    "bảng giá nông sản hôm nay Việt Nam",
    "giá rau củ quả hôm nay tại chợ đầu mối",
    "giá sầu riêng xoài thanh long chuối hôm nay",
    "giá lúa gạo ngô đậu tương hôm nay",
    "giá cà phê hồ tiêu điều mía hôm nay Tây Nguyên",
    "giá hành tây tỏi gừng nghệ ớt hôm nay",
]

# Regex tìm giá trong nội dung trả về
_PRICE_RE = re.compile(
    r"([^\n\r,;:<>\"]{3,40}?)"          # tên nông sản (3-40 ký tự)
    r"[\s:–\-]+?"
    r"(\d[\d\.,]{1,9})"                  # con số giá
    r"\s*"
    r"(?:đ|VNĐ|vnđ|đồng|nghìn|ngàn|k\b)?",
    re.IGNORECASE | re.UNICODE,
)


def _get_api_key() -> str:
    return os.getenv("TAVILY_API_KEY", "")


def _is_available() -> bool:
    return bool(_get_api_key())


def _get_client():
    key = _get_api_key()
    if not key:
        raise RuntimeError("TAVILY_API_KEY chưa được cấu hình")
    from tavily import TavilyClient  # lazy import — không crash nếu chưa cài
    return TavilyClient(api_key=key)


# ─── 1. Cào giá từ Tavily ──────────────────────────────────────────────────

def search_prices(max_queries: int = 4) -> List[Dict]:
    """
    Tìm kiếm giá nông sản qua Tavily Search.
    Trả về list raw items: {crop_name_raw, price_raw, url, source, region}.
    Cần đi qua prefilter + _normalize trước khi INSERT DB.
    """
    if not _is_available():
        logger.warning("[Tavily] API key chưa cấu hình — bỏ qua Tavily crawler")
        return []

    client = _get_client()
    today = date.today().isoformat()
    raw_items: List[Dict] = []
    queries = _PRICE_QUERIES[:max_queries]

    for query in queries:
        try:
            resp = client.search(
                query=f"{query} {today}",
                search_depth="basic",
                max_results=5,
                include_answer=False,
            )
            before = len(raw_items)
            for result in resp.get("results", []):
                content = result.get("content", "")
                url = result.get("url", "")
                # Trích xuất từng cặp (tên, giá) trong nội dung
                for m in _PRICE_RE.finditer(content):
                    raw_items.append({
                        "crop_name_raw": m.group(1).strip(),
                        "price_raw":     m.group(2).strip(),
                        "url":           url,
                        "source":        "tavily.com",
                        "region":        _guess_region(url + " " + content[:300]),
                        "date":          today,
                    })
            logger.info(f"[Tavily] '{query}': {len(raw_items) - before} kết quả thô")
        except Exception as e:
            logger.debug(f"[Tavily] Lỗi query '{query}': {e}")

    return raw_items


def _guess_region(text: str) -> str:
    """Đoán tỉnh/thành từ tiêu đề/URL."""
    text_lower = text.lower()
    _hints = {
        "hcm": "TP.HCM", "hồ chí minh": "TP.HCM", "sài gòn": "TP.HCM",
        "hà nội": "Hà Nội", "hanoi": "Hà Nội",
        "đà nẵng": "Đà Nẵng", "danang": "Đà Nẵng",
        "cần thơ": "Cần Thơ", "cantho": "Cần Thơ",
        "đắk lắk": "Đắk Lắk", "daklak": "Đắk Lắk",
        "lâm đồng": "Lâm Đồng", "đà lạt": "Lâm Đồng",
        "gia lai": "Gia Lai",
        "tiền giang": "Tiền Giang",
        "long an": "Long An",
        "bình thuận": "Bình Thuận",
    }
    for hint, region in _hints.items():
        if hint in text_lower:
            return region
    return None


# ─── 2. Hỏi-đáp định giá (Price Q&A) ─────────────────────────────────────

def ask_agri_qa(question: str, db_context: str = "") -> Dict:
    """Q&A nông nghiệp tổng quát: thời tiết, đất, sâu bệnh, kỹ thuật."""
    if not _is_available():
        return {"answer": "", "sources": [], "tavily_answer": ""}

    client = _get_client()
    today = date.today().strftime("%d/%m/%Y")
    enriched_q = f"{question} nông nghiệp Việt Nam {today}"

    try:
        resp = client.search(
            query=enriched_q,
            search_depth="basic",
            max_results=4,
            include_answer=True,
            include_raw_content=False,
        )
    except Exception as e:
        logger.warning(f"[Tavily agri QA] Lỗi: {e}")
        return {"answer": "", "sources": [], "tavily_answer": ""}

    tavily_answer = resp.get("answer") or ""
    results = resp.get("results", [])
    sources = [{"url": r.get("url", ""), "title": r.get("title", "")} for r in results]

    parts = []
    if tavily_answer:
        parts.append(tavily_answer)
    if db_context:
        parts.append(db_context)
    for r in results[:2]:
        snippet = r.get("content", "")[:300]
        if snippet:
            parts.append(f"**{r.get('title', '')}**: {snippet}")

    return {
        "answer": "\n\n".join(parts),
        "tavily_answer": tavily_answer,
        "sources": sources,
    }


class TavilySearchClient:
    """Wrapper class cho backward-compatibility — bọc các module-level functions."""

    def search_prices(self, max_queries: int = 4) -> List[Dict]:
        return search_prices(max_queries)

    def ask_price_qa(self, question: str, db_context: Optional[str] = None) -> Dict:
        return ask_price_qa(question, db_context)

    def is_available(self) -> bool:
        return _is_available()


def ask_price_qa(
    question: str,
    db_context: Optional[str] = None,
) -> Dict:
    """
    Hỏi-đáp định giá dùng Tavily + tuỳ chọn bổ sung context từ DB.

    Returns:
        answer      : câu trả lời tổng hợp
        sources     : danh sách nguồn URL
        raw_results : nội dung chi tiết từng nguồn
    """
    if not _is_available():
        return {
            "answer":      "Chưa cấu hình TAVILY_API_KEY.",
            "sources":     [],
            "raw_results": [],
        }

    client = _get_client()
    today = date.today().strftime("%d/%m/%Y")

    # Làm phong phú câu hỏi với ngữ cảnh ngày tháng
    enriched_q = f"{question} (ngày {today}, Việt Nam)"

    try:
        resp = client.search(
            query=enriched_q,
            search_depth="advanced",       # deep search — nhiều nguồn hơn
            max_results=6,
            include_answer=True,           # Tavily tổng hợp câu trả lời
            include_raw_content=False,
        )
    except Exception as e:
        logger.error(f"[Tavily QA] Lỗi: {e}")
        return {"answer": f"Lỗi tìm kiếm: {e}", "sources": [], "raw_results": []}

    tavily_answer = resp.get("answer") or ""
    results = resp.get("results", [])

    # Tổng hợp nội dung từ các nguồn
    source_texts = []
    sources = []
    for r in results:
        url   = r.get("url", "")
        title = r.get("title", "")
        snippet = r.get("content", "")[:400]
        sources.append({"url": url, "title": title})
        source_texts.append(f"**{title}** ({url})\n{snippet}")

    # Kết hợp Tavily answer + DB context thành câu trả lời cuối
    parts = []
    if tavily_answer:
        parts.append(f"## Tổng hợp từ web (Tavily)\n{tavily_answer}")
    if db_context:
        parts.append(f"## Dữ liệu trong hệ thống\n{db_context}")
    if source_texts:
        parts.append("## Nguồn tham khảo\n" + "\n\n".join(source_texts))

    final_answer = "\n\n".join(parts) if parts else "Không tìm thấy thông tin."

    return {
        "answer":      final_answer,
        "tavily_answer": tavily_answer,
        "sources":     sources,
        "raw_results": results,
    }
