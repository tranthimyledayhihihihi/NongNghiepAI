"""
News Crawler — Đọc tin tức nông nghiệp từ Tavily Search.

Phân loại sự kiện → gắn sentiment (bullish/bearish) + hệ số tác động giá.
"""
import logging
import os
import re
from datetime import date, datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def _get_api_key() -> str:
    return os.getenv("TAVILY_API_KEY", "")


# ─── Định nghĩa loại sự kiện ─────────────────────────────────────────────────
# base_factor: dương = giá tăng (khan hàng), âm = giá giảm (dư thừa / cạnh tranh)
# severity_scale: hệ số nhân theo mức độ nghiêm trọng (từ keyword)
EVENT_CATALOG = {
    # ── Thiên tai ──────────────────────────────────────────────────────────
    "lu_lut": {
        "label":       "Lũ lụt / Ngập úng",
        "base_factor": +0.22,
        "sentiment":   "bullish",
        "keywords":    [
            "lũ lụt", "ngập lụt", "ngập úng", "lũ quét", "lũ ống", "vỡ đê",
            "flood", "flooding", "inundation", "flash flood", "levee breach",
        ],
        "severe_kw":   ["nghiêm trọng", "lịch sử", "kỷ lục", "hàng nghìn ha",
                        "severe", "historic", "record", "thousands of hectares"],
    },
    "bao": {
        "label":       "Bão / Áp thấp nhiệt đới",
        "base_factor": +0.28,
        "sentiment":   "bullish",
        "keywords":    [
            "bão số", "siêu bão", "áp thấp nhiệt đới", "cơn bão", "bão đổ bộ",
            "typhoon", "tropical storm", "cyclone", "hurricane", "storm landfall",
        ],
        "severe_kw":   ["cấp 12", "cấp 13", "cấp 14", "siêu bão",
                        "category 4", "category 5", "super typhoon"],
    },
    "han_han": {
        "label":       "Hạn hán / Thiếu nước",
        "base_factor": +0.15,
        "sentiment":   "bullish",
        "keywords":    [
            "hạn hán", "khô hạn", "thiếu nước tưới", "xâm nhập mặn", "nước mặn",
            "drought", "water shortage", "saltwater intrusion", "dry spell",
            "irrigation shortage",
        ],
        "severe_kw":   ["nghiêm trọng", "kéo dài", "lịch sử",
                        "severe drought", "prolonged", "historic"],
    },
    "gia_ret": {
        "label":       "Rét đậm / Sương muối",
        "base_factor": +0.18,
        "sentiment":   "bullish",
        "keywords":    [
            "rét đậm", "rét hại", "giá rét", "sương muối", "băng giá",
            "cold snap", "frost", "freeze", "freezing temperatures", "crop freeze",
        ],
        "severe_kw":   ["dưới 10 độ", "dưới 5 độ", "thiệt hại nặng",
                        "below 10 degrees", "crop damage"],
    },
    "thien_tai_khac": {
        "label":       "Thiên tai khác",
        "base_factor": +0.12,
        "sentiment":   "bullish",
        "keywords":    [
            "sạt lở", "động đất", "cháy rừng", "triều cường",
            "landslide", "earthquake", "wildfire", "forest fire", "storm surge",
        ],
        "severe_kw":   ["nghiêm trọng", "thiệt hại lớn", "severe", "major damage"],
    },
    # ── Thương mại Trung Quốc ──────────────────────────────────────────────
    "tq_tang_mua": {
        "label":       "Trung Quốc tăng mua nông sản VN",
        "base_factor": +0.20,
        "sentiment":   "bullish",
        "keywords":    [
            "trung quốc tăng mua", "xuất khẩu sang trung quốc tăng",
            "trung quốc nhập khẩu nông sản", "thương nhân trung quốc mua",
            "tq thu mua", "china import vietnam",
            "china increases imports", "china buys vietnam", "chinese demand rises",
            "vietnam exports to china surge", "china agricultural imports up",
        ],
        "severe_kw":   ["kỷ lục", "tăng mạnh", "gấp đôi",
                        "record high", "surge", "doubled"],
    },
    "tq_han_che": {
        "label":       "Trung Quốc hạn chế/cấm nhập khẩu",
        "base_factor": -0.28,
        "sentiment":   "bearish",
        "keywords":    [
            "trung quốc hạn chế", "trung quốc cấm", "kiểm soát biên giới",
            "ùn ứ cửa khẩu", "ách tắc cửa khẩu", "tạm ngừng xuất khẩu",
            "trung quốc siết nhập khẩu",
            "china bans", "china restricts imports", "border control tightened",
            "china halts", "export suspension", "trade barrier china",
        ],
        "severe_kw":   ["cấm hoàn toàn", "đóng cửa khẩu", "ùn ứ nghìn xe",
                        "complete ban", "border closed", "thousands of trucks stranded"],
    },
    "hang_tq_tran": {
        "label":       "Hàng Trung Quốc tràn vào thị trường VN",
        "base_factor": -0.22,
        "sentiment":   "bearish",
        "keywords":    [
            "hàng trung quốc tràn vào", "rau trung quốc nhập", "nông sản trung quốc",
            "nhập lậu trung quốc", "hàng nhập trung quốc giá rẻ",
            "chinese goods flood", "cheap chinese imports", "chinese produce Vietnam",
            "smuggled from china",
        ],
        "severe_kw":   ["ồ ạt", "giá rẻ hơn", "khó cạnh tranh",
                        "flooding market", "cheaper", "hard to compete"],
    },
    "tq_mo_cua": {
        "label":       "Trung Quốc mở cửa / nới lỏng xuất nhập khẩu",
        "base_factor": +0.12,
        "sentiment":   "bullish",
        "keywords":    [
            "trung quốc mở cửa", "thông quan trở lại", "nới lỏng kiểm dịch",
            "china reopens", "china eases restrictions", "border reopened",
            "china lifts ban",
        ],
        "severe_kw":   [],
    },
    # ── Thị trường xuất khẩu khác ──────────────────────────────────────────
    "xuat_khau_tang": {
        "label":       "Xuất khẩu nông sản tăng (thị trường khác)",
        "base_factor": +0.12,
        "sentiment":   "bullish",
        "keywords":    [
            "xuất khẩu tăng", "ký hợp đồng xuất khẩu", "mở cửa thị trường mới",
            "export growth", "export surge", "new export market", "trade deal signed",
            "vietnam agriculture export up", "agricultural export record",
        ],
        "severe_kw":   ["kỷ lục", "tăng mạnh", "record", "surge"],
    },
    "xuat_khau_giam": {
        "label":       "Xuất khẩu giảm / khó khăn",
        "base_factor": -0.15,
        "sentiment":   "bearish",
        "keywords":    [
            "xuất khẩu giảm", "khó xuất khẩu", "bị trả hàng", "rào cản kỹ thuật",
            "export decline", "export ban", "trade barrier", "rejected shipment",
            "phytosanitary", "vietnam export slowdown",
        ],
        "severe_kw":   ["giảm mạnh", "cấm xuất", "sharp decline", "ban"],
    },
    # ── Dịch bệnh cây trồng ────────────────────────────────────────────────
    "dich_benh": {
        "label":       "Dịch bệnh cây trồng bùng phát",
        "base_factor": +0.25,
        "sentiment":   "bullish",
        "keywords":    [
            "dịch bệnh", "sâu bệnh bùng phát", "nấm bệnh lây lan",
            "rầy nâu", "bệnh vàng lá", "héo rũ", "khảm lá",
            "crop disease", "plant disease outbreak", "pest infestation",
            "blight", "fungal disease", "crop blight", "locust",
            "brown planthopper", "mosaic virus",
        ],
        "severe_kw":   ["bùng phát", "lan rộng", "hàng nghìn ha",
                        "outbreak", "widespread", "thousands of hectares"],
    },
    # ── Mùa vụ ─────────────────────────────────────────────────────────────
    "duoc_mua": {
        "label":       "Được mùa / Dư thừa sản lượng",
        "base_factor": -0.16,
        "sentiment":   "bearish",
        "keywords":    [
            "được mùa", "trúng mùa", "sản lượng kỷ lục", "dư thừa",
            "ế ẩm", "rớt giá vì dư", "giá rẻ do được mùa",
            "bumper harvest", "record harvest", "oversupply", "surplus",
            "price falls due to glut", "overproduction",
        ],
        "severe_kw":   ["kỷ lục", "dư thừa lớn", "record", "massive surplus"],
    },
    "mat_mua": {
        "label":       "Mất mùa / Thiệt hại sản lượng",
        "base_factor": +0.20,
        "sentiment":   "bullish",
        "keywords":    [
            "mất mùa", "thất thu", "thiệt hại nghiêm trọng", "năng suất giảm",
            "crop failure", "harvest loss", "yield decline", "production shortfall",
            "crop damage", "agricultural loss",
        ],
        "severe_kw":   ["mất hoàn toàn", "thiệt hại lớn", "total loss", "severe damage"],
    },
    # ── Chính sách ─────────────────────────────────────────────────────────
    "chinh_sach_ho_tro": {
        "label":       "Chính sách hỗ trợ nông nghiệp",
        "base_factor": -0.05,
        "sentiment":   "bearish",
        "keywords":    [
            "bình ổn giá", "hỗ trợ nông dân", "trợ giá", "thu mua tạm trữ",
            "price stabilization", "agricultural subsidy", "government support farmers",
            "strategic reserve", "price control",
        ],
        "severe_kw":   [],
    },
    # ── Giá nông sản tăng/giảm (EN) ────────────────────────────────────────
    "gia_tang": {
        "label":       "Giá nông sản tăng mạnh",
        "base_factor": +0.10,
        "sentiment":   "bullish",
        "keywords":    [
            "price rally", "prices soar", "prices jump", "commodity prices rise",
            "agricultural prices surge", "food prices increase",
            "vietnam rice price up", "coffee price rally", "pepper price surge",
        ],
        "severe_kw":   ["soar", "surge", "record high", "skyrocket"],
    },
    "gia_giam": {
        "label":       "Giá nông sản giảm",
        "base_factor": -0.10,
        "sentiment":   "bearish",
        "keywords":    [
            "price drop", "prices fall", "prices slump", "commodity prices decline",
            "agricultural prices down", "food prices decrease",
            "vietnam rice price down", "coffee prices tumble",
        ],
        "severe_kw":   ["plunge", "slump", "crash", "record low"],
    },
}

