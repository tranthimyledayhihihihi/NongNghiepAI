"""
Lấy giá nông sản tại các chuỗi cửa hàng lớn Việt Nam.

Ưu tiên:
  1. Scrape trực tiếp từng trang web chuỗi (httpx + BeautifulSoup)
  2. Fallback: Gemini 2.0 Flash + Google Search grounding
  3. Fallback cuối: ước tính từ giá sỉ + markup thông thường
"""
from __future__ import annotations

import asyncio
import os
import re
import time
from datetime import date
from pathlib import Path

import httpx
from dotenv import load_dotenv

from app.core.config import settings

env_path = Path(__file__).resolve().parents[2] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=False)

# ── Danh sách chuỗi cần tra giá ───────────────────────────────────────────────
STORES = [
    {
        "id": "bachhoaxanh",
        "name": "Bách Hóa Xanh",
        "type": "Bán lẻ",
        "search_url": "https://www.bachhoaxanh.com/search?q={query}",
        "price_pattern": r"(\d{1,3}(?:[.,]\d{3})+|\d{4,7})\s*(?:đ|₫|đồng)?",
        "markup": 0.18,
    },
    {
        "id": "winmart",
        "name": "WinMart / VinMart",
        "type": "Siêu thị",
        "search_url": "https://winmart.vn/tim-kiem?q={query}",
        "price_pattern": r"(\d{1,3}(?:[.,]\d{3})+|\d{4,7})\s*(?:đ|₫|đồng)?",
        "markup": 0.22,
    },
    {
        "id": "coopmart",
        "name": "Co.opmart",
        "type": "Siêu thị",
        "search_url": "https://www.coopmart.com.vn/tap-hoa/search/?s={query}",
        "price_pattern": r"(\d{1,3}(?:[.,]\d{3})+|\d{4,7})\s*(?:đ|₫|đồng)?",
        "markup": 0.22,
    },
    {
        "id": "bigc",
        "name": "BigC / GO!",
        "type": "Đại siêu thị",
        "search_url": "https://www.go24h.vn/san-pham?q={query}",
        "price_pattern": r"(\d{1,3}(?:[.,]\d{3})+|\d{4,7})\s*(?:đ|₫|đồng)?",
        "markup": 0.18,
    },
    {
        "id": "lottemart",
        "name": "Lotte Mart",
        "type": "Đại siêu thị",
        "search_url": "https://lottemart.com.vn/search?q={query}",
        "price_pattern": r"(\d{1,3}(?:[.,]\d{3})+|\d{4,7})\s*(?:đ|₫|đồng)?",
        "markup": 0.22,
    },
    {
        "id": "aeon",
        "name": "AEON",
        "type": "Đại siêu thị",
        "search_url": "https://aeoneshop.com/search?q={query}",
        "price_pattern": r"(\d{1,3}(?:[.,]\d{3})+|\d{4,7})\s*(?:đ|₫|đồng)?",
        "markup": 0.28,
    },
]

_SCRAPE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
}

# ── In-memory cache TTL = 30 phút ─────────────────────────────────────────────
_CACHE: dict[str, tuple[dict, float]] = {}
_CACHE_TTL = 1800


# ── helpers ───────────────────────────────────────────────────────────────────

def _get_gemini_key() -> str | None:
    key = (os.getenv("GOOGLE_API_KEY") or settings.GOOGLE_API_KEY or "").strip()
    if not key or key.startswith("$"):
        key = (os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY or "").strip()
    return key or None


