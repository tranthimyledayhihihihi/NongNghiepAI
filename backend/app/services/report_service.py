from collections import Counter, defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.harvest_service import harvest_service
from app.services.market_service import market_service
from app.services.quality_service import quality_service


class ReportService:
    def get_user_summary(self, db: Session, user_id: int, limit: int = 100) -> dict:
        market_history = market_service.get_history(db, user_id, limit)
        harvest_history = harvest_service.get_history(db, user_id, limit)
        quality_history = quality_service.get_history(db, user_id, limit)

        total_revenue = sum(float(item.get("estimated_profit") or 0) for item in market_history)
        total_quantity = sum(float(item.get("quantity") or 0) for item in market_history)

        quality_counts = Counter(item.get("quality_grade") or "unknown" for item in quality_history)
        monthly = defaultdict(float)
        for item in market_history:
            month = self._month_key(item.get("created_at"))
            monthly[month] += float(item.get("estimated_profit") or 0)

        monthly_revenue = [
            {"month": month, "revenue": revenue}
            for month, revenue in sorted(monthly.items())
        ]

        return {
            "total_revenue": total_revenue,
            "total_quantity": total_quantity,
            "quality_summary": dict(quality_counts),
            "top_quality_grade": quality_counts.most_common(1)[0][0] if quality_counts else None,
            "monthly_revenue": monthly_revenue,
            "harvest": harvest_history,
            "market": market_history,
            "quality": quality_history,
            "record_counts": {
                "harvest": len(harvest_history),
                "market": len(market_history),
                "quality": len(quality_history),
            },
            "generated_at": datetime.now(),
        }

    @staticmethod
    def _month_key(value) -> str:
        if isinstance(value, datetime):
            return value.strftime("%Y-%m")
        if isinstance(value, str) and value:
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m")
            except ValueError:
                return value[:7]
        return datetime.now().strftime("%Y-%m")


report_service = ReportService()