# ─── Truy vấn Tavily tìm tin tức ────────────────────────────────────────────
_NEWS_QUERIES = [
    "tin tức lũ lụt bão hạn hán ảnh hưởng nông nghiệp Việt Nam",
    "giá nông sản Việt Nam tăng giảm tin tức mới nhất",
    "Trung Quốc nhập khẩu xuất khẩu nông sản Việt Nam",
    "hàng Trung Quốc tràn vào thị trường Việt Nam rau củ quả",
    "thiên tai ảnh hưởng sản xuất nông nghiệp Việt Nam",
    "dịch bệnh cây trồng bùng phát Việt Nam",
    "xuất khẩu nông sản Việt Nam tình hình",
]

# ─── Alias vùng để nhận diện trong bài báo ──────────────────────────────────
_REGION_MENTIONS = {
    "đồng bằng sông cửu long": ["Cần Thơ", "Tiền Giang", "Long An", "Đồng Tháp", "An Giang"],
    "đbscl": ["Cần Thơ", "Tiền Giang", "Long An"],
    "tây nguyên": ["Đắk Lắk", "Gia Lai", "Lâm Đồng"],
    "miền nam": ["TP.HCM", "Cần Thơ", "Tiền Giang"],
    "miền bắc": ["Hà Nội"],
    "miền trung": ["Đà Nẵng"],
    "cả nước": ["TP.HCM", "Hà Nội", "Cần Thơ", "Đà Nẵng", "Đắk Lắk"],
}

