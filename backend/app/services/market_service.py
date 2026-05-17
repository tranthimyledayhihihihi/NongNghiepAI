"""
Market Service - merged Tien (API interface + repository) + Quang (MARKET_CHANNELS logic)
- API endpoint dùng: suggest_market(db, request: MarketSuggestRequest)
"""
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.repositories.common import CHANNEL_API_TO_DB, to_api_grade
from app.repositories.market_repository import (
    DEFAULT_MARKET_CHANNELS,
    create_market_suggestion,
    get_active_channels,
    get_market_suggestions_by_user,
)
from app.schemas.market_schema import MarketSuggestRequest
from app.schemas.price_schema import PricingSuggestRequest
from app.services.pricing_service import pricing_service

# Bảng kênh bán hàng (Quang) - chi tiết hơn Tien
MARKET_CHANNELS = {
    "xuat_khau":  {"name": "Xuất khẩu", "commission": 0.18, "min_qty_kg": 1000, "quality_rank": 3, "price_factor": 1.35},
    "sieu_thi":   {"name": "Siêu thị / chuỗi cửa hàng", "commission": 0.12, "min_qty_kg": 200, "quality_rank": 3, "price_factor": 1.20},
    "cho_dau_moi":{"name": "Chợ đầu mối", "commission": 0.07, "min_qty_kg": 100, "quality_rank": 2, "price_factor": 1.05},
    "thuong_lai": {"name": "Thương lái địa phương", "commission": 0.05, "min_qty_kg": 50, "quality_rank": 2, "price_factor": 0.95},
    "ban_le":     {"name": "Bán lẻ trực tiếp", "commission": 0.0, "min_qty_kg": 0, "quality_rank": 1, "price_factor": 1.15},
    "che_bien":   {"name": "Nhà máy chế biến", "commission": 0.03, "min_qty_kg": 500, "quality_rank": 1, "price_factor": 0.70},
}

QUALITY_RANK = {
    "Loai 1": 3, "grade_1": 3,
    "Loai 2": 2, "grade_2": 2,
    "Loai 3": 1, "grade_3": 1,
    "Loại 1": 3, "Loại 2": 2, "Loại 3": 1,
}
QUALITY_LABELS = {
    "grade_1": "Loại 1",
    "grade_2": "Loại 2",
    "grade_3": "Loại 3",
    "Loai 1": "Loại 1",
    "Loai 2": "Loại 2",
    "Loai 3": "Loại 3",
}


class MarketService:

    def suggest_market(self, db: Session, request: MarketSuggestRequest, user_id: int | None = None) -> dict:
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
        channel_source = self.get_channels(db, request.region)
        channels = self._build_channel_list(
            request.quantity,
            request.quality_grade,
            base_price,
            channel_source["channels"],
        )
        recommended = channels[0]
        warning = None if request.quantity < 5000 else "Sản lượng lớn, nên chia nhiều đợt bán để giảm rủi ro giá."

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
            user_id=user_id,
        )

        return {
            "crop_name": request.crop_name,
            "region": request.region,
            "recommended_channel": recommended["channel_name"],
            "reason": recommended["reason"],
            "profit_comparison": channels,
            "warning": warning,
            "source": channel_source["source"],
            "is_mock": channel_source["is_mock"],
            "pricing_source": pricing.get("source_name"),
        }

    def get_channels(self, db: Session, region: str | None = None) -> dict:
        rows = get_active_channels(db, region)
        if rows:
            channels = [
                {
                    "id": row.ChannelCode,
                    "channel_code": row.ChannelCode,
                    "name": row.ChannelName,
                    "channel_name": row.ChannelName,
                    "commission": f"{row.CommissionRate * 100:.0f}%",
                    "commission_rate": float(row.CommissionRate),
                    "min_quantity_kg": float(row.MinQuantityKg),
                    "required_quality_rank": int(row.RequiredQualityRank),
                    "price_factor": float(row.PriceFactor),
                    "region": row.Region,
                }
                for row in rows
            ]
            return {"channels": channels, "source": "database", "is_mock": False}

        channels = [
            {
                "id": channel["code"],
                "channel_code": channel["code"],
                "name": channel["name"],
                "channel_name": channel["name"],
                "commission": f"{channel['commission'] * 100:.0f}%",
                "commission_rate": channel["commission"],
                "min_quantity_kg": channel["min_qty"],
                "required_quality_rank": channel["quality_rank"],
                "price_factor": channel["price_factor"],
                "region": None,
            }
            for channel in DEFAULT_MARKET_CHANNELS
        ]
        return {"channels": channels, "source": "fallback", "is_mock": True}

    def get_history(self, db: Session, user_id: int, limit: int = 50) -> list[dict]:
        return [
            {
                "suggestion_id": suggestion.id,
                "user_id": suggestion.user_id,
                "crop_id": crop.id,
                "crop_name": crop.name,
                "region": suggestion.region,
                "quantity": suggestion.quantity_kg,
                "quality_grade": to_api_grade(suggestion.quality_grade),
                "recommended_channel": self._channel_to_api(suggestion.recommended_channel),
                "estimated_profit": float(suggestion.estimated_profit or 0),
                "reason": suggestion.reason,
                "warning": suggestion.warning,
                "created_at": suggestion.created_at,
            }
            for suggestion, crop in get_market_suggestions_by_user(db, user_id, limit)
        ]

    @staticmethod
    def _build_channel_list(
        quantity: float,
        quality_grade: str,
        base_price: float,
        channel_definitions: list[dict],
    ) -> list[dict]:
        """Tính danh sách kênh eligible, sắp xếp theo doanh thu giảm dần."""
        quality_rank = QUALITY_RANK.get(quality_grade, 1)
        quality_label = QUALITY_LABELS.get(quality_grade, quality_grade)
        eligible = []
        for ch in channel_definitions:
            key = ch["channel_code"]
            if quantity >= ch["min_quantity_kg"] and quality_rank >= ch["required_quality_rank"]:
                net = base_price * ch["price_factor"] * (1 - ch["commission_rate"])
                eligible.append({
                    "channel": key,
                    "channel_name": ch["channel_name"],
                    "commission_pct": int(ch["commission_rate"] * 100),
                    "estimated_price": round(net, 2),
                    "estimated_total_revenue": round(net * quantity),
                    "estimated_revenue": round(net * quantity, 2),
                    "reason": (
                        f"Với {quantity:.0f}kg chất lượng {quality_label}, "
                        f"kênh {ch['channel_name']} mang lại doanh thu cao."
                    ),
                })

        if not eligible:
            net = base_price * 1.1
            eligible = [{
                "channel": "ban_le",
                "channel_name": "Bán lẻ trực tiếp",
                "commission_pct": 0,
                "estimated_price": round(net, 2),
                "estimated_total_revenue": round(net * quantity),
                "estimated_revenue": round(net * quantity, 2),
                "reason": "Kênh mặc định cho sản lượng nhỏ hoặc chất lượng thấp.",
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

    @staticmethod
    def _channel_to_api(value: str | None) -> str:
        if not value:
            return "retail"
        db_to_api = {
            CHANNEL_API_TO_DB["retail"]: "retail",
            CHANNEL_API_TO_DB["wholesale"]: "wholesale",
            CHANNEL_API_TO_DB["export"]: "export",
        }
        return db_to_api.get(value, value)


market_service = MarketService()
