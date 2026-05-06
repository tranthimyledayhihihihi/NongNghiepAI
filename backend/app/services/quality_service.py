import json
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.common import to_api_grade, to_db_grade
from app.repositories.quality_repository import (
    create_quality_check,
    get_quality_check_by_id,
    get_quality_checks_by_user,
)
from app.schemas.price_schema import PricingSuggestRequest
from app.services.pricing_service import pricing_service


class QualityService:
    @staticmethod
    def _get_detector():
        try:
            from ai_models.quality_check.detector import quality_detector

            return quality_detector
        except ImportError:
            try:
                from ai_models.yolo_inference import quality_detector

                return quality_detector
            except ImportError:
                return None

    def check_quality(
        self,
        db: Session,
        *,
        image_path: str,
        crop_name: str,
        region: str,
        user_id: Optional[int] = None,
    ) -> dict:
        detector = self._get_detector()
        if detector:
            try:
                analysis = detector.detect_quality(image_path)
                grade = analysis.get("quality_grade", "grade_1")
                confidence = analysis.get("confidence", 0.80)
                defects = analysis.get("defects", [])
                disease_detected = analysis.get("disease_detected", bool(defects))
                damage_level = analysis.get("damage_level", self._damage_level(grade))
            except Exception:
                detector = None

        if not detector:
            grade, confidence, defects = self._mock_grade(image_path)
            disease_detected = bool(defects)
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
            disease_detected=disease_detected,
            damage_level=damage_level,
            suggested_price=pricing["suggested_price"],
            confidence=confidence,
            user_id=user_id,
        )

        self._save_quality_record_direct(
            db=db,
            crop_name=crop_name,
            user_id=user_id,
            image_path=image_path,
            grade=grade,
            confidence=confidence,
            defects=defects,
            min_price=pricing["min_price"],
            max_price=pricing["max_price"],
            recommendations=self._recommendations(grade),
        )

        return {
            "crop_name": crop_name,
            "region": region,
            "image_path": image_path,
            "quality_grade": grade,
            "disease_detected": disease_detected,
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

    def get_history(self, db: Session, user_id: int, limit: int = 50) -> list[dict]:
        return [
            self._record_to_dict(record, crop)
            for record, crop in get_quality_checks_by_user(db, user_id, limit)
        ]

    def get_detail(self, db: Session, record_id: int) -> dict | None:
        result = get_quality_check_by_id(db, record_id)
        if result is None:
            return None
        record, crop = result
        return self._record_to_dict(record, crop)

    @staticmethod
    def _save_quality_record_direct(
        db: Session,
        crop_name: str,
        user_id: Optional[int],
        image_path: str,
        grade: str,
        confidence: float,
        defects: list,
        min_price: float,
        max_price: float,
        recommendations: list,
    ) -> None:
        if not user_id:
            return
        try:
            from app.models.crop import CropType
            from app.models.quality import QualityRecord

            crop = db.query(CropType).filter(CropType.CropName == crop_name).first()
            if not crop:
                return
            record = QualityRecord(
                UserID=user_id,
                CropID=crop.CropID,
                ImagePath=image_path,
                AIGrade=to_db_grade(grade),
                ConfidenceScore=confidence,
                DetectedIssues=json.dumps(defects, ensure_ascii=False),
                SuggestedPriceMin=min_price,
                SuggestedPriceMax=max_price,
                Recommendation="\n".join(recommendations),
            )
            db.add(record)
            db.commit()
        except Exception:
            db.rollback()

    @staticmethod
    def _mock_grade(image_path: str) -> tuple[str, float, list[str]]:
        lowered = image_path.lower()
        if "bad" in lowered or "grade3" in lowered or "grade_3" in lowered:
            return "grade_3", 0.68, ["surface_damage"]
        if "medium" in lowered or "grade2" in lowered or "grade_2" in lowered:
            return "grade_2", 0.76, ["minor_spot"]
        return "grade_1", 0.86, []

    @staticmethod
    def _damage_level(grade: str) -> str:
        return {
            "grade_1": "low",
            "Loại 1": "low",
            "grade_2": "medium",
            "Loại 2": "medium",
            "grade_3": "high",
            "Loại 3": "high",
        }.get(grade, "low")

    @staticmethod
    def _recommendations(grade: str) -> list[str]:
        if grade in ("grade_1", "Loại 1"):
            return ["Uu tien ban kenh sieu thi, cua hang sach hoac xuat khau."]
        if grade in ("grade_2", "Loại 2"):
            return ["Phu hop cho cho dau moi hoac thuong lai dia phuong."]
        return ["Nen ban nhanh hoac chuyen sang kenh che bien de giam hao hut."]

    @staticmethod
    def _record_to_dict(record, crop) -> dict:
        issues = QualityService._parse_issues(record.detected_issues)
        suggested_min = float(record.suggested_price_min or 0)
        suggested_max = float(record.suggested_price_max or 0)
        suggested_price = round((suggested_min + suggested_max) / 2, 2) if suggested_min or suggested_max else 0
        grade = to_api_grade(record.quality_grade)
        return {
            "record_id": record.id,
            "schedule_id": record.schedule_id,
            "user_id": record.user_id,
            "crop_id": crop.id,
            "crop_name": crop.name,
            "image_path": record.image_path,
            "quality_grade": grade,
            "disease_detected": bool(issues.get("disease_detected", False)),
            "damage_level": issues.get("damage_level") or QualityService._damage_level(grade),
            "suggested_price": suggested_price,
            "confidence": float(record.confidence_score or 0),
            "defects": issues.get("defects", []),
            "suggested_price_range": {
                "min": suggested_min,
                "max": suggested_max,
            },
            "recommendation": record.recommendation,
            "recommendations": QualityService._recommendations(grade),
            "checked_at": record.checked_at,
        }

    @staticmethod
    def _parse_issues(raw: str | None) -> dict:
        if not raw:
            return {}
        try:
            issues = json.loads(raw)
        except (TypeError, ValueError):
            return {"defects": [raw]}
        if not isinstance(issues, dict):
            return {"defects": issues if isinstance(issues, list) else [str(issues)]}
        defects = issues.get("defects")
        if defects is None and issues.get("disease_detected"):
            defects = ["detected_issue"]
        return {**issues, "defects": defects or []}


quality_service = QualityService()