# ─── Alias cây trồng để nhận diện trong bài báo ──────────────────────────────
_CROP_MENTIONS = {
    "lúa": "Lúa", "gạo": "Lúa", "thóc": "Lúa",
    "ngô": "Ngô", "bắp": "Ngô",
    "sầu riêng": "Sầu riêng", "sau riêng": "Sầu riêng",
    "cà phê": "Cà phê", "cafe": "Cà phê",
    "hồ tiêu": "Hồ tiêu", "tiêu": "Hồ tiêu",
    "thanh long": "Thanh long",
    "xoài": "Xoài",
    "chuối": "Chuối",
    "rau": None,  # chung — ảnh hưởng nhiều loại rau
    "nông sản": None,  # chung
    "trái cây": None,
}


def _classify_event(title: str, content: str) -> Optional[Dict]:
    """Phân loại sự kiện từ tiêu đề + nội dung bài báo."""
    text = (title + " " + content).lower()
    best_event = None
    best_score = 0

    for event_id, cfg in EVENT_CATALOG.items():
        score = sum(1 for kw in cfg["keywords"] if kw in text)
        if score == 0:
            continue
        # Tăng điểm nếu có keyword nghiêm trọng
        severity = 1.0 + 0.3 * sum(1 for kw in cfg.get("severe_kw", []) if kw in text)
        total = score * severity
        if total > best_score:
            best_score = total
            best_event = (event_id, cfg, severity)

    if not best_event:
        return None

    event_id, cfg, severity = best_event
    factor = round(cfg["base_factor"] * min(severity, 1.8), 3)  # cap severity

    # Nhận diện tỉnh/thành
    affected_regions = []
    for hint, regions in _REGION_MENTIONS.items():
        if hint in text:
            affected_regions.extend(regions)
    # Tìm tên tỉnh trực tiếp
    direct_provinces = [
        "hà nội", "tp.hcm", "cần thơ", "đà nẵng", "đắk lắk",
        "lâm đồng", "gia lai", "tiền giang", "long an", "bình thuận",
        "đồng tháp", "an giang", "bình phước", "đồng nai",
    ]
    for prov in direct_provinces:
        if prov in text:
            affected_regions.append(prov.title().replace("Tp.Hcm", "TP.HCM"))
    affected_regions = list(dict.fromkeys(affected_regions))[:6]

    # Nhận diện cây trồng
    affected_crops = []
    for kw, crop in _CROP_MENTIONS.items():
        if kw in text and crop:
            affected_crops.append(crop)
    affected_crops = list(dict.fromkeys(affected_crops))[:5]

    return {
        "event_type":       event_id,
        "event_label":      cfg["label"],
        "sentiment":        cfg["sentiment"],
        "price_factor":     factor,
        "affected_regions": affected_regions,
        "affected_crops":   affected_crops,
    }


