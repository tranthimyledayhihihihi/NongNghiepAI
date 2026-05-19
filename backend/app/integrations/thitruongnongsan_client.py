"""
Scraper chính thức cho cổng Thị Trường Nông Sản Việt Nam
  Giá:     https://thitruongnongsan.gov.vn/vn/nguonwmy.aspx
  Tin tức: https://thitruongnongsan.gov.vn/vn/xc0_tin-tuc.html
"""
from __future__ import annotations

import re
import threading
import time
import unicodedata
from datetime import datetime
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings
from app.integrations.base_market_client import BaseMarketClient, MarketPriceResult

BASE_URL = "https://thitruongnongsan.gov.vn"
PRICE_URL = f"{BASE_URL}/vn/nguonwmy.aspx"
NEWS_URL = f"{BASE_URL}/vn/xc0_tin-tuc.html"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": BASE_URL,
}

# Tên chuẩn hóa → biến thể tiếng Việt xuất hiện trên trang
CROP_VARIANTS: dict[str, list[str]] = {
    "lua": ["lúa tẻ", "lúa nếp", "lúa", "thóc"],
    "gao": ["gạo tẻ", "gạo nếp", "gạo"],
    "ca phe": ["cà phê", "café", "robusta", "arabica"],
    "ho tieu": ["hồ tiêu", "tiêu đen", "tiêu sọ", "tiêu"],
    "dieu": ["điều", "hạt điều"],
    "ngo": ["ngô", "bắp ngô", "bắp"],
    "sau rieng": ["sầu riêng"],
    "xoai": ["xoài"],
    "thanh long": ["thanh long"],
    "chuoi": ["chuối"],
    "cam": ["cam sành", "cam"],
    "buoi": ["bưởi"],
    "mit": ["mít"],
    "dua hau": ["dưa hấu"],
    "ca chua": ["cà chua"],
    "dua chuot": ["dưa chuột", "dưa leo"],
    "ot": ["ớt chuông", "ớt"],
    "hanh": ["hành tây", "hành lá", "hành"],
    "toi": ["tỏi"],
    "khoai lang": ["khoai lang"],
    "khoai tay": ["khoai tây"],
    "rau muong": ["rau muống"],
    "cai xanh": ["cải xanh", "cải"],
    "dau nanh": ["đậu nành", "đậu tương"],
    "lac": ["lạc", "đậu phộng"],
    "mia": ["mía"],
    "dua": ["dừa"],
    "tieu": ["hồ tiêu", "tiêu"],
}


def _norm(text: str) -> str:
    """Chuẩn hoá tiếng Việt để so sánh không phân biệt dấu."""
    text = unicodedata.normalize("NFD", (text or "").lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text.replace("đ", "d")).strip()