def _parse_price_vnd(text: str) -> int | None:
    patterns = [
        r"(\d{1,3}(?:[.,]\d{3})+)\s*(?:–|-|~|đến)?\s*(?:\d{1,3}(?:[.,]\d{3})+)?\s*(?:đ\b|đồng|vnđ|vnd|₫)",
        r"(\d{4,7})\s*(?:đ\b|đồng|vnđ|vnd|₫)",
        r"(\d{1,3}(?:[.,]\d{3})+)\s*/\s*kg",
        r"(\d{4,7})\s*/\s*kg",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            raw = m.group(1).replace(".", "").replace(",", "")
            try:
                val = int(raw)
                if 500 <= val <= 20_000_000:
                    return val
            except ValueError:
                pass
    return None


def _friendly_error(last_error: str | None) -> str:
    base = "Đang hiển thị ước tính dựa trên giá sỉ + markup thông thường."
    if not last_error:
        return base
    e = last_error.lower()
    if "no_api_key" in e:
        return base
    if "503" in e or "unavailable" in e or "experimental" in e:
        return f"Không lấy được giá realtime (Gemini tạm thời quá tải). {base}"
    if "429" in e or "resource_exhausted" in e:
        return f"Không lấy được giá realtime (vượt giới hạn API). {base}"
    if "timeout" in e:
        return f"Không lấy được giá realtime (timeout). {base}"
    return f"Không lấy được giá realtime. {base}"


def _markup_fallback(crop_name: str, region: str, base_price: int, last_error: str | None) -> dict:
    today = date.today().strftime("%d/%m/%Y")
    stores_out = [
        {
            "id": s["id"],
            "name": s["name"],
            "type": s["type"],
            "price": round(base_price * (1 + s["markup"]) / 1000) * 1000,
            "unit": "đ/kg",
            "is_estimated": True,
        }
        for s in STORES
    ]
    return {
        "stores": stores_out,
        "crop_name": crop_name,
        "region": region,
        "fetched_at": today,
        "source": "estimated",
        "source_name": "Ước tính (giá sỉ + markup thông thường)",
        "confidence": 0.45,
        "warning": _friendly_error(last_error),
        "is_estimated": True,
        "cache_status": "miss",
        "from_cache": False,
    }


# ── Direct store scraper ───────────────────────────────────────────────────────

def _scrape_store(store: dict, crop_name: str, timeout: float = 8.0) -> int | None:
    """
    Thử scrape trang tìm kiếm của chuỗi và trích giá đầu tiên tìm thấy.
    Trả về giá (VNĐ/kg) hoặc None nếu thất bại.
    """
    url = store["search_url"].format(query=crop_name.replace(" ", "+"))
    try:
        with httpx.Client(headers=_SCRAPE_HEADERS, timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return None
            html = resp.text
    except Exception:
        return None

    # Thử parse bằng BeautifulSoup trước
    try:
        from bs4 import BeautifulSoup  # noqa: PLC0415
        soup = BeautifulSoup(html, "html.parser")
        # Tìm trong các thẻ chứa giá phổ biến
        price_selectors = [
            "[class*='price']", "[class*='gia']", "[class*='cost']",
            "span.price", "div.price", "p.price",
            "[data-price]", "[itemprop='price']",
        ]
        for sel in price_selectors:
            for el in soup.select(sel)[:5]:
                price_text = el.get("data-price") or el.get("content") or el.get_text(strip=True)
                price = _parse_price_vnd(price_text or "")
                if price:
                    return price
    except Exception:
        pass

    # Fallback: regex trên raw HTML
    price = _parse_price_vnd(html[:8000])
    return price


def _scrape_all_stores_sync(crop_name: str) -> dict[str, int]:
    """Scrape tất cả chuỗi tuần tự (dùng trong async context qua executor)."""
    found: dict[str, int] = {}
    for store in STORES:
        price = _scrape_store(store, crop_name, timeout=3.0)
        if price:
            found[store["id"]] = price
    return found


# ── Gemini fallback ────────────────────────────────────────────────────────────

async def _fetch_via_gemini(crop_name: str, region: str) -> dict:
    api_key = _get_gemini_key()
    if not api_key:
        return {}

    today = date.today().strftime("%d/%m/%Y")
    store_names = ", ".join(s["name"] for s in STORES)
    prompt = (
        f"Hôm nay {today}, giá bán lẻ của {crop_name} tại {region} Việt Nam "
        f"ở các chuỗi sau là bao nhiêu đồng/kg: {store_names}?\n"
        f"Ghi mỗi chuỗi một dòng, ví dụ: Bách Hóa Xanh: 28.000 đ/kg. "
        f"Nếu không tìm thấy giá tại một chuỗi nào đó thì bỏ qua."
    )
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return {}

    client = genai.Client(api_key=api_key)
    last_error: str | None = None
    # Thử theo thứ tự ưu tiên: model nhẹ/ổn trước, model nặng sau
    model_candidates = [
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash-lite-preview-06-17",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-2.5-flash",
    ]
    for model_name in model_candidates:
        try:
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.1,
                    ),
                ),
                timeout=float(settings.AI_TIMEOUT_SECONDS),
            )
            raw = (getattr(response, "text", None) or "").strip()
            if not raw:
                last_error = "empty_response"
                continue

            # Parse tên chuỗi → giá
            found: dict[str, int] = {}
            lines = raw.split("\n")
            for store in STORES:
                for alias in [store["name"].lower()] + [store["id"]]:
                    for line in lines:
                        if alias in line.lower():
                            price = _parse_price_vnd(line)
                            if price:
                                found[store["id"]] = price
                                break
                    if store["id"] in found:
                        break
            return {"prices": found, "raw": raw, "model": model_name}
        except asyncio.TimeoutError:
            last_error = "timeout"
            break
        except Exception as exc:
            last_error = str(exc)[:120]
            err_text = last_error.lower()
            # 503/429/unavailable → thử model khác; lỗi khác → dừng luôn
            if any(t in err_text for t in ("503", "429", "unavailable", "resource_exhausted", "404", "not_found", "experimental")):
                continue
            break
    return {"error": last_error}


