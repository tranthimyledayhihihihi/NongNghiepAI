from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta

from app.core.database import get_db
from app.models.price import MarketPrice, PriceHistory
from app.models.crop import CropType
from pydantic import BaseModel

router = APIRouter(prefix="/api/crawler", tags=["Crawler Data"])


class CrawledPriceData(BaseModel):
    crop_name: str
    region: str
    price_per_kg: float
    source_name: str
    price_date: date

    class Config:
        from_attributes = True


@router.get("/latest-crawled-data", response_model=List[CrawledPriceData])
async def get_latest_crawled_data(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    days: int = Query(7, ge=1, le=90, description="Lấy dữ liệu trong N ngày gần nhất"),
    crop_name: Optional[str] = Query(None, description="Lọc theo tên cây trồng (ví dụ: Sầu riêng)"),
    region: Optional[str] = Query(None, description="Lọc theo vùng (ví dụ: Đắk Lắk)"),
):
    """
    Lấy dữ liệu giá nông sản được cào về.

    - **days**: Lọc trong N ngày gần nhất (mặc định 7 ngày)
    - **crop_name**: Lọc theo tên cây trồng (tìm kiếm gần đúng)
    - **region**: Lọc theo vùng địa lý (tìm kiếm gần đúng)
    - **limit**: Số bản ghi tối đa trả về
    """
    since = date.today() - timedelta(days=days)

    query = (
        db.query(MarketPrice, CropType.CropName)
        .join(CropType, MarketPrice.CropID == CropType.CropID)
        .filter(MarketPrice.PriceDate >= since)
    )

    if crop_name:
        query = query.filter(CropType.CropName.ilike(f"%{crop_name}%"))

    if region:
        query = query.filter(MarketPrice.Region.ilike(f"%{region}%"))

    rows = query.order_by(MarketPrice.PriceDate.desc()).limit(limit).all()

    return [
        CrawledPriceData(
            crop_name=name,
            region=mp.Region,
            price_per_kg=float(mp.PricePerKg),
            source_name=mp.SourceName,
            price_date=mp.PriceDate,
        )
        for mp, name in rows
    ]


@router.get("/summary", response_model=List[dict])
async def get_crawl_summary(
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=90, description="Thống kê trong N ngày gần nhất"),
):
    """
    Thống kê tổng hợp giá trung bình, min, max theo từng loại cây và vùng
    trong N ngày gần nhất.
    """
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            CropType.CropName,
            MarketPrice.Region,
            func.avg(MarketPrice.PricePerKg).label("avg_price"),
            func.min(MarketPrice.PricePerKg).label("min_price"),
            func.max(MarketPrice.PricePerKg).label("max_price"),
            func.count().label("data_points"),
            func.max(MarketPrice.PriceDate).label("latest_date"),
        )
        .join(CropType, MarketPrice.CropID == CropType.CropID)
        .filter(MarketPrice.PriceDate >= since)
        .group_by(CropType.CropName, MarketPrice.Region)
        .order_by(CropType.CropName, MarketPrice.Region)
        .all()
    )

    return [
        {
            "crop_name": r.CropName,
            "region": r.Region,
            "avg_price": round(float(r.avg_price), 0),
            "min_price": round(float(r.min_price), 0),
            "max_price": round(float(r.max_price), 0),
            "data_points": r.data_points,
            "latest_date": str(r.latest_date),
            "period_days": days,
        }
        for r in rows
    ]


