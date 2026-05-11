"""
News Impact Service
Tổng hợp tin tức thị trường → tính hệ số tác động giá cho từng cây × vùng.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def _combine_factors(news_items: List[Dict], crop_name: Optional[str] = None,
                     region: Optional[str] = None) -> float:
    """
    Tính hệ số giá tổng hợp từ nhiều tin tức.
    Lọc theo crop và region nếu được chỉ định.
    Cộng dồn có trọng số (tin gần đây quan trọng hơn).
    """
    relevant = []
    for item in news_items:
        # Lọc theo vùng nếu chỉ định
        if region:
            regions = item.get("affected_regions", [])
            if regions and region not in regions:
                continue
        # Lọc theo cây nếu chỉ định
        if crop_name:
            crops = item.get("affected_crops", [])
            if crops and crop_name not in crops:
                continue
        relevant.append(item)

    if not relevant:
        return 1.0

    # Cộng dồn tất cả factor (giới hạn -0.40 đến +0.50)
    net = sum(item.get("price_factor", 0.0) for item in relevant)
    net = max(-0.40, min(0.50, net))
    return round(1.0 + net, 3)


def analyze_market_impact(
    crop_name: Optional[str] = None,
    region: Optional[str] = None,
    max_queries: int = 3,
) -> Dict:
    """
    Pipeline đầy đủ:
    1. Fetch tin tức từ Tavily
    2. Tính hệ số tác động
    3. Trả về báo cáo đầy đủ

    Args:
        crop_name : lọc theo tên cây (None = tất cả)
        region    : lọc theo tỉnh (None = tất cả)
        max_queries: số truy vấn Tavily (mỗi query ≈ 1 credit)
    """
    from app.integrations.news_crawler import fetch_market_news

    news = fetch_market_news(max_queries=max_queries)
    factor = _combine_factors(news, crop_name, region)
    pct = round((factor - 1.0) * 100, 1)

    # Tóm tắt sự kiện nổi bật
    bullish = [n for n in news if n.get("sentiment") == "bullish"]
    bearish = [n for n in news if n.get("sentiment") == "bearish"]

    # Kết luận tổng hợp
    if pct > 10:
        conclusion = f"Tin tức bất lợi (thiên tai, xuất khẩu tăng...) dự báo đẩy giá **tăng ~{pct}%**."
    elif pct < -10:
        conclusion = f"Nguồn cung dư thừa / hàng Trung Quốc tràn vào dự báo kéo giá **giảm ~{abs(pct)}%**."
    elif pct > 0:
        conclusion = f"Thị trường có xu hướng **tăng nhẹ ~{pct}%** do một số yếu tố bất lợi."
    elif pct < 0:
        conclusion = f"Thị trường có xu hướng **giảm nhẹ ~{abs(pct)}%** do nguồn cung tăng."
    else:
        conclusion = "Không có sự kiện nổi bật. Giá dự báo **ổn định**."

    return {
        "news_factor":       factor,
        "price_change_pct":  pct,
        "conclusion":        conclusion,
        "total_news":        len(news),
        "bullish_news":      len(bullish),
        "bearish_news":      len(bearish),
        "top_bullish":       bullish[:3],
        "top_bearish":       bearish[:3],
        "all_news":          news,
        "analyzed_at":       datetime.now().isoformat(),
        "filter_crop":       crop_name,
        "filter_region":     region,
    }


def get_china_trade_impact() -> Dict:
    """Phân tích riêng tác động thương mại Trung Quốc."""
    from app.integrations.news_crawler import fetch_china_trade_news

    news = fetch_china_trade_news()
    factor = _combine_factors(news)
    pct = round((factor - 1.0) * 100, 1)

    # Tách bullish/bearish
    bullish = [n for n in news if n.get("sentiment") == "bullish"]
    bearish = [n for n in news if n.get("sentiment") == "bearish"]

    if pct > 5:
        conclusion = f"Trung Quốc **đang tăng mua** → giá xuất khẩu dự báo tăng ~{pct}%."
    elif pct < -5:
        conclusion = (
            f"Trung Quốc **hạn chế nhập** hoặc hàng TQ tràn vào → "
            f"giá trong nước có thể giảm ~{abs(pct)}%."
        )
    else:
        conclusion = "Thương mại với Trung Quốc **ổn định**, ít tác động đến giá."

    return {
        "news_factor":      factor,
        "price_change_pct": pct,
        "conclusion":       conclusion,
        "news_items":       news,
        "bullish_count":    len(bullish),
        "bearish_count":    len(bearish),
        "analyzed_at":      datetime.now().isoformat(),
    }


def get_disaster_impact(region: Optional[str] = None) -> Dict:
    """Phân tích tác động thiên tai đến giá nông sản."""
    from app.integrations.news_crawler import fetch_disaster_news

    news = fetch_disaster_news(region=region)
    factor = _combine_factors(news, region=region)
    pct = round((factor - 1.0) * 100, 1)

    if pct > 15:
        conclusion = (
            f"Thiên tai **nghiêm trọng** đang ảnh hưởng sản xuất. "
            f"Giá dự kiến tăng mạnh ~{pct}% do khan hàng."
        )
    elif pct > 5:
        conclusion = f"Thiên tai gây ảnh hưởng nhất định, giá tăng nhẹ ~{pct}%."
    else:
        conclusion = "Không có thiên tai nổi bật ảnh hưởng đến giá."

    return {
        "news_factor":      factor,
        "price_change_pct": pct,
        "conclusion":       conclusion,
        "news_items":       news,
        "region_filter":    region,
        "analyzed_at":      datetime.now().isoformat(),
    }


class NewsImpactService:
    """Wrapper class cho backward-compatibility — bọc các module-level functions."""

    def analyze_market_impact(self, crop_name=None, region=None, max_queries=3):
        return analyze_market_impact(crop_name, region, max_queries)

    def get_china_trade_impact(self):
        return get_china_trade_impact()

    def get_disaster_impact(self, region=None):
        return get_disaster_impact(region)

    def get_combined_price_factor(self, crop_name, region, weather_factor=1.0):
        return get_combined_price_factor(crop_name, region, weather_factor)


news_impact_service = NewsImpactService()


def get_combined_price_factor(
    crop_name: str,
    region: str,
    weather_factor: float = 1.0,
) -> Dict:
    """
    Tính hệ số giá tổng hợp từ CẢ HAI nguồn: tin tức + thời tiết.
    Dùng để cung cấp giá dự báo cuối cùng cho người dùng.

    Returns:
        combined_factor : hệ số nhân cuối cùng (áp lên giá thị trường)
        breakdown       : phân tách đóng góp từng nguồn
    """
    from app.integrations.news_crawler import fetch_market_news, fetch_china_trade_news

    # Lấy tin tức (merge cả 2 nguồn)
    general_news = fetch_market_news(max_queries=2)
    china_news   = fetch_china_trade_news()
    all_news = general_news + china_news

    news_factor  = _combine_factors(all_news, crop_name, region)
    news_pct     = round((news_factor - 1.0) * 100, 1)
    weather_pct  = round((weather_factor - 1.0) * 100, 1)

    # Tổng hợp: trung bình có trọng số (tin tức 60%, thời tiết 40%)
    combined = round(news_factor * 0.6 + weather_factor * 0.4, 3)
    combined = max(0.60, min(1.60, combined))
    combined_pct = round((combined - 1.0) * 100, 1)

    return {
        "combined_factor":    combined,
        "combined_pct":       combined_pct,
        "news_factor":        news_factor,
        "news_pct":           news_pct,
        "weather_factor":     weather_factor,
        "weather_pct":        weather_pct,
        "relevant_news":      [n for n in all_news
                               if not n.get("affected_crops")
                               or crop_name in n.get("affected_crops", [])],
        "analyzed_at":        datetime.now().isoformat(),
    }