# ── Public entry point ─────────────────────────────────────────────────────────

async def fetch_store_prices(crop_name: str, region: str, base_price: int = 0) -> dict:
    """
    Lấy giá bán lẻ nông sản tại các chuỗi lớn:
      1. Scrape trực tiếp từng trang web chuỗi
      2. Gemini + Google Search (nếu scrape thất bại)
      3. Ước tính markup (nếu cả hai thất bại)
    """
    cache_key = f"{crop_name.lower().strip()}::{region.lower().strip()}"
    now = time.time()
    if cache_key in _CACHE:
        data, ts = _CACHE[cache_key]
        if now - ts < _CACHE_TTL:
            return {**data, "cache_status": "fresh", "from_cache": True}

    today = date.today().strftime("%d/%m/%Y")
    last_error: str | None = None

    # Nếu không có Gemini API key, bỏ qua scraping và Gemini → trả ước tính ngay
    if not _get_gemini_key():
        if base_price <= 0:
            try:
                from app.services.pricing_service import pricing_service  # noqa: PLC0415
                entry = pricing_service.crop_base_prices.get(crop_name) or {}
                raw = entry.get("price") or entry.get("base_price") or 0
                base_price = int(float(raw) * 1000) if raw < 1000 else int(float(raw))
            except Exception:
                pass
        if base_price <= 0:
            base_price = 25_000
        return _markup_fallback(crop_name, region, base_price, "no_api_key_configured")

    # ── Bước 1: scrape trực tiếp ──────────────────────────────────────────────
    loop = asyncio.get_running_loop()
    try:
        scraped = await asyncio.wait_for(
            loop.run_in_executor(None, _scrape_all_stores_sync, crop_name),
            timeout=10.0,
        )
    except Exception as exc:
        scraped = {}
        last_error = str(exc)[:80]

    stores_out = []
    for store in STORES:
        price = scraped.get(store["id"])
        if price:
            stores_out.append({
                "id": store["id"],
                "name": store["name"],
                "type": store["type"],
                "price": price,
                "unit": "đ/kg",
                "source": "direct_scrape",
            })

    if len(stores_out) >= 2:
        result = {
            "stores": stores_out,
            "crop_name": crop_name,
            "region": region,
            "fetched_at": today,
            "source": "direct_scrape",
            "source_name": "Scraped trực tiếp từ trang web chuỗi cửa hàng",
            "confidence": 0.78,
            "cache_status": "miss",
            "from_cache": False,
        }
        _CACHE[cache_key] = (result, now)
        return result

    # ── Bước 2: Gemini fallback ───────────────────────────────────────────────
    gemini_result = await _fetch_via_gemini(crop_name, region)
    if gemini_result.get("prices"):
        prices_by_id: dict[str, int] = gemini_result["prices"]
        # Merge với kết quả scrape (nếu có)
        for store in STORES:
            if store["id"] in scraped and store["id"] not in prices_by_id:
                prices_by_id[store["id"]] = scraped[store["id"]]

        stores_out = []
        for store in STORES:
            price = prices_by_id.get(store["id"])
            if price:
                stores_out.append({
                    "id": store["id"],
                    "name": store["name"],
                    "type": store["type"],
                    "price": price,
                    "unit": "đ/kg",
                    "source": "gemini_search",
                })

        if stores_out:
            result = {
                "stores": stores_out,
                "crop_name": crop_name,
                "region": region,
                "fetched_at": today,
                "source": "gemini_search",
                "source_name": f"Gemini {gemini_result.get('model', '')} + Google Search",
                "model": gemini_result.get("model"),
                "confidence": 0.72,
                "cache_status": "miss",
                "from_cache": False,
            }
            _CACHE[cache_key] = (result, now)
            return result

    last_error = gemini_result.get("error") or last_error

    # ── Bước 3: ước tính markup (luôn chạy) ──────────────────────────────────
    if base_price <= 0:
        base_price = 25_000

    return _markup_fallback(crop_name, region, base_price, last_error)
