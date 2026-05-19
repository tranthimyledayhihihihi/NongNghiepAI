"""
Lấy giá nông sản tại các chuỗi cửa hàng lớn Việt Nam.

Ưu tiên:
  1. DB cache (StorePrices, TTL 2h) — trả ngay
  2. Gemini + Google Search grounding → lưu DB (background)
  3. Scrape trực tiếp (fallback nếu Gemini thất bại) → lưu DB
  4. Ước tính markup (luôn available khi không có API)
"""
from __future__ import annotations

import asyncio
import os
import re
import threading
from datetime import date, datetime, timedelta
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

# In-memory set để tránh clear cache trùng lặp khi background fetch xong
_CACHE: dict[str, tuple[dict, float]] = {}


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

async def _fetch_via_gemini(crop_name: str, region: str, timeout: float | None = None) -> dict:
    api_key = _get_gemini_key()
    if not api_key:
        return {}

    # Timeout mỗi model = tối đa 8s hoặc phần budget còn lại, tối thiểu 3s
    per_model_timeout = min(8.0, max(3.0, timeout or 8.0))

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
                timeout=per_model_timeout,
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


# ── DB helpers ─────────────────────────────────────────────────────────────────

_DB_TTL_HOURS = 2  # dữ liệu DB còn hạn nếu FetchedAt < 2 giờ trước


def _load_from_db(crop_name: str, region: str) -> dict | None:
    """Đọc giá chuỗi cửa hàng từ DB nếu còn trong TTL."""
    try:
        from app.core.database import SessionLocal  # noqa: PLC0415
        from app.models.store_price import StorePrice  # noqa: PLC0415

        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(hours=_DB_TTL_HOURS)
            rows = (
                db.query(StorePrice)
                .filter(
                    StorePrice.CropName == crop_name,
                    StorePrice.Region == region,
                    StorePrice.FetchedAt >= cutoff,
                )
                .all()
            )
            if not rows:
                return None
            stores_out = [
                {
                    "id": r.StoreID,
                    "name": r.StoreName,
                    "type": r.StoreType or "",
                    "price": r.Price,
                    "unit": r.Unit or "đ/kg",
                    "source": r.Source or "db",
                }
                for r in rows
            ]
            fetched_at = max(r.FetchedAt for r in rows).strftime("%d/%m/%Y %H:%M")
            source_model = rows[0].SourceModel or ""
            return {
                "stores": stores_out,
                "crop_name": crop_name,
                "region": region,
                "fetched_at": fetched_at,
                "source": rows[0].Source or "db",
                "source_name": f"Gemini {source_model} + Google Search (DB cache)" if source_model else "DB cache",
                "confidence": 0.72,
                "cache_status": "from_db",
                "from_cache": True,
            }
        finally:
            db.close()
    except Exception:
        return None


def _save_to_db(crop_name: str, region: str, stores_out: list[dict], source: str, model_name: str = "") -> None:
    """Lưu giá chuỗi cửa hàng vào DB (xoá dữ liệu cũ trước)."""
    try:
        from app.core.database import SessionLocal  # noqa: PLC0415
        from app.models.store_price import StorePrice  # noqa: PLC0415

        db = SessionLocal()
        try:
            db.query(StorePrice).filter(
                StorePrice.CropName == crop_name,
                StorePrice.Region == region,
            ).delete(synchronize_session=False)
            now = datetime.utcnow()
            for s in stores_out:
                db.add(StorePrice(
                    CropName=crop_name,
                    Region=region,
                    StoreID=s["id"],
                    StoreName=s["name"],
                    StoreType=s.get("type", ""),
                    Price=s["price"],
                    Unit=s.get("unit", "đ/kg"),
                    Source=source,
                    SourceModel=model_name,
                    FetchedAt=now,
                    UpdatedAt=now,
                ))
            db.commit()
        finally:
            db.close()
    except Exception:
        pass


# Lock để tránh chạy nhiều background fetch cùng lúc cho cùng key
_BG_FETCHING: set[str] = set()


def _background_fetch(crop_name: str, region: str, base_price: int) -> None:
    """Fetch giá Gemini trong background thread và lưu vào DB."""
    key = f"{crop_name}::{region}"
    if key in _BG_FETCHING:
        return
    _BG_FETCHING.add(key)

    async def _run():
        try:
            # Thử Gemini (8s per model)
            gemini_result = await _fetch_via_gemini(crop_name, region, timeout=8.0)
            if gemini_result.get("prices"):
                prices_by_id = gemini_result["prices"]
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
                    _save_to_db(crop_name, region, stores_out, "gemini_search", gemini_result.get("model", ""))
                    # Xoá in-memory cache để lần sau đọc từ DB
                    _CACHE.pop(f"{crop_name.lower().strip()}::{region.lower().strip()}", None)
                    return

            # Thử scraping nếu Gemini thất bại
            loop = asyncio.get_running_loop()
            scraped = await asyncio.wait_for(
                loop.run_in_executor(None, _scrape_all_stores_sync, crop_name),
                timeout=10.0,
            )
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
                _save_to_db(crop_name, region, stores_out, "direct_scrape")
                _CACHE.pop(f"{crop_name.lower().strip()}::{region.lower().strip()}", None)
        except Exception:
            pass
        finally:
            _BG_FETCHING.discard(key)

    def _thread():
        try:
            asyncio.run(_run())
        except Exception:
            pass
        finally:
            _BG_FETCHING.discard(key)

    threading.Thread(target=_thread, daemon=True, name=f"store-price-{crop_name}").start()


# ── Public entry point (DB-first) ─────────────────────────────────────────────

async def fetch_store_prices(crop_name: str, region: str, base_price: int = 0) -> dict:
    """
    1. Trả DB cache ngay nếu còn hạn (< 2h)
    2. Nếu không có DB data → trả markup + trigger background fetch
    3. Background fetch lưu vào DB → lần sau request sẽ thấy giá thực
    """
    # Bước 1: Đọc DB
    db_data = _load_from_db(crop_name, region)
    if db_data:
        return db_data

    # Bước 2: Trigger background fetch (nếu có API key)
    if _get_gemini_key():
        _background_fetch(crop_name, region, base_price)

    # Bước 3: Trả markup ngay (không chờ background)
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

    result = _markup_fallback(crop_name, region, base_price, None)
    # Thêm thông báo về background fetch
    if _get_gemini_key():
        result["warning"] = (
            "Đang tải giá thực từ chuỗi cửa hàng. "
            "Vui lòng bấm 'Phân tích thị trường' lại sau 15 giây để xem giá cập nhật."
        )
    return result
