from sqlalchemy.orm import Session

from app.repositories.market_repository import create_market_suggestion
from app.schemas.market_schema import MarketSuggestRequest
from app.schemas.price_schema import PricingSuggestRequest
from app.services.pricing_service import pricing_service


class MarketService:
    def suggest_market(self, db: Session, request: MarketSuggestRequest) -> dict:
        pricing = pricing_service.suggest_price(
            db,
            PricingSuggestRequest(
                crop_name=request.crop_name,
                region=request.region,
                quantity=request.quantity,
                quality_grade=request.quality_grade,
            ),
        )
        channels = self._channels(request.quantity, request.quality_grade, pricing["suggested_price"])
        recommended = channels[0]
        warning = None if request.quantity < 5000 else "San luong lon, nen chia nhieu dot ban de giam rui ro gia."
        create_market_suggestion(
            db,
            crop_name=request.crop_name,
            region=request.region,
            quantity=request.quantity,
            quality_grade=request.quality_grade,
            recommended_channel=recommended["channel"],
            estimated_profit=recommended["estimated_revenue"],
            reason=recommended["reason"],
            warning=warning,
        )

        return {
            "crop_name": request.crop_name,
            "region": request.region,
            "recommended_channel": recommended["channel"],
            "reason": recommended["reason"],
            "profit_comparison": channels,
            "warning": warning,
        }

    @staticmethod
    def _channels(quantity: float, quality_grade: str, suggested_price: float) -> list[dict]:
        if quality_grade == "grade_1" and quantity >= 500:
            ordered = [
                ("supermarket", 1.08, "Chat luong cao, du san luong cho kenh gia tri cao."),
                ("wholesale", 0.96, "Thanh khoan nhanh voi san luong lon."),
                ("retail", 1.0, "Bien loi tot nhung can tu ban le."),
            ]
        elif quantity >= 1000:
            ordered = [
                ("wholesale", 0.96, "Phu hop ban nhanh san luong lon."),
                ("processor", 0.88, "Giam rui ro ton kho khi chat luong khong dong deu."),
                ("retail", 1.0, "Can nhieu nhan luc ban hang."),
            ]
        else:
            ordered = [
                ("retail", 1.0, "San luong vua, co the giu bien loi tot."),
                ("wholesale", 0.94, "Ban nhanh nhung gia thap hon."),
                ("processor", 0.85, "Phu hop khi can xa hang nhanh."),
            ]

        return [
            {
                "channel": channel,
                "estimated_price": round(suggested_price * factor, 2),
                "estimated_revenue": round(suggested_price * factor * quantity, 2),
                "reason": reason,
            }
            for channel, factor, reason in ordered
        ]


market_service = MarketService()
