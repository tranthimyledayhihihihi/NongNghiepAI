"""
News Market Impact API — Đọc tin tức → phân tích tác động giá nông sản.

Tất cả endpoint đều hiển thị đầy đủ trong Swagger UI (/docs).
"""
import asyncio
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter(prefix="/api/news", tags=["📰 Tin tức & Tác động Thị trường"])


# ─── Pydantic schemas (hiển thị trong Swagger) ───────────────────────────────

class NewsItem(BaseModel):
    title:            str   = Field(..., description="Tiêu đề bài báo")
    url:              str   = Field(..., description="URL nguồn")
    summary:          str   = Field(..., description="Tóm tắt nội dung (350 ký tự đầu)")
    published_at:     str   = Field(..., description="Thời gian đăng (ISO format)")
    source_domain:    str   = Field(..., description="Tên miền nguồn báo")
    event_type:       str   = Field(..., description="Loại sự kiện phân loại tự động")
    event_label:      str   = Field(..., description="Tên sự kiện tiếng Việt")
    sentiment:        str   = Field(..., description="'bullish' (giá tăng) | 'bearish' (giá giảm) | 'neutral'")
    price_factor:     float = Field(..., description="Hệ số tác động giá (-0.40 đến +0.50)")
    affected_regions: List[str] = Field(default=[], description="Tỉnh/thành bị ảnh hưởng")
    affected_crops:   List[str] = Field(default=[], description="Loại nông sản bị ảnh hưởng")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Lũ lụt nghiêm trọng tại Đồng bằng sông Cửu Long",
                "url": "https://vnexpress.net/...",
                "summary": "Lũ lụt kéo dài tại Cần Thơ, Tiền Giang làm ngập hàng nghìn ha lúa...",
                "published_at": "2026-05-07T08:30:00",
                "source_domain": "vnexpress.net",
                "event_type": "lu_lut",
                "event_label": "Lũ lụt / Ngập úng",
                "sentiment": "bullish",
                "price_factor": 0.22,
                "affected_regions": ["Cần Thơ", "Tiền Giang", "Long An"],
                "affected_crops": ["Lúa"],
            }
        }


class MarketImpactResponse(BaseModel):
    news_factor:      float = Field(..., description="Hệ số điều chỉnh giá tổng hợp (1.0 = không đổi)")
    price_change_pct: float = Field(..., description="% thay đổi giá dự báo")
    conclusion:       str   = Field(..., description="Kết luận phân tích bằng tiếng Việt")
    total_news:       int   = Field(..., description="Tổng số tin tức thu thập")
    bullish_news:     int   = Field(..., description="Số tin dự báo giá tăng")
    bearish_news:     int   = Field(..., description="Số tin dự báo giá giảm")
    top_bullish:      List[NewsItem] = Field(default=[], description="Top 3 tin dự báo tăng")
    top_bearish:      List[NewsItem] = Field(default=[], description="Top 3 tin dự báo giảm")
    all_news:         List[NewsItem] = Field(default=[], description="Toàn bộ tin tức")
    analyzed_at:      str   = Field(..., description="Thời điểm phân tích")
    filter_crop:      Optional[str] = Field(None, description="Bộ lọc cây trồng")
    filter_region:    Optional[str] = Field(None, description="Bộ lọc vùng")


class ChinaTradeResponse(BaseModel):
    news_factor:      float = Field(..., description="Hệ số tác động từ thương mại TQ")
    price_change_pct: float = Field(..., description="% thay đổi giá ước tính")
    conclusion:       str   = Field(..., description="Kết luận về tình hình thương mại Trung Quốc")
    bullish_count:    int   = Field(..., description="Số tin TQ tăng mua (giá nông sản tăng)")
    bearish_count:    int   = Field(..., description="Số tin TQ hạn chế / hàng TQ tràn vào")
    news_items:       List[NewsItem] = Field(default=[], description="Tin tức thương mại TQ")
    analyzed_at:      str   = Field(...)


class DisasterResponse(BaseModel):
    news_factor:      float = Field(..., description="Hệ số tác động từ thiên tai")
    price_change_pct: float = Field(..., description="% tăng giá do khan hàng")
    conclusion:       str   = Field(...)
    news_items:       List[NewsItem] = Field(default=[], description="Tin tức thiên tai")
    region_filter:    Optional[str]  = Field(None)
    analyzed_at:      str   = Field(...)


