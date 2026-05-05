"""
Market Service - merged Tien (API interface + repository) + Quang (MARKET_CHANNELS logic)
- API endpoint dùng: suggest_market(db, request: MarketSuggestRequest)
"""
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.repositories.market_repository import create_market_suggestion
from app.schemas.market_schema import MarketSuggestRequest
from app.schemas.price_schema import PricingSuggestRequest
from app.services.pricing_service import pricing_service

# Bảng kênh bán hàng (Quang) - chi tiết hơn Tien
MARKET_CHANNELS = {
    "xuat_khau":  {"name": "Xuat khau", "commission": 0.18, "min_qty_kg": 1000, "quality_rank": 3, "price_factor": 1.35},
    "sieu_thi":   {"name": "Sieu thi / chuoi cua hang", "commission": 0.12, "min_qty_kg": 200, "quality_rank": 3, "price_factor": 1.20},
    "cho_dau_moi":{"name": "Cho dau moi", "commission": 0.07, "min_qty_kg": 100, "quality_rank": 2, "price_factor": 1.05},
    "thuong_lai": {"name": "Thuong lai dia phuong", "commission": 0.05, "min_qty_kg": 50, "quality_rank": 2, "price_factor": 0.95},
    "ban_le":     {"name": "Ban le truc tiep", "commission": 0.0, "min_qty_kg": 0, "quality_rank": 1, "price_factor": 1.15},
    "che_bien":   {"name": "Nha may che bien", "commission": 0.03, "min_qty_kg": 500, "quality_rank": 1, "price_factor": 0.70},
}

QUALITY_RANK = {
    "Loai 1": 3, "grade_1": 3,
    "Loai 2": 2, "grade_2": 2,
    "Loai 3": 1, "grade_3": 1,
    "Loại 1": 3, "Loại 2": 2, "Loại 3": 1,
}


class MarketService:

    def suggest_market(self, db: Session, request: MarketSuggestRequest) -> dict:
        """Gợi ý kênh bán hàng tối ưu dựa trên giá, số lượng và chất lượng."""
        pricing = pricing_service.suggest_price(
            db,
            PricingSuggestRequest(
                crop_name=request.crop_name,
                region=request.region,
                quantity=request.quantity,
                quality_grade=request.quality_grade,
            ),
        )
        base_price = pricing["suggested_price"]
        channels = self._build_channel_list(request.quantity, request.quality_grade, base_price)
        recommended = channels[0]
        warning = None if request.quantity < 5000 else "San luong lon, nen chia nhieu dot ban de giam rui ro gia."

        create_market_suggestion(
            db,
            crop_name=request.crop_name,
            region=request.region,
            quantity=request.quantity,
            quality_grade=request.quality_grade,
            recommended_channel=recommended["channel_name"],
            estimated_profit=recommended["estimated_total_revenue"],
            reason=recommended["reason"],
            warning=warning,
        )

        return {
            "crop_name": request.crop_name,
            "region": request.region,
            "recommended_channel": recommended["channel_name"],
            "reason": recommended["reason"],
            "profit_comparison": channels,
            "warning": warning,
        }

    @staticmethod
    def _build_channel_list(quantity: float, quality_grade: str, base_price: float) -> list[dict]:
        """Tính danh sách kênh eligible, sắp xếp theo doanh thu giảm dần."""
        quality_rank = QUALITY_RANK.get(quality_grade, 1)
        eligible = []
        for key, ch in MARKET_CHANNELS.items():
            if quantity >= ch["min_qty_kg"] and quality_rank >= ch["quality_rank"]:
                net = base_price * ch["price_factor"] * (1 - ch["commission"])
                eligible.append({
                    "channel": key,
                    "channel_name": ch["name"],
                    "commission_pct": int(ch["commission"] * 100),
                    "estimated_price": round(net, 2),
                    "estimated_total_revenue": round(net * quantity),
                    "estimated_revenue": round(net * quantity, 2),
                    "reason": (
                        f"Voi {quantity:.0f}kg chat luong {quality_grade}, "
                        f"kenh {ch['name']} mang lai doanh thu cao."
                    ),
                })

        if not eligible:
            net = base_price * 1.1
            eligible = [{
                "channel": "ban_le",
                "channel_name": "Ban le truc tiep",
                "commission_pct": 0,
                "estimated_price": round(net, 2),
                "estimated_total_revenue": round(net * quantity),
                "estimated_revenue": round(net * quantity, 2),
                "reason": "Kenh mac dinh cho san luong nho hoac chat luong thap.",
            }]

        eligible.sort(key=lambda x: x["estimated_total_revenue"], reverse=True)
        return eligible

    @staticmethod
    def _get_base_price_from_db(db: Session, crop_name: str, region: str) -> float | None:
        """Lấy giá cơ sở từ DB (Quang) - dùng khi không có pricing_service."""
        try:
            from app.models.crop import CropType
            from app.models.price import MarketPrice
            crop = db.query(CropType).filter(CropType.CropName == crop_name).first()
            if not crop:
                return None
            row = (
                db.query(MarketPrice)
                .filter(MarketPrice.CropID == crop.CropID, MarketPrice.Region == region)
                .order_by(desc(MarketPrice.PriceDate))
                .first()
            )
            if row:
                return float(row.PricePerKg)
            if crop.TypicalPriceMin and crop.TypicalPriceMax:
                return (float(crop.TypicalPriceMin) + float(crop.TypicalPriceMax)) / 2
        except Exception:
            pass
        return None


market_service = MarketService()