class ThiTruongNongSanClient(BaseMarketClient):
    """Scraper cho thitruongnongsan.gov.vn – nguồn giá và tin tức chính thức của Bộ NN&PTNT."""

    # class-level in-memory cache để tất cả instance chia sẻ
    _price_rows: list[dict] = []
    _price_fetched_at: float = 0.0
    _news_items: list[dict] = []
    _news_fetched_at: float = 0.0
    _PRICE_TTL = 3600   # 1 giờ
    _NEWS_TTL = 7200    # 2 giờ
    _fetching: dict[str, bool] = {"price": False, "news": False}  # lock per type

    # ──────────────────────────── public API ────────────────────────────

    def get_current_price(
        self,
        crop_name: str,
        region: str | None = None,
        quality_grade: str = "grade_1",  # noqa: ARG002
        **kwargs: Any,
    ) -> MarketPriceResult | None:
        rows = self._get_price_rows()
        if not rows:
            return None

        norm_input = _norm(crop_name)
        variants = [_norm(v) for v in CROP_VARIANTS.get(norm_input, [])]
        if not variants:
            variants = [norm_input]

        target_region = _norm(region or "")
        best: dict | None = None

        for row in rows:
            name_n = _norm(row.get("name", ""))
            region_n = _norm(row.get("region", ""))
            # Kiểm tra tên nông sản có khớp không
            name_ok = any(v in name_n or name_n.startswith(v) for v in variants)
            if not name_ok:
                continue
            # Ưu tiên khớp khu vực
            region_ok = not target_region or (target_region in region_n or region_n in target_region)
            if region_ok:
                best = row
                break
            if best is None:
                best = row  # lưu kết quả bất kỳ để dùng nếu không có khớp khu vực

        if not best:
            return None

        return MarketPriceResult(
            crop_name=crop_name,
            region=best.get("region") or region or "Vietnam",
            price=float(best["price"]),
            unit="VNĐ/kg",
            currency="VND",
            source_type="local_agriculture",
            source_name="Thị trường nông sản Việt Nam (thitruongnongsan.gov.vn)",
            source_url=PRICE_URL,
            observed_at=_parse_vn_date(best.get("date", "")),
            fetched_at=datetime.now(),
            confidence_score=0.83,
            is_realtime=True,
            metadata={"raw_name": best.get("name"), "unit": best.get("unit", "đ/kg")},
        )

    def get_price_history(
        self,
        crop_name: str,
        region: str | None = None,
        days: int = 30,  # noqa: ARG002
        **kwargs: Any,
    ) -> list[MarketPriceResult]:
        # Trang chỉ cung cấp snapshot ngày hôm nay
        result = self.get_current_price(crop_name, region)
        return [result] if result else []

    def search_market_news(self, limit: int = 20, **kwargs: Any) -> list[dict]:
        return self._get_news_items()[:limit]

    def enabled(self) -> bool:
        return bool(getattr(settings, "THITRUONGNONGSAN_ENABLED", True))

    def _trigger_background_fetch(self, kind: str) -> None:
        """Chạy HTTP fetch trong daemon thread – không bao giờ block event loop."""
        if ThiTruongNongSanClient._fetching.get(kind):
            return  # đang fetch rồi, bỏ qua
        ThiTruongNongSanClient._fetching[kind] = True

        def _run():
            try:
                if kind == "price":
                    rows = self._fetch_price_page()
                    ThiTruongNongSanClient._price_rows = rows
                    ThiTruongNongSanClient._price_fetched_at = time.time()
                else:
                    items = self._fetch_news_page()
                    ThiTruongNongSanClient._news_items = items
                    ThiTruongNongSanClient._news_fetched_at = time.time()
            except Exception:
                pass
            finally:
                ThiTruongNongSanClient._fetching[kind] = False

        threading.Thread(target=_run, daemon=True, name=f"ttngs-{kind}").start()

    # ──────────────────────────── price fetching ────────────────────────────

    def _get_price_rows(self) -> list[dict]:
        """Trả về từ cache ngay; nếu cache cũ/rỗng → trigger background refresh, không block."""
        now = time.time()
        if ThiTruongNongSanClient._price_rows and (now - ThiTruongNongSanClient._price_fetched_at) < self._PRICE_TTL:
            return ThiTruongNongSanClient._price_rows
        self._trigger_background_fetch("price")
        return ThiTruongNongSanClient._price_rows  # có thể rỗng nếu lần đầu

    def _fetch_price_page(self) -> list[dict]:
        try:
            with self._make_client() as client:
                resp = client.get(PRICE_URL)
                resp.raise_for_status()
                return self._parse_price_html(resp.text)
        except Exception:
            return []

    def _parse_price_html(self, html: str) -> list[dict]:
        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception:
            return []

        rows: list[dict] = []

        for table in soup.find_all("table"):
            # Kiểm tra đây có phải bảng giá không
            all_text = _norm(table.get_text(" ", strip=True))
            price_signals = ["gia", "dong", "kg", "mat hang", "nong san"]
            if not any(s in all_text for s in price_signals):
                continue

            col = self._detect_col_indices(table)
            if col.get("price") is None:
                continue

            trs = table.find_all("tr")
            for tr in trs[1:]:  # bỏ hàng tiêu đề
                cells = tr.find_all(["td", "th"])
                row = self._extract_price_row(cells, col)
                if row:
                    rows.append(row)

            if rows:
                break  # Dùng bảng đầu tiên tìm thấy

        if not rows:
            rows = self._regex_price_parse(html)

        return rows

    def _detect_col_indices(self, table) -> dict[str, int | None]:
        col: dict[str, int | None] = {"name": None, "price": None, "unit": None, "region": None, "date": None}
        for tr in table.find_all("tr")[:4]:
            cells = tr.find_all(["th", "td"])
            for i, cell in enumerate(cells):
                t = _norm(cell.get_text(" ", strip=True))
                if col["name"] is None and any(k in t for k in ["mat hang", "ten hang", "nong san", "san pham", "loai hang"]):
                    col["name"] = i
                if col["price"] is None and any(k in t for k in ["gia", "don gia", "gia ban", "gia ca"]):
                    col["price"] = i
                if col["unit"] is None and any(k in t for k in ["don vi", "dv", "dvt"]):
                    col["unit"] = i
                if col["region"] is None and any(k in t for k in ["khu vuc", "dia diem", "noi", "tinh", "vung", "thi truong"]):
                    col["region"] = i
                if col["date"] is None and any(k in t for k in ["ngay", "thoi gian", "date"]):
                    col["date"] = i
        # Mặc định nếu không detect được
        if col["name"] is None:
            col["name"] = 0
        if col["price"] is None:
            # Thử tìm cột nào có số tiền
            col["price"] = 1
        return col

    def _extract_price_row(self, cells: list, col: dict) -> dict | None:
        def text(idx: int | None) -> str:
            if idx is None or idx >= len(cells):
                return ""
            return cells[idx].get_text(" ", strip=True).strip()

        name = text(col.get("name"))
        price_val = _parse_price_str(text(col.get("price")))
        if not price_val or not name or len(name) < 2:
            return None
        return {
            "name": name,
            "price": price_val,
            "unit": text(col.get("unit")) or "đ/kg",
            "region": text(col.get("region")) or "Vietnam",
            "date": text(col.get("date")) or "",
        }

    def _regex_price_parse(self, html: str) -> list[dict]:
        """Fallback: trích giá bằng regex khi không parse được bảng."""
        rows = []
        clean = re.sub(r"<[^>]+>", " ", html)
        # Tìm các mẫu "Tên hàng ... 12.000 đ/kg"
        pattern = re.compile(
            r"([A-Za-zÀ-ỹ][A-Za-zÀ-ỹ\s]{2,29}?)\s+"
            r"(\d{1,3}(?:[.,]\d{3})+|\d{4,7})\s*"
            r"(?:đ|đồng|vnđ|vnd)?(?:/kg|/tan)?",
            re.IGNORECASE,
        )
        seen: set[str] = set()
        for m in pattern.finditer(clean):
            name = m.group(1).strip()
            price = _parse_price_str(m.group(2))
            if price and name and _norm(name) not in seen:
                seen.add(_norm(name))
                rows.append({"name": name, "price": price, "unit": "đ/kg", "region": "Vietnam", "date": ""})
            if len(rows) >= 50:
                break
        return rows

    # ──────────────────────────── news fetching ────────────────────────────

    def _get_news_items(self) -> list[dict]:
        """Trả về từ cache; nếu cache rỗng → fetch đồng bộ lần đầu; nếu cache cũ → background refresh."""
        now = time.time()
        if ThiTruongNongSanClient._news_items and (now - ThiTruongNongSanClient._news_fetched_at) < self._NEWS_TTL:
            return ThiTruongNongSanClient._news_items
        if not ThiTruongNongSanClient._news_items:
            # Lần đầu gọi: fetch đồng bộ để có dữ liệu ngay
            self._blocking_news_fetch()
        else:
            # Cache cũ: refresh nền, trả dữ liệu cũ luôn
            self._trigger_background_fetch("news")
        return ThiTruongNongSanClient._news_items

    def _blocking_news_fetch(self) -> None:
        """Fetch đồng bộ lần đầu (gọi từ sync thread, không block event loop)."""
        if ThiTruongNongSanClient._fetching.get("news"):
            return
        ThiTruongNongSanClient._fetching["news"] = True
        try:
            items = self._fetch_news_page()
            if items:
                ThiTruongNongSanClient._news_items = items
                ThiTruongNongSanClient._news_fetched_at = time.time()
        except Exception:
            pass
        finally:
            ThiTruongNongSanClient._fetching["news"] = False

    def _fetch_news_page(self) -> list[dict]:
        try:
            with self._make_client() as client:
                resp = client.get(NEWS_URL)
                resp.raise_for_status()
                return self._parse_news_html(resp.text)
        except Exception:
            return []

    def _parse_news_html(self, html: str) -> list[dict]:
        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception:
            return []

        items: list[dict] = []

        # Thử nhiều selector phổ biến của trang tin tức Việt Nam
        candidates = []
        for sel in [
            "article", ".news-item", ".item-news", ".article-item",
            ".list-news li", "ul.list li", ".tin-tuc-item",
            ".content-news li", "div.row div.col",
        ]:
            found = soup.select(sel)
            if len(found) >= 2:
                candidates = found
                break

        if not candidates:
            # Fallback: lấy tất cả thẻ <a> trỏ đến bài viết
            candidates = soup.find_all("a", href=re.compile(r"\.html|\.aspx|/tin-|/news|/bai-viet"))

        for el in candidates[:30]:
            item = self._extract_news_item(el)
            if item:
                items.append(item)

        return items

    def _extract_news_item(self, el) -> dict | None:
        # Lấy link
        link = el if el.name == "a" else el.find("a", href=True)
        if not link:
            return None
        href = link.get("href", "").strip()
        if not href:
            return None
        if href.startswith("/"):
            href = BASE_URL + href
        elif not href.startswith("http"):
            href = BASE_URL + "/" + href

        # Tiêu đề
        title_el = el.find(["h1", "h2", "h3", "h4"]) or link
        title = re.sub(r"\s+", " ", title_el.get_text(" ", strip=True)).strip()
        if not title or len(title) < 8:
            return None

        # Tóm tắt
        summary_el = el.find("p") or el.find(class_=re.compile(r"summary|desc|mo-ta|sapo"))
        summary = re.sub(r"\s+", " ", summary_el.get_text(" ", strip=True)).strip() if summary_el else ""

        # Ngày
        date_el = (
            el.find("time")
            or el.find(class_=re.compile(r"date|ngay|time"))
            or el.find(attrs={"datetime": True})
        )
        date_str = ""
        if date_el:
            date_str = date_el.get("datetime") or date_el.get_text(strip=True)
        pub_at = _parse_vn_date(date_str)

        # Tự động phân loại sentiment đơn giản
        text_lower = _norm(title + " " + summary)
        positive = sum(w in text_lower for w in ["tang", "xuat khau", "don hang", "duoc gia", "co hoi", "tich cuc"])
        negative = sum(w in text_lower for w in ["giam", "dich", "bao", "han hán", "rui ro", "sut giam"])
        sentiment = "positive" if positive > negative else "negative" if negative > positive else "neutral"

        return {
            "title": title,
            "summary": summary or title,
            "content": None,
            "url": href,
            "source_url": href,
            "source_name": "Thị trường nông sản Việt Nam (gov.vn)",
            "published_at": pub_at.isoformat(),
            "fetched_at": datetime.now().isoformat(),
            "region": None,
            "sentiment": sentiment,
            "impact_level": "medium",
            "impact_score": 0.65 if sentiment != "neutral" else 0.5,
            "crop_tags": [],
            "region_tags": [],
            "is_realtime": True,
        }

    # ──────────────────────────── helpers ────────────────────────────

    def _make_client(self) -> httpx.Client:
        timeout = httpx.Timeout(
            connect=float(getattr(settings, "EXTERNAL_CONNECT_TIMEOUT_SECONDS", 5)),
            read=float(getattr(settings, "EXTERNAL_READ_TIMEOUT_SECONDS", 15)),
            write=float(getattr(settings, "EXTERNAL_WRITE_TIMEOUT_SECONDS", 10)),
            pool=float(getattr(settings, "EXTERNAL_POOL_TIMEOUT_SECONDS", 5)),
        )
        return httpx.Client(headers=_HEADERS, timeout=timeout, follow_redirects=True)


# ── helpers độc lập ────────────────────────────────────────────────────────────

def _parse_price_str(text: str) -> float | None:
    if not text:
        return None
    clean = text.replace(".", "").replace(",", "").replace("\xa0", "").replace(" ", "")
    m = re.search(r"\d{3,8}", clean)
    if m:
        val = int(m.group())
        if 500 <= val <= 20_000_000:
            return float(val)
    return None


def _parse_vn_date(text: str) -> datetime:
    text = (text or "").strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text[:len(fmt)], fmt)
        except (ValueError, IndexError):
            pass
    return datetime.now()


thitruongnongsan_client = ThiTruongNongSanClient()