def fetch_market_news(max_queries: int = 4) -> List[Dict]:
    """
    Dùng Tavily Search để lấy tin tức ảnh hưởng thị trường nông sản.
    Trả về list NewsItem đã phân loại sự kiện + hệ số giá.
    """
    if not _get_api_key():
        logger.warning("[News] TAVILY_API_KEY chưa cấu hình")
        return []

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=_get_api_key())
    except ImportError:
        logger.error("[News] tavily-python chưa cài: pip install tavily-python")
        return []

    today = date.today().strftime("%d/%m/%Y")
    news_items: List[Dict] = []
    seen_urls: set = set()

    for query in _NEWS_QUERIES[:max_queries]:
        try:
            resp = client.search(
                query=f"{query} {today}",
                search_depth="basic",
                max_results=5,
                include_answer=False,
                topic="news",          # Tavily news mode
            )
            for r in resp.get("results", []):
                url = r.get("url", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                title   = r.get("title", "")
                content = r.get("content", "")
                pub_date = r.get("published_date") or datetime.now().isoformat()

                event = _classify_event(title, content)
                news_items.append({
                    "title":       title,
                    "url":         url,
                    "summary":     content[:350].strip(),
                    "published_at": pub_date,
                    "source_domain": _extract_domain(url),
                    "event_type":   event["event_type"]   if event else "unknown",
                    "event_label":  event["event_label"]  if event else "Tin tức khác",
                    "sentiment":    event["sentiment"]     if event else "neutral",
                    "price_factor": event["price_factor"]  if event else 0.0,
                    "affected_regions": event["affected_regions"] if event else [],
                    "affected_crops":   event["affected_crops"]   if event else [],
                })
        except Exception as e:
            logger.debug(f"[News] Query '{query}' lỗi: {e}")

    logger.info(f"[News] Lấy được {len(news_items)} tin tức thị trường")
    return news_items


def fetch_china_trade_news() -> List[Dict]:
    """Chuyên tìm tin tức xuất nhập khẩu Trung Quốc."""
    if not _get_api_key():
        return []

    queries = [
        "Trung Quốc nhập khẩu nông sản Việt Nam 2026",
        "Trung Quốc hạn chế cấm nhập khẩu nông sản Việt Nam",
        "hàng Trung Quốc nông sản tràn vào Việt Nam",
        "xuất khẩu Việt Nam sang Trung Quốc cửa khẩu",
    ]
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=_get_api_key())
    except ImportError:
        return []

    results = []
    seen = set()
    today = date.today().strftime("%d/%m/%Y")
    for q in queries:
        try:
            resp = client.search(
                query=f"{q} {today}",
                search_depth="advanced",
                max_results=4,
                include_answer=True,
                topic="news",
            )
            for r in resp.get("results", []):
                url = r.get("url", "")
                if url in seen:
                    continue
                seen.add(url)
                title   = r.get("title", "")
                content = r.get("content", "")
                event   = _classify_event(title, content)
                results.append({
                    "title":        title,
                    "url":          url,
                    "summary":      content[:400].strip(),
                    "published_at": r.get("published_date") or datetime.now().isoformat(),
                    "source_domain": _extract_domain(url),
                    "tavily_answer": resp.get("answer", ""),
                    "event_type":   event["event_type"]   if event else "tq_unknown",
                    "event_label":  event["event_label"]  if event else "Thương mại Trung Quốc",
                    "sentiment":    event["sentiment"]     if event else "neutral",
                    "price_factor": event["price_factor"]  if event else 0.0,
                    "affected_regions": event["affected_regions"] if event else [],
                    "affected_crops":   event["affected_crops"]   if event else [],
                })
        except Exception as e:
            logger.debug(f"[News/China] Lỗi: {e}")

    return results


