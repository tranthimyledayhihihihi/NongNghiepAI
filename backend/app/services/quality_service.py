from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.quality_repository import create_quality_check
from app.schemas.price_schema import PricingSuggestRequest
from app.services.pricing_service import pricing_service


class QualityService:
    def check_quality(self, db: Session, *, image_path: str, crop_name: str, region: str) -> dict:
        grade, confidence, defects = self._mock_grade(image_path)
        damage_level = self._damage_level(grade)
        pricing = pricing_service.suggest_price(
            db,
            PricingSuggestRequest(
                crop_name=crop_name,
                region=region,
                quantity=1,
                quality_grade=grade,
            ),
        )

        record = create_quality_check(
            db,
            crop_name=crop_name,
            region=region,
            image_path=image_path,
            quality_grade=grade,
            disease_detected=bool(defects),
            damage_level=damage_level,
            suggested_price=pricing["suggested_price"],
            confidence=confidence,
        )

        return {
            "crop_name": crop_name,
            "region": region,
            "image_path": image_path,
            "quality_grade": grade,
            "disease_detected": bool(defects),
            "damage_level": damage_level,
            "suggested_price": pricing["suggested_price"],
            "confidence": confidence,
            "defects": defects,
            "suggested_price_range": {
                "min": pricing["min_price"],
                "max": pricing["max_price"],
            },
            "recommendations": self._recommendations(grade),
            "checked_at": getattr(record, "checked_at", None) or datetime.now(),
        }

    @staticmethod
    def _mock_grade(image_path: str) -> tuple[str, float, list[str]]:
        lowered = image_path.lower()
        if "bad" in lowered or "grade3" in lowered:
            return "grade_3", 0.68, ["surface_damage"]
        if "medium" in lowered or "grade2" in lowered:
            return "grade_2", 0.76, ["minor_spot"]
        return "grade_1", 0.86, []

    @staticmethod
    def _damage_level(grade: str) -> str:
        return {"grade_1": "low", "grade_2": "medium", "grade_3": "high"}.get(grade, "low")

    @staticmethod
    def _recommendations(grade: str) -> list[str]:
        if grade == "grade_1":
            return ["Uu tien ban kenh sieu thi, cua hang sach hoac xuat khau."]
        if grade == "grade_2":
            return ["Phu hop cho cho dau moi hoac thuong lai dia phuong."]
        return ["Nen ban nhanh hoac chuyen sang kenh che bien de giam hao hut."]


quality_service = QualityService()