class CombinedPriceFactorResponse(BaseModel):
    combined_factor:  float = Field(..., description="Hệ số giá tổng hợp (tin tức 60% + thời tiết 40%)")
    combined_pct:     float = Field(..., description="% thay đổi giá cuối cùng")
    news_factor:      float = Field(..., description="Hệ số từ tin tức thị trường")
    news_pct:         float = Field(..., description="% đóng góp từ tin tức")
    weather_factor:   float = Field(..., description="Hệ số từ thời tiết (đầu vào)")
    weather_pct:      float = Field(..., description="% đóng góp từ thời tiết")
    relevant_news:    List[NewsItem] = Field(default=[], description="Tin liên quan đến cây/vùng")
    analyzed_at:      str   = Field(...)


class NewsAdjustedPriceResponse(BaseModel):
    crop_name:        str   = Field(...)
    region:           str   = Field(...)
    base_price:       float = Field(..., description="Giá thị trường hiện tại (VNĐ/kg)")
    news_factor:      float = Field(...)
    news_adjusted_price: float = Field(..., description="Giá sau điều chỉnh tin tức (VNĐ/kg)")
    price_change_pct: float = Field(...)
    conclusion:       str   = Field(...)
    top_news:         List[NewsItem] = Field(default=[], description="Top tin tức ảnh hưởng")
    unit:             str   = Field(default="VNĐ/kg")


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get(
    "/market-impact",
    response_model=MarketImpactResponse,
    summary="Phân tích tác động tin tức đến thị trường",
    description="""
Đọc tin tức nông nghiệp từ Tavily Search, tự động phân loại sự kiện và tính hệ số tác động giá.

**Loại sự kiện được nhận diện:**
- 🌊 Lũ lụt / Bão / Hạn hán → giá **TĂNG** (khan hàng, vận chuyển khó)
- 🇨🇳 Trung Quốc tăng mua → giá **TĂNG** (nhu cầu ngoại tăng)
- 🇨🇳 Trung Quốc hạn chế nhập / hàng TQ tràn vào → giá **GIẢM**
- 🌾 Được mùa / Dư thừa → giá **GIẢM**
- 🦠 Dịch bệnh cây trồng → giá **TĂNG** (sản lượng giảm)

**Lưu ý:** Cần cấu hình `TAVILY_API_KEY` trong `.env`.
    """,
)
async def get_market_impact(
    crop_name: Optional[str] = Query(None, description="Lọc theo tên cây (ví dụ: Sầu riêng). Bỏ trống = tất cả"),
    region:    Optional[str] = Query(None, description="Lọc theo tỉnh (ví dụ: Đắk Lắk). Bỏ trống = tất cả"),
    max_queries: int = Query(3, ge=1, le=6, description="Số truy vấn Tavily (1 query = 1 API credit)"),
):
    from app.services.news_impact_service import analyze_market_impact
    result = await asyncio.to_thread(analyze_market_impact, crop_name, region, max_queries)
    return result


@router.get(
    "/china-trade",
    response_model=ChinaTradeResponse,
    summary="Tin tức thương mại Trung Quốc",
    description="""
Chuyên theo dõi tin tức xuất nhập khẩu Trung Quốc — yếu tố quan trọng nhất ảnh hưởng giá nông sản VN.

**Phân tích:**
- TQ tăng mua sầu riêng, lúa gạo, cà phê → giá trong nước **TĂNG**
- TQ hạn chế nhập, kiểm soát biên giới → hàng ùn ứ → giá **GIẢM mạnh**
- Hàng TQ (rau củ giá rẻ) tràn vào VN → cạnh tranh → giá **GIẢM**
- TQ mở cửa thị trường mới → cơ hội → giá **TĂNG nhẹ**
    """,
)
async def get_china_trade_news():
    from app.services.news_impact_service import get_china_trade_impact
    return await asyncio.to_thread(get_china_trade_impact)


@router.get(
    "/disasters",
    response_model=DisasterResponse,
    summary="Tin tức thiên tai ảnh hưởng nông nghiệp",
    description="""
Theo dõi các sự kiện thiên tai: lũ lụt, bão, hạn hán, rét đậm, sạt lở...

Thiên tai → phá hủy cây trồng, cản trở vận chuyển → **nguồn cung giảm → giá TĂNG**.

Dùng để cảnh báo nông dân và dự báo giá ngắn hạn.
    """,
)
async def get_disaster_news(
    region: Optional[str] = Query(None, description="Tỉnh/thành cần theo dõi (ví dụ: Cần Thơ). Bỏ trống = cả nước"),
):
    from app.services.news_impact_service import get_disaster_impact
    return await asyncio.to_thread(get_disaster_impact, region)