def fetch_disaster_news(region: Optional[str] = None) -> List[Dict]:
    """Tìm tin tức thiên tai ảnh hưởng nông nghiệp."""
    if not _get_api_key():
        return []

    region_hint = f"tại {region}" if region else "Việt Nam"
    queries = [
        f"lũ lụt bão hạn hán ảnh hưởng nông nghiệp {region_hint}",
        f"thiên tai thiệt hại nông sản {region_hint}",
    ]
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=_get_api_key())
    except ImportError:
        return []

    results = []
    seen = set()
    today = date.today().strftime("%d/%m/%Y")
    for q in queries:
        try:
            resp = client.search(
                query=f"{q} {today}",
                search_depth="advanced",
                max_results=5,
                include_answer=True,
                topic="news",
            )
            for r in resp.get("results", []):
                url = r.get("url", "")
                if url in seen:
                    continue
                seen.add(url)
                title   = r.get("title", "")
                content = r.get("content", "")
                event   = _classify_event(title, content)
                if event and event["sentiment"] == "bullish":  # chỉ giữ tin giá tăng do thiên tai
                    results.append({
                        "title":        title,
                        "url":          url,
                        "summary":      content[:400].strip(),
                        "published_at": r.get("published_date") or datetime.now().isoformat(),
                        "source_domain": _extract_domain(url),
                        "tavily_answer": resp.get("answer", ""),
                        **event,
                    })
        except Exception as e:
            logger.debug(f"[News/Disaster] Lỗi: {e}")

    return results


def _extract_domain(url: str) -> str:
    m = re.search(r"https?://(?:www\.)?([^/]+)", url)
    return m.group(1) if m else url
