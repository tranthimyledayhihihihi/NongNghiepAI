"""P2-12: Market Service"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

MARKET_CHANNELS = {
    "xuat_khau":  {"name": "Xuat khau", "commission": 0.18, "min_qty_kg": 1000, "quality_rank": 3, "price_factor": 1.35},
    "sieu_thi":   {"name": "Sieu thi / chuoi cua hang", "commission": 0.12, "min_qty_kg": 200, "quality_rank": 3, "price_factor": 1.20},
    "cho_dau_moi":{"name": "Cho dau moi", "commission": 0.07, "min_qty_kg": 100, "quality_rank": 2, "price_factor": 1.05},
    "thuong_lai": {"name": "Thuong lai dia phuong", "commission": 0.05, "min_qty_kg": 50, "quality_rank": 2, "price_factor": 0.95},
    "ban_le":     {"name": "Ban le truc tiep", "commission": 0.0, "min_qty_kg": 0, "quality_rank": 1, "price_factor": 1.15},
    "che_bien":   {"name": "Nha may che bien", "commission": 0.03, "min_qty_kg": 500, "quality_rank": 1, "price_factor": 0.70},
}

QUALITY_RANK = {"Loai 1": 3, "grade_1": 3, "Loai 2": 2, "grade_2": 2, "Loai 3": 1, "grade_3": 1,
                "Lo\u1ea1i 1": 3, "Lo\u1ea1i 2": 2, "Lo\u1ea1i 3": 1}


class MarketService:
    def suggest_market(self, db, crop_name, region, quantity_kg, quality_grade, base_price=None, trend="stable"):
        if base_price is None:
            base_price = self._get_base_price(db, crop_name, region) or 20000.0
        quality_rank = QUALITY_RANK.get(quality_grade, 1)
        eligible = []
        for key, ch in MARKET_CHANNELS.items():
            if quantity_kg >= ch["min_qty_kg"] and quality_rank >= ch["quality_rank"]:
                net = base_price * ch["price_factor"] * (1 - ch["commission"])
                eligible.append({
                    "channel_id": key,
                    "channel_name": ch["name"],
                    "commission_pct": int(ch["commission"] * 100),
                    "estimated_price_per_kg": round(net),
                    "estimated_total_revenue": round(net * quantity_kg),
                })
        if not eligible:
            eligible = [{"channel_id": "ban_le", "channel_name": "Ban le",
                         "commission_pct": 0,
                         "estimated_price_per_kg": round(base_price * 1.1),
                         "estimated_total_revenue": round(base_price * 1.1 * quantity_kg)}]
        eligible.sort(key=lambda x: x["estimated_total_revenue"], reverse=True)
        best = eligible[0]
        warning = None
        if trend == "decreasing":
            warning = "Gia dang giam - nen ban som."
        elif trend == "increasing" and quality_rank >= 2:
            warning = "Gia dang tang - co the cho them de ban gia tot hon."
        return {
            "crop_name": crop_name, "region": region,
            "recommended_channel": best["channel_name"],
            "reason": f"Voi {quantity_kg:.0f}kg chat luong {quality_grade}, kenh {best['channel_name']} mang lai doanh thu cao nhat.",
            "profit_comparison": eligible,
            "warning": warning,
        }

    @staticmethod
    def _get_base_price(db, crop_name, region):
        try:
            from ..models.crop import CropType
            from ..models.price import MarketPrice
            crop = db.query(CropType).filter(CropType.CropName == crop_name).first()
            if not crop:
                return None
            row = db.query(MarketPrice).filter(
                MarketPrice.CropID == crop.CropID, MarketPrice.Region == region
            ).order_by(desc(MarketPrice.PriceDate)).first()
            if row:
                return float(row.PricePerKg)
            if crop.TypicalPriceMin and crop.TypicalPriceMax:
                return (float(crop.TypicalPriceMin) + float(crop.TypicalPriceMax)) / 2
        except Exception:
            pass
        return None


market_service = MarketService()