@router.get("/standard-price")
async def get_standard_price(
    crop_name: str = Query(..., description="Tên cây trồng (ví dụ: Sầu riêng)"),
    region: Optional[str] = Query(None, description="Tỉnh/thành (để trống để lấy tất cả vùng)"),
    days: int = Query(7, ge=1, le=30, description="Số ngày tính giá trung bình"),
    db: Session = Depends(get_db),
):
    """
    Trả về **giá chuẩn** của một loại nông sản tính từ dữ liệu thực tế đã cào.

    Giá chuẩn = trung bình có trọng số của MarketPrices + PriceHistory trong N ngày,
    kết hợp:
    - avg_market: trung bình giá thị trường thực tế
    - avg_history: trung bình lịch sử (PriceHistory)
    - trend: xu hướng tăng/giảm so với 7 ngày trước
    """
    since = date.today() - timedelta(days=days)
    prev_since = since - timedelta(days=days)

    # --- Giá từ MarketPrices (dữ liệu cào thực tế) ---
    mq = (
        db.query(
            func.avg(MarketPrice.PricePerKg).label("avg"),
            func.min(MarketPrice.PricePerKg).label("mn"),
            func.max(MarketPrice.PricePerKg).label("mx"),
            func.count().label("cnt"),
        )
        .join(CropType, MarketPrice.CropID == CropType.CropID)
        .filter(CropType.CropName.ilike(f"%{crop_name}%"))
        .filter(MarketPrice.PriceDate >= since)
    )
    if region:
        mq = mq.filter(MarketPrice.Region.ilike(f"%{region}%"))
    market_row = mq.first()

    # --- Giá từ PriceHistory (dữ liệu tổng hợp) ---
    hq = (
        db.query(
            func.avg(PriceHistory.AvgPrice).label("avg"),
            func.min(PriceHistory.MinPrice).label("mn"),
            func.max(PriceHistory.MaxPrice).label("mx"),
            func.count().label("cnt"),
        )
        .join(CropType, PriceHistory.CropID == CropType.CropID)
        .filter(CropType.CropName.ilike(f"%{crop_name}%"))
        .filter(PriceHistory.RecordDate >= since)
    )
    if region:
        hq = hq.filter(PriceHistory.Region.ilike(f"%{region}%"))
    history_row = hq.first()

    # --- Giá kỳ trước để tính xu hướng ---
    prev_q = (
        db.query(func.avg(PriceHistory.AvgPrice).label("avg"))
        .join(CropType, PriceHistory.CropID == CropType.CropID)
        .filter(CropType.CropName.ilike(f"%{crop_name}%"))
        .filter(PriceHistory.RecordDate >= prev_since)
        .filter(PriceHistory.RecordDate < since)
    )
    if region:
        prev_q = prev_q.filter(PriceHistory.Region.ilike(f"%{region}%"))
    prev_row = prev_q.first()

    market_avg = float(market_row.avg) if market_row and market_row.avg else None
    history_avg = float(history_row.avg) if history_row and history_row.avg else None
    prev_avg = float(prev_row.avg) if prev_row and prev_row.avg else None

    if market_avg is None and history_avg is None:
        raise HTTPException(
            status_code=404,
            detail=f"Chưa có dữ liệu giá cho '{crop_name}'"
                   + (f" tại '{region}'" if region else "")
                   + f" trong {days} ngày qua. Hãy đợi crawler cập nhật.",
        )

    # Giá chuẩn = trung bình có trọng số (market 60%, history 40%)
    if market_avg and history_avg:
        standard_price = round(market_avg * 0.6 + history_avg * 0.4, -2)
    else:
        standard_price = round((market_avg or history_avg), -2)

    # Xu hướng giá
    trend = "ổn định"
    trend_pct = 0.0
    ref_price = history_avg or market_avg
    if prev_avg and ref_price:
        trend_pct = round((ref_price - prev_avg) / prev_avg * 100, 2)
        if trend_pct > 3:
            trend = "tăng"
        elif trend_pct < -3:
            trend = "giảm"

    return {
        "crop_name": crop_name,
        "region": region or "Tất cả vùng",
        "period_days": days,
        "standard_price": standard_price,
        "market_avg": round(market_avg, -2) if market_avg else None,
        "history_avg": round(history_avg, -2) if history_avg else None,
        "min_price": round(float(market_row.mn or history_row.mn), -2) if (market_row and market_row.mn) or (history_row and history_row.mn) else None,
        "max_price": round(float(market_row.mx or history_row.mx), -2) if (market_row and market_row.mx) or (history_row and history_row.mx) else None,
        "data_points": (market_row.cnt or 0) + (history_row.cnt or 0),
        "trend": trend,
        "trend_pct": trend_pct,
        "unit": "VNĐ/kg",
        "as_of": date.today().isoformat(),
    }