@router.get(
    "/combined-factor",
    response_model=CombinedPriceFactorResponse,
    summary="Hệ số giá tổng hợp (tin tức + thời tiết)",
    description="""
Tính hệ số điều chỉnh giá CUỐI CÙNG từ hai nguồn:
- **Tin tức thị trường** (60%): thiên tai, thương mại TQ, dịch bệnh...
- **Thời tiết 7 ngày tới** (40%): mưa lớn, hạn hán, nắng nóng...

**Công thức:**
```
combined_factor = news_factor × 0.6 + weather_factor × 0.4
final_price     = base_price × combined_factor
```

Kết quả được giới hạn trong khoảng [0.60, 1.60] để tránh nhiễu.
    """,
)
async def get_combined_factor(
    crop_name:      str   = Query(..., description="Tên cây trồng (ví dụ: Sầu riêng)"),
    region:         str   = Query(..., description="Tỉnh/thành (ví dụ: Đắk Lắk)"),
    weather_factor: float = Query(1.0, ge=0.5, le=2.0,
                                  description="Hệ số thời tiết từ /api/pricing/weather-forecast"),
):
    from app.services.news_impact_service import get_combined_price_factor
    return await asyncio.to_thread(get_combined_price_factor, crop_name, region, weather_factor)


@router.get(
    "/price-with-news",
    response_model=NewsAdjustedPriceResponse,
    summary="Giá nông sản điều chỉnh theo tin tức thị trường",
    description="""
Lấy giá thị trường từ DB → điều chỉnh theo tin tức nông nghiệp mới nhất → trả về giá đề xuất.

**Quy trình:**
1. Đọc giá thị trường gần nhất từ `MarketPrices`
2. Fetch tin tức từ Tavily (thiên tai, TQ, dịch bệnh...)
3. Tính hệ số tác động
4. Trả về giá điều chỉnh + danh sách tin tức liên quan

Dùng kết hợp với `/api/pricing/weather-forecast` để có giá đầy đủ nhất.
    """,
)
async def get_price_with_news(
    crop_name: str = Query(..., description="Tên cây trồng (ví dụ: Lúa)"),
    region:    str = Query(..., description="Tỉnh/thành (ví dụ: Cần Thơ)"),
    db: Session = Depends(get_db),
):
    # Lấy giá hiện tại từ DB
    base_price = await asyncio.to_thread(_get_base_price, db, crop_name, region)

    # Lấy tác động tin tức
    from app.services.news_impact_service import analyze_market_impact
    impact = await asyncio.to_thread(analyze_market_impact, crop_name, region, max_queries=2)

    factor    = impact["news_factor"]
    adjusted  = round(base_price * factor, -2)
    pct       = impact["price_change_pct"]
    top_news  = (impact["top_bullish"] + impact["top_bearish"])[:5]

    return {
        "crop_name":             crop_name,
        "region":                region,
        "base_price":            base_price,
        "news_factor":           factor,
        "news_adjusted_price":   adjusted,
        "price_change_pct":      pct,
        "conclusion":            impact["conclusion"],
        "top_news":              top_news,
        "unit":                  "VNĐ/kg",
    }


def _get_base_price(db: Session, crop_name: str, region: str) -> float:
    """Lấy giá mới nhất từ MarketPrices."""
    try:
        from app.models.crop import CropType
        from app.models.price import MarketPrice
        from sqlalchemy import desc

        crop = (
            db.query(CropType).filter(CropType.CropName == crop_name).first()
            or db.query(CropType).filter(CropType.CropName.ilike(f"%{crop_name}%")).first()
        )
        if not crop:
            return 0.0
        row = (
            db.query(MarketPrice)
            .filter(MarketPrice.CropID == crop.CropID, MarketPrice.Region == region)
            .order_by(desc(MarketPrice.PriceDate))
            .first()
        )
        if row:
            return float(row.PricePerKg)
        # Fallback: giá điển hình
        if crop.TypicalPriceMin and crop.TypicalPriceMax:
            return (float(crop.TypicalPriceMin) + float(crop.TypicalPriceMax)) / 2
    except Exception as e:
        logger.warning(f"[NewsAPI] Lỗi lấy giá: {e}")
    return 0.0
